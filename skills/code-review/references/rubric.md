# Review rubric

What sets a severity beyond the table in `SKILL.md`, what to ignore, and the
dbt findings this team sees most. For everything else, review against the kit
skill for the file type (`sql-style`, `dbt-modeling`, `python-style`,
`airflow-dag`, `data-quality`). Only verified findings go in the report.

## Escalation and downgrade

Always Sev 5: exposed secrets (even in comments or old commits), guaranteed
data loss in production, injection, authentication or authorization bypass, a
consumed financial or executive metric wrong with near certainty.

Always at least Sev 4: personal data in logs, breaking change in a consumed
contract, incremental filter on a business date, retries on a non-idempotent
task, a dependency with a known high-severity vulnerability.

Add +1 (max 5) when the change:

- is hard to reverse (migrations, deletes, schema changes on large tables);
- touches financial, regulatory or executive metrics;
- runs only in production (no dev path to catch it).

Subtract 1 when, and only when you can verify it in the code:

- the path is test-only (`tests/`, fixtures, mocks);
- the impact is limited to a dev environment;
- the code is behind a feature flag that is off by default;
- an existing safeguard already handles the case (retry with idempotency, a
  downstream test that would fail).

`TODO` or `FIXME` without a ticket: Sev 2.

## Noise: do not report

- Formatting, whitespace, import order, quote style: linters and CI. Report
  style only when lint does not run.
- Lockfiles, unless a dependency was downgraded, removed for security, or has
  a known vulnerability.
- Generated files (`target/`, `dbt_packages/`, `logs/`, `__pycache__/`). If
  they are committed, one Sev 2 finding for the `.gitignore`.
- Notebook metadata, unless outputs show personal data, secrets or internal
  paths (Sev 4 or 5).

## dbt

| Finding | Sev |
|---|---|
| Hardcoded database or schema instead of `ref()` or `source()` | 4 |
| Fan-out in a mart with aggregated or financial metrics | 4 to 5 |
| Incremental filter on a business date, or `> max()` without lookback | 4 |
| Incremental model on updatable data without `unique_key` | 4 |
| Incremental model without the approved justification of the data's nature | 4 |
| Column removed, renamed or retyped in a mart without updating consumers | 4 |
| Grain key without `unique` and `not_null` | 3 |
| Business logic (joins, aggregations, business filters) in staging | 3 |
| Intermediate or mart without an enforced contract | 3 |
| `.sql` changed without its YML (or the other way around) | 3 |
| New model or column without an English description | 3 |
| `relationships` to a model that does not exist, or foreign id left untested in a mart | 3 |
| Column names with type prefixes or abbreviations | 2 |
| Columns out of the standard order | 1 |

For every join, ask whether either side can have more than one row per key
(fan-out). Always check what is downstream: `dbt ls --select <model>+`. A
harmless change in staging can break three marts.
