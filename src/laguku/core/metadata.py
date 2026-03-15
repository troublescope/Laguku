import aiohttp
from typing import Optional
from loguru import logger
from laguku.config import LagukuConfig
from laguku.models import TrackMetadata
from laguku.core.spotify import SpotifyInternal
from laguku.core.songlink import SongLinkResolver
from laguku.exceptions import LagukuError

class MetadataProcessor:
    """
    Handles fetching and enriching track metadata.
    """
    def __init__(self, session: aiohttp.ClientSession, config: LagukuConfig):
        self.session = session
        self.config = config
        self._spotify = SpotifyInternal(
            session, 
            client_id=config.spotify_client_id, 
            client_secret=config.spotify_client_secret
        )
        self._songlink = SongLinkResolver(session)

    async def resolve(self, query: str) -> TrackMetadata:
        """
        Identify a track from a query/URL and fetch its metadata.
        """
        track_id = await self._identify_track_id(query)
        logger.info(f"Fetching metadata for Spotify ID: {track_id}")
        
        metadata = await self._spotify.get_track_metadata(track_id)
        metadata.isrc = await self._songlink.get_isrc(track_id)
        metadata.spotify_id = track_id
        
        return metadata

    async def _identify_track_id(self, query: str) -> str:
        if "spotify.com" in query:
            return query.split("/track/")[-1].split("?")[0]
        elif len(query) == 22 and " " not in query:
            return query
        
        # Search fallback
        logger.info(f"Searching Spotify for: {query}")
        search_results = await self._spotify.search(query, limit=1)
        if not search_results:
            raise LagukuError(f"No results found for query: {query}")
        
        # Extract ID from nested Spotify search response
        try:
            item = search_results[0]
            if "item" in item:
                return item['item']['data']['id']
            return item['id']
        except (KeyError, IndexError):
            raise LagukuError(f"Could not parse search results for: {query}")
