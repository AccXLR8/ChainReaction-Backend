from __future__ import annotations

from azure.storage.blob.aio import BlobServiceClient


class StorageService:
    def __init__(self, connection_string: str, container: str):
        self.connection_string = connection_string
        self.container = container
        self._client: BlobServiceClient | None = None

    async def _ensure_client(self) -> BlobServiceClient:
        if self._client is None:
            self._client = BlobServiceClient.from_connection_string(self.connection_string)
        return self._client

    async def upload_text(self, blob_name: str, data: str) -> None:
        client = await self._ensure_client()
        container_client = client.get_container_client(self.container)
        await container_client.upload_blob(name=blob_name, data=data, overwrite=True)

    async def download_text(self, blob_name: str) -> str:
        client = await self._ensure_client()
        blob_client = client.get_blob_client(container=self.container, blob=blob_name)
        stream = await blob_client.download_blob()
        return await stream.content_as_text()

    async def delete(self, blob_name: str) -> None:
        client = await self._ensure_client()
        await client.get_blob_client(container=self.container, blob=blob_name).delete_blob()
