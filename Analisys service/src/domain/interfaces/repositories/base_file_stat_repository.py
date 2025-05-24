from abc import ABC, abstractmethod

from src.domain.interfaces.repositories.base_repository import AbstractRepository
from src.domain.schemas.file_stats import FileStatSchema


class BaseFileStatRepository(AbstractRepository, ABC):
    @abstractmethod
    async def check_unique(self, normalized_hash: str):
        raise NotImplementedError

    @abstractmethod
    async def get_file_stat(self, file_id: int) -> FileStatSchema | None:
        raise NotImplementedError