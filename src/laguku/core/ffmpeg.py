import asyncio
import os
import ffmpeg
from loguru import logger
from laguku.exceptions import DownloadError, DecryptionError

class FFmpegProcessor:
    @staticmethod
    async def convert_to_mp3(input_path: str, output_path: str, bitrate: str = "320k"):
        try:
            process = (
                ffmpeg
                .input(input_path)
                .output(output_path, acodec='libmp3lame', audio_bitrate=bitrate)
                .overwrite_output()
                .run_async(pipe_stderr=True)
            )
            _, stderr = process.communicate()
            if process.returncode != 0:
                raise DownloadError(f"FFmpeg failed: {stderr.decode()}")
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            raise DownloadError(f"Conversion failed: {e}")

    @staticmethod
    async def decrypt_amazon(input_path: str, output_path: str, key: str):
        try:
            # Replicating Go: ffmpeg -decryption_key <key> -i <input> -c copy -y <output>
            # Amazon often serves FLAC in an M4A/MOV container. 
            # If the output path has a .dec extension, ffmpeg might struggle.
            # We ensure the output format is explicitly defined or uses a standard extension.
            
            # Use -f flac if we are outputting a flac file from a decrypted stream
            format_args = {}
            if output_path.endswith(".flac"):
                format_args["f"] = "flac"
            elif output_path.endswith(".m4a") or output_path.endswith(".mp4"):
                format_args["f"] = "mp4"

            process = (
                ffmpeg
                .input(input_path, decryption_key=key)
                .output(output_path, codec='copy', **format_args)
                .overwrite_output()
                .run_async(pipe_stderr=True)
            )
            _, stderr = process.communicate()
            if process.returncode != 0:
                raise DecryptionError(f"Decryption failed: {stderr.decode()}")
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise DecryptionError(f"Decryption failed: {e}")

    @staticmethod
    async def convert_to_flac(input_path: str, output_path: str):
        try:
            process = (
                ffmpeg
                .input(input_path)
                .output(output_path, acodec='flac')
                .overwrite_output()
                .run_async(pipe_stderr=True)
            )
            _, stderr = process.communicate()
            if process.returncode != 0:
                raise DownloadError(f"FFmpeg failed: {stderr.decode()}")
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            raise DownloadError(f"Conversion failed: {e}")

    @staticmethod
    async def convert_to_alac(input_path: str, output_path: str):
        try:
            # Apple Lossless (ALAC) in M4A container
            process = (
                ffmpeg
                .input(input_path)
                .output(output_path, acodec='alac')
                .overwrite_output()
                .run_async(pipe_stderr=True)
            )
            _, stderr = process.communicate()
            if process.returncode != 0:
                raise DownloadError(f"FFmpeg failed: {stderr.decode()}")
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            raise DownloadError(f"Conversion failed: {e}")

    @staticmethod
    async def probe_codec(file_path: str) -> str:
        try:
            probe = ffmpeg.probe(file_path)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            return audio_stream['codec_name'] if audio_stream else "unknown"
        except Exception:
            return "unknown"
