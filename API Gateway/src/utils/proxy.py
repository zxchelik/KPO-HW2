from fastapi import Request
from starlette.responses import Response
from httpx import AsyncClient, Response as HTTPXResponse
from typing import Callable

_client = AsyncClient()

async def forward(
    request: Request,
    base_url: str,
    rewrite_path: Callable[[str], str] = lambda p: p,
) -> Response:
    url = base_url + rewrite_path(request.url.path)

    response: HTTPXResponse = await _client.request(
        request.method,
        url,
        headers=request.headers.raw,
        params=request.query_params,
        content=await request.body(),
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers={k: v for k, v in response.headers.items() if k.lower() != "transfer-encoding"},
    )