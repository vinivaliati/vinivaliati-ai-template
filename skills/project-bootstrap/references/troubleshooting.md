# Troubleshooting setup

Check here before improvising a fix. Each row: symptom, cause, fix.

## WSL2

| Symptom | Cause | Fix |
|---|---|---|
| Installs, git and dbt are very slow | Project lives on the Windows drive (`/mnt/c/...`) | Keep projects in the Linux filesystem (`~/projects/...`) |
| Files ending in `:Zone.Identifier` appear | Windows marks files copied from downloads | Delete them; the kit's `.gitignore` already ignores them |
| `docker: command not found` inside WSL | Docker Desktop WSL integration off | Docker Desktop, Settings, Resources, WSL integration: enable the distro |

## Python: pyenv and Poetry

| Symptom | Cause | Fix |
|---|---|---|
| `pyenv: command not found` | Shell init missing | Add the pyenv init lines from its README to `~/.bashrc`, open a new shell |
| `pyenv install` fails on `_ssl`, `_ctypes`, `readline` | Build dependencies missing | `sudo apt install build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev` |
| Poetry uses the wrong Python | Poetry picked the system interpreter | `poetry env use $(pyenv which python)` |
| `.venv` not in the project folder | Poetry default stores venvs elsewhere | `poetry config virtualenvs.in-project true`, then recreate the env |
| `poetry.lock` is out of date | `pyproject.toml` changed by hand | `poetry lock`, then `poetry install` |

## pre-commit

| Symptom | Cause | Fix |
|---|---|---|
| Hook "failed" but changed files | Fixers (whitespace, ruff) edited files | Review, `git add` the changes, run again |
| gitleaks flags a fake or test value | False positive | Add the finding's fingerprint to `.gitleaksignore`; never disable the hook |
| gitleaks flags a real secret | A secret is in the code | Remove it, move it to `.env`, rotate it; if it was already committed, it is compromised |

## dbt

| Symptom | Cause | Fix |
|---|---|---|
| `Could not find profile named ...` | Profile name or location mismatch | Name in `dbt_project.yml` must match `profiles.yml`; file in `~/.dbt/` or set `DBT_PROFILES_DIR` |
| Credentials in `profiles.yml` | Written as plain text | Use `{{ env_var('NAME') }}` and keep values in `.env` |
| `'dbt_utils' is undefined` | Packages not installed | `dbt deps` |
| DuckDB: `database is locked` | Another process holds the file (DBeaver, a notebook) | Close the other connection, run again |
| `dbt debug` ok, `dbt compile` fails on a model | SQL or Jinja error in that model | Read the compiled SQL in `target/compiled/`, fix the model |

## sqlfluff

| Symptom | Cause | Fix |
|---|---|---|
| `PRS` parsing errors on valid SQL | Wrong `dialect` in `.sqlfluff` | Set the project's warehouse dialect |
| `TMP` warnings on dbt macros | Jinja templater cannot render package macros | Expected with `templater = jinja`; switch to the dbt templater if it matters |
| `PRS` on a model that calls `dbt_utils` | `.sqlfluff_libs/` missing or macro not stubbed | Copy the folder from the sql-style skill; add a stand-in for the new macro |
| `Path does not exist: macros` | `load_macros_from_path` set without the folder | Remove the setting or create the folder |
