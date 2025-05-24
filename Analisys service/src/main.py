from fastapi import FastAPI

from src.presentation.API.analysis import router

app = FastAPI()
app.include_router(router)

@app.get("/health_check",tags=["health check"])
async def health_check():
    return True
