# 调研报告：re3data API v40 迁移与 python-re3data-v2

> 调研日期：2026-11-10 · 所有结论均来自实测（真实 API 响应）与官方资料交叉验证。

## 1. API 现状

官方文档 <https://www.re3data.org/api/doc/>（页面内嵌 Swagger 2.0 spec，已提取分析）：

| Endpoint | 状态 | 说明 |
|---|---|---|
| `GET /api/v40/repositories` | **当前版本** | schema 4.0 索引列表 |
| `GET /api/v40/repository/{id}` | **当前版本** | schema 4.0 详情 |
| `GET /api/beta/repositories`、`/repository/{id}` | **Deprecated** | 旧库 python-re3data 0.10.0 所用 |
| `GET /api/v1/...` | **Deprecated** | 更老版本 |
| `/api/opensearch/*` | 辅助 | 搜索建议 |

实测确认的关键行为：

- **仅 XML**：`produces: application/xml`。`Accept: application/json` 与 `?format=json` 均无效，仍返回 XML。
- **无分页**：spec 中没有任何分页参数（无 `page`/`cursor`/`size`）。
- **全量列表当前 500**：不带任何参数请求 `/api/v40/repositories` 与 `/api/beta/repositories` 均返回 HTTP 500（服务端故障，两代 API 一致）。带 `query=` 或任意 filter 正常。**新库如实抛出 httpx.HTTPStatusError，由调用方决定重试/降级。**
- **列表元素**：v40 比 beta 多了 `<name>`（id/doi/name/link）。
- **过滤器**：v40 列表支持约 30 个 facet 参数（`countries[]`、`dataAccess[]`、`certificates[]`、`subjects[]`（新数字 ID 体系）、`contentType40[]`（COAR）、`metadataStandard40[]`、新增 `metrics[]`/`profiles[]`/`citationReferences[]`）。

## 2. Schema 2-2 → 4-0 字段级差异

权威 XSD：<https://schema.re3data.org/4-0/re3dataV4-0.xsd>（已抓取解析，见 [schema-mapping.md](schema-mapping.md) 完整对照表）。

结构性变化（对下游消费方影响最大）：

1. `re3data.orgIdentifier` → `identifiers/re3data` + `identifiers/doi`（DOI 成为一级字段）
2. `subject`：自由文本（"11204 Business Administration"）→ `subjectId` + `subjectName`（DFG 281 项枚举）
3. `contentType`："parse" 文本枚举 → COAR resource type URI 体系（22 项）
4. `certificate`：纯枚举 → 结构体（name/startDate/endDate/url/widget）
5. `repositoryContact`：纯文本 → 结构体（information/type）
6. `institutionIdentifier`：纯文本 → 结构体（type/url）
7. `api`：text+@apiType → `apiType`/`apiUrl`/`apiDocumentation` 三元素
8. `qualityManagement`：yes/no/unknown → 结构体（status + measures[]）
9. `endDate`：日期 → closed/offline 标志
10. URL 类字段命名统一小写：`repositoryURL`→`repositoryUrl`、`metadataStandardURL`→`metadataStandardUrl` 等

枚举值变化：

- `type`：3 → 6 值（新增 governmental/multidisciplinary/project-related）
- restriction 值：`"institutional membership"` → `"institutionalMembership"`（**注意：实测数据仍返回带空格的旧值，证明数据与 XSD 存在漂移**，这正是本库词表字段用纯 str 的原因）；`other` 全部移除；upload 新增 `storageLimit`
- `responsibilityType` 移除 `sponsoring`
- software/pidSystem/aidSystem/license 等旧枚举全部放宽为 `xs:string`

新增字段：`fundingInformation`、`relatedRepository`、`metrics`、`citationReference`、`profile`、`apiDocumentation`、`responsibilityStartDate/EndDate`、`certificate` 日期结构、`qualityManagementMeasure`。

移除：`size@updated` 日期属性等。

## 3. 上游 python-re3data

- 最新版 0.10.0（2024-12-11），此后仅有 CI/依赖维护提交，**无 v40 迁移计划**（issues 只有 dependabot）。
- 架构：httpx + xsdata（代码生成 dataclass）+ typer CLI；`Client/AsyncClient.repositories.{list,get}`，`return_type ∈ {dataclass, dict, json, xml, response, csv, dataframe}`。
- 其 dict 输出契约（xsdata DictEncoder）：XML 名做键、`{"value": 文本, "language": "eng"}` 平铺、日期字符串化——**本库保持一致**。
- 已知痛点（源码注释自述）：API 数据与 XSD 不一致导致大量 ConverterWarning，多处被迫放宽类型。

## 4. 本库设计（python-re3data-v2）

| 决策 | 选择 | 理由 |
|---|---|---|
| Python | **>=3.14**（实测 3.14.0） | 用户要求；httpx 0.28+/typer 0.29+ 均兼容 |
| 发行/导入名 | `python-re3data-v2` / `re3data` | data-sync 换依赖后 `import re3data` 零改动 |
| XML 解析 | **stdlib ElementTree + 手写 dataclass** | 去 xsdata 依赖；dict 契约完全可控；3.14 零风险 |
| 词表字段 | 纯 `str` + 参考 StrEnum | 上游数据已与 XSD 漂移（实测 "institutional membership"），永不因未知值解析失败 |
| 字段命名 | dataclass 字段名 = XML 名（camelCase） | `asdict` 直接产出旧库风格 dict 契约 |
| 依赖 | 仅 `httpx`；CLI 为 `typer` 可选 extra | 最小化 |
| 差异 | 无 pandas/dataframe；csv 用 stdlib | 减重；data-sync 只用 dict |

已知上游问题对策：全量列表 500 → 库如实抛错；建议 data-sync 发现阶段用 query 或等待上游修复。

## 5. data-sync 迁移要点（第二阶段）

1. 依赖：`python-re3data>=0.10,<0.11` → `python-re3data-v2`（本地路径/git）。
2. `Re3dataClient` 包装层：调用签名兼容（`return_type`），`_extract_id`/mapper 需适配：
   - `re3data.orgIdentifier` → `identifiers.re3data`
   - `subject[].value` → `subject[].subjectName`（+subjectId）
   - `contentType[].value` → `contentType[].contentTypeName`（COAR 词表，映射表需重做）
   - `certificate[]`（str 枚举）→ `certificate[].certificateName`（+日期/URL）
   - `api[].value` → `api[].apiUrl`
   - `repositoryURL` → `repositoryUrl`（大小写）
   - `institutionIdentifier`（str 列表）→ `{institutionIdentifierType, institutionIdentifierUrl}`
   - `size` 不再有 `updated` 属性（updater 已不依赖 size，无影响）
   - `metadataStandard` 无 scheme 属性、URL 小写
3. 全量列表 500 期间：`list_repository_ids()` 失败 → 依赖 DB 已有 id 集合跑 platform/raw 更新；新记录发现可临时用 `query` 分片（如按国家 filter 枚举）。

## 6. 验证记录

- 49 个单元/集成测试（4 份真实 v40 响应 fixture + httpx.MockTransport）全部通过。
- 4 个 e2e 冒烟（真实 API）：详情解析、详情 dict、带 query 列表、无 query 列表正确暴露上游 500。
- ruff lint 全绿；CLI（`re3data --version`、`re3data repository get ... --return-type json`）验证通过。
