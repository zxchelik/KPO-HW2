import pytest
from sqlalchemy import select
from src.infrastructure.database.repositories.file_stat import SQLFileStat, FileStat

class TestSQLFileStat:

    @pytest.mark.asyncio
    async def test_check_unique_returns_true_when_no_record_exists(self, mocker):
        # Arrange
        mock_session = mocker.AsyncMock()

        # <-- вот здесь обычный Mock, не AsyncMock
        mock_scalars = mocker.Mock()
        mock_scalars.one_or_none.return_value = None

        async def fake_scalars(stmt):
            return mock_scalars
        mock_session.scalars.side_effect = fake_scalars

        mock_ctx = mocker.AsyncMock()
        mock_ctx.__aenter__.return_value = mock_session
        mocker.patch(
            'src.infrastructure.database.repositories.file_stat.async_session_maker',
            return_value=mock_ctx
        )

        repo = SQLFileStat()
        normalized_hash = "test_hash_123"

        # Act
        result = await repo.check_unique(normalized_hash)

        # Assert
        assert result is True
        expected = select(FileStat).filter(FileStat.normalized_hash == normalized_hash)
        called = mock_session.scalars.call_args[0][0]
        assert str(called) == str(expected)


    @pytest.mark.asyncio
    async def test_check_unique_returns_false_when_record_exists(self, mocker):
        # Arrange
        mock_session = mocker.AsyncMock()

        mock_scalars = mocker.Mock()
        dummy = FileStat(id=1, normalized_hash="h")
        mock_scalars.one_or_none.return_value = dummy

        async def fake_scalars(stmt):
            return mock_scalars
        mock_session.scalars.side_effect = fake_scalars

        mock_ctx = mocker.AsyncMock()
        mock_ctx.__aenter__.return_value = mock_session
        mocker.patch(
            'src.infrastructure.database.repositories.file_stat.async_session_maker',
            return_value=mock_ctx
        )

        repo = SQLFileStat()

        # Act & Assert
        assert await repo.check_unique("h") is False


    @pytest.mark.asyncio
    async def test_check_unique_handles_empty_string_normalized_hash(self, mocker):
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
            'src.infrastructure.database.repositories.file_stat.async_session_maker',
            return_value=mock_ctx
        )

        repo = SQLFileStat()

        # Act
        result = await repo.check_unique("")

        # Assert
        assert result is True


    @pytest.mark.asyncio
    async def test_get_file_stat_returns_none_when_not_found(self, mocker):
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
            'src.infrastructure.database.repositories.file_stat.async_session_maker',
            return_value=mock_ctx
        )

        repo = SQLFileStat()

        # Act
        result = await repo.get_file_stat(42)

        # Assert
        assert result is None
        expected = select(FileStat).filter(FileStat.id == 42)
        called = mock_session.scalars.call_args[0][0]
        assert str(called) == str(expected)


    @pytest.mark.asyncio
    async def test_get_file_stat_returns_model_when_found(self, mocker):
        # Arrange
        dummy = FileStat(id=7, normalized_hash="abc")
        mock_session = mocker.AsyncMock()

        mock_scalars = mocker.Mock()
        mock_scalars.one_or_none.return_value = dummy

        async def fake_scalars(stmt):
            return mock_scalars
        mock_session.scalars.side_effect = fake_scalars

        mock_ctx = mocker.AsyncMock()
        mock_ctx.__aenter__.return_value = mock_session
        mocker.patch(
            'src.infrastructure.database.repositories.file_stat.async_session_maker',
            return_value=mock_ctx
        )

        repo = SQLFileStat()

        # Act
        result = await repo.get_file_stat(7)

        # Assert
        assert isinstance(result, FileStat)
        assert result.id == 7
        assert result.normalized_hash == "abc"
