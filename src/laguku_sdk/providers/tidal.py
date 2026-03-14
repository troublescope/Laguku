import random
import re
from laguku_sdk.providers.base import BaseProvider
from laguku_sdk.models import ProviderType, TrackMetadata, StreamInfo
from laguku_sdk.exceptions import ResolutionError
from laguku_sdk.core.songlink import SongLinkResolver

class TidalProvider(BaseProvider):
    APIS = [
        "https://hifi-one.spotisaver.net",
        "https://hifi-two.spotisaver.net",
        "https://eu-central.monochrome.tf",
        "https://us-west.monochrome.tf"
    ]

    @property
    def type(self) -> ProviderType:
        return ProviderType.TIDAL

    async def resolve_stream(self, metadata: TrackMetadata, target_format: str = "flac") -> StreamInfo:
        resolver = SongLinkResolver(self.session)
        tidal_url = await resolver.get_platform_url(metadata.spotify_id, "tidal")

        is_lossless = target_format.lower() in ["flac", "m4a"]
        quality = "LOSSLESS" if is_lossless else "HIGH"
        bitrate = 1411 if is_lossless else 320
        stream_format = "flac" if is_lossless else "m4a" # Tidal HIGH is often m4a/aac

        if not tidal_url:
            raise ResolutionError("Could not find Tidal link via SongLink")
        
        track_id_match = re.search(r'/track/(\d+)', tidal_url)
        if not track_id_match:
            raise ResolutionError(f"Tidal Track ID not found in URL: {tidal_url}")
            
        track_id = track_id_match.group(1)
        
        random.shuffle(self.APIS)
        for api in self.APIS:
            try:
                url = f"{api}/track/?id={track_id}&quality={quality}"
                async with self.session.get(url) as resp:
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
        raise ResolutionError("All Tidal APIs failed")
