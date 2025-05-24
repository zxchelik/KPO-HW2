import hashlib

from domain.interfaces.storage import AbstractFileStorage
from infrastructure.database.repositories.files import AbstractFileRepository


class FileService:
    def __init__(self, file_repo: AbstractFileRepository, file_storage: AbstractFileStorage):
        self._file_repo: AbstractFileRepository = file_repo
        self._file_storage: AbstractFileStorage = file_storage

    async def save_file(self, file_name: str, file_text: str) -> int:
        file_hash = await self._get_file_hash(file_text)
        file = await self._file_repo.get_file_by_hash(file_hash)
        if not file:
            return await self._save_file(file_name, file_text)
        return file.id

    async def get_file(self, file_id: int) -> str | None:
        file_location = await self._file_repo.get_location(file_id)
        if not file_location:
            return None
        return await self._file_storage.load(location=file_location)


    async def _save_file(self, file_name: str, file_text: str) -> int:
        location = await self._file_storage.save(file_text)
        return await self._file_repo.add_one(
            data={
                "name": file_name,
                "hash": await self._get_file_hash(file_text),
                "location": str(location)
            }
        )

    @staticmethod
    async def _get_file_hash(content: str, algo: str = "sha256") -> str:
        hash_func = getattr(hashlib, algo)()
        hash_func.update(content.encode("utf-8"))
        return hash_func.hexdigest()
