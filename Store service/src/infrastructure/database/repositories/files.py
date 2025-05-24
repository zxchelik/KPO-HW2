from sqlalchemy import select

from domain.interfaces.base_repository import SQLAlchemyRepository
from domain.interfaces.file_repository import AbstractFileRepository
from domain.schemas.file import FileSchema
from infrastructure.database.db_context import async_session_maker
from infrastructure.database.models import File


class SQLFileRepository(AbstractFileRepository, SQLAlchemyRepository):
    model = File

    async def get_location(self, file_id) -> str | None:
        async with async_session_maker() as session:
            stmt = select(self.model.location).filter(self.model.id == file_id)
            file_location = (await session.scalars(stmt)).one_or_none()
            if not file_location:
                return None
            return file_location

    async def get_file_by_hash(self, file_hash: str) -> FileSchema | None:
        async with async_session_maker() as session:
            stmt = select(self.model).filter(self.model.hash == file_hash)
            file = (await session.scalars(stmt)).one_or_none()
            if file:
                return file.to_read_model()
            return None
