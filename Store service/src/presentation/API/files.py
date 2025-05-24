import logging
import traceback

from fastapi import APIRouter, File, UploadFile, HTTPException, Path
from pydantic import BaseModel
from starlette import status

from presentation.dependencies.sevices import FileServiceDep

router = APIRouter(prefix="/files", tags=["Работа с файлами"])


class UploadResponse(BaseModel):
    file_id: int

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

@router.post("/", response_model=UploadResponse)
async def upload_file(file_service: FileServiceDep, file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files allowed")
    try:
        content = await file.read()
        text = content.decode("utf-8")
        return {"file_id": await file_service.save_file(file_name=file.filename, file_text=text)}

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {str(e)}")


class FileContentResponse(BaseModel):
    file_text: str


@router.get("/{file_id}", response_model=FileContentResponse)
async def get_file(file_service: FileServiceDep, file_id: int = Path(...,ge=1)):
    file_text = await file_service.get_file(file_id)

    if file_text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Файл с id={file_id} не найден"
        )

    return {"file_text": file_text}