---
name: legacy-to-dbt
description: >
  Migrates existing business logic into dbt models: SAP ABAP reports, stored
  procedures, old SQL views, scripts or spreadsheet formulas. Reads the legacy
  code first, asks only what it cannot answer, keeps the legacy result
  (same rows, same scope) and reconciles the new model against it. Use when
  the user shares legacy code to replicate or says "migrate this report to
  dbt", "convert this ABAP", "rewrite this procedure in dbt", "migra esse
  relatório", "converte esse ABAP", "replica essa procedure no dbt". Do not
  use for new models with no legacy logic (use dbt-modeling).
---

# Legacy to dbt

Legacy logic is a business rule that someone already trusts. The first goal
is a dbt model that returns the same result; improvements come after, as a
separate and visible change. A "better" model that does not match the legacy
output cannot be validated, so nobody will trust it.

## Rules

1. **Read the code before asking.** Sources, fields, joins, filters and
   calculations come from the legacy code. Ask only what it cannot tell.
2. **Translate intent, not steps.** Loops, temp tables and cursors become
   joins, filters, `group by` and window functions.
3. **Equivalence first.** Same join types, same scope, same grain as the
   legacy output. Propose improvements only after reconciliation passes.
4. **Never guess hidden logic.** Called functions, procedures, macros or
   lookups you cannot see may change values or filters. Flag each one and ask.
5. **The project's conventions win.** Read existing models first; use the
   kit defaults (`dbt-modeling`, `sql-style`) only where the project has none.
6. **Client code stays in the client repo.** Report names, filter values and
   field mappings from a real system never go into the kit or public repos.

## Workflow

1. **Read the legacy code** and list: purpose, sources, output columns,
   joins and lookups, calculations, parameters, calls to other code.
2. **Split the parameters.** Runtime filters (date ranges, document numbers)
   are dropped: the BI tool filters. Business scope (company, organization,
   plant) is kept, with values confirmed by the user. When unsure, ask.
3. **Ask the rest in one round:** who uses the output and how often, whether
   dbt replaces or complements it, scope values, what each hidden call does,
   where the legacy output can be read for reconciliation.
4. **Discover the project:** sources, existing staging models, naming,
   dialect. Reuse what exists; create only what is missing.
5. **Write the spec** with `dbt-modeling`'s `assets/model-spec.yml`, plus a
   mapping table: legacy field, model column, transformation.
6. **Write the models** with `dbt-modeling` and `sql-style`.
7. **Audit the joins** against the legacy code (below) and fix mismatches
   before running anything.
8. **Compile, then reconcile** (below). `dbt build` only after the user
   approves, in dev.

## Example: reading legacy code

Fictional ABAP report:

```abap
SELECT vbak~vbeln vbak~kunnr vbap~posnr vbap~matnr vbap~kwmeng
  INTO TABLE lt_items
  FROM vbak INNER JOIN vbap ON vbap~vbeln = vbak~vbeln
  WHERE vbak~vkorg = p_vkorg
    AND vbak~erdat IN s_erdat.

LOOP AT lt_items INTO ls_item.
  SELECT SINGLE name1 FROM kna1 INTO ls_item-name1
    WHERE kunnr = ls_item-kunnr.
  MODIFY lt_items FROM ls_item.
ENDLOOP.
```

Read: the `INNER JOIN` stays inner; the `SELECT SINGLE` inside the loop is a
lookup, so it becomes a `left join`; `p_vkorg` is business scope (ask the
value); `s_erdat` is a runtime filter and is dropped. The same reading applies
to a procedure (`#temp` tables become CTEs, `update ... from` becomes a
`left join` with `coalesce`) or a spreadsheet (`VLOOKUP` is a `left join`).

## Join audit

Before running, compare every join with the legacy code and show a table:

| Source | Legacy | dbt | Match |
|---|---|---|---|
| Order items | driving table | `from` | ok |
| Orders | `INNER JOIN` | `inner join` | ok |
| Customers | lookup (`SELECT SINGLE`) | `left join` | ok |

A wrong join type is the most common cause of a row count difference. A
lookup that does not use the full key returns one row in the legacy code but
fans out in a SQL join: deduplicate it and ask which row wins.

## Reconciliation

1. Sample keys on both sides first. Formats often differ (leading zeros,
   case, padding); normalize before comparing.
2. Compare distinct keys (in both, dbt only, legacy only), then totals of a
   key measure:

```sql
with
    dbt_keys as (
        select distinct ltrim(order_id, '0') as order_id
        from {{ ref('fct_order_items') }}
    )

    , legacy_keys as (
        select distinct ltrim(order_number, '0') as order_id
        from {{ source('legacy', 'order_items_report') }}
    )

select
    count_if(dbt_keys.order_id is not null and legacy_keys.order_id is not null) as in_both_count
    , count_if(legacy_keys.order_id is null) as dbt_only_count
    , count_if(dbt_keys.order_id is null) as legacy_only_count
from dbt_keys
full outer join legacy_keys
    on dbt_keys.order_id = legacy_keys.order_id
```

3. Explain differences before calling them bugs: the legacy output may cover
   only its last run's date range, or miss a recent load.
4. **Fewer rows in dbt:** inner join where the legacy had a lookup, dedup key
   too narrow, scope too strict. **More rows:** left join where the legacy had
   an inner join, missing scope filter, fan-out from a finer table.

## Done

- [ ] Every hidden call is explained or flagged.
- [ ] Runtime filters dropped; business scope confirmed and commented.
- [ ] Join audit shown, all rows match.
- [ ] Spec with the legacy field mapping; SQL and YML follow the project.
- [ ] Reconciliation run and differences explained.
- [ ] Improvements beyond the legacy output proposed separately.
