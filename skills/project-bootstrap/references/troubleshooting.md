# Troubleshooting setup

Problems specific to this kit and setup (WSL2, the kit's hooks and sqlfluff
config). Check here before improvising a fix.

| Symptom | Cause | Fix |
|---|---|---|
| Installs, git and dbt are very slow | Project lives on the Windows drive (`/mnt/c/...`) | Keep projects in the Linux filesystem (`~/projects/...`) |
| Files ending in `:Zone.Identifier` appear | Windows marks files copied from downloads | Delete them; the kit's `.gitignore` already ignores them |
| Poetry uses the wrong Python | Poetry picked the system interpreter | `poetry env use $(pyenv which python)` |
| gitleaks flags a fake or test value | False positive | Add the finding's fingerprint to `.gitleaksignore`; never disable the hook |
| gitleaks flags a real secret | A secret is in the code | Remove it, move it to `.env`, rotate it; if it was already committed, it is compromised |
| `PRS` on a model that calls `dbt_utils` | `.sqlfluff_libs/` missing or macro not stubbed | Copy the folder from the sql-style skill; add a stand-in for the new macro |
| `TMP` warnings on dbt macros | The jinja templater cannot render package macros | Expected with `templater = jinja`; switch to the dbt templater if it matters |
| `Path does not exist: macros` | `load_macros_from_path` set without the folder | Remove the setting or create the folder |
