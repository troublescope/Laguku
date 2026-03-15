from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from laguku.config import ProviderType

@dataclass
class Lyrics:
    """
    Lyrics data for a song, including source and synchronization status.
    """
    content: str
    is_synced: bool = False
    source: str = "unknown"

@dataclass
class TrackMetadata:
    """
    Comprehensive track metadata, often enriched via Spotify API.
    """
    title: str
    artist: str
    album: Optional[str] = None
    album_artist: Optional[str] = None
    track_number: Optional[int] = None
    disc_number: Optional[int] = None
    release_date: Optional[str] = None
    genre: Optional[str] = None
    isrc: Optional[str] = None
    cover_url: Optional[str] = None
    copyright: Optional[str] = None
    publisher: Optional[str] = None
    spotify_id: Optional[str] = None
    duration_ms: Optional[int] = None
    lyrics: Optional[Lyrics] = None

@dataclass
class StreamInfo:
    """
    Low-level stream information for downloading.
    """
    url: str
    bitrate: int
    format: str
    decryption_key: Optional[str] = None
    is_manifest: bool = False

@dataclass
class Song:
    """
    Represents a downloaded or resolvable song.
    """
    id: str
    title: str
    artist: str
    album: str
    provider: ProviderType
    duration: int
    bitrate: int
    cover_url: Optional[str] = None
    lyrics: Optional[str] = None
    stream_url: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[TrackMetadata] = None
