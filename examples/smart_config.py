import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from laguku_sdk import LagukuClient, LagukuConfig

async def main():
    # Configure SDK: Preserve source format, embed lyrics
    config = LagukuConfig(
        default_format="auto", # flac source -> flac file, m4a source -> m4a file
        embed_lyrics=True
    )

    async with LagukuClient(config=config) as client:
        try:
            print("\n--- Test: Preserve Source Format (Auto Mode) ---")
            query = "hindia - evaluasi"
            
            song = await client.download(query=query)
            
            print(f"\n--- Download Success ---")
            print(f"Title: {song.title}")
            print(f"Source Format detected & preserved: {song.file_path.split('.')[-1].upper()}")
            print(f"Lyrics Embedded: {bool(song.lyrics)}")
            print(f"File Path: {song.file_path}")
                
        except Exception as e:
            print(f"Download failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
