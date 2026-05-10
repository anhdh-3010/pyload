import uuid

from fastapi import APIRouter, Depends, Response, status

from app.api.v1.download_tasks.domain.dependences import DownloadTaskServiceDep
from app.api.v1.download_tasks.domain.schemas import (
    CreateDownloadTaskRequest,
    DownloadTaskResponse,
    UpdateDownloadTaskRequest,
)
from core import JWTHandler

router = APIRouter()
private_router = APIRouter()


@private_router.post(
    "/download-tasks",
    response_model=DownloadTaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["download_tasks"],
)
async def create_download_task(
    request: CreateDownloadTaskRequest,
    download_task_service: DownloadTaskServiceDep,
    current_user=Depends(JWTHandler.get_current_user),
) -> DownloadTaskResponse:
    """Create a download task for the current user."""
    task = await download_task_service.create_task(current_user.id, request)
    return DownloadTaskResponse.model_validate(task)


@private_router.get(
    "/download-tasks",
    response_model=list[DownloadTaskResponse],
    tags=["download_tasks"],
)
async def list_download_tasks(
    download_task_service: DownloadTaskServiceDep,
    current_user=Depends(JWTHandler.get_current_user),
) -> list[DownloadTaskResponse]:
    """List all download tasks for the current user."""
    tasks = await download_task_service.list_tasks(current_user.id)
    return [DownloadTaskResponse.model_validate(task) for task in tasks]


@private_router.get(
    "/download-tasks/{task_id}",
    response_model=DownloadTaskResponse,
    tags=["download_tasks"],
)
async def get_download_task(
    task_id: uuid.UUID,
    download_task_service: DownloadTaskServiceDep,
    current_user=Depends(JWTHandler.get_current_user),
) -> DownloadTaskResponse:
    """Get a single download task for the current user."""
    task = await download_task_service.get_task(current_user.id, task_id)
    return DownloadTaskResponse.model_validate(task)


@private_router.patch(
    "/download-tasks/{task_id}",
    response_model=DownloadTaskResponse,
    tags=["download_tasks"],
)
async def update_download_task(
    task_id: uuid.UUID,
    request: UpdateDownloadTaskRequest,
    download_task_service: DownloadTaskServiceDep,
    current_user=Depends(JWTHandler.get_current_user),
) -> DownloadTaskResponse:
    """Update a download task for the current user."""
    task = await download_task_service.update_task(current_user.id, task_id, request)
    return DownloadTaskResponse.model_validate(task)


@private_router.delete(
    "/download-tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["download_tasks"],
)
async def delete_download_task(
    task_id: uuid.UUID,
    download_task_service: DownloadTaskServiceDep,
    current_user=Depends(JWTHandler.get_current_user),
) -> Response:
    """Delete a download task for the current user."""
    await download_task_service.delete_task(current_user.id, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
