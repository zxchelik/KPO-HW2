from fastapi import APIRouter, Response

from src.presentation.DTO.FileStatDTO import FileStatDTO
from src.presentation.dependencies.analysis_service import AnalysisServiceDep

router = APIRouter(prefix="/analysis",tags=["Аналитика"])


@router.get("/{file_id}", response_model=FileStatDTO)
async def get_file_stat(file_id: int, analysis_service: AnalysisServiceDep):
    stat = await analysis_service.get_file_stat(file_id)
    return FileStatDTO(
        file_id=stat.file_id,
        word_count=stat.word_count,
        char_count=stat.char_count,
        is_unique=stat.is_unique,
        wordcloud_location=stat.wordcloud_location,
    )


@router.get("/wordcloud/{location:path}")
async def get_wordcloud(location: str, analysis_service: AnalysisServiceDep):
    content = await analysis_service.get_word_cloud(location)
    return Response(content=content, media_type="image/png")
