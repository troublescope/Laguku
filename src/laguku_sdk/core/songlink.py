import aiohttp
from typing import Optional
from laguku_sdk.exceptions import ProviderError

class SongLinkResolver:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self._cache = {} # Simple session cache

    async def get_isrc(self, spotify_id: str) -> Optional[str]:
        if spotify_id in self._cache:
            return self._cache[spotify_id].get("isrc")
            
        # Replicating songlink.go -> getDeezerISRC
        url = f"https://api.song.link/v1-alpha.1/links?url=https://open.spotify.com/track/{spotify_id}"
        async with self.session.get(url) as resp:
            if resp.status != 200: return None
            data = await resp.json()
            
            # Cache the whole response for future platform URL lookups
            if spotify_id not in self._cache:
                self._cache[spotify_id] = {"raw": data}

            deezer_link = data.get("linksByPlatform", {}).get("deezer", {}).get("url")
            if not deezer_link: return None
            
            track_id = deezer_link.split("/track/")[-1].split("?")[0]
            async with self.session.get(f"https://api.deezer.com/track/{track_id}") as d_resp:
                d_data = await d_resp.json()
                isrc = d_data.get("isrc")
                self._cache[spotify_id]["isrc"] = isrc
                return isrc

    async def get_platform_url(self, spotify_id: str, platform: str) -> Optional[str]:
        if spotify_id in self._cache and "raw" in self._cache[spotify_id]:
            data = self._cache[spotify_id]["raw"]
        else:
            url = f"https://api.song.link/v1-alpha.1/links?url=https://open.spotify.com/track/{spotify_id}"
            async with self.session.get(url) as resp:
                if resp.status != 200: return None
                data = await resp.json()
                self._cache[spotify_id] = {"raw": data}
        
        return data.get("linksByPlatform", {}).get(platform, {}).get("url")
