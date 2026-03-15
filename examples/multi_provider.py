import asyncio

from laguku import Laguku, AsyncLaguku, ProviderType

async def main_async():
    print("\n--- Testing Async SDK ---")
    # Async usage with context manager
    async with AsyncLaguku(quality="lossless", provider=ProviderType.QOBUZ) as sdk:
        query = "https://open.spotify.com/track/2dIBMHByUGcNPzmYBJ6OAj"
        song = await sdk.download(query)
        print(f"Async Download: {song.title} from {song.provider}")

def main_sync():
    print("\n--- Testing Sync SDK ---")
    # Sync usage with context manager
    with Laguku(quality="320", provider=ProviderType.AMAZON) as sdk:
        query = "https://open.spotify.com/track/2dIBMHByUGcNPzmYBJ6OAj"
        song = sdk.download(query)
        print(f"Sync Download: {song.title} from {song.provider}")

if __name__ == "__main__":
    # Test Sync first
    main_sync()
    # Then Test Async
    asyncio.run(main_async())
