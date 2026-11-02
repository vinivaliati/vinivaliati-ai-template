# Kickoff interview: question bank

Ask in rounds. A question enters a round only when the questions it depends
on are answered. Skip questions the repository or the user's earlier answers
already settle. Every question carries a recommendation.

Defaults depend on the project type (round 1):

- **Study or portfolio:** recommend the kit's stack: DuckDB, dbt, Python with
  Poetry and pyenv, GitHub public repository, files in English.
- **Company or client:** recommend nothing for the stack. Ask what the
  company uses and follow it. The kit's conventions still apply unless the
  company has its own.

## Round 1: purpose

| Question | Why it matters |
|---|---|
| Is this a study, portfolio, company or client project? | Sets every default below |
| What should exist when it is done, in one sentence? | Becomes the goal in `CLAUDE.md` and `docs/spec.md` |
| Who uses the result? (recruiters, a business team, an app) | Decides README depth, docs language, quality bar |
| What is explicitly out of scope? | Prevents scope creep; goes in the spec |
| Is there a deadline or a first milestone date? | Shapes the plan size |

## Round 2: data and stack

| Question | Study default | Company or client |
|---|---|---|
| Where does the data come from? | Public dataset or fictional generator | Ask the systems (ERP, TMS, APIs) |
| Warehouse? | DuckDB | Company's warehouse |
| Transformation? | dbt | Company's tool |
| Orchestration needed? | None, or Airflow if the goal is to learn it | Company's orchestrator |
| Python needed? (ingestion, app, ML) | Python 3.12, Poetry, pyenv | Company's versions and tools |
| BI or app on top? | Optional | Company's BI tool |
| Personal or sensitive data involved? | No; use fictional data | Ask; affects access, masking and logs |

## Round 3: environment and workflow

| Question | Study default | Company or client |
|---|---|---|
| Where will it run? | WSL2 locally; Dev Container optional | Company's environment |
| Repository hosting and visibility? | GitHub, public | Company's Git server, private |
| Files and docs language? | English | Ask (team language) |
| Definition of done? | Lint, tests and `dbt build` in dev pass; docs updated | Company's CI gates plus the kit's |
| CI now or later? | Later; add when the first model exists | Follow company pipelines |

## Round 4: first step

| Question | Why it matters |
|---|---|
| Which part comes first? (ingestion, first staging model, first mart) | Becomes the first item in the spec and the next step |
| Anything already decided that I should not question? | Records constraints as decisions, not open points |

## Closing summary

When no question is open, summarize in this shape and wait for "ok":

```markdown
**Project:** <name>, <type>. <goal in one sentence>
**Users:** <who>
**Out of scope:** <list>
**Stack:** <warehouse>, <tools>, Python <version> (Poetry, pyenv)
**Data:** <sources>; sensitive data: <yes or no>
**Environment:** <where it runs>, <repo hosting and visibility>
**Done means:** <checks>
**First step:** <item>
```

Each line becomes a dated entry in `docs/decisions.md`.
