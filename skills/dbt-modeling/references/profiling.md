# Profiling a source before modeling

Look at the data before deciding grain, keys, types and tests. Ten minutes of
queries prevent the classic failures: a "unique" key with duplicates, an
integer column that has cents, a date column with year 2099, a code with a
value nobody documented.

## Ground rules

- Query the raw source (the table behind `source()`), not a model built on it.
- Read only. Never create, alter or delete anything while profiling.
- On large tables, filter to a recent period or sample, and select only the
  columns you need. Ask before running a query that scans a very large table
  on a warehouse that charges per byte or per second.
  Sampling: Snowflake `sample (1)`, BigQuery `tablesample system (1 percent)`,
  Postgres `tablesample system (1)`, Databricks `tablesample (1 percent)`.
- Do not paste personal data (names, documents, emails, phones) into the
  report. Summarize: counts, ranges, patterns.
- If you cannot query the warehouse, give the user the queries below, filled
  in, and ask for the output.

Ad hoc profiling queries are the one place where `select *` with `limit` is
fine; they are not models.

## 1. Look at a sample

```sql
select *
from raw.erp.orders
limit 20
```

Check: what one row represents, cryptic column names, columns that are always
empty, values stored as text that should be numbers or dates.

## 2. Candidate key and grain

```sql
select
    count(*) as row_count
    , count(order_number) as key_not_null_count
    , count(distinct order_number) as key_distinct_count
from raw.erp.orders
```

`row_count = key_distinct_count` and no nulls: the key is unique. Otherwise,
look at the duplicates before deciding anything:

```sql
select
    order_number
    , count(*) as row_count
from raw.erp.orders
group by order_number
having count(*) > 1
order by row_count desc
limit 20
```

Duplicates usually mean one of: the grain is finer than assumed (one row per
item, not per order), the source keeps history (one row per change), or the
extraction loaded the same data twice. Each needs a different fix; ask which
one it is when the data does not make it obvious.

## 3. Nulls and empty values

```sql
select
    count(*) as row_count
    , count(*) - count(customer_number) as customer_null_count
    , count_if(trim(customer_number) = '') as customer_empty_count
    , count(*) - count(promised_date) as promised_date_null_count
from raw.erp.orders
```

`count_if` is Snowflake and Databricks; elsewhere use
`sum(case when <condition> then 1 else 0 end)`.

## 4. Numeric precision

```sql
select
    min(order_quantity) as quantity_min
    , max(order_quantity) as quantity_max
    , max(abs(order_quantity - trunc(order_quantity))) as quantity_max_decimal_part
    , count_if(order_quantity < 0) as quantity_negative_count
from raw.erp.orders
```

`max_decimal_part = 0` over the full history: integer. Anything else: exact
decimal with enough scale. Negative values in a quantity usually mean returns
or cancellations; ask how they should be treated.

## 5. Dates and freshness

```sql
select
    min(order_date) as order_date_min
    , max(order_date) as order_date_max
    , count_if(order_date > current_date) as order_date_future_count
    , max(_loaded_at) as last_loaded_at
from raw.erp.orders
```

Check: placeholder dates (`1900-01-01`, `9999-12-31`), future dates that
should not exist, and whether the last load is as recent as expected.

## 6. Codes and categories

```sql
select
    order_status
    , count(*) as row_count
from raw.erp.orders
group by order_status
order by row_count desc
```

Few distinct values: candidate for `accepted_values` and for a readable
classifier column. Ask what each code means; never invent the mapping.

## 7. Late and backdated data

Required before proposing an incremental model. It shows how far in the past
new rows land, which is the nature of the data that a lookback window must
cover.

```sql
select
    datediff('day', order_date, cast(_loaded_at as date)) as days_late
    , count(*) as row_count
from raw.erp.orders
where _loaded_at >= dateadd('day', -90, current_date)
group by days_late
order by days_late
```

Read the tail, not the average. If 1% of rows arrive 40 days late, a 7 day
lookback loses them. Also check whether existing rows are updated in place
(same key, newer `_loaded_at`, different values) and whether rows are ever
deleted at the source. The date functions above are Snowflake; see
[`sql-style` dialects](../../sql-style/references/dialects.md) for others.

## 8. Relationships

```sql
select count(*) as orphan_count
from raw.erp.orders as orders
left join raw.erp.customers as customers
    on orders.customer_number = customers.customer_number
where customers.customer_number is null
```

Orphans decide whether a `relationships` test is an error, a warning, or
needs an "unknown" member in the dimension.

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
