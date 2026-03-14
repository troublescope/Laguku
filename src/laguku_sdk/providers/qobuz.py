from typing import List
from laguku_sdk.providers.base import BaseProvider
from laguku_sdk.models import ProviderType, TrackMetadata, StreamInfo
from laguku_sdk.exceptions import ResolutionError

class QobuzProvider(BaseProvider):
    APP_ID = "798273057"
    APIS = [
        "https://dab.yeet.su/api/stream?trackId=",
        "https://qbz.afkarxyz.fun/api/track/"
    ]

    @property
    def type(self) -> ProviderType:
        return ProviderType.QOBUZ

    async def resolve_stream(self, metadata: TrackMetadata, target_format: str = "flac") -> StreamInfo:
        qobuz_id = None
        # Map format to Qobuz quality (5 = 320kbps MP3, 6 = Lossless FLAC)
        # m4a is treated as lossless (ALAC)
        is_lossless = target_format.lower() in ["flac", "m4a"]
        quality = "6" if is_lossless else "5"
        stream_format = "flac" if is_lossless else "mp3"
        bitrate = 1411 if is_lossless else 320

        if metadata.isrc:
            search_url = f"https://www.qobuz.com/api.json/0.2/track/search?query={metadata.isrc}&limit=1&app_id={self.APP_ID}"
            async with self.session.get(search_url) as resp:
                data = await resp.json()
                items = data.get("tracks", {}).get("items", [])
                if items:
                    qobuz_id = items[0]['id']
        
        if not qobuz_id:
            # Search fallback by Title and Artist
            query = f"{metadata.artist} {metadata.title}"
            search_url = f"https://www.qobuz.com/api.json/0.2/track/search?query={query}&limit=1&app_id={self.APP_ID}"
            async with self.session.get(search_url) as resp:
                data = await resp.json()
                items = data.get("tracks", {}).get("items", [])
                if items:
                    qobuz_id = items[0]['id']

        if not qobuz_id:
            raise ResolutionError("Track not found on Qobuz via ISRC or Search")

        for api in self.APIS:
            try:
                # Handle different API URL structures
                final_api_url = f"{api}{qobuz_id}"
                if "?" in api:
                    final_api_url += f"&quality={quality}"
                else:
                    final_api_url += f"?quality={quality}"

                async with self.session.get(final_api_url) as resp:
                    if resp.status == 200:
                        s_data = await resp.json()
                        return StreamInfo(url=s_data['url'], bitrate=bitrate, format=stream_format)
            except Exception:
                continue
        raise ResolutionError("All Qobuz APIs failed")
