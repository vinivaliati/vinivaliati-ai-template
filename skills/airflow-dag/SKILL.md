---
name: airflow-dag
description: >
  Writes and reviews Apache Airflow DAGs (Airflow 3, TaskFlow API) for data
  pipelines: idempotent tasks, retries and timeouts, scheduling and backfill,
  connections without secrets in code, running dbt from Airflow, and DAG
  tests. Use when the user asks to "create a DAG", "schedule this pipeline",
  "orchestrate dbt", "backfill", "why did the DAG fail", "cria uma DAG",
  "agenda esse pipeline", "orquestra o dbt". Do not use for the Python inside
  a task's helper modules (use python-style) or for the SQL models (use
  dbt-modeling).
---

# Airflow DAG

A DAG is a schedule plus a list of steps that must be safe to run again. Any
task may be retried, rerun by hand or backfilled for last month, so every
task must produce the same result for the same date, however many times it
runs.

## Rules

1. **Idempotent tasks.** A run for a date overwrites that date's output
   (partition, file or `delete` + `insert`); it never appends blindly. Why: a
   retry after a partial failure must not duplicate rows.
2. **Dates come from the run**, the data interval or `ds`, never `now()` or
   `today()`. Why: a backfill for March must load March.
3. **Fixed `start_date` in the past, `catchup=False`** unless the user wants
   history loaded on deploy.
4. **Retries and timeouts on every task**: `retries`, `retry_delay` and
   `execution_timeout` in `default_args`. Why: a hung task blocks the next
   run silently.
5. **`max_active_runs=1`** when runs depend on each other (incremental
   models, snapshots).
6. **No work at the top level of the DAG file.** No database calls, API calls
   or heavy imports outside tasks. Why: the scheduler parses the file every
   few seconds.
7. **Airflow moves orchestration, not data.** Tasks write to storage or the
   warehouse; XCom carries only small metadata (a path, a row count).
8. **Secrets in Airflow Connections or a secrets backend.** No credentials,
   hostnames or internal URLs in the DAG file or in Variables shown in the UI.
9. **Logic lives in modules, the DAG wires it.** Task bodies call functions
   from the project package, which follow `python-style` and have unit tests.
10. **Every DAG has an owner, tags and `doc_md`**: what it loads, for whom,
    and what to do when it fails.

## Running dbt

Default: one `BashOperator` running `dbt build` with a `--select` for the
models this DAG owns. Simple to read and the same command runs locally.

[SUGGESTION] Astronomer Cosmos renders each dbt model as its own task, with
per-model retries and lineage in the UI. Propose it only for large projects
where that matters, and ask before adding the dependency.

The dbt target comes from the environment (`profiles.yml` with `env_var`),
not from the DAG. The kit's rule still holds: Claude never runs a DAG or dbt
against prod.

## Example

Fictional distribution company: land the daily deliveries extract, then build
the deliveries models.

```python
"""Daily deliveries: land the TMS extract for the run date, then build the dbt models.

Owner: analytics engineering. On failure, check the TMS API status first,
then clear the failed task; both tasks are safe to rerun.
"""

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag, task

DBT_PROJECT_DIR = "/opt/airflow/dbt"


@dag(
    schedule="0 6 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="America/Sao_Paulo"),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "analytics-engineering",
        "retries": 2,
        "retry_delay": pendulum.duration(minutes=10),
        "execution_timeout": pendulum.duration(hours=1),
    },
    tags=["deliveries", "dbt"],
    doc_md=__doc__,
)
def deliveries_daily():
    @task
    def land_deliveries(ds: str | None = None) -> str:
        # Imported here so the scheduler does not load it on every parse.
        from tms_ingest.deliveries import land_deliveries_for_date

        # Overwrites the partition for ds, so retries and backfills are safe.
        return land_deliveries_for_date(ds)

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"dbt build --project-dir {DBT_PROJECT_DIR} --select +fct_deliveries",
    )

    land_deliveries() >> dbt_build


deliveries_daily()
```

What a bad version usually has: `datetime.now()` inside the task, `start_date`
set to `datetime.now()`, a database connection opened at the top of the file,
a dataframe returned through XCom, and a token pasted in the `bash_command`.

## Backfill

1. Confirm every task in the range is idempotent (rule 1) before starting.
2. Agree on the range and on the load it puts on the source and the warehouse.
3. Run it in a non-production environment first when one exists.
4. Run `airflow backfill create --dag-id <dag> --from-date <start>
   --to-date <end> --max-active-runs 1` (raise the limit only if runs are
   independent).
5. Reconcile the result with the source (see `data-quality`).

## Tests

A DAG import test catches broken DAGs before deploy:

```python
from airflow.dag_processing.dagbag import DagBag


def test_dags_import_without_errors():
    dag_bag = DagBag(dag_folder="dags")
    assert dag_bag.import_errors == {}


def test_dags_have_owner_retries_and_tags():
    dag_bag = DagBag(dag_folder="dags")
    for dag_id, dag in dag_bag.dags.items():
        assert dag.tags, f"{dag_id} has no tags"
        for task in dag.tasks:
            assert task.owner != "airflow", f"{dag_id}.{task.task_id} has no owner"
            assert task.retries > 0, f"{dag_id}.{task.task_id} has no retries"
```

The functions the tasks call get normal unit tests (see `python-style`).

## Workflow

1. Ask what the DAG loads, how often, by when the data must be ready, and
   who acts on failures.
2. Check the project's Airflow version and existing DAGs; follow their
   patterns when consistent.
3. Write the task logic as module functions, then the DAG that wires them.
4. Run `ruff` and the DAG tests; show the output.
5. Test one run locally with `airflow dags test <dag_id> <date>` in a dev
   environment, after the user approves.
