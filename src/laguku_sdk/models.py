from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum

class ProviderType(str, Enum):
    """
    Supported music providers for stream resolution and metadata.
    """
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    AMAZON = "amazon"
    TIDAL = "tidal"
    QOBUZ = "qobuz"
    GENERIC = "generic"

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
class LagukuConfig:
    """
    Configuration for the LagukuClient.
    
    Attributes:
        default_format: The target audio format (e.g., 'flac', 'mp3', 'm4a', 'auto').
        embed_lyrics: Whether to embed lyrics in the output file.
        concurrency: Number of concurrent downloads for collections.
        preferred_quality: Preferred stream quality ('lossless' or 'high').
        preferred_providers: List of providers to try in order.
        filename_format: Template for output filenames.
    """
    default_format: str = "auto" 
    embed_lyrics: bool = True
    concurrency: int = 3
    preferred_quality: str = "lossless" # 'lossless' or 'high' (mp3)
    preferred_providers: Optional[List[ProviderType]] = None
    filename_format: str = "{title} - {artist}{version}"

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
