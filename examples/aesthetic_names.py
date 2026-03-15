import asyncio
import os

from laguku import LagukuClient, LagukuConfig

async def main():
    # Test with a track name containing special characters
    config = LagukuConfig(
        filename_format="{title} - {artist}", # Beautiful format
        default_format="auto"
    )

    async with LagukuClient(config=config) as client:
        try:
            print("\n--- Test: Aesthetic and Safe Filenames ---")
            # This live session track has dashes and specific collaborative naming
            query = "Walau Berantakan Live Session Feby Putri Prince Husein"
            
            song = await client.download(query=query)
            
            print(f"\n--- Result ---")
            print(f"Original Title: {song.metadata.title}")
            print(f"Original Artist: {song.metadata.artist}")
            print(f"Final Aesthetic Filename: {os.path.basename(song.file_path)}")
            
            # Check if directory name is also beautiful
            playlist_url = "https://open.spotify.com/playlist/37i9dQZEVXbMDoHDG32m6P" # Top 50 Global
            print(f"\n--- Test: Beautiful Directory Names ---")
            songs = await client.download_playlist(playlist_url, output_dir="downloads/beauty_test", concurrency=1)
            if songs:
                print(f"Directory used: {os.path.dirname(songs[0].file_path)}")
                
        except Exception as e:
            print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
