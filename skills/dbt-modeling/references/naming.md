# Naming

Names are the documentation people read most. The rule behind every item
below: the same concept has the same name in every model, and a name says what
the column holds without opening the YML.

## Models

| Layer | Pattern | Examples |
|---|---|---|
| staging | `stg_<source>__<entities>` (plural entity, double underscore) | `stg_erp__orders`, `stg_tms__deliveries` |
| intermediate | `int_<entities>_<verb or description>` | `int_orders_with_deliveries`, `int_deliveries_deduplicated`, `int_inventory_daily_snapshot` |
| facts | `fct_<process or event>` (plural) | `fct_deliveries`, `fct_order_otif` |
| dimensions | `dim_<entity>` (singular) | `dim_customer`, `dim_warehouse` |

- `<source>` is the system, not the vendor or the client: `erp`, `tms`, `wms`.
- Never version a model in its name (`_v2`, `_new`, `_final`). Use git, or
  dbt model versions when consumers need a migration period.
- A YML file in intermediate or marts has the same name as its model.
- Staging YML files: `_<source>__sources.yml` and `_<source>__models.yml`.

## Columns

General rules:

- English, `snake_case`, lowercase.
- No type prefixes (`vl_`, `dt_`, `fl_`, `cd_`). The suffix carries the type.
- No reserved words: `date`, `order`, `user`, `value`, `type`, `status`
  alone. Qualify them: `order_date`, `user_id`, `stock_value`.
- No abbreviations except `id` and `sk`:

| Avoid | Use |
|---|---|
| `qty`, `amt`, `nr`, `num` | `quantity`, `amount`, `number` |
| `cust`, `whs`, `dlv` | `customer`, `warehouse`, `delivery` |
| `dt`, `ts`, `flg` | `_date`, `_at`, `is_` |

### Keys

- A model's own key is `<entity>_id`, never `id`. Rename `id` from the source
  in staging: `id as order_id`.
- A foreign key keeps the exact name of the key it points to:
  `customer_id` in `fct_deliveries` joins to `customer_id` in `dim_customer`.
- When the same entity appears twice, prefix the role:
  `origin_warehouse_id`, `destination_warehouse_id`.
- Surrogate keys (hash of one or more columns) end in `_sk` and are built with
  `dbt_utils.generate_surrogate_key`. Use one when the grain has a composite
  key or when natural keys can collide across sources.
- Business identifiers that are not keys of this model (invoice number shown
  to customers, tracking code) use `_number` or `_code`:
  `invoice_number`, `tracking_code`.

### Descriptive columns

| Kind | Pattern | Example |
|---|---|---|
| Code as delivered by the source | `<thing>_code` | `order_status_code` (`'C'`, `'D'`), `carrier_code` |
| Human-readable label | `<thing>_name` | `carrier_name`, `warehouse_name` |
| Long free text | `<thing>_description` | `product_description` |
| [SUGGESTION] Readable classifier | `<thing>_status`, `<thing>_type`, `<thing>_category` | `order_status` (`'delivered'`), `vehicle_type` |

When the source only has a code, keep the `_code` in staging and add the
readable classifier in intermediate or the mart, with `accepted_values` tests
on both.

### Booleans

- `is_<state>` or `has_<thing>`: `is_on_time`, `is_active`, `has_return`.
- Always the positive form: `is_active`, not `is_not_inactive`.
- Never nullable in intermediate and marts: build them with
  `coalesce(<condition>, false)`.

### Dates and timestamps

- `<event>_date` for dates, `<event>_at` for timestamps: `promised_date`,
  `delivered_at`.
- Name the event, not the format: `delivered_at`, not `delivery_timestamp`.

### Measures

| Kind | Pattern | Example |
|---|---|---|
| Quantity | `<thing>_quantity` | `ordered_quantity`, `delivered_quantity` |
| Money | `<thing>_amount`, with currency when more than one exists | `freight_amount`, `freight_amount_brl` |
| Count of rows or events | `<thing>_count` | `delivery_count` |
| [SUGGESTION] Ratio | `<thing>_rate`, stored as a fraction from 0 to 1 | `otif_rate` (0.93, not 93) |
| Duration, weight, distance | unit as suffix | `lead_time_days`, `gross_weight_kg`, `route_distance_km` |

Why the fraction: dashboards format 0.93 as 93% on their own, and a stored
93 gets multiplied twice sooner or later.

### Technical columns

- [SUGGESTION] Load metadata starts with an underscore so it is never confused
  with business data: `_extracted_at`, `_loaded_at`, `_source_file_name`.
- Keep them in staging and intermediate; expose them in marts only when a
  consumer needs freshness information.

## Column order

Same order in SQL and YML, so a reviewer can read both side by side:

1. ids: surrogate key, the model's own id, then foreign ids
2. strings: codes, names, classifiers, descriptions
3. numerics: quantities, amounts, counts, rates
4. booleans
5. dates
6. timestamps (technical columns last)

```sql
    , final as (
        select
            order_delivery_sk
            , order_id
            , customer_id
            , carrier_id
            , order_status_code
            , carrier_name
            , ordered_quantity
            , delivered_quantity
            , freight_amount
            , is_on_time
            , is_in_full
            , promised_date
            , delivered_at
            , _loaded_at
        from orders_with_deliveries
    )
```

## Renaming in staging

Staging is the only place where source names are translated. Keep the mapping
explicit, one column per line, so the source name stays searchable:

```sql
    , renamed as (
        select
            cast(ord_no as varchar) as order_id
            , cast(cust_no as varchar) as customer_id
            , cast(ord_stat as varchar) as order_status_code
            , cast(ord_qty as number(38, 2)) as ordered_quantity
            , cast(prom_dt as date) as promised_date
            , cast(load_ts as timestamp_ntz) as _loaded_at
        from source
    )
```

When a source name is cryptic and the meaning is not obvious from the data,
ask before naming it. A wrong name is worse than a cryptic one, because people
trust it.
