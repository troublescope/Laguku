import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from laguku_sdk import LagukuClient

async def main():
    # Example: Spotify Top 50 - Global (Partial test)
    playlist_url = "https://open.spotify.com/playlist/37i9dQZEVXbMDoHDG32m6P" 
    
    async with LagukuClient() as client:
        try:
            print(f"Starting playlist download...")
            songs = await client.download_playlist(
                playlist_query=playlist_url,
                output_dir="downloads/playlist_test",
                output_format="mp3",
                concurrency=3 # Parallel downloads
            )
            
            print(f"\n--- Playlist Download Finished ---")
            print(f"Successfully downloaded {len(songs)} songs.")
            for song in songs[:5]: # Show first 5
                print(f"- {song.title} by {song.artist}")
                
        except Exception as e:
            print(f"Playlist download failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
