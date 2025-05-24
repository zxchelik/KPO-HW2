import hashlib
import pytest

from src.application.services.analysis import AnalysisService
from src.domain.interfaces.base_file_text_reader import BaseFileTextReader
from src.domain.interfaces.base_picture_storage import BasePictureStorage
from src.domain.interfaces.base_wordcloud import BaseWordCloud
from src.domain.interfaces.repositories.base_file_stat_repository import BaseFileStatRepository
from src.domain.schemas.file_stats import FileStatSchema


class BaseTestAnalysisService:
    """Базовый класс, готовит мок-объекты и сам сервис."""
    @pytest.fixture(autouse=True)
    def _setup(self, mocker):
        self.mock_text_reader = mocker.Mock(spec=BaseFileTextReader)
        self.mock_word_cloud  = mocker.Mock(spec=BaseWordCloud)
        self.mock_pic_storage = mocker.Mock(spec=BasePictureStorage)
        self.mock_file_stat_repository = mocker.Mock(spec=BaseFileStatRepository)

        # По умолчанию — нет статистики
        self.mock_file_stat_repository.get_file_stat = mocker.AsyncMock(return_value=None)

        # И создаём сервис
        self.service = AnalysisService(
            text_reader=self.mock_text_reader,
            pic_storage=self.mock_pic_storage,
            word_cloud=self.mock_word_cloud,
            file_stat_repository=self.mock_file_stat_repository
        )


class TestAnalysisService(BaseTestAnalysisService):

    @pytest.mark.asyncio
    async def test_get_word_cloud(self, mocker):
        # Arrange
        self.mock_pic_storage.load = mocker.AsyncMock(return_value=b"img")
        # Act
        result = await self.service.get_word_cloud(location="path.png")
        # Assert
        assert result == b"img"
        self.mock_pic_storage.load.assert_awaited_once_with(location="path.png")


    @pytest.mark.asyncio
    async def test_existing_file_stat(self):
        # Arrange
        stat = FileStatSchema(id=1, file_id=5, word_count=2, char_count=10, is_unique=True, wordcloud_location="x")
        self.mock_file_stat_repository.get_file_stat.return_value = stat
        # Act
        got = await self.service.get_file_stat(5)
        # Assert
        assert got == stat
        self.mock_file_stat_repository.get_file_stat.assert_awaited_once_with(5)
        self.mock_text_reader.get_file_text_by_id.assert_not_called()


    @pytest.mark.asyncio
    async def test_creates_new_unique_stat(self, mocker):
        # Arrange
        file_id = 7
        raw = "One two"
        norm = "one two"
        h = hashlib.sha256(norm.encode()).hexdigest()

        self.mock_text_reader.get_file_text_by_id = mocker.AsyncMock(return_value=raw)
        self.mock_file_stat_repository.check_unique = mocker.AsyncMock(return_value=True)
        self.mock_file_stat_repository.add_one = mocker.AsyncMock(return_value=99)
        self.mock_word_cloud.get_word_cloud = mocker.AsyncMock(return_value=b"wc")
        self.mock_pic_storage.save = mocker.AsyncMock(return_value="loc")

        # Act
        stat = await self.service.get_file_stat(file_id)

        # Assert schema
        assert isinstance(stat, FileStatSchema)
        assert stat.id == 99
        assert stat.word_count == 2
        assert stat.char_count == len(raw)
        assert stat.is_unique is True
        assert stat.wordcloud_location == "loc"

        # Assert calls
        self.mock_file_stat_repository.get_file_stat.assert_awaited_once_with(file_id)
        self.mock_text_reader.get_file_text_by_id.assert_awaited_once_with(file_id)
        self.mock_file_stat_repository.check_unique.assert_awaited_once_with(h)
        self.mock_word_cloud.get_word_cloud.assert_awaited_once_with(raw)
        self.mock_pic_storage.save.assert_awaited_once_with(b"wc")
        data = self.mock_file_stat_repository.add_one.call_args[1]["data"]
        assert data == {
            "file_id": file_id,
            "word_count": 2,
            "char_count": len(raw),
            "is_unique": True,
            "wordcloud_location": "loc",
            "normalized_hash": h
        }


    @pytest.mark.asyncio
    async def test_creates_new_nonunique_stat(self, mocker):
        # Arrange
        file_id = 8
        raw = "Foo bar baz"
        norm = "foo bar baz"
        h = hashlib.sha256(norm.encode()).hexdigest()

        self.mock_text_reader.get_file_text_by_id = mocker.AsyncMock(return_value=raw)
        self.mock_file_stat_repository.check_unique = mocker.AsyncMock(return_value=False)
        self.mock_file_stat_repository.add_one = mocker.AsyncMock(return_value=100)
        self.mock_word_cloud.get_word_cloud = mocker.AsyncMock(return_value=b"wc2")
        self.mock_pic_storage.save = mocker.AsyncMock(return_value="loc2")

        # Act
        stat = await self.service.get_file_stat(file_id)

        # Assert
        assert stat.is_unique is False
        assert stat.id == 100
        self.mock_file_stat_repository.check_unique.assert_awaited_once_with(h)


def test_static_normalization():
    text = "  A  B\nC "
    expected = hashlib.sha256("a b c".encode()).hexdigest()
    assert AnalysisService._get_text_normalized_hash(text) == expected
