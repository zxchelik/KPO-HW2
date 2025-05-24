import os
import uuid

import aiofiles
from typing import Union

from domain.interfaces.storage import AbstractFileStorage


class LocalFileStorage(AbstractFileStorage):
    def __init__(self, base_path: str):
        self.base_path = base_path

    async def save(self,content: Union[str, bytes]) -> str:
        location = uuid.uuid4()
        full_path = os.path.join(self.base_path, f"{location}")
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        mode = 'w' if isinstance(content, str) else 'wb'
        async with aiofiles.open(full_path, mode) as f:
            await f.write(content)
        return location

    async def load(self, location: str) -> str:
        full_path = os.path.join(self.base_path, location)
        mode = 'r' if full_path.endswith('.txt') else 'rb'
        async with aiofiles.open(full_path, mode) as f:
            return await f.read()

    async def delete(self, location: str) -> None:
        full_path = os.path.join(self.base_path, location)
        if os.path.exists(full_path):
            os.remove(full_path)
