from typing import Optional
from laguku.providers.base import BaseProvider
from laguku.providers.registry import ProviderRegistry
from laguku.config import ProviderType
from laguku.models import TrackMetadata, StreamInfo

@ProviderRegistry.register(ProviderType.QOBUZ)
class QobuzProvider(BaseProvider):
    APP_ID = "798273057"
    APIS = [
        "https://dab.yeet.su/api/stream?trackId=",
        "https://qbz.afkarxyz.fun/api/track/"
    ]

    async def resolve_stream(self, metadata: TrackMetadata, target_format: str = "auto") -> Optional[StreamInfo]:
        qobuz_id = None
        
        is_lossless = (target_format == "auto" and self.config.quality == "lossless") or target_format in ["flac", "m4a"]
        quality = "6" if is_lossless else "5"
        stream_format = "flac" if is_lossless else "mp3"
        bitrate = 1411 if is_lossless else 320

        # Try to find Qobuz ID via ISRC
        if metadata.isrc:
            search_url = f"https://www.qobuz.com/api.json/0.2/track/search?query={metadata.isrc}&limit=1&app_id={self.APP_ID}"
            async with self.session.get(search_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("tracks", {}).get("items", [])
                    if items:
                        qobuz_id = items[0]['id']
        
        if not qobuz_id:
            # Search fallback by Title and Artist
            query = f"{metadata.artist} {metadata.title}"
            search_url = f"https://www.qobuz.com/api.json/0.2/track/search?query={query}&limit=1&app_id={self.APP_ID}"
            async with self.session.get(search_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("tracks", {}).get("items", [])
                    if items:
                        qobuz_id = items[0]['id']

        if not qobuz_id:
            return None

        for api in self.APIS:
            try:
                final_api_url = f"{api}{qobuz_id}"
                final_api_url += "&" if "?" in final_api_url else "?"
                final_api_url += f"quality={quality}"

                async with self.session.get(final_api_url) as resp:
                    if resp.status == 200:
                        s_data = await resp.json()
                        return StreamInfo(url=s_data['url'], bitrate=bitrate, format=stream_format)
            except Exception:
                continue
        return None
