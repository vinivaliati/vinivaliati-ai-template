# Global instructions

These rules apply to every project. A project `CLAUDE.md` may add rules; when
it contradicts this file, the project file wins for that project. Likewise,
when a project's conventions differ from the kit skills, follow the project
and say so.

## Who I am

Vinicius Valiati, Team Leader and Analytics Engineer. Main stack: SQL, dbt,
Airflow, Python, cloud data warehouses, SAP as a frequent source.

## Communication

- Talk to me in Portuguese (pt-BR). Write code, comments, docs, commit
  messages and every file in English, unless the project says otherwise.
- Be direct. Start with the answer or the outcome, then the details.
- Never use em dashes, in chat or in files. Use a comma, colon, period or
  parentheses instead.
- When information is missing or ambiguous, ask. Do not guess table names,
  business rules, grains or credentials.
- When you propose a convention that is not written down yet, mark it
  **[SUGESTÃO]** in chat (`[SUGGESTION]` in files) and ask before applying it.

## Working style

- When you create or rewrite a file for me to review, show its full content,
  not a patch or a diff.
- For multi-file work, build one file at a time: create it, show it, wait for
  my approval, then move on.
- Explain the "why" behind non-obvious choices in one or two sentences.
- Prefer the simplest solution that works. Do not add dependencies,
  abstractions or configuration I did not ask for.

## Data and security

- Never write credentials, tokens, internal URLs, client names or client data
  into code, docs, examples, commits or prompts to external services.
- Examples and test data are always fictional (for instance, a distribution
  company with orders, OTIF, inventory and transport).
- Never read `.env` files or secret stores unless I ask for it explicitly.
- Third-party skills run with my permissions: read every file before
  installing one, and never install one without my approval.

## SQL and dbt

- Follow the `vini-ai-kit:sql-style` and `vini-ai-kit:dbt-modeling` skills.
  The short version: lowercase keywords, leading commas, one column per line,
  named CTEs, `select *` only in import CTEs and in `select * from final`.
- You may run `dbt compile`, `dbt parse` and `dbt ls` on your own.
- `dbt build`, `dbt run`, `dbt test` and `dbt seed` only after I approve, only
  against the dev target, never prod.

## Python

- Poetry for dependencies, pyenv for the Python version.
- Follow the `vini-ai-kit:python-style` skill.

## Git

- Never commit, push, rebase or force anything unless I ask.
- Never commit secrets, data extracts or local environment files.
