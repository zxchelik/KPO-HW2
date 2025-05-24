from abc import ABC, abstractmethod


class BaseWordCloud(ABC):
    @abstractmethod
    async def get_word_cloud(self, file_text: str) -> bytes:
        raise NotImplementedError
