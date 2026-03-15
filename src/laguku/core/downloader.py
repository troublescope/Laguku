import os
import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
from laguku.config import LagukuConfig
from laguku.models import StreamInfo
from laguku.exceptions import DownloadError

class Downloader:
    """
    Handles downloading audio streams and manifests.
    """
    def __init__(self, session: aiohttp.ClientSession, config: LagukuConfig):
        self.session = session
        self.config = config

    async def download(self, stream_info: StreamInfo, filename: str) -> str:
        """
        Download a stream and return the temporary file path.
        """
        os.makedirs(self.config.output_dir, exist_ok=True)
        dest = os.path.join(self.config.output_dir, f"{filename}.tmp.{stream_info.format}")
        
        logger.info(f"Downloading {stream_info.format.upper()} stream...")
        
        if stream_info.is_manifest:
            await self._download_manifest(stream_info.url.replace("MANIFEST:", ""), dest)
        else:
            await self.download_file(stream_info.url, dest)
            
        return dest

    async def _download_manifest(self, manifest_b64: str, dest: str):
        import base64
        import json
        try:
            manifest_data = base64.b64decode(manifest_b64).decode('utf-8')
            if manifest_data.startswith('{'):
                # BTS/JSON Format
                data = json.loads(manifest_data)
                urls = data.get("urls", [])
                if urls:
                    await self.download_file(urls[0], dest)
                else:
                    raise DownloadError("No URLs found in JSON manifest")
            else:
                # DASH/XML Format (simplified)
                import re
                urls = re.findall(r'media="([^"]+)"', manifest_data)
                if not urls:
                    urls = re.findall(r'<BaseURL>([^<]+)</BaseURL>', manifest_data)
                
                if urls:
                    await self.download_file(urls[0].replace("&amp;", "&"), dest)
                else:
                    raise DownloadError("Unsupported or empty DASH manifest")
        except Exception as e:
            logger.error(f"Manifest processing failed: {e}")
            raise DownloadError(f"Could not process download manifest: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def download_file(self, url: str, dest: str):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
        }
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise DownloadError(f"Server returned status {response.status}")
                
                with open(dest, 'wb') as f:
                    while True:
                        chunk = await response.content.read(64 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
            logger.debug(f"File saved to {dest}")
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise DownloadError(str(e))
