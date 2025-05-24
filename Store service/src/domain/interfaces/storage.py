from abc import ABC, abstractmethod
from typing import Union


class AbstractFileStorage(ABC):
    @abstractmethod
    async def save(self, content: Union[str, bytes]) -> str:
        """Сохраняет данные и возвращает строковый идентификатор (путь)."""
        raise NotImplementedError

    @abstractmethod
    async def load(self, location: str) -> Union[str, bytes]:
        """Загружает данные по строковому идентификатору."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, location: str) -> None:
        """Удаляет данные по строковому идентификатору."""
        raise NotImplementedError