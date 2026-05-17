from collections.abc import Set

from modules.download_tasks.domain.enums import DownloadStatus

ALLOWED_TRANSITIONS: dict[DownloadStatus, Set[DownloadStatus]] = {
    DownloadStatus.PENDING: {
        DownloadStatus.SCHEDULED,
        DownloadStatus.CANCELED,
    },
    DownloadStatus.SCHEDULED: {
        DownloadStatus.PROCESSING,
        DownloadStatus.PENDING,
        DownloadStatus.PAUSED,
        DownloadStatus.CANCELED,
    },
    DownloadStatus.PROCESSING: {
        DownloadStatus.PENDING,
        DownloadStatus.SCHEDULED,
        DownloadStatus.SUCCESS,
        DownloadStatus.FAILED,
        DownloadStatus.PAUSED,
        DownloadStatus.CANCELED,
    },
    DownloadStatus.FAILED: {
        DownloadStatus.SCHEDULED,
        DownloadStatus.CANCELED,
    },
    DownloadStatus.PAUSED: {
        DownloadStatus.SCHEDULED,
        DownloadStatus.CANCELED,
    },
    DownloadStatus.SUCCESS: set(),
    DownloadStatus.CANCELED: set(),
}


def can_transition(current: DownloadStatus, target: DownloadStatus) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())


def ensure_can_transition(current: DownloadStatus, target: DownloadStatus) -> None:
    current_status = DownloadStatus(current)
    target_status = DownloadStatus(target)

    if not can_transition(current_status, target_status):
        raise ValueError(
            f"Invalid task status transition: {current_status.name} -> {target_status.name}"
        )
