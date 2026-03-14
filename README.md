# lagukuSDK

A production-grade asynchronous music downloader SDK for Python, replicated from advanced Go backends.

## Features

- **Async-First**: Built on `asyncio` and `aiohttp` for high-performance concurrent operations.
- **Multi-Provider**: Supports Qobuz, Tidal, Amazon Music, and more with automatic fallback.
- **Production Pipelines**:
  - Spotify metadata enrichment via partner APIs.
  - ISRC-based cross-platform resolution.
  - Automatic decryption (Amazon).
  - DASH/BTS manifest handling (Tidal).
  - Mutagen-based metadata tagging (synced lyrics, high-res covers).
  - FFmpeg-powered audio processing.

## Installation

```bash
poetry install
```

Requires `ffmpeg` installed on your system.

## Usage

```python
from laguku_sdk import LagukuClient

async def download():
    async with LagukuClient() as client:
        song = await client.download(
            query="https://open.spotify.com/track/...",
            output_dir="music",
            output_format="flac"
        )
        print(f"Downloaded: {song.title} to {song.file_path}")
```

## Architecture

- `src/laguku_sdk/client.py`: Main orchestrator.
- `src/laguku_sdk/core/`: Internal logic (Spotify, Downloader, FFmpeg, Tagger).
- `src/laguku_sdk/providers/`: Provider implementations.
- `src/laguku_sdk/models.py`: Typed data models.
