from sqlalchemy import select

from src.domain.interfaces.repositories.base_file_stat_repository import BaseFileStatRepository
from src.domain.interfaces.repositories.base_repository import SQLAlchemyRepository
from src.domain.schemas.file_stats import FileStatSchema
from src.infrastructure.database.db_context import async_session_maker
from src.infrastructure.database.models.file_stat import FileStat


class SQLFileStat(SQLAlchemyRepository, BaseFileStatRepository):
    model = FileStat

    async def check_unique(self, normalized_hash: str) -> bool:
        async with async_session_maker() as session:
            stmt = select(FileStat).filter(FileStat.normalized_hash == normalized_hash)
            return (await session.scalars(stmt)).one_or_none() is None

    async def get_file_stat(self, file_id: int) -> FileStatSchema | None:
        async with async_session_maker() as session:
            stmt = select(FileStat).filter(FileStat.id == file_id)
            return (await session.scalars(stmt)).one_or_none()

