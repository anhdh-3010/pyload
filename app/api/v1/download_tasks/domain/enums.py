from enum import Enum


class DownloadStatus(int, Enum):
    PENDING = 0
    SCHEDULED = 1
    PROCESSING = 2
    SUCCESS = 3
    FAILED = 4
    PAUSED = 5
    CANCELED = 6


class DownloadType(int, Enum):
    DIRECT_HTTP = 1
    TORRENT = 2
    YOUTUBE = 3
    GOOGLE_DRIVE = 4
    TIKTOK = 5
