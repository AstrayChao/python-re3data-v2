<div align="center">

# python-re3data-v2

**re3data API 的 Python 客户端 — v40 · schema 4.0 · Python 3.14+**

[![PyPI version](https://img.shields.io/pypi/v/python-re3data-v2?logo=pypi&logoColor=white)](https://pypi.org/project/python-re3data-v2/)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-3776ab?logo=python&logoColor=white)](pyproject.toml)
[![Tests](https://github.com/AstrayChao/python-re3data-v2/actions/workflows/test.yml/badge.svg)](https://github.com/AstrayChao/python-re3data-v2/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![代码风格: ruff](https://img.shields.io/badge/%E4%BB%A3%E7%A0%81%E9%A3%8E%E6%A0%BC-ruff-261230?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)
[![原仓库已归档](https://img.shields.io/badge/%E5%8E%9F%E4%BB%93%E5%BA%93-%E5%B7%B2%E5%BD%92%E6%A1%A3-lightgrey?logo=github)](https://github.com/afuetterer/python-re3data)

[English](README.md) · [简体中文](README.zh-CN.md)

</div>

---

> [!NOTE]
> **本仓库的由来** — 原客户端 [`python-re3data`](https://github.com/afuetterer/python-re3data)
>（作者 Heinz-Alexander Fütterer，MIT 协议）已被官方**归档（archived）**，且仅支持已废弃的
> `/api/beta` 接口（schema 2-2）。本项目是在其架构与输出约定基础上**从零重写**的独立实现，
> 面向当前 **v40 REST API** 与 [re3data 元数据 schema 4.0](https://doi.org/10.48440/re3.014)。

> [!WARNING]
> **尚未正式发布，请谨慎用于生产环境。** v40 API 与 schema 4.0 均为较新的接口，
> 可能仍存在未覆盖的边界情况；正式稳定版发布前请自行评估风险。

## ✨ 特性

| | |
|---|---|
| 🚀 **v40 接口** | `GET /api/v40/repositories` · `GET /api/v40/repository/{id}` |
| 🧬 **schema 4.0 类型化模型** | 按[官方 XSD](https://schema.re3data.org/4-0/re3dataV4-0.xsd) 手写 dataclass，不依赖 `xsdata` |
| 🛡️ **容错解析** | 词表未知值、畸形日期都不会导致解析失败 |
| ⚡ **同步 + 异步** | 基于 `httpx` 的 `Client` 与 `AsyncClient` |
| 🔄 **多种序列化** | `dataclass` · `dict` · `json` · `xml` · `csv` · `response` |
| 🎛️ **facet 过滤** | 一个 `filters` 字典覆盖 v40 全部约 30 个过滤参数 |
| 🪶 **极简依赖** | Python 3.14+，运行时仅依赖 `httpx` |

## 📦 安装

```bash
pip install python-re3data-v2        # 或：uv add python-re3data-v2
```

安装可选 CLI：

```bash
pip install 'python-re3data-v2[cli]'
```

## 🚀 快速开始

```python
import re3data

# 模块级同步入口
summaries = re3data.repositories.list(query="UCL")
for summary in summaries:
    print(summary.id, summary.doi, summary.name, summary.href)

repository = re3data.repositories.get("r3d100012417")
print(repository.repositoryName.value)   # "UCL Discovery"
print(repository.identifiers.doi)        # "https://doi.org/10.17616/R34F41"
print(repository.subject[0].subjectId)   # "4"（DFG 学科分类 ID）
print(repository.entryDate)              # datetime.date(2017, 7, 21)
```

显式客户端与异步用法：

```python
from re3data import AsyncClient, Client, ReturnType

client = Client()
payload = client.repositories.get("r3d100012417", return_type=ReturnType.DICT)

async with AsyncClient() as async_client:
    repository = await async_client.repositories.get("r3d100012417")
```

`ReturnType.DICT` 输出 XML 风格键名（`repositoryUrl`、`identifiers.re3data`、
`subject[].subjectId`……），带属性元素为 `{"value": ..., "language": ...}`，日期为
ISO-8601 字符串 —— 与原 `python-re3data` 的约定一致，存量消费方可以平滑迁移。

facet 过滤（序列化为重复的 `name[]` 查询参数）：

```python
client.repositories.list(
    query="climate",
    filters={"countries": ["DEU", "NZL"], "certificates": "CoreTrustSeal"},
)
```

CLI：

```console
$ re3data repository get r3d100012417 --return-type json
$ re3data repository list --query "UCL" --return-type csv
```

## 🔀 与原版 `python-re3data` 的差异

| 维度 | python-re3data 0.10 | python-re3data-v2 |
|---|---|---|
| API | `/api/beta`（已废弃） | `/api/v40`（当前） |
| 元数据 schema | 2-2 | **4.0**（2023-08） |
| Python | ≥ 3.10 | **≥ 3.14** |
| XML 绑定 | `xsdata` 代码生成 | 标准库 `ElementTree` + 手写模型 |
| 列表字段 | id、doi、link | id、doi、**name**、link |
| `dataframe` 返回类型 | ✅（需 pandas） | ❌（移除；内置 `csv`） |
| facet 过滤 | 仅 `query` | `query` + `filters` 字典 |

schema 2-2 → 4-0 的逐字段对照见 [docs/schema-mapping.md](docs/schema-mapping.md)，
调研与迁移记录见 [docs/research.md](docs/research.md)（中文）。

## ⚠️ 已知上游问题

- 不带 `query`/过滤参数的 `GET /api/v40/repositories` 当前**服务端返回 HTTP 500**
  （已废弃的 beta 接口同样如此）。全量列表暂时需要 query 或 filter；客户端会如实抛出错误。
- API 仅提供 `application/xml`，没有 JSON 格式。
- 线上数据偶发与 XSD 词表不一致（如 `"institutional membership"` 与
  `"institutionalMembership"` 并存）。词表字段统一为纯 `str` 原样保留，未知值不会报错。

## 🛠️ 开发

```bash
uv sync --all-groups   # 创建 Python 3.14 环境
uv run pytest          # 单元 + 集成测试（离线，真实 v40 XML 样本）
uv run pytest -m e2e   # 真实 API 冒烟测试
uv run ruff check .    # 代码检查
```

## 📄 许可证

[MIT](LICENSE)，与原项目一致。本项目在架构与 dict 输出约定上刻意与
[python-re3data](https://github.com/afuetterer/python-re3data)（作者
Heinz-Alexander Fütterer）保持兼容，但不共享任何代码。

## 🙏 致谢

- [python-re3data](https://github.com/afuetterer/python-re3data) —— 本项目延续的原客户端。
- [re3data.org](https://www.re3data.org) —— 研究数据仓库注册库，卡尔斯鲁厄理工学院 / FIZ Karlsruhe。
