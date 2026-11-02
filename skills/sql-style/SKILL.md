---
name: sql-style
description: >
  SQL formatting and writing conventions for any warehouse (Snowflake, BigQuery,
  Postgres, Databricks, Redshift): leading commas, lowercase keywords, one
  column per line, named CTEs ending in a `final` CTE, explicit aliases and
  `cast()`. Use when writing, reformatting or reviewing any .sql file or SQL
  snippet, dbt model SQL, ad hoc analysis queries, or when the user says
  "format this query", "clean up this SQL", "lint", "sqlfluff", "padroniza essa
  query" or "deixa no meu padrão". Also use when setting up sqlfluff in a
  project. Do not use for dbt project structure, layers, YML or tests (use
  dbt-modeling) or for migrating legacy logic (use legacy-to-dbt).
---

# SQL style

One readable, diff-friendly style for every query, enforced by sqlfluff where
possible. The point is that any query can be read top to bottom like a recipe,
and a code review diff shows only the lines that changed.

## Rules

### Layout

1. **Lowercase everything**: keywords, functions, types, identifiers.
   Why: no shift key debates, and uppercase adds noise without meaning.
2. **Leading commas, one column per line.** Applies to `select`, `group by`,
   `partition by`, function arguments that list columns and CTE separators.
   Why: adding or removing a column changes exactly one line, and a missing
   comma is visible at the start of the line.
3. **Indent 4 spaces.** No tabs. Max line length 120.
4. **Logical operators lead the line** (`and`, `or`), same reason as commas.
5. **Each clause starts its own line**: `select`, `from`, `join`, `where`,
   `group by`, `having`, `qualify`, `order by`.

### Structure

6. **Named CTEs, never nested subqueries.** Each CTE does one thing and its
   name says what (`orders`, `late_deliveries`, `orders_with_otif`), not
   `cte1` or `tmp`.
7. **Import CTEs first.** One CTE per source, `select *` plus filters only.
   In dbt, `ref()` and `source()` appear only here.
8. **End with a `final` CTE and `select * from final`.** Why: anyone can
   debug a model by swapping `final` for any CTE name in the last line.
9. **`select *` only in import CTEs and in `select * from final`.** Every
   other CTE lists its columns explicitly, so the column contract is visible
   in the code.
10. **Rename and cast in the CTE where the column enters**, not in the last
    select. The `final` CTE shows the output columns in their final names.

### Expressions

11. **Always alias with `as`**, for columns and tables. Never use a reserved
    word as an alias (`date`, `order`, `user`, `value`).
12. **`cast(x as type)`, never `x::type`.** Why: portable across dialects
    and easier to read.
13. **Qualify columns whenever more than one relation is in scope**, using
    the full CTE name (`orders.order_id`), not one-letter aliases.
    [SUGGESTION] Short aliases are allowed only when a CTE name is longer
    than 25 characters, with at least 3 letters (`dlv`, not `d`).
14. **Explicit join types**: `inner join`, `left join`. Never a bare `join`
    or comma joins. Put the left relation first in the `on` condition.
15. **[SUGGESTION] `group by` lists column names**, never positions
    (`group by 1, 2`). Why: positions break silently when a column is added.
16. **`union all` by default.** Use `union` only when deduplication is
    intended, and say so in a comment.
17. **Booleans read as booleans**: `where is_late`, not `where is_late = true`.
    Build flags with `coalesce(<condition>, false) as is_<thing>`.
18. **Deduplicate with a window function** (`qualify row_number() ... = 1`
    where the dialect supports it), never with `distinct` to hide a fanout.
19. **Comments explain why, in English**, with `--`. Do not comment what the
    code already says.

## Example

Fictional distribution company: compute OTIF (on time, in full) per order.

Good:

```sql
with
    orders as (
        select *
        from {{ ref('stg_erp__orders') }}
        where order_status_code != 'cancelled'
    )

    , deliveries as (
        select *
        from {{ ref('stg_tms__deliveries') }}
    )

    , latest_delivery as (
        select
            order_id
            , delivered_at
            , delivered_quantity
        from deliveries
        -- a redelivery creates a new row; the last attempt is the one the customer saw
        qualify row_number() over (
            partition by order_id
            order by delivered_at desc
        ) = 1
    )

    , orders_with_otif as (
        select
            orders.order_id
            , orders.customer_id
            , orders.ordered_quantity
            , latest_delivery.delivered_quantity
            , orders.promised_date
            , latest_delivery.delivered_at
            , coalesce(
                cast(latest_delivery.delivered_at as date) <= orders.promised_date
                , false
            ) as is_on_time
            , coalesce(
                latest_delivery.delivered_quantity >= orders.ordered_quantity
                , false
            ) as is_in_full
        from orders
        left join latest_delivery
            on orders.order_id = latest_delivery.order_id
    )

    , final as (
        select
            order_id
            , customer_id
            , ordered_quantity
            , delivered_quantity
            , is_on_time
            , is_in_full
            , is_on_time and is_in_full as is_otif
            , promised_date
            , delivered_at
        from orders_with_otif
    )

select *
from final
```

Bad (and why):

```sql
SELECT o.ORDER_ID, o.CUSTOMER_ID,                     -- uppercase, trailing commas
  CASE WHEN d.DELIVERED_AT::DATE <= o.PROMISED_DATE   -- :: cast
       THEN TRUE ELSE FALSE END on_time,              -- no "as", verbose boolean
  o.ORDERED_QUANTITY = d.DELIVERED_QUANTITY in_full   -- null when not delivered
FROM {{ ref('stg_erp__orders') }} o                   -- ref outside an import CTE, 1-letter alias
JOIN (SELECT DISTINCT * FROM {{ ref('stg_tms__deliveries') }}) d  -- subquery, bare join, distinct hides redeliveries
  ON d.ORDER_ID = o.ORDER_ID
WHERE o.ORDER_STATUS_CODE <> 'cancelled'
GROUP BY 1, 2, 3, 4                                   -- positional group by
```

## Workflow

1. **Detect the dialect** from the project (`profiles.yml`, `dbt_project.yml`,
   existing models, `.sqlfluff`). If it is unclear, ask.
2. **Read existing models** before writing. If the project already follows a
   different documented style, ask which one wins; do not mix styles in one
   file.
3. **Write or rewrite** following the rules above. For dialect-specific
   functions (dates, dedup, string handling), read
   [references/dialects.md](references/dialects.md).
4. **Lint** when sqlfluff is available:
   `sqlfluff lint <path>` then `sqlfluff fix <path>` for layout only. Review
   what `fix` changed; it can reorder things in ways that hurt readability.
5. **Report** what changed in one short list. When rewriting someone else's
   query, change style only; flag logic problems separately instead of
   silently fixing them.

## Setting up sqlfluff

Copy [assets/.sqlfluff](assets/.sqlfluff) and the `assets/.sqlfluff_libs/` folder
(lint-only stand-ins for `dbt_utils` macros) to the project root and set
`dialect` (and `templater`, `dbt` or `jinja`). It encodes rules 1 to 5, 6
(no subqueries), 11 to 15. The rest of the structure rules (import CTEs,
`final`, where renames happen) are not lintable, so they stay a review
responsibility.

## When something is not covered

Ask. If the answer becomes a recurring rule, propose adding it here and mark
it [SUGGESTION] until approved.
