import asyncio
import uuid
from typing import Union

from minio import Minio

from src.domain.interfaces.base_picture_storage import BasePictureStorage


class MiniOPictureStorage(BasePictureStorage):
    """
        Асинхронная обёртка над MinIO Python SDK.
        """

    def __init__(
            self,
            endpoint: str,
            access_key: str,
            secret_key: str,
            bucket_name: str,
            secure: bool = False,
            prefix: str = "picture",
    ):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.bucket_name = bucket_name
        self.prefix = prefix.rstrip("/") + "/" if prefix else ""
        self._bucket_checked = False  # отложенная проверка бакета

    async def init(self) -> None:
        """Вызывать вручную, если нужно явно инициализировать бакет"""
        if not self._bucket_checked:
            await self._ensure_bucket()
            self._bucket_checked = True

    async def _ensure_bucket(self) -> None:
        def _create_bucket():
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)

        await asyncio.get_running_loop().run_in_executor(None, _create_bucket)

    async def save(self, content: bytes) -> str:
        """Сохраняет строку или байты в MinIO."""
        await self.init()

        key = f"{self.prefix}{uuid.uuid4()}.png"

        def _put():
            from io import BytesIO
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=key,
                data=BytesIO(content),
                length=len(content),
            )

        await asyncio.get_running_loop().run_in_executor(None, _put)
        return key

    async def load(self, location: str) -> bytes:
        """Загружает объект из MinIO по ключу."""
        await self.init()

        def _get():
            response = self.client.get_object(self.bucket_name, location)
            payload = response.read()
            response.close()
            response.release_conn()
            return payload

        return await asyncio.get_running_loop().run_in_executor(None, _get)

    async def delete(self, location: str) -> None:
        """Удаляет объект из MinIO по ключу."""

        def _remove():
            self.client.remove_object(self.bucket_name, location)

        await asyncio.get_running_loop().run_in_executor(None, _remove)