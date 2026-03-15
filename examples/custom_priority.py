import asyncio

from laguku import LagukuClient, LagukuConfig, ProviderType

async def main():
    # Configure SDK to prefer TIDAL, then AMAZON, then QOBUZ
    config = LagukuConfig(
        preferred_providers=[
            ProviderType.TIDAL,
            ProviderType.AMAZON,
            ProviderType.QOBUZ
        ],
        default_format="auto"
    )

    async with LagukuClient(config=config) as client:
        try:
            print("\n--- Test: Custom Provider Priority (Tidal First) ---")
            query = "hindia - evaluasi"
            
            song = await client.download(query=query)
            
            print(f"\n--- Download Success ---")
            print(f"Title: {song.title}")
            print(f"Provider used: {song.provider.value}") # Should be tidal if successful
            print(f"File Path: {song.file_path}")
                
        except Exception as e:
            print(f"Download failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
