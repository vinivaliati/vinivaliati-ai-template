---
name: data-quality
description: >
  Data quality checks beyond a model's own tests: source freshness, volume
  changes, reconciliation between a model and its source, distribution
  anomalies, and what to do when a check fails. Use when the user asks
  "how do we know this data is right", "add data quality", "monitor this
  table", "reconcile with the source", "the numbers don't match", "valida a
  qualidade", "confere com a origem", "por que esse número mudou", or after
  building an incremental model without periodic full refresh. Do not use for
  a model's basic tests (grain, relationships, accepted values: use
  dbt-modeling) or for code review.
---

# Data quality

A model can pass every test and still be wrong: yesterday's load never
arrived, half the rows went missing, an incremental drifted from the source.
These checks catch what model tests cannot. Each one costs attention when it
fires, so add a check only when someone will act on it.

## Every check has three things

1. **A threshold** based on the data's history, not a guess.
2. **A severity**: `error` stops the pipeline, `warn` notifies.
3. **An owner and an action**: who looks at it and what they do first.

A check without an owner becomes noise, and noise trains people to ignore
alerts. Write the owner in the test's `meta` or in a comment.

## Which checks, when

| Check | Catches | Add when |
|---|---|---|
| Freshness | Load did not arrive or is late | [SUGGESTION] Suggest for sources behind consumer-facing marts; enable only after the user confirms load frequency and tolerance |
| Volume | Rows missing or duplicated in a load | The source loads in batches that can arrive partial |
| Reconciliation | Model drifted from the source | Incremental models without regular full refresh (mandatory); financial or executive marts |
| Distribution | Values shift (nulls spike, a category disappears) | Marts feeding decisions or ML |
| Business rules | Logic broke (OTIF above 100%, negative stock) | Rules the business states as always true |

Basic model tests (grain, relationships, accepted values) come first and
live in the `dbt-modeling` skill.

## Freshness (suggest, do not impose)

Propose it, then ask: how often does the source load, and how late is too late
for the people using the data? Only then enable it in the source YAML:

```yaml
    loaded_at_field: _loaded_at
    freshness:
      warn_after: {count: 26, period: hour}
      error_after: {count: 50, period: hour}
```

Run with `dbt source freshness`. Thresholds come from the load schedule plus
a margin, never from a default.

## Volume

Compare the latest load with recent history. Singular test, fails when the
last load is below half or above double the 7-day average:

```sql
-- tests/assert_deliveries_daily_volume_is_normal.sql
with
    daily as (
        select
            cast(_loaded_at as date) as load_date
            , count(*) as row_count
        from {{ ref('stg_erp__deliveries') }}
        group by cast(_loaded_at as date)
    )

    , compared as (
        select
            load_date
            , row_count
            , avg(row_count) over (
                order by load_date
                rows between 7 preceding and 1 preceding
            ) as avg_previous_7_days
            , max(load_date) over () as latest_load_date
        from daily
    )

select
    load_date
    , row_count
    , avg_previous_7_days
from compared
where
    load_date = latest_load_date
    and (
        row_count < avg_previous_7_days * 0.5
        or row_count > avg_previous_7_days * 2
    )
```

Tune the factors with the history; weekends and month ends often need their
own baseline.

## Reconciliation

Compare the model with the source by period: row counts and the sum of a key
measure. Differences should be zero or explained.

```sql
-- analyses/reconcile_fct_deliveries.sql
with
    source_totals as (
        select
            date_trunc('month', cast(dlv_ts as date)) as delivery_month
            , count(*) as row_count
            , sum(dlv_qty) as delivered_quantity
        from {{ source('erp', 'deliveries') }}
        group by date_trunc('month', cast(dlv_ts as date))
    )

    , model_totals as (
        select
            date_trunc('month', cast(delivered_at as date)) as delivery_month
            , count(*) as row_count
            , sum(delivered_quantity) as delivered_quantity
        from {{ ref('fct_deliveries') }}
        group by date_trunc('month', cast(delivered_at as date))
    )

select
    coalesce(source_totals.delivery_month, model_totals.delivery_month) as delivery_month
    , source_totals.row_count as source_row_count
    , model_totals.row_count as model_row_count
    , source_totals.delivered_quantity - model_totals.delivered_quantity as quantity_difference
from source_totals
full outer join model_totals
    on source_totals.delivery_month = model_totals.delivery_month
where
    source_totals.row_count is distinct from model_totals.row_count
    or source_totals.delivered_quantity is distinct from model_totals.delivered_quantity
```

Keep it as an analysis for investigation; turn it into a test (in `tests/`)
when it must run on every build. Filters applied in the model (cancelled
rows, test customers) must be applied to the source side too, or every month
will "differ".

## Distribution and anomalies

Start with simple singular tests (share of nulls, count of distinct
categories). [SUGGESTION] Packages such as Elementary or dbt-expectations add
anomaly detection; propose one only when simple tests are not enough, and ask
before adding a dependency.

## When a check fails

1. **Do not loosen the check** to make it pass.
2. Look at the source first: did the load arrive, is it complete, did the
   source system change?
3. Tell the consumers when a consumer-facing mart is affected, with what is
   wrong, since when, and when it will be fixed.
4. Fix the cause (the load, the model or the assumption), rerun, confirm the
   check passes.
5. Record what happened and the fix in `docs/decisions.md` if it changed a
   rule or a threshold.

## Workflow

1. List the marts that matter and who consumes them.
2. For each, pick checks from the table above; start with the fewest that
   cover the real risks.
3. Profile history to set thresholds (see `dbt-modeling` profiling).
4. Write the checks, each with severity, owner and first action.
5. Run them in dev, show the output, and agree on where alerts go.
