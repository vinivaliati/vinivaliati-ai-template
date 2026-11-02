# Testing dbt models

A test exists to protect an assumption the model depends on: the grain, a
join, a set of codes, a business rule. Test those assumptions well and skip
the rest. Fifty `not_null` tests that nobody reads are noise; one missing
`unique` on the grain is a wrong dashboard.

Freshness, volume, reconciliation and anomaly detection belong to the
`data-quality` skill.

## What to test, by layer

| Layer | Required | Add when it applies |
|---|---|---|
| sources | key `unique` and `not_null` when the source promises it | freshness (see `data-quality`) |
| staging | key `unique` and `not_null`; `accepted_values` on codes | `not_null` on columns the business cannot live without |
| intermediate | grain key `unique` and `not_null` | unit test for non-trivial logic |
| marts | grain key; `relationships` on every foreign id; `accepted_values` on codes and classifiers; `not_null` on booleans | ranges on measures; unit tests on business rules |

Test a column where it is created or changed, not on every pass-through.

## Syntax

`data_tests:` (dbt 1.8+) with arguments under `arguments:` (dbt 1.10+, where
top-level arguments are deprecated). On older projects, drop the `arguments:`
level. A warning always carries its reason and owner:

```yaml
      - name: carrier_id
        data_tests:
          - not_null
          - relationships:
              arguments:
                to: ref('dim_carrier')
                field: carrier_id
              # 14 legacy orders reference carriers deleted in the ERP; owner: logistics data team
              config:
                severity: warn
```

## Rules

- **Composite grain:** test it with `dbt_utils.unique_combination_of_columns`.
  With a surrogate key, test the key **and** the combination: the hash can be
  unique while the combination is not the grain you think it is.
- **Relationships only to a model that exists.** Never create an orphan
  foreign key to make a test pass. Known orphans from profiling: add an
  "unknown" member to the dimension, or `severity: warn` with reason and owner.
- **Accepted values come from profiling,** meanings from the user. A new code
  failing the build is the desired behavior.
- **Ranges only for rules that are physically or contractually true** (a rate
  between 0 and 1, a non-negative stock). "Normal" values that change with the
  business are anomaly detection, in `data-quality`.
- **Unit tests** (dbt 1.8+) for any calculation a reviewer could get wrong by
  reading it: OTIF, lead times, status derivations. One input row per edge
  case found in profiling.
- **Singular tests** for rules that do not fit a generic test: a query in
  `tests/assert_<what_must_be_true>.sql` that returns the failing rows.
- **Severity:** `error` when consumers get a wrong answer if it fails; `warn`
  only for a known, documented issue with an owner. A warning nobody owns
  becomes permanent noise.

## Do not

- Add `not_null` to every column. Test only columns where null is a bug.
- Test what the contract already guarantees (column names and data types).
- Loosen a failing test to make the build pass. Find out why it fails, then
  fix the data, the model or the assumption, and say which one.
