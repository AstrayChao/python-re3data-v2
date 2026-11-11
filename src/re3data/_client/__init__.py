"""Clients for the re3data API."""

from re3data._client._async import AsyncClient, AsyncRepositoryManager
from re3data._client._sync import Client, RepositoryManager
from re3data._client.base import API_ROOT_URL, APIVersion, ReturnType

__all__ = (
    "API_ROOT_URL",
    "APIVersion",
    "AsyncClient",
    "AsyncRepositoryManager",
    "Client",
    "RepositoryManager",
    "ReturnType",
)
