import hashlib
import re

from src.domain.interfaces.base_file_text_reader import BaseFileTextReader
from src.domain.interfaces.base_picture_storage import BasePictureStorage
from src.domain.interfaces.base_wordcloud import BaseWordCloud
from src.domain.interfaces.repositories.base_file_stat_repository import BaseFileStatRepository
from src.domain.schemas.file_stats import FileStatSchema


class AnalysisService:
    def __init__(
            self,
            text_reader: BaseFileTextReader,
            pic_storage: BasePictureStorage,
            word_cloud: BaseWordCloud,
            file_stat_repository: BaseFileStatRepository
    ):
        self.text_reader = text_reader
        self.pic_storage = pic_storage
        self.word_cloud = word_cloud
        self.file_stat_repository = file_stat_repository

    async def get_file_stat(self, file_id: int) -> FileStatSchema:
        if stat := await self.file_stat_repository.get_file_stat(file_id):
            return stat
        return await self._get_file_stat(file_id)

    async def get_word_cloud(self, location: str) -> bytes:
        return await self.pic_storage.load(location=location)

    async def _get_file_stat(self, file_id: int) -> FileStatSchema:
        file_text = await self.text_reader.get_file_text_by_id(file_id)
        normalized_hash = self._get_text_normalized_hash(file_text)
        is_unique = await self.file_stat_repository.check_unique(normalized_hash)
        word_cloud_content = await self.word_cloud.get_word_cloud(file_text)
        word_cloud_location = await self.pic_storage.save(word_cloud_content)
        char_count = len(file_text)
        word_count = len(file_text.split())
        file_stat_id = await self.file_stat_repository.add_one(
            data={
                "file_id": file_id,
                "word_count": word_count,
                "char_count": char_count,
                "is_unique": is_unique,
                "wordcloud_location": word_cloud_location,
                "normalized_hash": normalized_hash
            }
        )
        return FileStatSchema(
            id=file_stat_id,
            file_id=file_id,
            word_count=word_count,
            char_count=char_count,
            is_unique=is_unique,
            wordcloud_location=word_cloud_location
        )

    @staticmethod
    def _get_text_normalized_hash(file_text: str) -> str:
        normalized = re.sub(r"\s+", " ", file_text.strip().lower())
        encoded = normalized.encode("utf-8")
        hash_value = hashlib.sha256(encoded).hexdigest()
        return hash_value
