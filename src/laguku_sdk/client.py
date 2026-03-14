import os
import aiohttp
import asyncio
from typing import Optional, List
from loguru import logger

from laguku_sdk.models import Song, ProviderType, TrackMetadata, StreamInfo, LagukuConfig
from laguku_sdk.core.spotify import SpotifyInternal
from laguku_sdk.core.songlink import SongLinkResolver
from laguku_sdk.core.downloader import AsyncDownloader
from laguku_sdk.core.ffmpeg import FFmpegProcessor
from laguku_sdk.core.tagger import MetadataTagger
from laguku_sdk.core.lyrics import LyricsResolver
from laguku_sdk.core.utils import sanitize_filename, build_filename
from laguku_sdk.providers.amazon import AmazonProvider
from laguku_sdk.providers.tidal import TidalProvider
from laguku_sdk.providers.qobuz import QobuzProvider
from laguku_sdk.exceptions import LagukuError

class LagukuClient:
    def __init__(
        self, 
        preferred_providers: List[ProviderType] = None,
        spotify_client_id: Optional[str] = None,
        spotify_client_secret: Optional[str] = None,
        config: Optional[LagukuConfig] = None
    ):
        self.config = config or LagukuConfig()
        self.preferred_providers = preferred_providers or self.config.preferred_providers or [
            ProviderType.QOBUZ,
            ProviderType.TIDAL,
            ProviderType.AMAZON
        ]
        self.spotify_creds = {"client_id": spotify_client_id, "client_secret": spotify_client_secret}
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Session-persistent components
        self._spotify: Optional[SpotifyInternal] = None
        self._songlink: Optional[SongLinkResolver] = None
        self._lyrics: Optional[LyricsResolver] = None

    def _get_spotify(self) -> SpotifyInternal:
        if not self._spotify:
            self._spotify = SpotifyInternal(self.session, **self.spotify_creds)
        return self._spotify

    def _get_songlink(self) -> SongLinkResolver:
        if not self._songlink:
            self._songlink = SongLinkResolver(self.session)
        return self._songlink

    def _get_lyrics(self) -> LyricsResolver:
        if not self._lyrics:
            self._lyrics = LyricsResolver(self.session)
        return self._lyrics

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def download_playlist(
        self, 
        playlist_query: str, 
        output_dir: str = "downloads", 
        output_format: Optional[str] = None,
        concurrency: Optional[int] = None
    ) -> List[Song]:
        if not self.session: self.session = aiohttp.ClientSession()
        spotify = self._get_spotify()
        playlist_id = playlist_query.split("/playlist/")[-1].split("?")[0] if "spotify.com" in playlist_query else playlist_query
        
        name, track_ids = await spotify.get_playlist_info(playlist_id)
        final_dir = os.path.join(output_dir, sanitize_filename(name))
        return await self._download_collection(
            track_ids, 
            final_dir, 
            output_format or self.config.default_format, 
            concurrency or self.config.concurrency
        )

    async def download_album(
        self, 
        album_query: str, 
        output_dir: str = "downloads", 
        output_format: Optional[str] = None,
        concurrency: Optional[int] = None
    ) -> List[Song]:
        if not self.session: self.session = aiohttp.ClientSession()
        spotify = self._get_spotify()
        album_id = album_query.split("/album/")[-1].split("?")[0] if "spotify.com" in album_query else album_query
        
        name, track_ids = await spotify.get_album_info(album_id)
        final_dir = os.path.join(output_dir, sanitize_filename(name))
        return await self._download_collection(
            track_ids, 
            final_dir, 
            output_format or self.config.default_format, 
            concurrency or self.config.concurrency
        )

    async def download_artist(
        self, 
        artist_query: str, 
        output_dir: str = "downloads", 
        output_format: Optional[str] = None,
        concurrency: Optional[int] = None
    ) -> List[Song]:
        if not self.session: self.session = aiohttp.ClientSession()
        spotify = self._get_spotify()
        artist_id = artist_query.split("/artist/")[-1].split("?")[0] if "spotify.com" in artist_query else artist_query
        
        name, track_ids = await spotify.get_artist_info(artist_id)
        final_dir = os.path.join(output_dir, sanitize_filename(name))
        return await self._download_collection(
            track_ids, 
            final_dir, 
            output_format or self.config.default_format, 
            concurrency or self.config.concurrency
        )

    async def _download_collection(self, track_ids: List[str], output_dir: str, output_format: str, concurrency: int) -> List[Song]:
        logger.info(f"Downloading {len(track_ids)} tracks to {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
        semaphore = asyncio.Semaphore(concurrency)
        async def limited_download(tid):
            async with semaphore:
                try:
                    return await self.download(tid, output_dir=output_dir, output_format=output_format)
                except Exception as e:
                    logger.error(f"Failed to download track {tid}: {e}")
                    return None

        tasks = [limited_download(tid) for tid in track_ids]
        results = await asyncio.gather(*tasks)
        return [s for s in results if s is not None]

    async def download(self, query: str, output_dir: str = "downloads", output_format: Optional[str] = None) -> Song:
        if not self.session:
            self.session = aiohttp.ClientSession()

        os.makedirs(output_dir, exist_ok=True)
        spotify = self._get_spotify()

        # 1. Detect query type
        track_id = None
        if "spotify.com" in query:
            track_id = query.split("/track/")[-1].split("?")[0]
        elif len(query) == 22 and not " " in query:
            track_id = query
        else:
            logger.info(f"Searching for: {query}")
            search_results = await spotify.search(query, limit=1)
            if not search_results: raise LagukuError(f"No results found: {query}")
            
            # Extract ID from search result
            first_result = search_results[0]
            if "item" in first_result:
                track_id = first_result['item']['data']['id']
            else:
                track_id = first_result['item']['data']['id'] 

        # 2. Get Metadata
        logger.info(f"Fetching metadata for: {track_id}")
        metadata = await spotify.get_track_metadata(track_id)
        
        resolver = self._get_songlink()
        metadata.isrc = await resolver.get_isrc(track_id)

        # 3. Resolve Stream with Format Logic
        requested_format = output_format or self.config.default_format
        # For 'auto', we resolve as flac but preserve whatever we get
        resolve_format = "flac" if requested_format == "auto" else requested_format

        stream_info = None
        selected_provider = None
        providers = {
            ProviderType.QOBUZ: QobuzProvider(self.session),
            ProviderType.TIDAL: TidalProvider(self.session),
            ProviderType.AMAZON: AmazonProvider(self.session)
        }

        for p_type in self.preferred_providers:
            provider = providers.get(p_type)
            if not provider: continue
            try:
                logger.info(f"Trying provider: {p_type.value}")
                stream_info = await provider.resolve_stream(metadata, target_format=resolve_format)
                selected_provider = p_type
                break
            except Exception as e:
                logger.warning(f"Provider {p_type.value} failed: {e}")

        if not stream_info:
            raise LagukuError("Could not resolve stream")

        # 4. Download Pipeline
        downloader = AsyncDownloader(self.session)
        display_name = build_filename(metadata, self.config.filename_format)
        
        source_ext = f".{stream_info.format}"
        temp_file = os.path.join(output_dir, f"{display_name}.tmp{source_ext}")
        
        # Final extension logic
        if requested_format == "auto":
            final_ext = source_ext # Preserve source
        else:
            final_ext = f".{requested_format.lower()}"
            
        final_file = os.path.join(output_dir, f"{display_name}{final_ext}")

        logger.info(f"Downloading {stream_info.format.upper()} stream from {selected_provider.value}...")
        if stream_info.is_manifest:
            await downloader.download_manifest(stream_info.url.replace("MANIFEST:", ""), temp_file)
        else:
            await downloader.download_file(stream_info.url, temp_file)

        # 5. Processing
        ffmpeg = FFmpegProcessor()
        if stream_info.decryption_key:
            logger.info("Decrypting media...")
            dec_file = temp_file.replace(".tmp", ".dec")
            await ffmpeg.decrypt_amazon(temp_file, dec_file, stream_info.decryption_key)
            os.remove(temp_file)
            temp_file = dec_file

        # Only convert if explicit target differs from source or we decrypted
        if (requested_format != "auto" and source_ext != final_ext) or stream_info.decryption_key:
            logger.info(f"Processing/Converting to {final_ext[1:].upper()}...")
            if final_ext == ".mp3":
                await ffmpeg.convert_to_mp3(temp_file, final_file)
            elif final_ext == ".m4a":
                await ffmpeg.convert_to_alac(temp_file, final_file)
            else:
                await ffmpeg.convert_to_flac(temp_file, final_file)
            os.remove(temp_file)
        else:
            if os.path.exists(final_file): os.remove(final_file)
            os.rename(temp_file, final_file)

        # 6. Metadata Enrichment
        if self.config.embed_lyrics:
            lyrics_resolver = self._get_lyrics()
            metadata.lyrics = await lyrics_resolver.fetch_lrclib(metadata.title, metadata.artist, metadata.album)
        
        cover_data = None
        if metadata.cover_url:
            async with self.session.get(metadata.cover_url) as resp:
                cover_data = await resp.read()

        # 7. Tagging
        tagger = MetadataTagger()
        tagger.embed(final_file, metadata, cover_data)

        return Song(
            id=track_id,
            title=metadata.title,
            artist=metadata.artist,
            album=metadata.album or "Unknown",
            provider=selected_provider,
            duration=metadata.duration_ms or 0,
            bitrate=stream_info.bitrate,
            cover_url=metadata.cover_url,
            lyrics=metadata.lyrics.content if metadata.lyrics else None,
            stream_url=stream_info.url,
            file_path=final_file,
            metadata=metadata
        )
