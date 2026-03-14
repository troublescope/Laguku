import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
from laguku_sdk.exceptions import DownloadError

class AsyncDownloader:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def download_manifest(self, manifest_b64: str, dest: str):
        import base64
        import json
        try:
            manifest_data = base64.b64decode(manifest_b64).decode('utf-8')
            if manifest_data.startswith('{'):
                # BTS Format
                data = json.loads(manifest_data)
                urls = data.get("urls", [])
                if urls:
                    await self.download_file(urls[0], dest)
            else:
                # DASH format - simplified for now
                import re
                urls = re.findall(r'media="([^"]+)"', manifest_data)
                if not urls:
                    # Try to find direct URL
                    urls = re.findall(r'<BaseURL>([^<]+)</BaseURL>', manifest_data)
                
                if urls:
                    # DASH segments logic would go here
                    await self.download_file(urls[0].replace("&amp;", "&"), dest)
                else:
                    raise DownloadError("Unsupported or empty DASH manifest")
        except Exception as e:
            logger.error(f"Manifest download failed: {e}")
            raise DownloadError(f"Manifest processing failed: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def download_file(self, url: str, dest: str, headers: dict = None):
        if not headers:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
            }
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise DownloadError(f"Failed to download: {response.status}")
                
                with open(dest, 'wb') as f:
                    while True:
                        chunk = await response.content.read(64 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
            logger.info(f"Successfully downloaded to {dest}")
        except Exception as e:
            logger.error(f"Download error: {e}")
            raise DownloadError(f"Download failed: {e}")

    async def download_segments(self, urls: list[str], dest: str):
        # Used for DASH/Tidal manifests as seen in tidal.go
        with open(dest, 'wb') as f:
            for i, url in enumerate(urls):
                logger.debug(f"Downloading segment {i+1}/{len(urls)}")
                async with self.session.get(url) as response:
                    if response.status == 200:
                        f.write(await response.read())
                    else:
                        logger.warning(f"Failed to download segment {i+1}")
