import re
from typing import Optional
from laguku.providers.base import BaseProvider
from laguku.providers.registry import ProviderRegistry
from laguku.config import ProviderType
from laguku.models import TrackMetadata, StreamInfo
from laguku.exceptions import ResolutionError
from laguku.core.songlink import SongLinkResolver

@ProviderRegistry.register(ProviderType.AMAZON)
class AmazonProvider(BaseProvider):
    async def resolve_stream(self, metadata: TrackMetadata, target_format: str = "auto") -> Optional[StreamInfo]:
        resolver = SongLinkResolver(self.session)
        amazon_url = await resolver.get_platform_url(metadata.spotify_id, "amazonMusic")
        
        # Determine quality based on target format and global config
        # Default to flac/lossless if auto and config says lossless
        is_lossless = (target_format == "auto" and self.config.quality == "lossless") or target_format in ["flac", "m4a"]
        
        quality = "7" if is_lossless else "1"
        bitrate = 1411 if is_lossless else 320
        stream_format = "flac" if is_lossless else "m4a"

        if not amazon_url:
            return None

        asin_match = re.search(r'(B[0-9A-Z]{9})', amazon_url)
        if not asin_match:
            return None
        
        asin = asin_match.group(1)
        api_url = f"https://amzn.afkarxyz.fun/api/track/{asin}?quality={quality}"
        
        async with self.session.get(api_url) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            
            return StreamInfo(
                url=data['streamUrl'],
                bitrate=bitrate,
                format=stream_format,
                decryption_key=data.get("decryptionKey")
            )
