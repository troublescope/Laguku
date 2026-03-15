# Laguku SDK 🎵

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade, asynchronous music downloader SDK for Python. Replicated from advanced Go-based music backends, it provides a unified interface to download high-quality music from multiple providers including Qobuz, Tidal, and Amazon Music, with automatic fallback and Spotify metadata enrichment.

## 🚀 Features

- **Async-First Architecture**: Built on `asyncio` and `aiohttp` for high-performance, concurrent downloads.
- **Smart Multi-Provider Fallback**: Automatically tries multiple providers (Qobuz, Tidal, Amazon) to find the best quality stream.
- **Spotify Enrichment**: Resolves search queries and Spotify URLs into rich metadata (ISRC, high-res covers, release dates).
- **Advanced Processing**:
  - **Automatic Decryption**: Handles encrypted streams (e.g., Amazon Music).
  - **Manifest Handling**: Native support for DASH/BTS manifests (Tidal).
  - **FFmpeg Integration**: High-quality audio conversion and processing.
  - **Metadata Tagging**: Comprehensive tagging including synced lyrics and high-resolution album art using Mutagen.
- **Production-Ready**: Typed models, clean abstractions, and robust error handling.

## 📦 Installation

### Prerequisites

- **Python 3.8+**
- **FFmpeg**: Required for audio processing and conversion.
  - **Ubuntu/Debian**: `sudo apt install ffmpeg`
  - **macOS**: `brew install ffmpeg`
  - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

### Install via Pip/Poetry

```bash
# Using pip
pip install laguku-sdk

# Using poetry
poetry add laguku-sdk
```

## 🛠️ Quick Start

### Basic Download

```python
import asyncio
from laguku_sdk import LagukuClient

async def main():
    async with LagukuClient() as client:
        # Supports Spotify URLs or search queries
        song = await client.download(
            query="https://open.spotify.com/track/2dIBMHByUGcNPzmYBJ6OAj",
            output_dir="my_music",
            output_format="flac"
        )
        print(f"✅ Downloaded: {song.title} - {song.artist}")
        print(f"📍 Saved to: {song.file_path}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Batch Downloading (Albums & Playlists)

```python
async with LagukuClient() as client:
    # Download an entire album
    songs = await client.download_album(
        "https://open.spotify.com/album/...",
        output_dir="downloads",
        concurrency=3 # Number of parallel downloads
    )
    
    # Download a playlist
    playlist_songs = await client.download_playlist(
        "https://open.spotify.com/playlist/..."
    )
```

## ⚙️ Configuration

The `LagukuClient` can be customized via `LagukuConfig` or direct parameters.

### Spotify Credentials (Optional)

While not strictly required for basic track resolution, providing Spotify credentials allows for higher rate limits and better search capabilities.

```python
client = LagukuClient(
    spotify_client_id="YOUR_ID",
    spotify_client_secret="YOUR_SECRET"
)
```

### Advanced Config

```python
from laguku_sdk.models import LagukuConfig, ProviderType

config = LagukuConfig(
    default_format="flac",      # flac, mp3, m4a, auto
    embed_lyrics=True,          # Fetch and embed lyrics
    concurrency=5,              # Parallel downloads for collections
    preferred_quality="lossless" # lossless or high
)

async with LagukuClient(config=config) as client:
    # ...
```

## 📂 Project Structure

- `src/laguku_sdk/client.py`: Main orchestrator and public API.
- `src/laguku_sdk/core/`: Internal logic for Spotify, FFmpeg, Tagger, and Lyrics.
- `src/laguku_sdk/providers/`: Provider-specific implementations (Amazon, Tidal, Qobuz).
- `src/laguku_sdk/models.py`: Pydantic-like dataclasses for typed data.

## 📖 Examples

Check the [examples/](examples/) directory for more advanced usage:
- `custom_priority.py`: Change the order of providers.
- `m4a_lossless.py`: Download in Apple Lossless format.
- `smart_config.py`: Using the configuration object.
- `aesthetic_names.py`: Customizing output filename formats.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
