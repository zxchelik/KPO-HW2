from pydantic import BaseModel


class FileStatDTO(BaseModel):
    file_id: int
    word_count: int
    char_count: int
    is_unique: bool
    wordcloud_location: str

    class Config:
        from_attributes = True