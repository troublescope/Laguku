from abc import ABC, abstractmethod
import aiohttp
from typing import Optional
from laguku.config import LagukuConfig
from laguku.models import TrackMetadata, StreamInfo

class BaseProvider(ABC):
    """
    Abstract base class for music providers.
    
    Providers are only responsible for fetching stream information
    for a given set of metadata.
    """
    def __init__(self, session: aiohttp.ClientSession, config: Optional[LagukuConfig] = None):
        self.session = session
        self.config = config or LagukuConfig()

    @abstractmethod
    async def resolve_stream(self, metadata: TrackMetadata, target_format: str = "auto") -> Optional[StreamInfo]:
        """
        Fetch stream information for the given track metadata.
        """
        pass
