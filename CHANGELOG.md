# Changelog

## 0.1.0 (2026-11-10)

- Initial release targeting the re3data v40 API (schema 4.0).
- Sync `Client` / async `AsyncClient` with a `repositories` manager (`list`, `get`).
- Typed schema 4.0 dataclass models, stdlib-ElementTree based XML parser.
- Return types: `dataclass`, `dict`, `json`, `xml`, `csv`, `response`.
- Facet filter support for the list endpoint (`filters={"countries": [...]}`).
- Optional CLI (`python-re3data-v2[cli]`, `re3data` command).
