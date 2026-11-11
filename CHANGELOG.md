# Changelog

## 0.2.0 (2026-11-11)

- Selectable API versions: `Client(api_version=..., list_api_version=..., detail_api_version=...)`
  accepts `v40` (default), `v1` or `beta`; list and detail endpoints can target different
  versions. Works around the ongoing upstream HTTP 500 of the v40 list endpoint via
  `Client(list_api_version="v1")`.
- Schema 2-2 detail documents (v1/beta) are auto-detected by XML namespace and converted
  into the schema 4.0 model, so callers always receive one shape.
- Facet filters are ignored with a warning on non-v40 list endpoints (v1 ignores them).
- CLI unchanged; `APIVersion` exported from the package root.

## 0.1.0 (2026-11-10)

- Initial release targeting the re3data v40 API (schema 4.0).
- Sync `Client` / async `AsyncClient` with a `repositories` manager (`list`, `get`).
- Typed schema 4.0 dataclass models, stdlib-ElementTree based XML parser.
- Return types: `dataclass`, `dict`, `json`, `xml`, `csv`, `response`.
- Facet filter support for the list endpoint (`filters={"countries": [...]}`).
- Optional CLI (`python-re3data-v2[cli]`, `re3data` command).
