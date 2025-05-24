from abc import ABC,abstractmethod


class BaseFileTextReader(ABC):
    @abstractmethod
    async def get_file_text_by_id(self,file_id:int) -> str:
        raise NotImplementedError