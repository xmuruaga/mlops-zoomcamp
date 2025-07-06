# Airflow local quick‑start

You already converted the training notebook into the standalone script **`duration‑prediction.py`** and you now want to orchestrate it with Apache Airflow running on your laptop or in a Codespace.

**Remember, you must launch the MLflow tracking server** by running the following command in your terminal:

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db
```

The MLflow UI will be available at [http://localhost:5000](http://localhost:5000) by default after you start the server.

---

## 1  Activate the venv & install Airflow

```bash
# activate your virtual environment and install Airflow
source .venv/bin/activate
cd 03-orchestration/airflow
pip install apache-airflow pandas scikit-learn xgboost mlflow pyarrow
```

---

## 2  Configure Airflow

### 2.1  Core environment variables

```bash
# keep all Airflow assets (DB, logs, dags) in the project folder
export AIRFLOW_HOME=/workspaces/mlops-zoomcamp/03-orchestration/airflow
# skip Airflow's built‑in example DAGs (keeps the UI clean)
export AIRFLOW__CORE__LOAD_EXAMPLES=False
```

### 2.2  Enable the FAB auth‑manager for static credentials

```bash
# install the provider that ships the auth‑manager (Airflow 3 no longer supports
# "airflow providers install", so use pip):
pip install apache-airflow-providers-fab

# tell Airflow to use it
export AIRFLOW__CORE__AUTH_MANAGER="airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager"
```

---

## 3  Initialise the metadata DB and create the user

```bash
# create / upgrade schema (safe to run as many times as you like)
airflow db migrate

# one‑off user creation
airflow users create \
  --username admin --password admin \
  --firstname Admin --lastname User \
  --role Admin --email admin@example.com
```

---

## 4  Start Airflow (`standalone`)

```bash
# everything inherits the env vars you just exported
airflow standalone    # launches web UI, scheduler & triggerer
```

The first time you run it, Airflow prints a random admin password and stores it in
`$AIRFLOW_HOME/simple_auth_manager_passwords.json.generated` – handy if you forget it.

Open [http://localhost:8080](http://localhost:8080) and log in with **admin / admin**.

<details>
<summary><strong>Troubleshooting – “connection in use: ('::', 8793)”</strong></summary>

The scheduler spins up a tiny internal **Gunicorn** service on port 8793 for log streaming and health checks.
**That port is *not* the Airflow UI**—pointing your browser to [http://localhost:8793](http://localhost:8793) will always yield *Forbidden*.

If you see the “connection in use” error, it only means another scheduler (or a stray Gunicorn worker) is still listening there. Stop it with **Ctrl‑C** in the original terminal **or** kill the processes:

```bash
pkill -f "gunicorn.*8793"        # blanket kill
# or the surgical option
kill $(lsof -t -i :8793)
```

Then launch `airflow scheduler` again.

</details>

<details>
<summary><strong>Troubleshooting – DAG not showing up in the UI</strong></summary>

1. Verify the file really lives in **\$AIRFLOW\_HOME/dags** and ends with `.py` (sometimes editors save it as `hello_world.py.txt`).
2. Run `airflow dags list | grep hello_world` – if it isn’t listed, the scheduler hasn’t imported it yet.
3. Open **Admin → Import Errors** (or look at the scheduler’s stdout). Any Python exception in the module stops the DAG from loading.
4. Ensure the **scheduler was launched *after* you exported `AIRFLOW_HOME`**; otherwise it may still be watching the previous location.
5. A quick fix is to simply restart the scheduler – it scans the DAG directory at startup and then every 30 s (`min_file_process_interval`).

</details>

---

## 5  Create the minimal **hello\_world** DAG

Ensure the folder `$AIRFLOW_HOME/dags` exists, then save **`hello_world.py`** inside:

```python
from datetime import datetime
from airflow import DAG
from airflow.decorators import task

with DAG(
    dag_id="hello_world",
    description="The tiniest possible Airflow DAG",
    start_date=datetime(2025, 1, 1),
    schedule=None,      # run only when manually triggered
    catchup=False,
    tags=["tutorial"],
):

    @task
    def say_hello():
        print("Hello, world! 👋")

    say_hello()
```

Within \~30 seconds the scheduler will detect the new DAG.

---

## 6  Trigger and inspect the DAG

### Web UI

1. In **DAGs**, locate *hello\_world*.
2. Click **Trigger DAG** (▶️ icon).
3. Select the run → **Logs** → confirm *Hello, world!* appears.

### CLI (optional)

```bash
# trigger
airflow dags trigger hello_world
# view logs
airflow tasks logs hello_world say_hello <RUN_ID>
```

---

## 7  Next step – orchestrate `duration‑prediction.py`

Create a new `duration‑prediction-dag.py` with your script:

```python
"""
duration-prediction-dag.py
Runs duration-prediction.py once a month, passing the logical run date
as command-line arguments.
"""

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="duration_prediction",
    description="Train an XGBoost model to predict NYC-taxi duration",
    start_date=datetime(2025, 1, 1),
    schedule="0 0 2 * *",      # 02:00 on the 2nd of every month
    catchup=False,             # flip to True if you want back-fills
    tags=["mlops-zoomcamp"],
):

    run_model = BashOperator(
        task_id="train_xgb_model",
        bash_command=(
            "python /workspaces/mlops-zoomcamp/03-orchestration/homework/duration-prediction.py "
            "--year {{ dag_run.logical_date.year }} "
            "--month {{ '%02d' % dag_run.logical_date.month }}"
        ),
    )

```

Wire it into a larger DAG (add extraction, preprocessing, upload tasks, etc.) and you’ve got a reproducible ML pipeline ready for experimentation.
