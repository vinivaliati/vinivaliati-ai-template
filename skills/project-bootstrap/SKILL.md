---
name: project-bootstrap
description: >
  Starts a new project with the kit: a kickoff interview in rounds (numbered
  questions, each with a recommended answer) until scope and stack are
  settled, a search for useful third-party skills, then the base files (lean
  CLAUDE.md, docs/ with spec and decision log, .gitignore, pre-commit, Python
  and dbt setup). Use when the user says "new project", "start a project",
  "bootstrap", "set up this repo", "novo projeto", "vamos começar um projeto",
  "inicia esse repositório" or opens an empty repository asking how to begin.
  Do not use for adding a feature to an existing project or for writing the
  README alone (use portfolio-readme).
---

# Project bootstrap

A project starts well when its goal, scope and stack are decided before the
first file exists. Most rework comes from assumptions nobody stated. This
skill makes them explicit, records them, and only then creates files.

## 1. Kickoff interview

Interview the user until every decision the project depends on is settled.
The question bank is in [references/kickoff-interview.md](references/kickoff-interview.md).

How to run it:

- **Rounds.** Ask every question you can ask now (the ones whose
  prerequisites are already answered), numbered, in one message. Wait for the
  answers, then ask the next round.
- **Recommend.** Every question carries your recommended answer, so "ok"
  accepts it. Use the defaults in the question bank as recommendations.
- **Facts are yours, decisions are the user's.** Look up what you can (the
  repository, installed tools, Python and dbt versions) instead of asking.
  Ask only for choices.
- **Stop when nothing is open.** Summarize the decisions in a short list and
  wait for confirmation before going on.

Format of a round:

```markdown
**1. Project type?** Study, portfolio, company or client.
Recommended: portfolio, so files and README are in English.

**2. Warehouse?** Snowflake, BigQuery, Postgres, Databricks, DuckDB.
Recommended: DuckDB, since this is a study project (free, runs locally).
```

## 2. Skill discovery

If the `find-skills` skill (vercel-labs/skills) is installed, search for
skills that match the stack decided in the interview (for example the
warehouse, the orchestrator, the BI tool). Present at most five, with source,
install count and what each adds that this kit does not cover. Prefer
official or well-known sources.

- Reject any skill that fetches remote code, asks for credentials or
  contradicts this kit.
- If `find-skills` is not installed, skip this step and mention once that it
  exists.

## 3. Plan the files

Show the tree of files to create and wait for approval. Typical project:

```text
.
├── CLAUDE.md                     # from assets/CLAUDE.md
├── README.md                     # skeleton; full version with portfolio-readme
├── .gitignore                    # from assets/.gitignore
├── .pre-commit-config.yaml       # from assets/.pre-commit-config.yaml
├── .sqlfluff                     # from the sql-style skill, dialect set
├── .sqlfluff_libs/               # from the sql-style skill, next to .sqlfluff
├── .env.example                  # names only, never values
├── .python-version               # pyenv
├── pyproject.toml                # poetry init
└── docs/
    ├── spec.md                   # from assets/docs/spec.md, filled from the interview
    ├── decisions.md              # from assets/docs/decisions.md
    └── adr/                      # created with the first ADR (assets/docs/adr-template.md)
```

Add only what the interview asked for. A project without SQL gets no
`.sqlfluff`; a project without Python gets no `pyproject.toml`. The Dev
Container in [assets/.devcontainer/devcontainer.json](assets/.devcontainer/devcontainer.json)
is optional; offer it when the user works on Windows with WSL2 or wants a
reproducible environment for others.

## 4. Create the files

- Fill templates with the interview decisions. Leave no placeholder behind;
  if a value is unknown, ask.
- `CLAUDE.md` stays lean: what the project is, rules, stack, definition of
  done, current state. Everything long goes to `docs/`.
- Record every interview decision in `docs/decisions.md` with today's date.
- For dbt, run `dbt init` only after asking; then apply the `dbt-modeling`
  folder layout and `dbt_project.yml` defaults.

## 5. Verify

Run what applies and show the output:

- `pyenv local <version>` and `poetry install`
- `pre-commit install` and `pre-commit run --all-files` (needs a git
  repository; if there is none, ask before `git init`)
- `dbt debug` and `dbt compile` (dev target only)

If something fails, check [references/troubleshooting.md](references/troubleshooting.md)
before improvising. Do not run `git init`, commit or create a remote
repository unless the user asks.

## Done when

- [ ] Interview summary confirmed by the user.
- [ ] Every created file approved; no placeholders left.
- [ ] `docs/decisions.md` lists the kickoff decisions.
- [ ] Verification commands ran, output shown.
- [ ] Next step proposed (usually the first spec item).
