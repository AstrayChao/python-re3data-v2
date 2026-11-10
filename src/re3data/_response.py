"""A structured representation of responses from the re3data API."""

from __future__ import annotations

from dataclasses import dataclass, field

import httpx


@dataclass(slots=True)
class Response:
    """A response received from the re3data API, encapsulating the HTTP response.

    Attributes:
        url: The URL of the request.
        status_code: The HTTP status code of the response.
        headers: The response headers.
        text: The raw XML response text.
    """

    url: httpx.URL
    status_code: httpx.codes
    headers: httpx.Headers = field(repr=False)
    text: str = field(repr=False)


def _build_response(http_response: httpx.Response) -> Response:
    """Build a :class:`Response` object from an ``httpx.Response``."""
    return Response(
        url=http_response.url,
        status_code=httpx.codes(http_response.status_code),
        headers=http_response.headers,
        text=http_response.text,
    )
