from pydantic import BaseModel


class FileStatSchema(BaseModel):
    id: int
    file_id: int
    word_count: int
    char_count: int
    is_unique: bool
    wordcloud_location: str
