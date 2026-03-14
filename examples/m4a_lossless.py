import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from laguku_sdk import LagukuClient

async def main():
    async with LagukuClient() as client:
        try:
            # Test M4A Lossless (ALAC) Download
            print("\n--- Test: M4A Lossless (ALAC) Download ---")
            query = "hindia - evaluasi"
            
            song = await client.download(
                query=query,
                output_dir="downloads/m4a_test",
                output_format="m4a"
            )
            
            print(f"\n--- Download Success ---")
            print(f"Title: {song.title}")
            print(f"Format: M4A (ALAC)")
            print(f"File Path: {song.file_path}")
                
        except Exception as e:
            print(f"M4A download failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
