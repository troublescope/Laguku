from laguku import Laguku

def main():
    # Initialize with simple config
    sdk = Laguku(quality="320", provider="amazon")
    
    try:
        # 1. Test Album Download
        print("\n--- Test 1: Album Download (Sync) ---")
        album_url = "https://open.spotify.com/album/1DAuVHMlBvIjzWZALSUXbn" # Menari Dengan Bayangan
        songs = sdk.download_album(album_url, concurrency=2)
        print(f"Downloaded {len(songs)} songs from album.")

        # 2. Test Artist Download (Top Tracks)
        print("\n--- Test 2: Artist Download (Sync) ---")
        artist_url = "https://open.spotify.com/artist/51kyrUsAVqUBcoDEMFkX12" # Hindia
        songs = sdk.download_artist(artist_url, concurrency=2)
        print(f"Downloaded {len(songs)} songs from artist top tracks.")

    except Exception as e:
        print(f"Collection download failed: {e}")
    finally:
        sdk.close()

if __name__ == "__main__":
    main()
