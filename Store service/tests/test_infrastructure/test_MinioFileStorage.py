# tests/test_infrastructure/test_MinioFileStorage.py

import asyncio
import uuid
import importlib

import pytest
from infrastructure.storage.minio_storage import MinioFileStorage  # путь адаптируй под себя


class DummyLoop:
    def run_in_executor(self, executor, func, *args):
        async def runner():
            return func(*args)
        return runner()

class TestMinioFileStorage:
    @pytest.fixture(autouse=True)
    def _setup(self, mocker):
        # --- Stub Minio client ---
        mock_client = mocker.Mock()
        mock_client.bucket_exists.return_value = False
        mock_client.make_bucket = mocker.Mock()
        mock_client.put_object = mocker.Mock()

        # --- Simulate get_object response ---
        mock_response = mocker.Mock()
        mock_response.read.return_value = b"binary-data"
        mock_response.close = mocker.Mock()
        mock_response.release_conn = mocker.Mock()
        mock_client.get_object.return_value = mock_response

        mock_client.remove_object = mocker.Mock()

        # --- Patch Minio import ---
        mod = importlib.import_module(MinioFileStorage.__module__)
        mocker.patch.object(mod, 'Minio', return_value=mock_client)

        # --- Patch uuid ---
        fixed_uuid = uuid.UUID(int=0)
        mocker.patch.object(mod.uuid, 'uuid4', return_value=fixed_uuid)

        # --- Patch asyncio loop ---
        class DummyLoop:
            def run_in_executor(self, executor, func, *args):
                async def runner():
                    return func(*args)
                return runner()

        mocker.patch('asyncio.get_running_loop', return_value=DummyLoop())

        # --- Instantiate the storage ---
        self.storage = MinioFileStorage(
            endpoint="localhost:9000",
            access_key="minio",
            secret_key="minio123",
            bucket_name="test-bucket",
            secure=False,
            prefix="docs"
        )
        self.client = mock_client
        self.response = mock_response
        self.fixed_key = "docs/00000000-0000-0000-0000-000000000000.txt"

    @pytest.mark.asyncio
    async def test_init_creates_bucket_once(self):
        await self.storage.init()
        self.client.bucket_exists.assert_called_once_with("test-bucket")
        self.client.make_bucket.assert_called_once_with("test-bucket")

        await self.storage.init()
        assert self.client.bucket_exists.call_count == 1
        assert self.client.make_bucket.call_count == 1

    @pytest.mark.asyncio
    async def test_save_puts_object_and_returns_key(self):
        content = b"Hello!"
        key = await self.storage.save(content)

        assert key == self.fixed_key
        assert self.client.put_object.call_count == 1

        _, kwargs = self.client.put_object.call_args
        assert kwargs["bucket_name"] == "test-bucket"
        assert kwargs["object_name"] == self.fixed_key
        assert kwargs["length"] == len(content)
        assert kwargs["data"].read() == content

    @pytest.mark.asyncio
    async def test_save_encodes_string_content(self):
        key = await self.storage.save("Привет, мир!")
        put_args = self.client.put_object.call_args[1]
        data = put_args["data"].read()
        assert isinstance(data, bytes)
        assert data == "Привет, мир!".encode("utf-8")

    @pytest.mark.asyncio
    async def test_load_decodes_utf8_to_string(self):
        self.response.read.return_value = b"binary-data"
        data = await self.storage.load("some/key.txt")

        assert isinstance(data, str)
        assert data == "binary-data"

    @pytest.mark.asyncio
    async def test_load_decodes_utf8_when_possible(self, mocker):
        self.response.read.return_value = b"utf8-text"
        data = await self.storage.load("file.txt")
        assert data == "utf8-text"

    @pytest.mark.asyncio
    async def test_load_falls_back_to_bytes_on_decode_error(self, mocker):
        self.response.read.return_value = b"\xff\xfe\xfa"
        data = await self.storage.load("binfile")
        assert isinstance(data, bytes)

    @pytest.mark.asyncio
    async def test_delete_removes_file(self):
        await self.storage.delete("old/file.txt")
        self.client.remove_object.assert_called_once_with("test-bucket", "old/file.txt")

    @pytest.mark.asyncio
    async def test_save_with_empty_prefix(self, mocker):
        storage2 = MinioFileStorage(
            endpoint="host", access_key="a", secret_key="b",
            bucket_name="bucket", prefix="", secure=False
        )
        mod = importlib.import_module(storage2.__class__.__module__)
        new_uuid = uuid.UUID(int=2)
        mocker.patch.object(mod.uuid, 'uuid4', return_value=new_uuid)
        mocker.patch('asyncio.get_running_loop', return_value=DummyLoop())
        storage2.client = self.client

        key = await storage2.save(b"abc")
        assert key == f"{new_uuid}.txt"
        assert self.client.put_object.called
