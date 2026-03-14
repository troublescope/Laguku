import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from laguku_sdk import LagukuClient

# Load credentials from .env file if it exists
load_dotenv()

async def main():
    # To test this, either create a .env file with these keys or set them directly here
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Warning: No Spotify credentials found in environment. Running in anonymous mode.")
    else:
        print("Running with official Spotify API credentials.")

    query = "https://open.spotify.com/track/2dIBMHByUGcNPzmYBJ6OAj" # Hindia - Evaluasi
    
    async with LagukuClient(
        spotify_client_id=client_id,
        spotify_client_secret=client_secret
    ) as client:
        try:
            song = await client.download(query=query, output_format="mp3")
            print(f"\n--- Download Success ---")
            print(f"Title: {song.title}")
            print(f"Artist: {song.artist}")
            print(f"Provider: {song.provider.value}")
            print(f"File Path: {song.file_path}")
        except Exception as e:
            print(f"Download failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
