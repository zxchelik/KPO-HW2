# tests/test_application/test_file_service.py

import pytest
from unittest.mock import AsyncMock, Mock
from application.services.file_service import FileService  # путь адаптируй под себя


class TestFileService:

    @pytest.fixture(autouse=True)
    def _setup(self, mocker):
        self.mock_repo = mocker.Mock()
        self.mock_repo.get_file_by_hash = AsyncMock()
        self.mock_repo.get_location = AsyncMock()
        self.mock_repo.add_one = AsyncMock()

        self.mock_storage = mocker.Mock()
        self.mock_storage.save = AsyncMock()
        self.mock_storage.load = AsyncMock()

        self.service = FileService(
            file_repo=self.mock_repo,
            file_storage=self.mock_storage
        )

    @pytest.mark.asyncio
    async def test_save_file_when_not_exists(self):
        # Arrange
        file_name = "test.txt"
        file_text = "hello world"
        fake_hash = await self.service._get_file_hash(file_text)
        self.mock_repo.get_file_by_hash.return_value = None
        self.mock_storage.save.return_value = "file/key"
        self.mock_repo.add_one.return_value = 42

        # Act
        file_id = await self.service.save_file(file_name, file_text)

        # Assert
        assert file_id == 42
        self.mock_repo.get_file_by_hash.assert_called_once_with(fake_hash)
        self.mock_storage.save.assert_called_once_with(file_text)
        self.mock_repo.add_one.assert_called_once()
        data = self.mock_repo.add_one.call_args[1]["data"]
        assert data["name"] == file_name
        assert data["hash"] == fake_hash
        assert data["location"] == "file/key"

    @pytest.mark.asyncio
    async def test_save_file_when_already_exists(self):
        # Arrange
        file_text = "same content"
        fake_hash = await self.service._get_file_hash(file_text)
        existing_file = Mock(id=99)
        self.mock_repo.get_file_by_hash.return_value = existing_file

        # Act
        file_id = await self.service.save_file("ignored.txt", file_text)

        # Assert
        assert file_id == 99
        self.mock_repo.get_file_by_hash.assert_called_once_with(fake_hash)
        self.mock_storage.save.assert_not_called()
        self.mock_repo.add_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_file_when_exists(self):
        # Arrange
        self.mock_repo.get_location.return_value = "key/123"
        self.mock_storage.load.return_value = "file contents"

        # Act
        result = await self.service.get_file(7)

        # Assert
        assert result == "file contents"
        self.mock_repo.get_location.assert_called_once_with(7)
        self.mock_storage.load.assert_called_once_with(location="key/123")

    @pytest.mark.asyncio
    async def test_get_file_when_missing(self):
        # Arrange
        self.mock_repo.get_location.return_value = None

        # Act
        result = await self.service.get_file(404)

        # Assert
        assert result is None
        self.mock_repo.get_location.assert_called_once_with(404)
        self.mock_storage.load.assert_not_called()
