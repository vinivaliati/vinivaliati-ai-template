# Incremental models

Default: `table`, rebuilt in full on every run. It is always correct and
needs no thought about late data. Make a model incremental only when a full
rebuild is measurably too slow or too expensive, and only after the nature of
the data is understood and written down.

The trap this file exists to prevent: an incremental filter that works on the
first day and then silently drops rows. A filter on `extracted_at` or on a
business date looks right in review and in the demo. It fails the first time
a correction, a backdated entry or a late file arrives, and nothing errors.

## The justification (required)

Fill this in the model spec (`incremental` section of `model-spec.yml`) and
get approval before writing incremental code. Use the profiling results,
especially [late and backdated data](profiling.md#7-late-and-backdated-data).

```yaml
incremental:
  why_not_full_rebuild: "fct_deliveries has 480M rows; full rebuild takes 52 min and costs ~USD 9 per run"
  arrival_pattern: updates_in_place     # append_only | updates_in_place | snapshots
  hard_deletes: false                   # do rows disappear from the source?
  late_data: "99.9% of rows load within 30 days of delivered_date; max seen 41 days"
  change_column: _loaded_at             # column that reliably moves on every insert and update
  change_column_evidence: "Full extraction daily; corrections re-extracted with a new _loaded_at (checked on 20 known corrections)"
  unique_key: delivery_id
  strategy: merge
  lookback_days: 45
  full_refresh_plan: "Monthly full refresh on the first Sunday; reconciliation check weekly"
```

If any field cannot be answered with evidence, the model stays a full
rebuild. "Probably" is not evidence.

## Understand how the data arrives

| Pattern | Example | What can go wrong |
|---|---|---|
| Append only, immutable | GPS pings, scan events, logs | Late events (device offline for days), reloaded files creating duplicates |
| Updates in place | Orders changing status, deliveries corrected | Old rows changed after the window; a change column that does not move on every change |
| Backdated entries | Invoice created today with last month's date, manual adjustments | Any filter on the business date drops them |
| Hard deletes | Cancelled orders removed from the source | Incremental never sees a deleted row; it stays in the model forever |
| Snapshots | Daily stock position per warehouse | Reprocessed days must replace, not add |

## Choosing the change column

- **Filter on when the row arrived or changed** (load or update timestamp),
  never on the business date. `order_date >= max(order_date)` drops every
  backdated order.
- A load timestamp like `_extracted_at` or `_loaded_at` only works when the
  extraction brings every new **and changed** row with a new timestamp. Check
  how the extraction works:
  - full extraction every run, or CDC: changes arrive, the filter works;
  - extraction by a business date window (for example "orders from the last
    7 days by `order_date`"): changes to older rows never arrive. No dbt
    filter fixes that; it is an extraction problem. Flag it and keep the
    model as a full rebuild until the extraction changes.
- A source `updated_at` only works if the source system really updates it on
  every change. Verify with known corrections before trusting it.

## Lookback window

Never filter with a strict `> max(...)`. Reprocess a window that covers the
late-data tail from profiling, plus a margin:

```sql
{{
    config(
        materialized='incremental'
        , unique_key='delivery_id'
        , incremental_strategy='merge'
        , on_schema_change='fail'
    )
}}

with
    deliveries as (
        select *
        from {{ ref('stg_tms__deliveries') }}
        {% if is_incremental() %}
            -- lookback covers late data: 99.9% of rows load within 30 days, max seen 41 (profiling 2026-10-31)
            where _loaded_at >= (
                -- RF02 silenced: sqlfluff wrongly sees the outer table inside this subquery
                select dateadd('day', -{{ var('deliveries_lookback_days', 45) }}, max(_loaded_at))  -- noqa: RF02
                from {{ this }}
            )
        {% endif %}
    )
```

- The window is a `var` so it can be widened for a one-off backfill without a
  code change.
- The model must keep the change column (`_loaded_at`) so `{{ this }}` can be
  queried.
- `on_schema_change='fail'`: with an enforced contract, a schema change should
  stop the run, not quietly add or drop columns.

## Strategies

| Strategy | Use for | Warehouses |
|---|---|---|
| `merge` | updates in place, with a `unique_key` | Snowflake, BigQuery, Databricks, Postgres 15+ |
| `delete+insert` | same as merge where merge is slow or missing | Snowflake, Postgres, Redshift |
| `insert_overwrite` | snapshots and daily aggregates: replace whole partitions | BigQuery, Databricks |
| `append` | only append-only data that can never be reloaded twice | all |
| `microbatch` (dbt 1.9+) | large event tables processed by time batches, with a `lookback` | check adapter support |

`append` without a `unique_key` duplicates rows the first time a file is
reloaded. Prefer `merge` even for append-only data unless volume forbids it.

## Deletes

Incremental models never notice a row that disappeared from the source.
Pick one, and write it in the spec:

- the source sends a delete flag (CDC): carry it through staging and remove
  or mark the row in the incremental model;
- the source soft-deletes (`is_deleted`, `cancelled_at`): treat it as an
  update in place;
- neither: schedule a periodic full refresh and accept that deleted rows live
  until then. Say this to the consumers.

## Keeping it honest

- Schedule periodic full refreshes when the table allows it. If a full
  refresh is impossible (`full_refresh: false` on huge tables), the
  reconciliation check becomes mandatory.
- Reconcile: compare the incremental model with the source (row counts and
  key sums by month). This check lives in the `data-quality` skill.
- Revisit the lookback when profiling shows a longer tail.

## Do not

- Make staging incremental. Staging is a view; incremental logic belongs to
  the model where volume hurts.
- Make a model incremental "to be faster" without run time or cost numbers.
- Filter on a business date, or on `> max(...)` without a lookback.
- Use `append` on data that can be updated or reloaded.
- Approve an incremental model whose justification says "probably".
