import os
import aiohttp
from typing import Optional
from loguru import logger
from laguku.config import LagukuConfig
from laguku.models import TrackMetadata, StreamInfo
from laguku.core.ffmpeg import FFmpegProcessor
from laguku.core.lyrics import LyricsResolver
from laguku.core.tagger import MetadataTagger # Reusing existing static logic

class Tagger:
    """
    Handles audio post-processing, conversion, and metadata tagging.
    """
    def __init__(self, session: aiohttp.ClientSession, config: LagukuConfig):
        self.session = session
        self.config = config
        self._ffmpeg = FFmpegProcessor()
        self._lyrics_resolver = LyricsResolver(session)
        self._tagger = MetadataTagger()

    async def process(self, temp_file: str, metadata: TrackMetadata, stream_info: StreamInfo, filename: str) -> str:
        """
        Process the temporary file: decrypt, convert, enrichment, and tag.
        Returns the final file path.
        """
        # 1. Decryption (Amazon specific)
        if stream_info.decryption_key:
            logger.info("Decrypting media...")
            dec_file = temp_file.replace(".tmp", ".dec")
            await self._ffmpeg.decrypt_amazon(temp_file, dec_file, stream_info.decryption_key)
            if os.path.exists(temp_file): os.remove(temp_file)
            temp_file = dec_file

        # 2. Conversion
        requested_format = self.config.quality if self.config.quality in ["mp3", "flac", "m4a"] else "auto"
        # If config doesn't specify quality as a format, we use source or default to flac if needed
        # But for simplicity, let's use a mapping or just trust the pipeline.
        
        source_ext = f".{stream_info.format}"
        final_ext = source_ext
        
        # If we need to force a format (e.g. 320 -> mp3)
        if self.config.quality == "320":
            final_ext = ".mp3"
        elif self.config.quality == "lossless":
            # Keep flac/m4a as is, but if source is mp3 and we want lossless, we can't upconvert
            # usually lossless means flac.
            if source_ext not in [".flac", ".m4a"]:
                final_ext = ".flac"
        
        final_file = os.path.join(self.config.output_dir, f"{filename}{final_ext}")
        
        if source_ext != final_ext or stream_info.decryption_key:
            logger.info(f"Converting to {final_ext[1:].upper()}...")
            if final_ext == ".mp3":
                await self._ffmpeg.convert_to_mp3(temp_file, final_file)
            elif final_ext == ".m4a":
                await self._ffmpeg.convert_to_alac(temp_file, final_file)
            else:
                await self._ffmpeg.convert_to_flac(temp_file, final_file)
            if os.path.exists(temp_file): os.remove(temp_file)
        else:
            if os.path.exists(final_file): os.remove(final_file)
            os.rename(temp_file, final_file)

        # 3. Enrichment (Lyrics & Cover)
        if self.config.lyric and not metadata.lyrics:
            logger.info("Fetching lyrics...")
            metadata.lyrics = await self._lyrics_resolver.fetch_lrclib(metadata.title, metadata.artist, metadata.album)
        
        cover_data = None
        if self.config.cover and metadata.cover_url:
            async with self.session.get(metadata.cover_url) as resp:
                if resp.status == 200:
                    cover_data = await resp.read()

        # 4. Tagging
        logger.info("Embedding metadata...")
        self._tagger.embed(final_file, metadata, cover_data)
        
        return final_file
