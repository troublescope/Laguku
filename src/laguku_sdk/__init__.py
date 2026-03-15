"""
Laguku SDK: A high-performance, asynchronous music downloader for Python.

Supported providers: Qobuz, Tidal, Amazon Music, and more.
Includes automatic metadata enrichment via Spotify.
"""

from laguku_sdk.client import LagukuClient
from laguku_sdk.models import Song, ProviderType, TrackMetadata, LagukuConfig
from laguku_sdk.exceptions import LagukuError

__all__ = ["LagukuClient", "Song", "ProviderType", "TrackMetadata", "LagukuConfig", "LagukuError"]
