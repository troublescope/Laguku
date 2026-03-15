import aiohttp
import re
from typing import Optional
from laguku.models import Lyrics
from loguru import logger

class LyricsResolver:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def fetch_lrclib(self, track: str, artist: str, album: str = "", duration: int = 0) -> Optional[Lyrics]:
        # Clean title for better matching
        clean_track = re.sub(r'\(.*?\)', '', track)
        clean_track = re.sub(r'\[.*?\]', '', clean_track)
        clean_track = re.sub(r' - .*$', '', clean_track).strip()
        
        primary_artist = artist.split(',')[0].strip()
        
        # 1. Try exact match with original metadata
        lyrics = await self._query_lrclib(clean_track, artist, album, duration)
        if lyrics: return lyrics
        
        # 2. Try exact match with primary artist only
        if primary_artist != artist:
            lyrics = await self._query_lrclib(clean_track, primary_artist, album, duration)
            if lyrics: return lyrics

        # 3. Fallback: Search with primary artist + title
        logger.debug(f"Exact lyrics match failed for {clean_track}, trying search fallback")
        search_params = {"artist_name": primary_artist, "track_name": clean_track}
        async with self.session.get("https://lrclib.net/api/search", params=search_params) as resp:
            if resp.status == 200:
                results = await resp.json()
                if results:
                    best = results[0]
                    content = best.get("syncedLyrics") or best.get("plainLyrics")
                    if content:
                        return Lyrics(content=content, is_synced=bool(best.get("syncedLyrics")), source="lrclib_search")
        
        # 4. Final Fallback: Search with track title only (handles covers/live collaborations)
        async with self.session.get("https://lrclib.net/api/search", params={"q": clean_track}) as resp:
            if resp.status == 200:
                results = await resp.json()
                # Find result with highest similarity (first one usually)
                if results:
                    best = results[0]
                    content = best.get("syncedLyrics") or best.get("plainLyrics")
                    if content:
                        return Lyrics(content=content, is_synced=bool(best.get("syncedLyrics")), source="lrclib_broad_search")
        return None

    async def _query_lrclib(self, track: str, artist: str, album: str, duration: int) -> Optional[Lyrics]:
        url = f"https://lrclib.net/api/get?artist_name={artist}&track_name={track}"
        if album: url += f"&album_name={album}"
        if duration: url += f"&duration={duration // 1000}" # LRCLib uses seconds

        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data.get("syncedLyrics") or data.get("plainLyrics")
                    if content:
                        return Lyrics(content=content, is_synced=bool(data.get("syncedLyrics")), source="lrclib")
        except Exception as e:
            logger.debug(f"LRCLib query failed: {e}")
        return None
