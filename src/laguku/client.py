import asyncio
import aiohttp
import os
from typing import Optional, List, Dict, Any, Union
from loguru import logger

from laguku.config import LagukuConfig, ProviderType
from laguku.models import Song, TrackMetadata
from laguku.core.metadata import MetadataProcessor
from laguku.core.downloader import Downloader
from laguku.core.processor import Tagger # The post-processor
from laguku.core.utils import sanitize_filename, build_filename
from laguku.providers.registry import ProviderRegistry
import laguku.providers # Trigger registration
from laguku.exceptions import LagukuError, ResolutionError

class AsyncLaguku:
    """
    The asynchronous implementation of the Laguku SDK.
    """
    def __init__(self, **config_params):
        self.config = LagukuConfig.from_dict(config_params)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def search(self, query: str, limit: int = 10, **overrides) -> List[Dict[str, Any]]:
        """
        Search for tracks on Spotify.
        """
        config = self.config.merge(**overrides)
        session = await self._get_session()
        mp = MetadataProcessor(session, config)
        return await mp._spotify.search(query, limit=limit)

    async def download(self, query: str, **overrides) -> Song:
        """
        Download a single track asynchronously.
        """
        config = self.config.merge(**overrides)
        session = await self._get_session()
        
        # 1. Metadata resolution
        metadata_processor = MetadataProcessor(session, config)
        metadata = await metadata_processor.resolve(query)
        
        # 2. Provider resolution (with 'auto' logic)
        stream_info = None
        selected_provider = None
        
        if config.provider == ProviderType.AUTO:
            logger.info(f"Auto-resolving stream via preferred providers: {[p.value for p in config.preferred_providers]}")
            for p_type in config.preferred_providers:
                provider_cls = ProviderRegistry.get_provider_class(p_type)
                if not provider_cls: continue
                
                try:
                    logger.debug(f"Trying provider: {p_type.value}")
                    provider = provider_cls(session, config)
                    stream_info = await provider.resolve_stream(metadata)
                    if stream_info:
                        selected_provider = p_type
                        break
                except Exception as e:
                    logger.warning(f"Provider {p_type.value} failed: {e}")
        else:
            # Single provider specified
            provider_cls = ProviderRegistry.get_provider_class(config.provider)
            if not provider_cls:
                raise LagukuError(f"Provider '{config.provider}' is not registered or supported.")
            
            provider = provider_cls(session, config)
            stream_info = await provider.resolve_stream(metadata)
            selected_provider = config.provider
        
        if not stream_info:
            raise ResolutionError(f"Could not resolve stream for '{metadata.title}' via {config.provider}")

        # 3. Download & Process
        filename = build_filename(metadata, config.filename_format)
        downloader = Downloader(session, config)
        temp_file = await downloader.download(stream_info, filename)
        
        processor = Tagger(session, config)
        final_file = await processor.process(temp_file, metadata, stream_info, filename)
        
        return Song(
            id=metadata.spotify_id,
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

    async def download_playlist(self, query: str, **overrides) -> List[Song]:
        """Download all tracks from a Spotify playlist."""
        config = self.config.merge(**overrides)
        session = await self._get_session()
        # Access internal spotify instance
        mp = MetadataProcessor(session, config)
        spotify = mp._spotify
        
        playlist_id = query.split("/playlist/")[-1].split("?")[0] if "spotify.com" in query else query
        name, track_ids = await spotify.get_playlist_info(playlist_id)
        
        output_dir = os.path.join(config.output_dir, sanitize_filename(name))
        return await self._download_collection(track_ids, output_dir, config)

    async def download_album(self, query: str, **overrides) -> List[Song]:
        """Download all tracks from a Spotify album."""
        config = self.config.merge(**overrides)
        session = await self._get_session()
        mp = MetadataProcessor(session, config)
        spotify = mp._spotify
        
        album_id = query.split("/album/")[-1].split("?")[0] if "spotify.com" in query else query
        name, track_ids = await spotify.get_album_info(album_id)
        
        output_dir = os.path.join(config.output_dir, sanitize_filename(name))
        return await self._download_collection(track_ids, output_dir, config)

    async def download_artist(self, query: str, **overrides) -> List[Song]:
        """Download top tracks from a Spotify artist."""
        config = self.config.merge(**overrides)
        session = await self._get_session()
        mp = MetadataProcessor(session, config)
        spotify = mp._spotify
        
        artist_id = query.split("/artist/")[-1].split("?")[0] if "spotify.com" in query else query
        name, track_ids = await spotify.get_artist_info(artist_id)
        
        output_dir = os.path.join(config.output_dir, sanitize_filename(name))
        return await self._download_collection(track_ids, output_dir, config)

    async def _download_collection(self, track_ids: List[str], output_dir: str, config: LagukuConfig) -> List[Song]:
        """Internal helper for concurrent downloads."""
        logger.info(f"Downloading {len(track_ids)} tracks to {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
        semaphore = asyncio.Semaphore(config.concurrency)
        async def limited_download(tid):
            async with semaphore:
                try:
                    # Explicitly pass output_dir override
                    return await self.download(tid, output_dir=output_dir)
                except Exception as e:
                    logger.error(f"Failed to download {tid}: {e}")
                    return None

        tasks = [limited_download(tid) for tid in track_ids]
        results = await asyncio.gather(*tasks)
        return [s for s in results if s is not None]

class Laguku:
    """
    The synchronous entry point for the Laguku SDK.
    Designed for simplicity and ease of use.
    """
    def __init__(self, **config_params):
        """
        Initialize the SDK with global settings.
        Example:
            sdk = Laguku(quality="320", provider="spotify")
        """
        self._async_sdk = AsyncLaguku(**config_params)
        
    def _run_async(self, coro):
        """Helper to run async code in a synchronous context."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            
        return loop.run_until_complete(coro)

    def download(self, query: str, **overrides) -> Song:
        """
        Download a track synchronously.
        """
        return self._run_async(self._async_sdk.download(query, **overrides))

    def download_playlist(self, url: str, **overrides) -> List[Song]:
        """Synchronously download all tracks from a Spotify playlist."""
        return self._run_async(self._async_sdk.download_playlist(url, **overrides))

    def download_album(self, url: str, **overrides) -> List[Song]:
        """Synchronously download all tracks from a Spotify album."""
        return self._run_async(self._async_sdk.download_album(url, **overrides))

    def download_artist(self, url: str, **overrides) -> List[Song]:
        """Synchronously download top tracks from a Spotify artist."""
        return self._run_async(self._async_sdk.download_artist(url, **overrides))

    def close(self):
        """Close the underlying session."""
        if self._async_sdk.session:
            self._run_async(self._async_sdk.session.close())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
