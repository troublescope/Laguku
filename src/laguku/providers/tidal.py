import random
import re
from typing import Optional
from laguku.providers.base import BaseProvider
from laguku.providers.registry import ProviderRegistry
from laguku.config import ProviderType
from laguku.models import TrackMetadata, StreamInfo
from laguku.core.songlink import SongLinkResolver

@ProviderRegistry.register(ProviderType.TIDAL)
class TidalProvider(BaseProvider):
    APIS = [
        "https://hifi-one.spotisaver.net",
        "https://hifi-two.spotisaver.net",
        "https://eu-central.monochrome.tf",
        "https://us-west.monochrome.tf"
    ]

    async def resolve_stream(self, metadata: TrackMetadata, target_format: str = "auto") -> Optional[StreamInfo]:
        resolver = SongLinkResolver(self.session)
        tidal_url = await resolver.get_platform_url(metadata.spotify_id, "tidal")

        is_lossless = (target_format == "auto" and self.config.quality == "lossless") or target_format in ["flac", "m4a"]
        quality = "LOSSLESS" if is_lossless else "HIGH"
        bitrate = 1411 if is_lossless else 320
        stream_format = "flac" if is_lossless else "m4a"

        if not tidal_url:
            return None
        
        track_id_match = re.search(r'/track/(\d+)', tidal_url)
        if not track_id_match:
            return None
            
        track_id = track_id_match.group(1)
        
        # Shuffle APIs to distribute load
        apis = self.APIS.copy()
        random.shuffle(apis)
        
        for api in apis:
            try:
                url = f"{api}/track/?id={track_id}&quality={quality}"
                async with self.session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        manifest_b64 = data.get("data", {}).get("manifest")
                        if manifest_b64:
                            return StreamInfo(
                                url=f"MANIFEST:{manifest_b64}",
                                bitrate=bitrate,
                                format=stream_format,
                                is_manifest=True
                            )
            except Exception:
                continue
        return None
