# Testing dbt models

A test exists to protect an assumption the model depends on: the grain, a
join, a set of codes, a business rule. Test those assumptions well and skip
the rest. Fifty `not_null` tests that nobody reads are noise; one missing
`unique` on the grain is a wrong dashboard.

This file covers tests that live next to the model. Freshness, volume,
reconciliation with the source system and anomaly detection belong to the
`data-quality` skill.

## What to test, by layer

| Layer | Required | Add when it applies |
|---|---|---|
| sources | key `unique` and `not_null` when the source promises it | freshness (see `data-quality`) |
| staging | key `unique` and `not_null`; `accepted_values` on codes | `not_null` on columns the business cannot live without |
| intermediate | grain key `unique` and `not_null` | unit test for non-trivial logic |
| marts | grain key; `relationships` on every foreign id; `accepted_values` on codes and classifiers; `not_null` on booleans | ranges on measures; unit tests on business rules |

Test a column where it is created or changed. Do not repeat `accepted_values`
on a pass-through column in every layer; test it in staging and again in the
mart that consumers read.

Test syntax follows the project's dbt version. Examples below use
`data_tests:` (dbt 1.8+) and put test arguments under `arguments:`
(dbt 1.10+, where top-level arguments are deprecated). On older projects,
drop the `arguments:` level and keep the arguments at the top.

## Grain

Single key:

```yaml
      - name: order_id
        description: Order identifier from the ERP. One row per order.
        data_tests:
          - unique
          - not_null
```

Composite grain, at model level (needs `dbt_utils`):

```yaml
    data_tests:
      - dbt_utils.unique_combination_of_columns:
          arguments:
            combination_of_columns:
              - order_id
              - delivery_id
```

If the grain has a surrogate key, test the surrogate key **and** the
combination. The hash can be unique while the combination it hides is not
the grain you think it is.

## Relationships

```yaml
      - name: customer_id
        description: Customer who placed the order. Joins to dim_customer.
        data_tests:
          - not_null
          - relationships:
              arguments:
                to: ref('dim_customer')
                field: customer_id
```

- Only test a relationship to a model that exists. If the target does not
  exist yet, leave the id without the test and list it as an open question;
  never create an orphan foreign key to make a test pass.
- Known orphans found in profiling: either add an "unknown" member to the
  dimension and map orphans to it, or set `severity: warn` with a comment
  explaining why and who tracks it.

## Accepted values

```yaml
      - name: order_status_code
        description: Raw order status code from the ERP.
        data_tests:
          - accepted_values:
              arguments:
                values: ['C', 'D', 'P', 'R', 'X']
```

A new code failing the build is the desired behavior: someone must decide what
it means before it reaches a dashboard. Get the list from profiling and the
meanings from the user, never from guesses.

## Ranges and expressions

With `dbt_utils`:

```yaml
      - name: otif_rate
        data_tests:
          - dbt_utils.accepted_range:
              arguments:
                min_value: 0
                max_value: 1
```

```yaml
    data_tests:
      - dbt_utils.expression_is_true:
          arguments:
            expression: "delivered_quantity <= ordered_quantity * 1.1"
          config:
            severity: warn
```

Use ranges for rules that are physically or contractually true (a rate between
0 and 1, a non-negative stock). Do not encode "normal" values that change with
the business; that is anomaly detection, in `data-quality`.

## Unit tests

Use a dbt unit test (dbt 1.8+) for any calculation that a reviewer could get
wrong by reading it: OTIF, lead times, status derivations, date logic. They run
on fixed input rows, so they test the logic, not the data.

```yaml
unit_tests:
  - name: otif_requires_on_time_and_in_full
    model: fct_order_otif
    given:
      - input: ref('int_orders_with_deliveries')
        rows:
          - {order_id: 'A', ordered_quantity: 10, delivered_quantity: 10, is_on_time: true}
          - {order_id: 'B', ordered_quantity: 10, delivered_quantity: 8, is_on_time: true}
          - {order_id: 'C', ordered_quantity: 10, delivered_quantity: 10, is_on_time: false}
    expect:
      rows:
        - {order_id: 'A', is_otif: true}
        - {order_id: 'B', is_otif: false}
        - {order_id: 'C', is_otif: false}
```

Cover the edge cases that profiling found (not delivered, partial delivery,
late delivery, negative quantities), one row each.

## Severity

- `error` (default): the model is wrong for consumers if the test fails.
  Grain, relationships without known orphans, accepted values in marts.
- `warn`: a known, documented issue that should not stop the pipeline.
  Every `warn` has a comment with the reason and who follows up. A warning
  nobody owns becomes permanent noise; remove it or fix the data.

```yaml
          - relationships:
              arguments:
                to: ref('dim_carrier')
                field: carrier_id
              # 14 legacy orders reference carriers deleted in the ERP; owner: logistics data team
              config:
                severity: warn
```

## Singular tests

For a rule that does not fit a generic test, write a query in `tests/` that
returns the failing rows, named `assert_<what_must_be_true>.sql`:

```sql
-- tests/assert_delivered_orders_have_delivered_at.sql
select
    order_id
    , delivered_quantity
    , delivered_at
from {{ ref('fct_order_otif') }}
where
    delivered_quantity > 0
    and delivered_at is null
```

## Do not

- Add `not_null` to every column. Test only columns where null is a bug.
- Test what the contract already guarantees (column names and data types).
- Loosen a failing test to make the build pass. Find out why it fails, then
  fix the data, the model or the assumption, and say which one.
