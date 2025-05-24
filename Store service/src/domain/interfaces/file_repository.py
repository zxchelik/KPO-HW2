from abc import ABC, abstractmethod

from domain.interfaces.base_repository import AbstractRepository
from domain.schemas.file import FileSchema


class AbstractFileRepository(AbstractRepository, ABC):
    @abstractmethod
    async def get_location(self, file_id: int) -> str:
        raise NotImplementedError

    async def get_file_by_hash(self, file_hash: str) -> FileSchema | None:
        raise NotImplementedError