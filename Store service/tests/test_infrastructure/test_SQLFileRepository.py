import pytest
from sqlalchemy import select
from infrastructure.database.models import File
from infrastructure.database.repositories.files import SQLFileRepository


class TestSQLFileRepository:

    @pytest.mark.asyncio
    async def test_get_location_returns_path_when_exists(self, mocker):
        # Arrange
        mock_session = mocker.AsyncMock()
        mock_scalars = mocker.Mock()
        mock_scalars.one_or_none.return_value = "/path/to/file.txt"

        async def fake_scalars(stmt):
            return mock_scalars
        mock_session.scalars.side_effect = fake_scalars

        mock_ctx = mocker.AsyncMock()
        mock_ctx.__aenter__.return_value = mock_session
        mocker.patch(
            'infrastructure.database.repositories.files.async_session_maker',
            return_value=mock_ctx
        )

        repo = SQLFileRepository()

        # Act
        location = await repo.get_location(123)

        # Assert
        assert location == "/path/to/file.txt"
        expected = select(File.location).filter(File.id == 123)
        called_stmt = mock_session.scalars.call_args[0][0]
        assert str(called_stmt) == str(expected)

    @pytest.mark.asyncio
    async def test_get_location_returns_none_when_not_exists(self, mocker):
        # Arrange
        mock_session = mocker.AsyncMock()
        mock_scalars = mocker.Mock()
        mock_scalars.one_or_none.return_value = None

        async def fake_scalars(stmt):
            return mock_scalars
        mock_session.scalars.side_effect = fake_scalars

        mock_ctx = mocker.AsyncMock()
        mock_ctx.__aenter__.return_value = mock_session
        mocker.patch(
            'infrastructure.database.repositories.files.async_session_maker',
            return_value=mock_ctx
        )

        repo = SQLFileRepository()

        # Act
        location = await repo.get_location(999)

        # Assert
        assert location is None
        expected = select(File.location).filter(File.id == 999)
        called_stmt = mock_session.scalars.call_args[0][0]
        assert str(called_stmt) == str(expected)

    @pytest.mark.asyncio
    async def test_get_file_by_hash_returns_schema_when_exists(self, mocker):
        # Arrange
        mock_session = mocker.AsyncMock()
        mock_scalars = mocker.Mock()
        fake_file = mocker.Mock()
        fake_schema = mocker.Mock()
        fake_file.to_read_model.return_value = fake_schema
        mock_scalars.one_or_none.return_value = fake_file

        async def fake_scalars(stmt):
            return mock_scalars
        mock_session.scalars.side_effect = fake_scalars

        mock_ctx = mocker.AsyncMock()
        mock_ctx.__aenter__.return_value = mock_session
        mocker.patch(
            'infrastructure.database.repositories.files.async_session_maker',
            return_value=mock_ctx
        )

        repo = SQLFileRepository()

        # Act
        result = await repo.get_file_by_hash("hash_abc")

        # Assert
        assert result is fake_schema
        expected = select(File).filter(File.hash == "hash_abc")
        called_stmt = mock_session.scalars.call_args[0][0]
        assert str(called_stmt) == str(expected)

    @pytest.mark.asyncio
    async def test_get_file_by_hash_returns_none_when_not_exists(self, mocker):
        # Arrange
        mock_session = mocker.AsyncMock()
        mock_scalars = mocker.Mock()
        mock_scalars.one_or_none.return_value = None

        async def fake_scalars(stmt):
            return mock_scalars
        mock_session.scalars.side_effect = fake_scalars

        mock_ctx = mocker.AsyncMock()
        mock_ctx.__aenter__.return_value = mock_session
        mocker.patch(
            'infrastructure.database.repositories.files.async_session_maker',
            return_value=mock_ctx
        )

        repo = SQLFileRepository()

        # Act
        result = await repo.get_file_by_hash("no_such_hash")

        # Assert
        assert result is None
        expected = select(File).filter(File.hash == "no_such_hash")
        called_stmt = mock_session.scalars.call_args[0][0]
        assert str(called_stmt) == str(expected)
