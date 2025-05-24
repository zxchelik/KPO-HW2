import pytest
import httpx

from src.infrastructure.external_api.HTTPFileTextReader import HTTPFileTextReader


class TestHTTPFileTextReader:
    @pytest.fixture(autouse=True)
    def patch_async_client(self, mocker):
        # Create a fake httpx.Response
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = mocker.Mock()
        mock_response.json = mocker.Mock()

        # Create a fake AsyncClient
        mock_client = mocker.MagicMock()
        mock_client.get = mocker.AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=None)

        # Patch AsyncClient in our module
        mocker.patch(
            'src.infrastructure.external_api.HTTPFileTextReader.AsyncClient',
            return_value=mock_client
        )

        return mock_client, mock_response

    @pytest.mark.asyncio
    async def test_successfully_retrieves_file_text_and_constructs_https_url(self, patch_async_client):
        client, response = patch_async_client
        response.json.return_value = {"file_text": "content"}

        reader = HTTPFileTextReader(host="example.com", port=443, path="/api/files", secure=True)
        result = await reader.get_file_text_by_id(123)

        assert result == "content"
        client.get.assert_awaited_once_with("https://example.com:443/api/files/123")

    @pytest.mark.asyncio
    async def test_constructs_http_url_when_secure_false(self, patch_async_client):
        client, response = patch_async_client
        response.json.return_value = {"file_text": "x"}

        reader = HTTPFileTextReader(host="host.com", port=80, path="files", secure=False)
        await reader.get_file_text_by_id(1)

        client.get.assert_awaited_once_with("http://host.com:80/files/1")

    @pytest.mark.asyncio
    async def test_strips_slashes_and_handles_multiple_edge_cases(self, patch_async_client):
        client, response = patch_async_client
        response.json.return_value = {"file_text": "z"}

        # multiple leading/trailing slashes
        reader1 = HTTPFileTextReader(host="h.com", port=1234, path="///p//q///", secure=True)
        await reader1.get_file_text_by_id(7)
        client.get.assert_awaited_with("https://h.com:1234/p//q/7")

        # empty path yields a double slash
        client.get.reset_mock()
        reader2 = HTTPFileTextReader(host="h.com", port=1234, path="", secure=False)
        await reader2.get_file_text_by_id(8)
        client.get.assert_awaited_with("http://h.com:1234//8")

    @pytest.mark.asyncio
    async def test_handles_file_id_zero_negative_and_large(self, patch_async_client):
        client, response = patch_async_client
        response.json.return_value = {"file_text": "ok"}

        reader = HTTPFileTextReader(host="h", port=9, path="api", secure=False)
        await reader.get_file_text_by_id(0)
        await reader.get_file_text_by_id(-1)
        big = 10**12
        await reader.get_file_text_by_id(big)

        urls = [call.args[0] for call in client.get.await_args_list]
        assert "api/0" in urls[0]
        assert "api/-1" in urls[1]
        assert f"api/{big}" in urls[2]

    @pytest.mark.asyncio
    async def test_manages_special_host_chars(self, patch_async_client):
        client, response = patch_async_client
        response.json.return_value = {"file_text": "spec"}

        special_host = "ex-ample_1.com"
        reader = HTTPFileTextReader(host=special_host, port=99, path="p", secure=True)
        await reader.get_file_text_by_id(22)

        client.get.assert_awaited_once_with(f"https://{special_host}:99/p/22")

    @pytest.mark.asyncio
    async def test_non_200_and_network_errors(self, patch_async_client):
        client, response = patch_async_client

        # non-200 status: code doesn't call raise_for_status, so .json returns default None → TypeError on indexing
        response.status_code = 404
        response.json.return_value = None
        reader = HTTPFileTextReader(host="h", port=9, path="api", secure=False)
        with pytest.raises(TypeError):
            await reader.get_file_text_by_id(1)

        # network error
        client.get.side_effect = httpx.ConnectError("fail", request=None)
        with pytest.raises(httpx.ConnectError):
            await reader.get_file_text_by_id(2)

    @pytest.mark.asyncio
    async def test_fails_on_bad_json_or_missing_key(self, patch_async_client):
        client, response = patch_async_client

        # malformed JSON
        response.status_code = 200
        response.raise_for_status = lambda: None
        response.json.side_effect = ValueError("Bad JSON")
        reader = HTTPFileTextReader(host="h", port=9, path="api", secure=False)
        with pytest.raises(ValueError):
            await reader.get_file_text_by_id(3)

        # missing 'file_text'
        response.json.side_effect = None
        response.json.return_value = {"other": "v"}
        with pytest.raises(KeyError):
            await reader.get_file_text_by_id(4)

    @pytest.mark.asyncio
    async def test_respects_context_manager_lifecycle(self, patch_async_client):
        client, response = patch_async_client
        response.json.return_value = {"file_text": "ok"}

        reader = HTTPFileTextReader(host="a", port=1, path="", secure=False)
        await reader.get_file_text_by_id(5)

        client.__aenter__.assert_awaited_once()
        client.__aexit__.assert_awaited_once()
