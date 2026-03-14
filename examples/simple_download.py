import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from laguku_sdk import LagukuClient

async def main():
    # Example using a Spotify URL
    query = "https://open.spotify.com/track/2dIBMHByUGcNPzmYBJ6OAj" # Hindia - Evaluasi
    
    async with LagukuClient() as client:
        try:
            song = await client.download(
                query=query,
                output_dir="downloads"
            )
            print(f"Successfully downloaded: {song.file_path}")
            print(f"Artist: {song.artist}")
            print(f"Album: {song.album}")
            print(f"Lyrics snippet: {song.lyrics[:50] if song.lyrics else 'None'}...")
        except Exception as e:
            print(f"Download failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
