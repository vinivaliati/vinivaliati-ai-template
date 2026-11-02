---
name: dbt-modeling
description: >
  How to design and build dbt models: staging, intermediate and marts layers,
  model and column naming, contracts, YML layout, required tests, profiling the
  source before writing, and a model spec before any SQL. Use when creating,
  changing or reviewing a dbt model, source, YML file or dbt_project.yml; when
  the user says "create a model", "new staging for", "build a fact/dimension",
  "add this column to the mart", "cria um modelo", "modela essa tabela" or
  "sobe essa fonte no dbt"; or when deciding grain, keys or materialization.
  Do not use for SQL formatting alone (use sql-style), for migrating legacy
  logic such as ABAP or stored procedures (use legacy-to-dbt) or for test
  strategy beyond the minimum below (use data-quality).
---

# dbt modeling

Every model answers three questions before it has SQL: what is one row (grain),
what makes a row unique (key), and who consumes it. The layers, names and tests
below exist so that anyone can open a project and know where logic lives
without reading it.

Write the SQL itself following the `sql-style` skill.

## Layers

| Layer | Purpose | Name | Materialized | Contract | YML |
|---|---|---|---|---|---|
| staging | One model per source table: rename, cast, light cleaning. No joins, no aggregations. | `stg_<source>__<entities>` | view | no | one per source folder |
| intermediate | Reusable building blocks: joins, deduplication, business rules. Not for end users. | `int_<entities>_<verb or description>` | table | enforced | one per model |
| marts | Final grain for consumers (BI, apps, exports). | `fct_<process>`, `dim_<entity>` [SUGGESTION] | table | enforced | one per model |

Why: staging is a clean, 1:1 mirror of the source, so source changes break in
one place. Intermediate holds logic once, so marts do not duplicate it. Marts
are a contract with consumers, so their columns cannot change by accident.

Rules:

- A mart never selects from a source or another layer's raw table; only from
  staging, intermediate or other marts.
- Staging never joins. If a source needs a join to make sense (header and
  item tables), the join happens in intermediate.
- Do not create an intermediate model that is used by only one mart and has
  no reusable logic; keep that logic as CTEs in the mart.

### Folder layout

```text
models/
├── staging/
│   └── erp/
│       ├── _erp__sources.yml
│       ├── _erp__models.yml
│       ├── stg_erp__orders.sql
│       └── stg_erp__order_items.sql
├── intermediate/
│   └── logistics/
│       ├── int_orders_with_deliveries.sql
│       └── int_orders_with_deliveries.yml
└── marts/
    └── logistics/
        ├── fct_order_otif.sql
        └── fct_order_otif.yml
```

Staging folders are named after the source system; intermediate and marts
folders after the business domain.

### Materialization in `dbt_project.yml`

Set defaults per folder, not in every model:

```yaml
models:
  my_project:
    staging:
      +materialized: view
    intermediate:
      +materialized: table
      +contract:
        enforced: true
    marts:
      +materialized: table
      +contract:
        enforced: true
```

Override in a model's `config()` only with a reason in a SQL comment (for
example, incremental because the table is too large to rebuild daily).

## Column naming

dbt Labs style, no type prefixes. Full rules and edge cases in
[references/naming.md](references/naming.md).

| Kind | Pattern | Example |
|---|---|---|
| Primary or foreign key (natural) | `<entity>_id` | `order_id`, `customer_id` |
| Surrogate key (hash) | `<entity>_sk` | `order_delivery_sk` |
| Code from the source | `<thing>_code` | `order_status_code` |
| Name or label | `<thing>_name` | `carrier_name` |
| Boolean | `is_<state>`, `has_<thing>` | `is_on_time`, `has_return` |
| Date | `<event>_date` | `promised_date` |
| Timestamp | `<event>_at` | `delivered_at` |
| Measure | plain noun with unit when ambiguous | `ordered_quantity`, `freight_amount_brl` |

Column order in every model (SQL and YML): **ids** (surrogate key first, then
the model's own id, then foreign ids), **strings**, **numerics**, **booleans**,
**dates**, **timestamps**.

## Contracts

- Every column of an intermediate or mart model is listed in its YML with a
  `data_type` that matches the `cast()` in the SQL. A contract fails the build
  when they differ; that is the point.
- Cast in the CTE where the column enters (usually staging). The mart only
  re-casts when the type changes on purpose.
- Types follow [`sql-style` dialects](../sql-style/references/dialects.md).
  Defaults when the spec is silent:
  - decimal part found in profiling: exact decimal (`number(38, 2)` or the
    dialect equivalent); widen the scale only if profiling shows more digits;
  - no decimal part found: integer;
  - text: no length;
  - write every default you applied in the final report.

## Minimum tests

Every model ships with SQL and YML in the same change. At minimum:

- the grain key: `unique` and `not_null` (or `dbt_utils.unique_combination_of_columns`
  for a composite grain);
- every foreign id in a mart: `relationships` to the model that owns it, but
  only when that model exists; never create an orphan foreign key;
- every `_code` column with a small, known set of values: `accepted_values`.

Details, severities and what goes beyond the minimum:
[references/testing.md](references/testing.md). Freshness, volume,
reconciliation and anomaly checks belong to the `data-quality` skill.

## Workflow

1. **Spec first.** Fill [assets/model-spec.yml](assets/model-spec.yml) with the
   user: purpose, consumer, grain, keys, sources, columns, business rules.
   Ask about every missing field; do not guess grain, keys or rules. Show the
   filled spec and wait for approval before writing SQL.
2. **Read the project.** `dbt_project.yml`, the existing models in the
   target folders, `packages.yml`, macros. Reuse existing staging and
   intermediate models instead of creating parallel ones. If the project
   breaks a rule here on purpose, follow the project and mention it.
3. **Profile the source.** Run the queries in
   [references/profiling.md](references/profiling.md) (sample, candidate key
   uniqueness, nulls, decimal part, date range, latest timestamp). Summarize
   the results before writing. If you cannot query the warehouse, ask the
   user to run them and paste the output.
4. **Write SQL and YML together.** SQL structure comes from the `sql-style`
   example; staging renames follow [references/naming.md](references/naming.md);
   YML tests follow [references/testing.md](references/testing.md).
   Descriptions in English for every model and every column of intermediate
   and mart models.
5. **Incremental needs a written justification.** A full rebuild is the
   default because it is simpler and cannot drift. Before proposing
   incremental, read [references/incremental.md](references/incremental.md),
   describe the nature of the data in the spec and get approval:
   - why a full rebuild is not enough, with numbers (rows, run time, cost);
   - how rows arrive: append-only events, updates in place, hard deletes;
   - whether late or backdated data exists (created today with an event
     date in the past) and how late it can arrive;
   - which column reliably marks a change, and the evidence for it;
   - the lookback window and the plan for periodic full refreshes.

   Why: an incremental filter on `extracted_at` or on a business date works
   in the demo and then silently drops backdated rows or corrections. If
   nobody can explain how late data behaves, the model stays a full rebuild.
6. **Validate.**
   - Run `dbt compile --select <model>` and `sqlfluff lint` on your own.
   - Then ask: "Run `dbt build --select +<model>+ --target dev`?" Run it only
     after a yes, only against the dev target, never prod.
7. **Report**: files created or changed, profiling summary, defaults applied,
   tests added, open questions, and the build command if it was not run.

## Example

Good spec excerpt (fictional distribution company):

```yaml
name: fct_order_otif
purpose: Daily OTIF (on time, in full) per order for the logistics dashboard.
consumer: BI, logistics managers
grain: one row per order
keys:
  primary: [order_id]
  foreign:
    - column: customer_id
      references: dim_customer.customer_id
```

Bad (and why):

```yaml
name: orders_final_v2          # no layer prefix, versioned name
grain: orders                  # not a grain; one row per order? per item? per day?
keys: {}                       # no key, so no uniqueness test is possible
```

## Before saying "done"

- [ ] Spec approved and matches what was built.
- [ ] Model name and folder follow the layer table.
- [ ] Columns follow naming and order rules; no type prefixes.
- [ ] SQL follows `sql-style` and ends with `select * from final`.
- [ ] YML exists, every contract column has a matching `data_type`.
- [ ] Grain key tested `unique` and `not_null`; foreign ids tested.
- [ ] Incremental models have an approved justification of the data's nature.
- [ ] Descriptions in English.
- [ ] `dbt compile` passed; `dbt build` run only after approval, in dev.
- [ ] Report delivered with defaults and open questions.
