from httpx import AsyncClient

from src.domain.interfaces.base_wordcloud import BaseWordCloud


class HTTPWordCloud(BaseWordCloud):
    def __init__(
            self,
            host: str,
            path: str,
            pic_format: str,
            width: int,
            height: int,
            font_family: str,
            font_scale: int,
            scale: str,
    ):
        self.host = host
        self.path = path
        self.format = pic_format
        self.width = width
        self.height = height
        self.fontFamily = font_family
        self.fontScale = font_scale
        self.scale = scale

    @property
    def base_url(self):
        return f"https://{self.host}/{self.path.strip('/')}"

    async def get_word_cloud(self, file_text: str) -> bytes:
        async with AsyncClient() as client:
            payload = {
                "format": self.format,
                "width": self.width,
                "height": self.height,
                "fontFamily": self.fontFamily,
                "fontScale": self.fontScale,
                "scale": self.scale,
                "text": file_text
            }
            headers = {
                "Content-Type": "application/json",
            }

            response = await client.post(url=self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.content
