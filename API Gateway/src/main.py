import asyncio

import httpx
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi

from utils.config import load_config
from utils.proxy import forward

app = FastAPI(title="Gateway", version="1.0.0", docs_url="/")
settings = load_config()

FILES_API_URL = f"{settings.FILES_API_URL}/openapi.json"
ANALYSIS_API_URL = f"{settings.ANALYSIS_API_URL}/openapi.json"


@app.api_route("/analysis/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
async def analysis_proxy(path: str, request: Request):
    return await forward(request, settings.ANALYSIS_API_URL, lambda p: f"/{path}")


@app.api_route("/files/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
async def files_proxy(path: str, request: Request):
    return await forward(request, settings.FILES_API_URL, lambda p: f"/{path}")


@app.on_event("startup")
async def fetch_openapi_schemas():
    # ...
    async with httpx.AsyncClient() as client:
        files_schema, analysis_schema = await asyncio.gather(
            client.get(FILES_API_URL),
            client.get(ANALYSIS_API_URL),
        )
    app.state.files_openapi = files_schema.json()
    app.state.analysis_openapi = analysis_schema.json()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    base_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        description="Объединённый Swagger для всех сервисов"
    )

    # Объединяем пути
    for path, path_data in app.state.files_openapi["paths"].items():
        base_schema["paths"][f"/files{path}"] = path_data

    for path, path_data in app.state.analysis_openapi["paths"].items():
        base_schema["paths"][f"/analysis{path}"] = path_data

    # Объединяем компоненты (если нужно)
    base_schema["components"] = {
        "schemas": {
            **app.state.files_openapi.get("components", {}).get("schemas", {}),
            **app.state.analysis_openapi.get("components", {}).get("schemas", {})
        }
    }

    app.openapi_schema = base_schema
    return app.openapi_schema


app.openapi = custom_openapi
