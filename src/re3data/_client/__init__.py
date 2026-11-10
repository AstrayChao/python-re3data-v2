"""Clients for the re3data v40 API."""

from re3data._client._async import AsyncClient, AsyncRepositoryManager
from re3data._client._sync import Client, RepositoryManager
from re3data._client.base import BASE_URL, ReturnType

__all__ = (
    "BASE_URL",
    "AsyncClient",
    "AsyncRepositoryManager",
    "Client",
    "RepositoryManager",
    "ReturnType",
)
