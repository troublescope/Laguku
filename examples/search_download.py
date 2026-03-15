from laguku import Laguku

def main():
    # 1. Initialize with global config
    sdk = Laguku(quality="320", provider="spotify")
    
    try:
        # Test Search-based Download
        print("\n--- Test: Search-based Download (Sync) ---")
        query = "hindia - evaluasi"
        
        # Override output_dir per call
        song = sdk.download(
            query=query,
            output_dir="downloads/search_test"
        )
        
        print(f"\n--- Download Success ---")
        print(f"Query used: {query}")
        print(f"Matched Title: {song.title}")
        print(f"Matched Artist: {song.artist}")
        print(f"File Path: {song.file_path}")
            
    except Exception as e:
        print(f"Search download failed: {e}")
    finally:
        sdk.close()

if __name__ == "__main__":
    main()
