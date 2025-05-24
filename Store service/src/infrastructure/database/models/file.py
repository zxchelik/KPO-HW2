from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from domain.schemas.file import FileSchema
from infrastructure.database.db_context import Base
from infrastructure.database.models.types import String64


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[String64]
    hash: Mapped[String64] = mapped_column(unique=True)
    location: Mapped[str] = mapped_column(String)

    def to_read_model(self):
        return FileSchema(
            id=self.id,
            name=self.name,
            hash=self.hash,
            location=self.location
        )
