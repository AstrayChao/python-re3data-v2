"""Exception classes for errors encountered when using the re3data API."""


class Re3dataError(Exception):
    """Base exception class for errors related to the re3data API."""


class RepositoryNotFoundError(Re3dataError):
    """Exception raised when a repository is not found."""
