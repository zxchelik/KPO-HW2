import pytest
import httpx

from src.infrastructure.external_api.HTTPWordCloud import HTTPWordCloud


class TestHTTPWordCloud:
    @pytest.fixture(autouse=True)
    def patch_async_client(self, mocker):
        # Create a fake httpx.Response
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_response.content = b"fake-bytes"

        # Create a fake AsyncClient
        mock_client = mocker.MagicMock()
        mock_client.post = mocker.AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=None)

        # Patch AsyncClient in our module
        mocker.patch(
            'src.infrastructure.external_api.HTTPWordCloud.AsyncClient',
            return_value=mock_client
        )

        return mock_client, mock_response

    def test_base_url_strips_slashes(self):
        wc = HTTPWordCloud(
            host="example.com",
            path="///path/to/cloud///",
            pic_format="png",
            width=100,
            height=200,
            font_family="Arial",
            font_scale=2,
            scale="linear"
        )
        assert wc.base_url == "https://example.com/path/to/cloud"

        wc2 = HTTPWordCloud(
            host="example.com",
            path="no/slashes",
            pic_format="jpg",
            width=1, height=1, font_family="", font_scale=1, scale=""
        )
        assert wc2.base_url == "https://example.com/no/slashes"

    @pytest.mark.asyncio
    async def test_get_word_cloud_sends_correct_payload_and_returns_bytes(self, patch_async_client):
        client, response = patch_async_client

        wc = HTTPWordCloud(
            host="hc",
            path="api/cloud",
            pic_format="svg",
            width=300,
            height=400,
            font_family="Times",
            font_scale=3,
            scale="log"
        )
        text = "some file text"

        result = await wc.get_word_cloud(text)

        # returns the content
        assert result == b"fake-bytes"

        expected_payload = {
            "format": "svg",
            "width": 300,
            "height": 400,
            "fontFamily": "Times",
            "fontScale": 3,
            "scale": "log",
            "text": text
        }
        expected_headers = {"Content-Type": "application/json"}

        # Assert that post was called once with the correct arguments
        client.post.assert_awaited_once_with(
            url=wc.base_url,
            json=expected_payload,
            headers=expected_headers
        )

    @pytest.mark.asyncio
    async def test_raises_on_non_200_status(self, patch_async_client):
        client, response = patch_async_client

        # simulate HTTP error
        def raise_err():
            raise httpx.HTTPStatusError("Bad", request=None, response=None)
        response.raise_for_status = raise_err

        wc = HTTPWordCloud(
            host="h", path="p", pic_format="", width=0, height=0,
            font_family="", font_scale=0, scale=""
        )

        with pytest.raises(httpx.HTTPStatusError):
            await wc.get_word_cloud("txt")

    @pytest.mark.asyncio
    async def test_handles_network_errors(self, patch_async_client):
        client, _ = patch_async_client

        # simulate network error on post
        client.post.side_effect = httpx.ConnectError("fail", request=None)

        wc = HTTPWordCloud(
            host="h", path="p", pic_format="", width=0, height=0,
            font_family="", font_scale=0, scale=""
        )

        with pytest.raises(httpx.ConnectError):
            await wc.get_word_cloud("txt")
