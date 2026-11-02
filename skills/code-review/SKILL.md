---
name: code-review
description: >
  Reviews code changes (a diff, branch, pull request or set of files) for SQL,
  dbt, Python, Airflow and config files, and reports verified findings ranked
  by a 1 to 5 severity scale (impact x probability), with file, line, why it
  matters and a concrete fix. Use when the user says "review this", "code
  review", "review my PR", "check before merge", "revisa esse código",
  "revisa meu PR", "dá uma olhada nessas mudanças" or "isso está pronto para
  merge?". Do not use to reformat code (run sqlfluff or ruff), to apply fixes
  the user did not ask for, or for a review focused only on
  over-engineering (Ponytail's review, if installed, does that).
---

# Code review

A review exists to stop real problems before merge: wrong numbers, lost data,
leaked secrets, broken consumers. Every finding costs the author time, so each
one must be true, specific and worth fixing. Five verified findings beat
twenty guesses.

## Principles

- **Verify before reporting.** Re-read the code and trace the data or call
  path. If you are not sure, write it as a question, not a finding.
- **Rank by severity.** Use the scale below and the rules in
  [references/rubric.md](references/rubric.md). Most severe first.
- **No linter noise.** Formatting, import order and whitespace belong to
  sqlfluff, ruff and CI. Run them if available and report one line with the
  count, not each item.
- **Every finding is actionable**: file and line, what is wrong, why it
  matters, how to fix it (with code when it helps).
- **Say what is good.** Two or three specific things done well. It tells the
  author what to keep doing.
- **Respect the project's rules.** The project `CLAUDE.md` and the kit skills
  (`sql-style`, `dbt-modeling`, `python-style`) are the standard; when they
  disagree, the project wins.

## Severity scale

| Sev | Name | Meaning | Merge |
|---|---|---|---|
| 5 | Critical | Data loss, leaked secret, security hole, consumers get wrong numbers with near certainty | Blocks |
| 4 | High | Probable bug in core logic, breaking change for consumers, unhandled failure in a critical path | Blocks |
| 3 | Medium | Missing tests on new logic, maintainability debt that will cause bugs, performance or cost problem | Fix now or track |
| 2 | Low | Readability, naming, small refactor | Optional |
| 1 | Note | Preference, FYI | Optional |

Choose with impact x probability:

| Impact | High probability | Medium | Low |
|---|---|---|---|
| Critical (data loss, security, compliance) | 5 | 4 to 5 | 4 |
| High (core feature or metric breaks) | 4 | 3 to 4 | 3 |
| Medium (secondary feature affected) | 3 | 2 to 3 | 2 |
| Low (style, readability) | 1 to 2 | 1 to 2 | 1 |

## Workflow

1. **Define the scope.** Ask what to review if it is not clear: current
   branch against `main` (`git diff main...HEAD`), a PR (`gh pr diff <n>`),
   or specific files. Note the size; for very large diffs, propose reviewing
   by area.
2. **Read context, not just the diff.** Open the full changed files, the
   project `CLAUDE.md`, and what depends on the change: downstream dbt models
   (`dbt ls --select <model>+`), callers of a changed function, DAGs that run
   a changed task.
3. **Run the cheap checks** when available: `sqlfluff lint`, `ruff check`,
   `dbt compile`, the test suite. Never run anything that writes to a shared
   environment.
4. **Review in this order**, stopping to verify each suspicion:
   1. correctness and data (logic, joins and fan-out, grain, nulls, time
      zones, incremental filters);
   2. security and privacy (secrets, injection, personal data in logs or
      outputs);
   3. contracts and breaking changes (renamed or removed columns, changed
      types, public function signatures);
   4. tests (new logic without tests, grain without `unique`);
   5. performance and cost (full scans, repeated work, warehouse cost);
   6. maintainability and documentation.

   File-type checklists are in [references/rubric.md](references/rubric.md).
5. **Classify** each verified finding with the matrix and the escalation rules
   in the rubric.
6. **Write the report** using
   [assets/review-template.md](assets/review-template.md). Verdict:
   - **Request changes** if any finding is Sev 4 or 5.
   - **Approve with comments** if the worst is Sev 3.
   - **Approve** otherwise.
7. **Stop.** Do not fix, commit, approve or post comments on the PR unless the
   user asks. When asked to post, show the text first.

## Writing a finding

Good:

```markdown
### [Sev 4] Join to deliveries duplicates orders and inflates OTIF denominator
**File:** `models/marts/logistics/fct_order_otif.sql:42-45`
`stg_erp__deliveries` has one row per delivery attempt, so orders with a
redelivery appear twice. In last month's data that is 3.1% of orders, which
lowers OTIF by about 1.5 pp.
**Fix:** deduplicate to the latest attempt before the join (see the
`latest_delivery` CTE pattern in `sql-style`), and add `unique` on `order_id`.
```

Bad (and why):

```markdown
- This join looks wrong, maybe check it.        <- no line, no proof, no fix
- Consider using CTEs for readability.          <- vague, and probably Sev 2 at most
- Line 12: trailing whitespace.                 <- linter noise
```

## Tone

Objective and specific, never personal. Describe the code, not the author:
"this join duplicates orders", not "you broke the join". Assume good reasons;
when something looks odd but might be intentional, ask.

## Language

Talk to the user in their language. Text meant to be posted on a PR follows
the language the team uses in that repository.

## Isolated review

For a large change, or when the user wants a second opinion, delegate to the
`code-reviewer` agent of this kit. It runs this skill in a fresh context, so
it reviews what the code does, not what the conversation assumed it does.
