# Review rubric

Details behind the severity scale in `SKILL.md`: objective criteria,
escalation rules, what to ignore, and checklists per file type. Use the
checklists to look for problems, not as a list to report; only verified
findings go in the report.

## Severity criteria

### Sev 5: Critical (blocks merge)

- Secret, token, password or private key in code, config, comments, notebook
  output or commit history.
- Data loss: `delete` or `update` without `where`, `drop`, `truncate` or a
  `--full-refresh` on a table that cannot be rebuilt.
- Injection: SQL, shell or template built by concatenating user input.
- Personal data exposed to people or systems that should not see it.
- A metric consumers rely on (financial, executive, regulatory) becomes wrong
  with near certainty: fan-out in a revenue mart, a filter that drops a
  whole segment.

### Sev 4: High (blocks merge)

- Probable bug in core logic: wrong join type, wrong grain, null handling that
  changes a result, time zone mix-up in a cut-off.
- Breaking change for consumers without a migration: column renamed, removed
  or retyped in a mart, public function signature changed.
- Incremental model that can silently lose or duplicate rows (see dbt below).
- Personal data or secrets written to logs.
- Unhandled failure in a critical path (a DAG task that swallows errors, a
  retry that duplicates loads).
- Dependency with a known high-severity vulnerability.

### Sev 3: Medium (fix now or track with a ticket)

- New logic without tests; grain without `unique` and `not_null`.
- Performance or cost problem with real impact (full scan of a large table
  every run, repeated computation, N+1 queries).
- Maintainability debt likely to cause bugs: duplicated business logic,
  business rules in staging, a 200-line function doing five things.
- Missing documentation on new marts or public functions.

### Sev 2: Low (optional)

- Naming that breaks conventions, unclear variable names, small refactors.
- `TODO` or `FIXME` without a ticket.

### Sev 1: Note (optional)

- Preferences, alternatives, FYI.

## Escalation and downgrade

Always Sev 5: exposed secrets (even in comments or old commits), guaranteed
data loss in production, injection, authentication or authorization bypass.

Always at least Sev 4: personal data in logs, breaking change in a consumed
contract, incremental filter on a business date.

Add +1 (max 5) when the change:

- is hard to reverse (migrations, deletes, schema changes on large tables);
- touches financial, regulatory or executive metrics;
- runs only in production (no dev path to catch it).

Subtract 1 when, and only when you can verify it in the code:

- the path is test-only (`tests/`, fixtures, mocks);
- the impact is limited to a dev environment;
- the code is behind a feature flag that is off by default;
- an existing safeguard already handles the case (retry with idempotency,
  a downstream test that would fail).

## Noise: do not report

- Formatting, whitespace, import order, quote style: linters and CI.
- Lockfiles (`poetry.lock`, `package-lock.json`), unless a dependency was
  downgraded, removed for security, or has a known vulnerability.
- Generated files and folders: `target/`, `dbt_packages/`, `logs/`,
  `__pycache__/`, `dist/`, `manifest.json`. If they are committed, one Sev 2
  finding for the `.gitignore`.
- Notebook metadata: execution counts, kernel info, plot outputs. Exception:
  outputs that show personal data, secrets or internal paths (Sev 4 or 5).
- YAML key order.

## Checklists by file type

### SQL

- Joins: can either side have more than one row per key? (fan-out)
- `left join` followed by a `where` on the right table (turns into inner join).
- `not in` with a subquery that can return nulls (returns nothing).
- Division without `nullif(..., 0)`; integer division that truncates.
- `distinct` hiding a duplication instead of fixing it.
- Date and time: time zones, inclusive or exclusive bounds, `between` on
  timestamps.
- `delete`, `update`, `merge` without a precise condition.
- Queries built by string concatenation.
- Style follows `sql-style`, but report style only when lint does not run.

### dbt

| Finding | Sev |
|---|---|
| Hardcoded database or schema instead of `ref()` or `source()` | 4 |
| Fan-out in a mart with aggregated or financial metrics | 4 to 5 |
| Incremental filter on a business date, or `> max()` without lookback | 4 |
| Incremental model on updatable data without `unique_key` | 4 |
| Incremental model without the approved justification of the data's nature | 4 |
| Incremental logic not wrapped in `is_incremental()` | 4 |
| Column removed, renamed or retyped in a mart without updating consumers | 4 |
| Grain key without `unique` and `not_null` | 3 |
| Business logic (joins, aggregations, business filters) in staging | 3 |
| Intermediate or mart without an enforced contract | 3 |
| `select *` outside import CTEs and the final `select * from final` | 3 |
| `.sql` changed without its YML (or the other way around) | 3 |
| New model or column without an English description | 3 |
| `relationships` to a model that does not exist, or foreign id left untested in a mart | 3 |
| New `models/` folder without config in `dbt_project.yml` | 3 |
| Column names with type prefixes or abbreviations (see `dbt-modeling` naming) | 2 |
| Columns out of the standard order | 1 |

Always check what is downstream: `dbt ls --select <model>+`. A harmless change
in staging can break three marts.

### Python

- Secrets in code or default arguments; `.env` committed.
- `eval`, `exec`, `pickle.load` or `yaml.load` on untrusted input.
- SQL built with f-strings or `+` instead of parameters.
- Bare `except:` or `except Exception: pass` that hides failures.
- Mutable default arguments (`def f(items=[])`).
- `print` instead of logging in production code; logs with personal data.
- Missing type hints on public functions (Sev 2), as defined in `python-style`.
- Network or database calls without timeout.
- pandas: chained assignment, silent dtype changes, `apply` over large frames
  where a vectorized operation exists.

### Airflow

- Task not idempotent: rerunning it duplicates or corrupts data.
- `datetime.now()` or `today()` in task logic instead of the data interval.
- Heavy code or queries at the top level of a DAG file (runs on every parse).
- `catchup` not set explicitly; `start_date` dynamic.
- Credentials in code instead of Airflow connections or a secrets backend.
- No retries, or retries on a non-idempotent task.
- Schedule time zone not explicit.

### YAML, JSON and config

- Credentials or tokens in plain text.
- Internal URLs, hosts or account identifiers hardcoded instead of variables.
- Environment-specific values (prod schema, paths) where a variable belongs.

### Markdown and docs

- Setup steps that no longer match the code; broken links.
- Usually Sev 1 or 2, unless wrong docs would cause data loss or a leak.

## Edge cases worth checking

Division by zero, nulls in joins and aggregates, empty inputs, duplicates in
the source, late or backdated rows, time zones and daylight saving, floating
point in money, very large values, concurrent runs of the same job.
