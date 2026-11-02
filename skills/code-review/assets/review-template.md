# Review: <branch, PR number or files>

**Verdict:** <Request changes | Approve with comments | Approve>
**Scope:** <what was reviewed: N files, M lines; what was out of scope>
**Checks run:** <sqlfluff: 0 issues | ruff: 3 issues (run `ruff check --fix`) | dbt compile: ok | tests: 42 passed | not run: reason>

## Summary

<Two or three sentences: what the change does and the main risk, if any.>

| Sev | Count |
|---|---|
| 5 | 0 |
| 4 | 0 |
| 3 | 0 |
| 2 | 0 |
| 1 | 0 |

## Findings

<!-- Most severe first. One block per verified finding. Remove this section if
there are no findings. -->

### [Sev <n>] <What is wrong, as a statement>

**File:** `<path>:<line or range>`

<What happens and why it matters: the input or data that triggers it and the
consequence for consumers. Numbers when you have them.>

**Fix:** <Concrete change.>

```<language>
<corrected code, only when it makes the fix clearer>
```

## Questions

<!-- Things that look odd but may be intentional. Remove if none. -->

- `<path>:<line>`: <question>

## What is good

- <Specific thing done well, with file when useful.>
- <Another one.>
