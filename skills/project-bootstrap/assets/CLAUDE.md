# <Project name>

<Goal in one sentence, from the kickoff interview.>

- **Type:** <study | portfolio | company | client>
- **Users:** <who uses the result>
- **Out of scope:** <list>
- **Spec:** [docs/spec.md](docs/spec.md) · **Decisions:** [docs/decisions.md](docs/decisions.md) · **ADRs:** `docs/adr/`

## Rules

The global `~/.claude/CLAUDE.md` applies. On top of it:

- Use the `vini-ai-kit` skills: `sql-style`, `dbt-modeling`, `python-style`,
  `code-review`<, others that apply>.
- <Project-specific rule, only if it differs from the kit.>

## Stack and commands

| What | Tool | Command |
|---|---|---|
| Warehouse | <DuckDB> | |
| Transformations | dbt <version>, target `dev` | `dbt build --select <model>+` (after approval) |
| Python | <3.12>, Poetry, pyenv | `poetry install` |
| Lint | sqlfluff, ruff | `pre-commit run --all-files` |
| Tests | <pytest, dbt tests> | `<command>` |

## Definition of done

- Lint, tests and `dbt build` in dev pass, with output shown.
- New behavior has a test; new models have SQL and YML.
- Docs touched by the change are updated.
- Decisions taken during the task are in `docs/decisions.md`.

## Session ritual

- **Start:** read this file and the last entries of `docs/decisions.md`, run
  `git status`, then summarize in three lines where we stopped.
- **End:** update "Current state" below and add the session's decisions to
  `docs/decisions.md`, with absolute dates.

## Current state

- <YYYY-MM-DD>: Project bootstrapped. Next step: <first item of the spec>.
