from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import httpx

from core import config
from modules.download_tasks.domain.enums import DownloadType
from modules.download_tasks.domain.models import DownloadTask


@dataclass
class DownloadResult:
    file_path: Path
    file_size: int


class BaseDownloader:
    download_type: DownloadType

    async def download(self, task: DownloadTask) -> DownloadResult:
        raise NotImplementedError


class DirectHttpDownloader(BaseDownloader):
    download_type = DownloadType.DIRECT_HTTP

    def __init__(self, download_dir: Path):
        self._download_dir = download_dir
        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/136.0.0.0 Safari/537.36"
            ),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def download(self, task: DownloadTask) -> DownloadResult:
        file_path = self._build_file_path(task)

        async with (
            httpx.AsyncClient(
                follow_redirects=True,
                timeout=config.worker_http_timeout_seconds,
                headers=self._headers,
            ) as client,
            client.stream("GET", task.url) as response,
        ):
            self._raise_for_status(task, response)
            size = 0
            with file_path.open("wb") as output_file:
                async for chunk in response.aiter_bytes():
                    output_file.write(chunk)
                    size += len(chunk)

        return DownloadResult(file_path=file_path, file_size=size)

    def _build_file_path(self, task: DownloadTask) -> Path:
        parsed = urlparse(task.url)
        original_name = Path(parsed.path).name or f"{task.id}.bin"
        target_name = f"{task.id}-{original_name}"
        return self._download_dir / target_name

    def _raise_for_status(self, task: DownloadTask, response: httpx.Response) -> None:
        if response.status_code == 403 and response.headers.get("cf-mitigated") == "challenge":
            raise ValueError(
                f"URL {task.url} is protected by Cloudflare challenge; "
                "direct HTTP downloader cannot access it"
            )

        response.raise_for_status()
