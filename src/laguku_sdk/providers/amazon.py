import re
from laguku_sdk.providers.base import BaseProvider
from laguku_sdk.models import ProviderType, TrackMetadata, StreamInfo
from laguku_sdk.exceptions import ResolutionError
from laguku_sdk.core.songlink import SongLinkResolver

class AmazonProvider(BaseProvider):
    @property
    def type(self) -> ProviderType:
        return ProviderType.AMAZON

    async def resolve_stream(self, metadata: TrackMetadata, target_format: str = "flac") -> StreamInfo:
        resolver = SongLinkResolver(self.session)
        amazon_url = await resolver.get_platform_url(metadata.spotify_id, "amazonMusic")
        
        # Amazon quality (7 = High Res/Lossless, 1 = Standard MP3)
        is_lossless = target_format.lower() in ["flac", "m4a"]
        quality = "7" if is_lossless else "1"
        bitrate = 1411 if is_lossless else 320
        stream_format = "flac" if is_lossless else "m4a"

        if not amazon_url:
            raise ResolutionError("Could not find Amazon Music link via SongLink")

        asin_match = re.search(r'(B[0-9A-Z]{9})', amazon_url)
        if not asin_match:
            raise ResolutionError(f"ASIN not found in Amazon URL: {amazon_url}")
        
        asin = asin_match.group(1)
        api_url = f"https://amzn.afkarxyz.fun/api/track/{asin}?quality={quality}"
        
        async with self.session.get(api_url) as resp:
            if resp.status != 200:
                raise ResolutionError(f"Amazon API returned {resp.status}")
            data = await resp.json()
            
            return StreamInfo(
                url=data['streamUrl'],
                bitrate=bitrate,
                format=stream_format,
                decryption_key=data.get("decryptionKey")
            )
