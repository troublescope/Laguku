import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from laguku_sdk import LagukuClient

async def main():
    async with LagukuClient() as client:
        try:
            # 1. Test Album Download
            print("\n--- Test 1: Album Download ---")
            album_url = "https://open.spotify.com/album/1DAuVHMlBvIjzWZALSUXbn" # Menari Dengan Bayangan
            songs = await client.download_album(album_url, output_format="mp3", concurrency=2)
            print(f"Downloaded {len(songs)} songs from album.")

            # 2. Test Artist Download (Top Tracks)
            print("\n--- Test 2: Artist Download (Top Tracks) ---")
            artist_url = "https://open.spotify.com/artist/51kyrUsAVqUBcoDEMFkX12" # Hindia
            songs = await client.download_artist(artist_url, output_format="mp3", concurrency=2)
            print(f"Downloaded {len(songs)} songs from artist top tracks.")

        except Exception as e:
            print(f"Collection download failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
