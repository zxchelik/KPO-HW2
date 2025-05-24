from pydantic import BaseModel


class FileSchema(BaseModel):
    id: int
    name: str
    hash: str
    location: str

    class Config:
        from_attributes = True