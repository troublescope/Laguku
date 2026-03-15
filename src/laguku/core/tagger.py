from typing import Optional
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, TDRC, TCON, USLT, APIC, TXXX
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
from laguku.models import TrackMetadata
from loguru import logger

class MetadataTagger:
    @staticmethod
    def embed(file_path: str, metadata: TrackMetadata, cover_data: Optional[bytes] = None):
        if file_path.endswith('.mp3'):
            MetadataTagger._tag_mp3(file_path, metadata, cover_data)
        elif file_path.endswith('.flac'):
            MetadataTagger._tag_flac(file_path, metadata, cover_data)
        elif file_path.endswith('.m4a'):
            MetadataTagger._tag_m4a(file_path, metadata, cover_data)

    @staticmethod
    def _tag_m4a(file_path: str, metadata: TrackMetadata, cover_data: Optional[bytes]):
        try:
            audio = MP4(file_path)
            # Map standard fields to MP4 tags (Atom IDs)
            audio["\xa9nam"] = metadata.title
            audio["\xa9ART"] = metadata.artist
            if metadata.album: audio["\xa9alb"] = metadata.album
            if metadata.track_number: audio["trkn"] = [(metadata.track_number, 0)]
            if metadata.release_date: audio["\xa9day"] = metadata.release_date[:10]
            if metadata.genre: audio["\xa9gen"] = metadata.genre
            if metadata.isrc: audio["----:com.apple.iTunes:ISRC"] = metadata.isrc.encode()
            
            if metadata.lyrics:
                audio["\xa9lyr"] = metadata.lyrics.content

            if cover_data:
                audio["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]

            audio.save()
        except Exception as e:
            logger.error(f"M4A Tagging failed: {e}")

    @staticmethod
    def _tag_mp3(file_path: str, metadata: TrackMetadata, cover_data: Optional[bytes]):
        try:
            try:
                audio = ID3(file_path)
            except Exception:
                audio = ID3()

            audio.add(TIT2(encoding=3, text=metadata.title))
            audio.add(TPE1(encoding=3, text=metadata.artist))
            if metadata.album:
                audio.add(TALB(encoding=3, text=metadata.album))
            if metadata.track_number:
                audio.add(TRCK(encoding=3, text=str(metadata.track_number)))
            if metadata.release_date:
                audio.add(TDRC(encoding=3, text=metadata.release_date[:4]))
            if metadata.genre:
                audio.add(TCON(encoding=3, text=metadata.genre))
            if metadata.isrc:
                audio.add(TXXX(encoding=3, desc="ISRC", text=metadata.isrc))
            if metadata.publisher:
                audio.add(TXXX(encoding=3, desc="PUBLISHER", text=metadata.publisher))
            
            if metadata.lyrics:
                audio.add(USLT(encoding=3, lang='eng', desc='Lyrics', text=metadata.lyrics.content))

            if cover_data:
                audio.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Front Cover', data=cover_data))

            audio.save(file_path)
        except Exception as e:
            logger.error(f"MP3 Tagging failed: {e}")

    @staticmethod
    def _tag_flac(file_path: str, metadata: TrackMetadata, cover_data: Optional[bytes]):
        try:
            audio = FLAC(file_path)
            audio["title"] = metadata.title
            audio["artist"] = metadata.artist
            if metadata.album: audio["album"] = metadata.album
            if metadata.track_number: audio["tracknumber"] = str(metadata.track_number)
            if metadata.release_date: audio["date"] = metadata.release_date
            if metadata.genre: audio["genre"] = metadata.genre
            if metadata.isrc: audio["isrc"] = metadata.isrc
            if metadata.publisher: audio["publisher"] = metadata.publisher
            if metadata.lyrics: audio["lyrics"] = metadata.lyrics.content

            if cover_data:
                pic = Picture()
                pic.data = cover_data
                pic.type = 3
                pic.mime = "image/jpeg"
                audio.add_picture(pic)

            audio.save()
        except Exception as e:
            logger.error(f"FLAC Tagging failed: {e}")
