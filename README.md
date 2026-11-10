# python-re3data-v2

The Pythonic client for the [re3data](https://www.re3data.org) API — targeting the current
**v40 REST interface** based on the **re3data metadata schema 4.0** (August 2023).

This is an independent re-implementation inspired by the architecture of
[python-re3data](https://github.com/afuetterer/python-re3data) (MIT), which targets the
deprecated `/api/beta` endpoints and schema 2-2 and has no v40 migration. The v40 API and
schema are documented at <https://www.re3data.org/api/doc/>.

## Highlights

- **v40 endpoints**: `GET /api/v40/repositories` and `GET /api/v40/repository/{id}`.
- **Typed schema 4.0 models**: hand-written dataclasses mirroring the
  [official XSD](https://schema.re3data.org/4-0/re3dataV4-0.xsd) — no `xsdata` dependency.
- **Robust parsing**: unknown vocabulary values and malformed dates never break a parse
  (the upstream data has already shown drift against the XSD).
- **Sync + async**: `Client` and `AsyncClient` on top of `httpx`.
- **Flexible serialization**: `dataclass`, `dict`, `json`, `xml`, `csv`, `response`.
- **Python 3.14+**, zero runtime dependencies except `httpx`.

## Installation

```shell
uv add python-re3data-v2        # or: pip install python-re3data-v2
```

With the optional CLI:

```shell
uv add 'python-re3data-v2[cli]'
```

## Usage

```python
import re3data

# module-level convenience manager (synchronous)
summaries = re3data.repositories.list(query="UCL")
for summary in summaries:
    print(summary.id, summary.doi, summary.name, summary.href)

repository = re3data.repositories.get("r3d100012417")
print(repository.repositoryName.value)      # "UCL Discovery"
print(repository.identifiers.doi)           # "https://doi.org/10.17616/R34F41"
print(repository.subject[0].subjectId)      # "4" (DFG classification id)
print(repository.entryDate)                 # datetime.date(2017, 7, 21)
```

```python
from re3data import AsyncClient

async with AsyncClient() as client:
    repository = await client.repositories.get("r3d100012417")
```

### Return types

```python
from re3data import Client, ReturnType

client = Client()
payload = client.repositories.get("r3d100012417", return_type=ReturnType.DICT)
```

`ReturnType.DICT` reproduces the document with XML-style keys (`repositoryUrl`,
`identifiers.re3data`, `subject[].subjectId`, ...), localized elements as
`{"value": ..., "language": ...}` and dates as ISO-8601 strings — the same conventions the
original python-re3data established.

### Facet filters

The v40 list endpoint supports ~30 facet filters. They are exposed via the `filters`
mapping and serialized as repeated `name[]` query parameters:

```python
client.repositories.list(
    query="climate",
    filters={"countries": ["DEU", "NZL"], "certificates": "CoreTrustSeal"},
)
```

## Known upstream issues

- `GET /api/v40/repositories` **without** a `query`/filter currently fails with HTTP 500
  on the server side (the deprecated beta endpoint shows the same behaviour). Listing all
  repositories therefore requires a query or filter; the client surfaces the error
  transparently.
- The API only serves `application/xml`; there is no JSON representation.

## Development

```shell
uv sync --all-groups
uv run pytest
uv run ruff check .
```

## License

MIT — see [LICENSE](LICENSE).
