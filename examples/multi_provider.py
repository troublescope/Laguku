import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from laguku_sdk import LagukuClient, ProviderType

async def main():
    # Hindia - Evaluasi
    query = "https://open.spotify.com/track/2dIBMHByUGcNPzmYBJ6OAj"
    
    # Demonstration 1: Default (Qobuz preference) - FLAC
    print("\n--- Test 1: High Quality FLAC (Qobuz Preference) ---")
    async with LagukuClient() as client:
        try:
            song = await client.download(query=query, output_format="flac")
            print(f"Provider: {song.provider}")
            print(f"Format: {song.file_path.split('.')[-1].upper()}")
            print(f"Path: {song.file_path}")
        except Exception as e:
            print(f"Test 1 failed: {e}")

    # Demonstration 2: Fallback Logic (Force Amazon) - MP3
    print("\n--- Test 2: Fallback Demonstration (Force Amazon) ---")
    # We pass only Amazon to simulate Qobuz/Tidal being unavailable or skipped
    async with LagukuClient(preferred_providers=[ProviderType.AMAZON]) as client:
        try:
            song = await client.download(query=query, output_format="mp3")
            print(f"Provider: {song.provider}")
            print(f"Format: {song.file_path.split('.')[-1].upper()}")
            print(f"Path: {song.file_path}")
        except Exception as e:
            print(f"Test 2 failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
