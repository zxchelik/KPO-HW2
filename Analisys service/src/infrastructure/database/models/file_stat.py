from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.schemas.file_stats import FileStatSchema
from src.infrastructure.database.db_context import Base


class FileStat(Base):
    __tablename__ = "file_stat"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_id: Mapped[int] = mapped_column(unique=True)
    normalized_hash: Mapped[str]
    word_count: Mapped[int]
    char_count: Mapped[int]
    is_unique: Mapped[bool]
    wordcloud_location: Mapped[str] = mapped_column(String)

    def to_read_model(self) -> FileStatSchema:
        return FileStatSchema(
            id=self.id,
            file_id=self.file_id,
            word_count=self.word_count,
            char_count=self.char_count,
            is_unique=self.is_unique,
            wordcloud_location=self.wordcloud_location,
        )
