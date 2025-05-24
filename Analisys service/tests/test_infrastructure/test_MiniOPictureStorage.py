import uuid
import asyncio
import importlib

import pytest

from src.infrastructure.picture_storage.MiniOPictureStorage import MiniOPictureStorage


class TestMiniOPictureStorage:
    @pytest.fixture(autouse=True)
    def _setup(self, mocker):
        # --- Stub out Minio client ---
        mock_client = mocker.Mock()
        mock_client.bucket_exists.return_value = False
        mock_client.make_bucket = mocker.Mock()
        mock_client.put_object = mocker.Mock()
        # Simulate get_object response
        mock_response = mocker.Mock()
        mock_response.read.return_value = b"data-bytes"
        mock_response.close = mocker.Mock()
        mock_response.release_conn = mocker.Mock()
        mock_client.get_object.return_value = mock_response
        mock_client.remove_object = mocker.Mock()

        # --- Patch Minio in the module where it's imported ---
        mops_mod = importlib.import_module(MiniOPictureStorage.__module__)
        mocker.patch.object(mops_mod, 'Minio', return_value=mock_client)

        # --- Patch uuid.uuid4 in that module to a fixed value ---
        fixed_uuid = uuid.UUID(int=0)
        mocker.patch.object(mops_mod.uuid, 'uuid4', return_value=fixed_uuid)

        # --- Patch asyncio.get_running_loop so executors run inline ---
        class DummyLoop:
            def run_in_executor(self, executor, func, *args):
                async def runner():
                    return func(*args)
                return runner()

        mocker.patch('asyncio.get_running_loop', return_value=DummyLoop())

        # --- Instantiate the storage ---
        self.storage = MiniOPictureStorage(
            endpoint="endpoint",
            access_key="ak",
            secret_key="sk",
            bucket_name="mybucket",
            secure=True,
            prefix="pic"
        )
        self.client = mock_client
        self.response = mock_response
        self.fixed_key = f"pic/{fixed_uuid}.png"

    @pytest.mark.asyncio
    async def test_init_creates_bucket_once(self):
        # First call should check & create bucket
        await self.storage.init()
        self.client.bucket_exists.assert_called_once_with("mybucket")
        self.client.make_bucket.assert_called_once_with("mybucket")

        # Second call should do nothing
        await self.storage.init()
        assert self.client.bucket_exists.call_count == 1
        assert self.client.make_bucket.call_count == 1

    @pytest.mark.asyncio
    async def test_save_puts_object_and_returns_key(self):
        content = b"hello"
        key = await self.storage.save(content)

        # ключ должен совпадать
        assert key == self.fixed_key

        # Проверяем вызов put_object с именованными параметрами
        assert self.client.put_object.call_count == 1
        _, kwargs = self.client.put_object.call_args
        assert kwargs["bucket_name"] == "mybucket"
        assert kwargs["object_name"] == self.fixed_key

        data_io = kwargs["data"]
        assert hasattr(data_io, "read")
        assert data_io.read() == content

        assert kwargs["length"] == len(content)

    @pytest.mark.asyncio
    async def test_load_gets_object_and_returns_bytes(self):
        payload = await self.storage.load("some/key.png")

        assert payload == b"data-bytes"
        self.client.get_object.assert_called_once_with("mybucket", "some/key.png")
        self.response.read.assert_called_once()
        self.response.close.assert_called_once()
        self.response.release_conn.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_removes_object(self):
        await self.storage.delete("old/key.png")
        self.client.remove_object.assert_called_once_with("mybucket", "old/key.png")

    @pytest.mark.asyncio
    async def test_save_with_empty_prefix(self, mocker):
        # New storage with no prefix
        storage2 = MiniOPictureStorage(
            endpoint="e", access_key="a", secret_key="s",
            bucket_name="bkt", secure=False, prefix=""
        )
        # Patch its module's uuid4 again
        mops_mod = importlib.import_module(storage2.__class__.__module__)
        new_uuid = uuid.UUID(int=1)
        mocker.patch.object(mops_mod.uuid, 'uuid4', return_value=new_uuid)
        # Re-use same Minio client stub
        storage2.client = self.client

        key = await storage2.save(b"bytes")
        assert key == f"{new_uuid}.png"
        assert self.client.put_object.called
