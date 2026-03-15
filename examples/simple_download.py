from laguku import Laguku

def main():
    # 1. Initialize with global config
    sdk = Laguku(
        quality="lossless",
        provider="qobuz",
        lyric=True,
        cover=True
    )

    # 2. Simple download
    query = "https://open.spotify.com/track/2dIBMHByUGcNPzmYBJ6OAj" # Hindia - Evaluasi
    
    try:
        # Per-call override example
        song = sdk.download(query, quality="320")
        
        print(f"Successfully downloaded: {song.file_path}")
        print(f"Title: {song.title}")
        print(f"Artist: {song.artist}")
        print(f"Format: {song.file_path.split('.')[-1].upper()}")
        print(f"Lyrics attached: {'Yes' if song.lyrics else 'No'}")
        
    except Exception as e:
        print(f"Download failed: {e}")
    finally:
        sdk.close()

if __name__ == "__main__":
    main()
