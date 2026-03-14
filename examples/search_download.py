import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from laguku_sdk import LagukuClient

async def main():
    async with LagukuClient() as client:
        try:
            # Test Search-based Download
            print("\n--- Test: Search-based Download ---")
            query = "hindia - evaluasi"
            
            song = await client.download(
                query=query,
                output_dir="downloads/search_test",
                output_format="mp3"
            )
            
            print(f"\n--- Download Success ---")
            print(f"Query used: {query}")
            print(f"Matched Title: {song.title}")
            print(f"Matched Artist: {song.artist}")
            print(f"File Path: {song.file_path}")
                
        except Exception as e:
            print(f"Search download failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
