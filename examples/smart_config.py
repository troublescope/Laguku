from laguku import Laguku

def main():
    # Demonstrating global configuration and per-call override
    print("\n--- Test: Smart Config & Per-call Overrides ---")
    
    # 1. Initialize with global defaults
    sdk = Laguku(
        quality="lossless",
        provider="qobuz",
        lyric=True,
        cover=True,
        output_dir="downloads/global_config"
    )
    
    query = "hindia - evaluasi"
    
    try:
        # 2. First download: uses global defaults (Lossless, Qobuz, Lyrics, Cover)
        print("\n--- Download 1: Global Defaults (Lossless Qobuz) ---")
        song1 = sdk.download(query)
        print(f"File 1: {song1.file_path} (Quality: {song1.bitrate}kbps)")

        # 3. Second download: Override quality and provider for this call only
        print("\n--- Download 2: Per-call Override (320kbps Amazon) ---")
        song2 = sdk.download(
            query, 
            quality="320", 
            provider="amazon",
            output_dir="downloads/override_test"
        )
        print(f"File 2: {song2.file_path} (Quality: {song2.bitrate}kbps)")

        # Global defaults are preserved for the next call
        print("\n--- Download 3: Verifying Global Defaults (Still Lossless) ---")
        song3 = sdk.download(query, output_dir="downloads/back_to_global")
        print(f"File 3: {song3.file_path} (Quality: {song3.bitrate}kbps)")
            
    except Exception as e:
        print(f"Download failed: {e}")
    finally:
        sdk.close()

if __name__ == "__main__":
    main()
