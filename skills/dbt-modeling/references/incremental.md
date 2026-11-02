# Incremental models

Default: `table`, rebuilt in full on every run. It is always correct and
needs no thought about late data. Make a model incremental only when a full
rebuild is measurably too slow or too expensive, and only after the nature of
the data is understood and written down.

The trap this file exists to prevent: an incremental filter that works on the
first day and then silently drops rows. A filter on `extracted_at` or on a
business date looks right in review and in the demo. It fails the first time
a correction, a backdated entry or a late file arrives, and nothing errors.

## The justification

Fill the `incremental` section of the model spec with evidence from profiling
(especially late and backdated data) and get approval before writing
incremental code. If any field cannot be answered with evidence, the model
stays a full rebuild. "Probably" is not evidence.

## Choosing the change column

- **Filter on when the row arrived or changed** (load or update timestamp),
  never on the business date. `order_date >= max(order_date)` drops every
  backdated order.
- A load timestamp like `_loaded_at` only works when the extraction brings
  every new **and changed** row with a new timestamp:
  - full extraction every run, or CDC: changes arrive, the filter works;
  - extraction by a business date window ("orders from the last 7 days by
    `order_date`"): changes to older rows never arrive. No dbt filter fixes
    that; flag it and keep the model a full rebuild until the extraction
    changes.
- A source `updated_at` only works if the source really updates it on every
  change. Verify with known corrections before trusting it.

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

- The window is a `var`, so a one-off backfill can widen it without a code
  change.
- Keep the change column in the model, so `{{ this }}` can be queried.
- `on_schema_change='fail'`: with an enforced contract, a schema change stops
  the run instead of quietly adding or dropping columns.

Strategy: `merge` with a `unique_key` by default; `insert_overwrite` for
snapshots that replace whole partitions; never `append` on data that can be
updated or reloaded.

## Deletes

Incremental models never notice a row that disappeared from the source. Pick
one and write it in the spec:

- the source sends a delete flag (CDC): carry it through staging and remove
  the row in the incremental model;
- the source soft-deletes (`is_deleted`, `cancelled_at`): treat it as an
  update in place;
- neither: schedule a periodic full refresh and tell the consumers that
  deleted rows live until then.

## Keeping it honest

- Without a scheduled full refresh, reconciliation with the source is
  mandatory (see `data-quality`).
- Revisit the lookback when profiling shows a longer tail.
- Never make staging incremental; it is a view.
