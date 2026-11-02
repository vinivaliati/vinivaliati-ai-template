---
name: python-style
description: >
  Python conventions for data projects: pyenv and Poetry, ruff for lint and
  format, type hints, logging, error handling, safe SQL from Python, pandas
  habits, project layout and pytest. Use when writing, refactoring or
  reviewing Python (.py files, ingestion scripts, Airflow task code, small
  apps, notebooks turned into modules), when setting up pyproject.toml, or
  when the user says "write a script", "clean up this Python", "add tests",
  "escreve um script", "organiza esse código Python". Do not use for DAG
  structure (use airflow-dag) or SQL inside .sql files (use sql-style).
---

# Python style

Code that a reviewer can trust at a glance: typed, linted, logged, tested,
and boring in the best sense. The tools enforce the mechanical part, so
reviews can focus on logic.

## Tooling

| Need | Tool | Rule |
|---|---|---|
| Python version | pyenv | `.python-version` in the repo |
| Dependencies | Poetry | runtime deps in `[tool.poetry.dependencies]`, tools in the `dev` group |
| Lint and format | ruff | `ruff check --fix` and `ruff format`, via pre-commit |
| Tests | pytest | `poetry run pytest` |
| Types | [SUGGESTION] mypy | only when the project asks for it (portfolio apps, shared libraries) |

Minimal ruff config in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "S", "PTH"]
# E/F errors, I imports, B bugbear, UP pyupgrade, SIM simplify, S security, PTH pathlib

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]  # assert is fine in tests
```

## Layout

```text
src/<package>/        # importable code
tests/                # mirrors src/, test_<module>.py
pyproject.toml
```

Scripts that are run, not imported, still live in the package and expose a
`main()` called under `if __name__ == "__main__":`.

## Rules

1. **Type hints on every public function** (parameters and return). Why: the
   signature becomes documentation the editor checks.
2. **Docstring on public functions when the name is not enough**: one line
   for what it does, then arguments or raises only if non-obvious.
3. **`logging`, never `print`**, in code that runs unattended. Log events and
   counts, never personal data or secrets.
4. **Catch specific exceptions.** No bare `except:` and no
   `except Exception: pass`. If you catch, log and re-raise or handle on purpose.
5. **Configuration from the environment** (`os.environ`, `.env` loaded in
   development). No credentials or URLs in code or default arguments.
6. **Timeouts on every network and database call.**
7. **SQL from Python uses parameters**, never f-strings or `+` with values.
   Long SQL lives in `.sql` files that follow `sql-style`.
8. **`pathlib` for paths**, not string concatenation.
9. **No mutable default arguments**; use `None` and create inside.
10. **Small functions that do one thing.** A function that needs "and" in its
    name is two functions.
11. **Constants in `UPPER_SNAKE_CASE`** at module top; no magic numbers in
    logic.

### pandas and dataframes

- Set dtypes when reading (`dtype=`, `parse_dates=`); never trust inference
  for ids (leading zeros) or money.
- Vectorize; avoid `apply` row by row and `iterrows` on large frames.
- No chained assignment; use `.loc` or `assign`.
- Do not print or log frames that contain personal data.

## Example

Fictional distribution company: load daily deliveries from an API.

Good:

```python
import logging
import os

import requests

logger = logging.getLogger(__name__)

API_URL = os.environ["TMS_API_URL"]
TIMEOUT_SECONDS = 30


def fetch_deliveries(delivery_date: str) -> list[dict]:
    """Return the deliveries registered on one date (YYYY-MM-DD)."""
    response = requests.get(
        f"{API_URL}/deliveries",
        params={"date": delivery_date},
        headers={"Authorization": f"Bearer {os.environ['TMS_API_TOKEN']}"},
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    deliveries = response.json()["items"]
    logger.info("Fetched %d deliveries for %s", len(deliveries), delivery_date)
    return deliveries
```

Bad (and why):

```python
def get(d, out=[]):                                   # no types, mutable default, vague name
    try:
        r = requests.get("https://tms.example.com/api/deliveries?date=" + d,
                         headers={"Authorization": "Bearer abc123"})  # hardcoded URL and token, no timeout
        out.extend(r.json()["items"])
        print("ok", r.json())                         # print, logs the whole payload
    except:                                           # bare except hides every failure
        pass
    return out
```

## Tests

- One test file per module, `test_<behavior>` names that read as sentences:
  `test_fetch_deliveries_raises_on_http_error`.
- Small fictional data built in the test or in fixtures; no real extracts.
- Unit tests never hit the network or a warehouse; mock at the boundary
  (`requests`, the database client).
- Test the edge cases that matter for data: empty input, nulls, duplicates,
  time zones, very large values.

## Workflow

1. Read the project's `pyproject.toml` and existing modules; follow what is
   there when it is consistent.
2. Write the code following the rules above.
3. Run `ruff check --fix`, `ruff format` and `pytest`; show the output.
4. If a rule here conflicts with the project, follow the project and say so.
