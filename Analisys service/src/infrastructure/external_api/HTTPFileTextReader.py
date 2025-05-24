from httpx import AsyncClient

from src.domain.interfaces.base_file_text_reader import BaseFileTextReader

class HTTPFileTextReader(BaseFileTextReader):

    def __init__(self, host: str, port: int, path: str, secure: bool = False):
        self.host = host
        self.port = port
        self.path = path
        self.secure = secure

    @property
    def base_url(self):
        return f"http{'s' if self.secure else ''}://{self.host}:{self.port}/{self.path.strip('/')}"


    async def get_file_text_by_id(self, file_id: int):
        async with AsyncClient() as client:
            response = await client.get(f"{self.base_url}/{file_id}")
            return response.json()["file_text"]