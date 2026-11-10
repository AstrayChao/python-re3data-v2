<div align="center">

# python-re3data-v2

**The Pythonic client for the [re3data](https://www.re3data.org) API — v40 · schema 4.0 · Python 3.14+**

[![Original repo archived](https://img.shields.io/badge/original%20repo-archived-lightgrey?logo=github)](https://github.com/afuetterer/python-re3data)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-3776ab?logo=python&logoColor=white)](pyproject.toml)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-261230?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)
[![Tests](https://img.shields.io/badge/tests-53%20passed-brightgreen)](tests)

[English](README.md) · [简体中文](README.zh-CN.md)

</div>

---

> [!NOTE]
> **Why this fork exists** — the original client [`python-re3data`](https://github.com/afuetterer/python-re3data)
> by Heinz-Alexander Fütterer (MIT) has been **archived** and targets the deprecated
> `/api/beta` endpoints (schema 2-2). This repository is an independent re-implementation,
> built from scratch against the current **v40 REST API** and the
> [re3data metadata schema 4.0](https://doi.org/10.48440/re3.014), keeping the familiar
> architecture and dict conventions of the original.

> [!WARNING]
> **Not production-ready yet.** This library is young: the v40 API and schema 4.0 are new,
> and edge cases may still exist. **Use with caution in production environments until the
> first stable release.** 非正式发布阶段，请谨慎用于生产环境。

## ✨ Highlights

| | |
|---|---|
| 🚀 **v40 endpoints** | `GET /api/v40/repositories` · `GET /api/v40/repository/{id}` |
| 🧬 **Typed schema 4.0 models** | Hand-written dataclasses mirroring the [official XSD](https://schema.re3data.org/4-0/re3dataV4-0.xsd) — no `xsdata` |
| 🛡️ **Drift-tolerant parsing** | Unknown vocabulary values / malformed dates never break a parse |
| ⚡ **Sync + async** | `Client` and `AsyncClient` on top of `httpx` |
| 🔄 **Flexible serialization** | `dataclass` · `dict` · `json` · `xml` · `csv` · `response` |
| 🎛️ **Facet filters** | ~30 v40 filter facets via a single `filters` mapping |
| 🪶 **Minimal footprint** | Python 3.14+, the only runtime dependency is `httpx` |

## 📦 Installation

```bash
pip install python-re3data-v2        # or: uv add python-re3data-v2
```

With the optional CLI:

```bash
pip install 'python-re3data-v2[cli]'
```

## 🚀 Quick start

### Module-level manager (synchronous)

```python
import re3data

summaries = re3data.repositories.list(query="UCL")
for summary in summaries:
    print(summary.id, summary.doi, summary.name, summary.href)

repository = re3data.repositories.get("r3d100012417")
print(repository.repositoryName.value)   # "UCL Discovery"
print(repository.identifiers.doi)        # "https://doi.org/10.17616/R34F41"
print(repository.subject[0].subjectId)   # "4" (DFG classification id)
print(repository.entryDate)              # datetime.date(2017, 7, 21)
```

### Explicit clients

```python
from re3data import Client, AsyncClient

client = Client()
repository = client.repositories.get("r3d100012417")

async with AsyncClient() as async_client:
    repository = await async_client.repositories.get("r3d100012417")
```

### Return types

```python
from re3data import Client, ReturnType

client = Client()
payload = client.repositories.get("r3d100012417", return_type=ReturnType.DICT)
```

`ReturnType.DICT` reproduces the document with XML-style keys (`repositoryUrl`,
`identifiers.re3data`, `subject[].subjectId`, …), localized elements as
`{"value": ..., "language": ...}` and dates as ISO-8601 strings — the same
conventions the original `python-re3data` established, so existing consumers
keep working with minimal changes.

### Facet filters

The v40 list endpoint supports ~30 facet filters, serialized as repeated
`name[]` query parameters:

```python
client.repositories.list(
    query="climate",
    filters={"countries": ["DEU", "NZL"], "certificates": "CoreTrustSeal"},
)
```

### CLI

```console
$ re3data repository get r3d100012417 --return-type json
$ re3data repository list --query "UCL" --return-type csv
```

## 🔀 Differences vs. the original `python-re3data`

| Aspect | python-re3data 0.10 | python-re3data-v2 |
|---|---|---|
| API | `/api/beta` (deprecated) | `/api/v40` (current) |
| Metadata schema | 2-2 | **4.0** (August 2023) |
| Python | ≥ 3.10 | **≥ 3.14** |
| XML binding | `xsdata` codegen | stdlib `ElementTree` + hand-written models |
| List entry fields | id, doi, link | id, doi, **name**, link |
| `dataframe` return type | ✅ (requires pandas) | ❌ (dropped; `csv` is built-in) |
| Facet filters | `query` only | `query` + `filters` mapping |

A complete field-by-field mapping between schema 2-2 and 4.0 is available in
[docs/schema-mapping.md](docs/schema-mapping.md); the underlying research and
migration notes live in [docs/research.md](docs/research.md).

## ⚠️ Known upstream issues

- `GET /api/v40/repositories` **without** a `query`/filter currently fails with
  HTTP 500 server-side (the deprecated beta endpoint behaves the same). Listing
  everything therefore requires a query or filter for now; the client surfaces
  the error transparently.
- The API only serves `application/xml` — there is no JSON representation.
- Live data occasionally deviates from the XSD vocabularies (e.g.
  `"institutional membership"` vs. `"institutionalMembership"`). Vocabulary
  fields are typed as plain `str` and parsed verbatim, so unknown values never
  raise.

## 📚 API reference

`re3data.repositories` · `re3data.Client` · `re3data.AsyncClient`

| Method | Description |
|---|---|
| `repositories.list(query=None, filters=None, return_type=..., count=False)` | List repositories, optionally filtered |
| `repositories.get(repository_id, return_type=...)` | Fetch one repository by its re3data id |

<details>
<summary>Reference enums exported for convenience</summary>

`RepositoryType`, `ProviderType`, `DatabaseAccessType`, `DatabaseAccessRestriction`,
`DataAccessType`, `DataAccessRestriction`, `DataUploadType`, `DataUploadRestriction`,
`InstitutionType`, `ResponsibilityType`, `RelatedRepositoryType`, `YesNo`

</details>

## 🛠️ Development

```bash
uv sync --all-groups   # Python 3.14 environment
uv run pytest          # unit + integration (offline, real v40 XML fixtures)
uv run pytest -m e2e   # live API smoke tests
uv run ruff check .    # lint
```

## 📄 License

[MIT](LICENSE) — same as the original project. The architecture and dict
conventions are deliberately compatible with
[python-re3data](https://github.com/afuetterer/python-re3data) by
Heinz-Alexander Fütterer; this repository shares no code with it.

## 🙏 Credits

- [python-re3data](https://github.com/afuetterer/python-re3data) — the original
  Pythonic client this project continues, in spirit and API shape.
- [re3data.org](https://www.re3data.org) — registry of research data
  repositories, Karlsruhe Institute of Technology / FIZ Karlsruhe.
