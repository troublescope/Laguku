# Laguku SDK 🎵

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade, synchronous and asynchronous music downloader SDK for Python. It provides an extremely simple unified interface to download high-quality music from multiple providers (Qobuz, Tidal, Amazon) with automatic fallback and Spotify metadata enrichment.

## 🚀 Features

- **Extreme Simplicity**: Minimal top-level imports and clean, intuitive API.
- **Sync & Async Support**: Use `Laguku` for simple scripts or `AsyncLaguku` for high-performance applications.
- **Smart "Auto" Provider**: Automatically tries multiple providers (Qobuz, Tidal, Amazon) to find the best quality stream.
- **Global & Per-call Configuration**: Set defaults at initialization and override them for specific calls.
- **Advanced Processing**:
  - **Automatic Decryption**: Handles encrypted streams (e.g., Amazon Music).
  - **FFmpeg Integration**: High-quality audio conversion and processing.
  - **Metadata Tagging**: Comprehensive tagging including synced lyrics and high-resolution album art.
- **No Pydantic**: Lightweight and efficient using pure Python dataclasses.

## 📦 Installation

### Prerequisites

- **Python 3.10+**
- **FFmpeg**: Required for audio processing and conversion.

### Install via Pip

```bash
pip install laguku-sdk
```

## 🛠️ Quick Start

### Simple Synchronous Download

```python
from laguku import Laguku

# 1. Initialize with global defaults
sdk = Laguku(
    quality="lossless",  # lossless, 320, 128
    provider="auto",     # Try multiple providers automatically
    lyric=True,
    cover=True
)

# 2. Download from Spotify URL or Search Query
# Supports per-call overrides (e.g., override quality for this track)
song = sdk.download(
    "https://open.spotify.com/track/2dIBMHByUGcNPzmYBJ6OAj",
    quality="320"
)

print(f"✅ Downloaded: {song.title} - {song.artist}")
print(f"📍 Saved to: {song.file_path} (Quality: {song.bitrate}kbps)")

# Close the session when done
sdk.close()
```

### Asynchronous Usage

```python
import asyncio
from laguku import AsyncLaguku

async def main():
    async with AsyncLaguku(quality="lossless") as sdk:
        song = await sdk.download("hindia - evaluasi")
        print(f"Downloaded: {song.file_path}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Batch Downloading (Albums & Playlists)

```python
with Laguku(quality="320") as sdk:
    # Download an entire album concurrently
    songs = sdk.download_album(
        "https://open.spotify.com/album/...",
        concurrency=3
    )
    
    # Download a playlist
    playlist_songs = sdk.download_playlist(
        "https://open.spotify.com/playlist/..."
    )
```

## ⚙️ Configuration

The SDK can be customized during initialization or overridden in each `download` call.

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `quality` | `str` | `"320"` | Target quality: `"128"`, `"320"`, `"lossless"` |
| `provider`| `str` | `"auto"`| `"auto"`, `"amazon"`, `"tidal"`, `"qobuz"`, `"spotify"` |
| `preferred_providers` | `list` | `["qobuz", "tidal", "amazon"]` | Order of providers to try in `auto` mode |
| `lyric`   | `bool`| `True`  | Whether to fetch and embed lyrics |
| `cover`   | `bool`| `True`  | Whether to fetch and embed cover art |
| `output_dir` | `str` | `"downloads"` | Directory to save files |
| `filename_format` | `str` | `"{title} - {artist}"` | Template for output filenames |

### Spotify Credentials (Optional)

Providing credentials improves search success rates and enables private playlist access.

```python
sdk = Laguku(
    spotify_client_id="YOUR_ID",
    spotify_client_secret="YOUR_SECRET"
)
```

## 📂 Project Structure

- `src/laguku/client.py`: Public API (Laguku & AsyncLaguku).
- `src/laguku/config.py`: Centralized configuration management.
- `src/laguku/core/`: Internal logic for metadata, downloading, and tagging.
- `src/laguku/providers/`: Extensible provider system.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
