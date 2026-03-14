from abc import ABC, abstractmethod
from typing import List, Optional
import aiohttp
from laguku_sdk.models import TrackMetadata, StreamInfo, ProviderType

class BaseProvider(ABC):
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    @property
    @abstractmethod
    def type(self) -> ProviderType:
        pass

    @abstractmethod
    async def resolve_stream(self, metadata: TrackMetadata, target_format: str = "flac") -> StreamInfo:
        pass

    async def search(self, query: str) -> List[TrackMetadata]:
        return []
