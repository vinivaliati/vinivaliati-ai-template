# Dialect patterns

The style rules in `SKILL.md` are the same in every warehouse. Only function
names and a few behaviors change. Use this file to pick the right function for
the detected dialect. If a function is not listed, check the existing models
in the project first, then the official docs; do not guess.

## Quick reference

| Task | Snowflake | BigQuery | Postgres | Databricks | Redshift |
|---|---|---|---|---|---|
| Safe cast (null on failure) | `try_cast(x as number(38, 2))` | `safe_cast(x as numeric)` | none, validate with a regex first | `try_cast(x as decimal(38, 2))` | none, validate with a regex first |
| Text to date | `to_date(x, 'YYYYMMDD')` | `parse_date('%Y%m%d', x)` | `to_date(x, 'YYYYMMDD')` | `to_date(x, 'yyyyMMdd')` | `to_date(x, 'YYYYMMDD')` |
| Date to text | `to_varchar(d, 'YYYY-MM-DD')` | `format_date('%Y-%m-%d', d)` | `to_char(d, 'YYYY-MM-DD')` | `date_format(d, 'yyyy-MM-dd')` | `to_char(d, 'YYYY-MM-DD')` |
| Days between | `datediff('day', start_date, end_date)` | `date_diff(end_date, start_date, day)` | `end_date - start_date` | `datediff(end_date, start_date)` | `datediff(day, start_date, end_date)` |
| Truncate to month | `date_trunc('month', d)` | `date_trunc(d, month)` | `date_trunc('month', d)` | `date_trunc('month', d)` | `date_trunc('month', d)` |
| Add days | `dateadd('day', 7, d)` | `date_add(d, interval 7 day)` | `d + interval '7 day'` | `date_add(d, 7)` | `dateadd(day, 7, d)` |
| Current timestamp | `current_timestamp()` | `current_timestamp()` | `current_timestamp` | `current_timestamp()` | `getdate()` |
| `qualify` | yes | yes (see note) | no | yes | yes |
| Integer / integer | decimal result | float result | **truncates** | decimal result | **truncates** |

Watch the argument order of date differences: it is not consistent across
warehouses, and a swapped order returns a negative number without an error.

## Type names for `cast()`

| Logical type | Snowflake | BigQuery | Postgres | Databricks | Redshift |
|---|---|---|---|---|---|
| Text | `varchar` | `string` | `text` | `string` | `varchar` |
| Integer | `int` | `int64` | `bigint` | `bigint` | `bigint` |
| Exact decimal | `number(38, 2)` | `numeric` | `numeric(38, 2)` | `decimal(38, 2)` | `decimal(38, 2)` |
| Boolean | `boolean` | `bool` | `boolean` | `boolean` | `boolean` |
| Date | `date` | `date` | `date` | `date` | `date` |
| Timestamp, no zone | `timestamp_ntz` | `datetime` | `timestamp` | `timestamp_ntz` | `timestamp` |
| Timestamp, UTC instant | `timestamp_tz` | `timestamp` | `timestamptz` | `timestamp` | `timestamptz` |

Rules that hold everywhere:

- Money and quantities use an exact decimal, never float.
- Use an integer type only when the data has no decimal part. Check with a
  query (max of the fractional part) before choosing; do not infer it from a
  sample of ten rows.
- Do not set a length on text types (`varchar`, not `varchar(50)`) unless the
  target system requires it. Lengths cause silent truncation or load errors
  when the source grows.

## Deduplication

Where `qualify` exists:

```sql
    , latest_delivery as (
        select
            order_id
            , delivered_at
            , delivered_quantity
        from deliveries
        qualify row_number() over (
            partition by order_id
            order by delivered_at desc
        ) = 1
    )
```

Postgres (no `qualify`): rank in one CTE, filter in the next.

```sql
    , ranked_deliveries as (
        select
            order_id
            , delivered_at
            , delivered_quantity
            , row_number() over (
                partition by order_id
                order by delivered_at desc
            ) as delivery_rank
        from deliveries
    )

    , latest_delivery as (
        select
            order_id
            , delivered_at
            , delivered_quantity
        from ranked_deliveries
        where delivery_rank = 1
    )
```

BigQuery note: some versions reject `qualify` when the query has no `where`,
`group by` or `having`. If you hit that error, add `where true` before
`qualify`.

Always add a tiebreaker to `order by` when the ordering column can repeat
(for example `order by delivered_at desc, delivery_id desc`). Without it, the
row kept can change between runs.

## Identifiers and case

- **Snowflake** folds unquoted identifiers to uppercase; Postgres and Redshift
  fold to lowercase; BigQuery column names are case-insensitive but table
  names can be case-sensitive.
- Write everything lowercase and unquoted. Quote only when a source column
  forces it (spaces, mixed case created with quotes, reserved words), and do
  it once, in the staging import CTE, renaming to a clean snake_case name.

```sql
    , source as (
        select *
        from {{ source('erp', 'orders') }}
    )

    , renamed as (
        select
            cast("Order Number" as varchar) as order_id
            , cast("Customer" as varchar) as customer_id
        from source
    )
```

## Division

Integer division silently truncates in Postgres and Redshift (`7 / 2 = 3`).
Cast one side to an exact decimal, and guard against zero:

```sql
            , cast(on_time_orders as numeric(38, 4))
                / nullif(total_orders, 0) as on_time_rate
```

## Surrogate keys in dbt

Use `dbt_utils.generate_surrogate_key` in every dialect, with one column per
line, so the hashing is the same across warehouses:

```sql
            , {{ dbt_utils.generate_surrogate_key([
                'order_id'
                , 'delivery_id'
            ]) }} as order_delivery_sk
```
