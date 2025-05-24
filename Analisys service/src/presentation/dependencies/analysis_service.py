from typing import Annotated

from fastapi import Depends

from src.application.services.analysis import AnalysisService
from src.infrastructure.database.repositories.file_stat import SQLFileStat
from src.infrastructure.external_api.HTTPFileTextReader import HTTPFileTextReader
from src.infrastructure.external_api.HTTPWordCloud import HTTPWordCloud
from src.infrastructure.picture_storage.MiniOPictureStorage import MiniOPictureStorage
from src.utils.config import load_config


def get_analysis_service():
    config = load_config()
    return AnalysisService(
        text_reader=HTTPFileTextReader(
            **config.file_store_service.model_dump()
        ),
        pic_storage=MiniOPictureStorage(
            endpoint=config.minio.endpoint,
            access_key=config.minio.access_key,
            secret_key=config.minio.secret_key,
            bucket_name=config.minio.bucket_name,
            secure=config.minio.secure,
            prefix="picture"
        ),
        word_cloud=HTTPWordCloud(
            **config.word_cloud.model_dump()
        ),
        file_stat_repository=SQLFileStat()
    )

AnalysisServiceDep = Annotated[AnalysisService,Depends(get_analysis_service)]