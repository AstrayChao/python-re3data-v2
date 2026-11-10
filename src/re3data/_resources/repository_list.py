"""API resources for the /repositories endpoint (v40).

The list endpoint returns a HATEOAS-style index document:

.. code-block:: xml

    <list>
        <repository>
            <id>r3d100012417</id>
            <doi>https://doi.org/10.17616/R34F41</doi>
            <name>UCL Discovery</name>
            <link href="https://www.re3data.org/api/v40/repository/r3d100012417" rel="self" />
        </repository>
    </list>

Note: compared to the deprecated beta API, the v40 list additionally includes
the repository ``name``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__NAMESPACE__ = "http://www.re3data.org/schema/4-0"


@dataclass(slots=True)
class Link:
    """A hyperlink pointing to a repository resource.

    Attributes:
        href: The URL of the linked resource.
        rel: The relation type of the link, e.g. "self".
    """

    href: str | None = None
    rel: str | None = None


@dataclass(slots=True)
class RepositorySummary:
    """A single repository entry of the list endpoint.

    Attributes:
        id: The re3data identifier of the repository, e.g. "r3d100012417".
        doi: The DOI of the repository.
        name: The name of the repository.
        link: A hyperlink to the repository detail resource.
    """

    id: str | None = None
    doi: str | None = None
    name: str | None = None
    link: Link | None = None

    @property
    def href(self) -> str | None:
        """The URL of the detail resource, derived from the link element."""
        return self.link.href if self.link else None


@dataclass(slots=True)
class RepositoryList:
    """The root element of the list endpoint response."""

    repository: list[RepositorySummary] = field(default_factory=list)
