import uuid

from pydantic import BaseModel, Field, HttpUrl

from app.api.v1.download_tasks.domain.enums import DownloadStatus, DownloadType


class CreateDownloadTaskRequest(BaseModel):
    download_type: DownloadType
    url: HttpUrl
    metadata: dict = Field(default_factory=dict)


class UpdateDownloadTaskRequest(BaseModel):
    download_type: DownloadType | None = None
    url: HttpUrl | None = None
    metadata: dict | None = None


class DownloadTaskResponse(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    download_type: DownloadType
    url: str
    download_status: DownloadStatus
    metadata: dict = Field(alias="task_metadata")

    class Config:
        from_attributes = True
        populate_by_name = True
