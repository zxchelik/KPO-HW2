from typing import Annotated

from fastapi import Depends

from application.services.file_service import FileService
from infrastructure.database.repositories.files import SQLFileRepository
from infrastructure.storage.minio_storage import MinioFileStorage
from utils.config import load_config


def file_service():
    config = load_config()
    return FileService(
        file_repo=SQLFileRepository(),
        file_storage=MinioFileStorage(
            endpoint=config.minio.endpoint,
            access_key=config.minio.access_key,
            secret_key=config.minio.secret_key,
            bucket_name=config.minio.bucket_name,
            secure=config.minio.secure,
            prefix="files/",
        )
    )


FileServiceDep = Annotated[FileService, Depends(file_service)]
