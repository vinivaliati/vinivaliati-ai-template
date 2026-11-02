# Dialect notes

The style rules in `SKILL.md` are the same in every warehouse. For function
names, follow the project's existing models first, then the official docs; do
not guess. These are the choices and traps that matter across warehouses.

## Types

- Money and quantities: exact decimal (`number(38, 2)`, `numeric`,
  `decimal(38, 2)`), never float.
- Integer only when profiling shows no decimal part over the full history.
- Text without a length (`varchar`, not `varchar(50)`) unless the target
  requires one; lengths truncate or fail when the source grows.

## Traps

- **Date difference argument order** varies by warehouse (Snowflake
  `datediff('day', start, end)`, BigQuery `date_diff(end, start, day)`); a
  swapped order returns a negative number without an error.
- **Integer division truncates** in Postgres and Redshift (`7 / 2 = 3`). Cast
  one side to an exact decimal and guard against zero:
  `cast(on_time_orders as numeric(38, 4)) / nullif(total_orders, 0)`.
- **No `qualify` in Postgres:** rank with `row_number()` in one CTE, filter
  `where rank = 1` in the next. BigQuery may need `where true` before
  `qualify`.
- **Deduplication needs a tiebreaker** in `order by` when the ordering column
  can repeat, or the row kept changes between runs.
- **Identifier case:** Snowflake folds unquoted names to uppercase, Postgres
  and Redshift to lowercase. Write everything lowercase and unquoted; quote a
  source column only when it forces it (spaces, mixed case, reserved word),
  once, in the staging CTE that renames it.

## Surrogate keys

Use `dbt_utils.generate_surrogate_key` in every dialect, one column per line,
so the hashing is the same across warehouses:

```sql
            , {{ dbt_utils.generate_surrogate_key([
                'order_id'
                , 'delivery_id'
            ]) }} as order_delivery_sk
```
