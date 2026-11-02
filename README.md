# vini-ai-kit

My way of working with Claude Code as an analytics engineer and team lead,
packaged as a plugin: SQL and dbt conventions, data quality, Airflow, Python,
project setup, code review, portfolio READMEs and presentations in my
personal brand.

The kit encodes how I work (workflows, checks and defaults), not everything
there is to know about each tool. Every example uses fictional data.

## Install

```bash
git clone https://github.com/vinivaliati/vinivaliati-ai-template.git
cd vinivaliati-ai-template
./install.sh   # installs user/CLAUDE.md as ~/.claude/CLAUDE.md, with a backup
```

Then, inside Claude Code:

```text
/plugin marketplace add vinivaliati/vinivaliati-ai-template
/plugin install vini-ai-kit@vinivaliati
```

Skills load on their own when a request matches; call one directly with
`/vini-ai-kit:<skill>`.

## Skills

| Skill | Use it to |
|---|---|
| `sql-style` | Write and format SQL: leading commas, lowercase, named CTEs, one column per line; sqlfluff config included |
| `dbt-modeling` | Design dbt models: layers, naming, contracts, tests, profiling and a model spec before any SQL |
| `legacy-to-dbt` | Migrate ABAP reports, procedures or spreadsheets into dbt, matching and reconciling the legacy output |
| `data-quality` | Add checks beyond model tests: freshness (suggested), volume, reconciliation, what to do when one fails |
| `airflow-dag` | Write idempotent DAGs with retries, timeouts, backfill and import tests (Airflow 3) |
| `python-style` | Python with pyenv, Poetry, ruff, type hints, logging and pytest |
| `project-bootstrap` | Start a project: kickoff interview, skill discovery, then the base files one at a time |
| `portfolio-readme` | Make a portfolio repo clear to a recruiter in 30 seconds and runnable in five minutes |
| `code-review` | Review a diff or PR with a 1 to 5 severity scale and concrete fixes |
| `presentations` | Build decks for five occasions in my brand, from an approved storyline of action titles |

Agent: `code-reviewer` runs the review in a fresh, read-only context.

## How the kit works

- **Ask before assuming.** Skills interview first and mark new conventions as
  suggestions until approved.
- **Spec before code.** A model spec, a storyline or a file plan comes before
  the work.
- **Evidence before done.** Lint, tests and compiled output are shown, not
  claimed. Nothing runs against production, and `dbt build` waits for approval.
- **Safe by default.** No credentials, client data or internal URLs in any
  file; examples are fictional.

## Recommended companions

The kit works without them. Read any third-party skill in full before
installing it.

- [Superpowers](https://github.com/obra/superpowers): brainstorming, planning and verification.
- [Ponytail](https://github.com/DietrichGebert/ponytail): keeps solutions minimal.
- [find-skills](https://github.com/vercel-labs/skills) (MIT): `project-bootstrap` uses it, when
  installed, to suggest skills for a new project's stack.
- [grill-me](https://github.com/mattpocock/skills) (MIT): on-demand interview to stress-test a
  plan. The kickoff interview in `project-bootstrap` is inspired by it.

## Repository layout

```text
.claude-plugin/   plugin.json and marketplace.json
skills/<name>/    SKILL.md, plus references/, assets/ and scripts/ when needed
agents/           code-reviewer
user/CLAUDE.md    global rules, installed by install.sh
```

## License

[MIT](LICENSE). Made by Vinicius Valiati.
