# Profiling a source before modeling

Look at the data before deciding grain, keys, types and tests. Ten minutes of
queries prevent the classic failures: a "unique" key with duplicates, an
integer column that has cents, a date in 2099, a code nobody documented.

## Ground rules

- Query the raw source (the table behind `source()`), read only.
- On large tables, filter to a recent period or sample; ask before a query
  that scans a very large table on a warehouse that charges per use.
- Never paste personal data into the report: counts, ranges and patterns only.
- If you cannot query the warehouse, give the user the queries and ask for
  the output.

## What to check

| Check | Decides |
|---|---|
| A sample of rows: what one row represents | Grain, cryptic names to ask about |
| Candidate key: count vs distinct count, nulls; look at duplicates | Grain. Duplicates mean finer grain, history rows or a double load: ask which |
| Nulls and empty strings per important column | `not_null` tests, `nullif` in staging |
| Decimal part over the full history; negative values | Integer vs exact decimal; how returns or cancellations are treated |
| Date range, placeholder dates (`1900-01-01`, `9999-12-31`), future dates, last load | Cleaning rules, freshness |
| Distinct values of codes | `accepted_values`; ask what each code means, never invent it |
| Orphans against the parent table | `relationships` as error, warning or an "unknown" member |
| Late and backdated rows (below) | Whether incremental is safe, and the lookback |

## Late and backdated data

Required before proposing an incremental model. It shows how far in the past
new rows land:

```sql
select
    datediff('day', order_date, cast(_loaded_at as date)) as days_late
    , count(*) as row_count
from raw.erp.orders
where _loaded_at >= dateadd('day', -90, current_date)
group by days_late
order by days_late
```

Read the tail, not the average: if 1% of rows arrive 40 days late, a 7 day
lookback loses them. Also check whether rows are updated in place (same key,
newer `_loaded_at`, different values) and whether the source deletes rows.

## Report

Summarize before writing any model:

```text
Source: raw.erp.orders (2.4M rows, last load 2026-10-31 06:10 UTC)
Grain: one row per order_number; 0 nulls, 0 duplicates
Types: order_quantity has decimals (max 3 digits) -> number(38, 3)
Dates: order_date 2019-01-02 to 2026-10-31; 0 future; 12 rows at 1900-01-01 (ask)
Codes: order_status has 5 values: C, D, P, R, X (meaning of R and X: ask)
Late data: 97% loaded within 2 days; 0.8% up to 35 days late
Orphans: 14 orders with customer_number missing in customers
Open questions: 1900-01-01 dates, codes R and X, negative quantities (31 rows)
```
