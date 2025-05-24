from abc import ABC, abstractmethod


class BasePictureStorage(ABC):
    @abstractmethod
    async def save(self, content: bytes) -> str:
        raise NotImplementedError

    @abstractmethod
    async def load(self, location: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def delete(self,location:str) -> None:
        raise NotImplementedError
