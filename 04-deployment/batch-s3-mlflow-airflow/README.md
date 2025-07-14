

# Batch Scoring Pipeline: NYC Taxi Duration Prediction

This directory contains code and orchestration for batch scoring NYC taxi trip durations using MLflow models. The pipeline uses public NYC taxi data for input and writes results to your S3 bucket.

---

## Quick Start

### 1. Prerequisites

- AWS account with write access to your output S3 bucket
- MLflow tracking server accessible at the URI set in the script
- S3 bucket for batch prediction outputs: `nyc-duration-prediction-xabi`
- S3 bucket for MLflow tracking: `mlflow-models-xabi`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure AWS Credentials

Set up your AWS credentials so the code can write to your S3 bucket. You can use `aws configure` or set the following environment variables:

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=...
```

### 4. Start the MLflow Tracking Server

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root s3://mlflow-models-xabi/ --host 0.0.0.0
```
The MLflow UI will be available at http://localhost:5000

### 5. Train and Log a Model to MLflow

Run the training script (update the path as needed):

```bash
python /workspaces/mlops-zoomcamp/03-orchestration/homework/duration-prediction.py --year 2023 --month 03
```
Find the run ID in the MLflow UI and use it for batch scoring.

---

## Batch Scoring (Recommended): Airflow Orchestration

> **Recommended:** Use Airflow to orchestrate batch scoring and backfill. Manual script/notebook runs are for testing or one-off jobs only.

### 1. Airflow Setup & Launch

1. **Activate your venv & enter the project directory:**
    ```bash
    source .venv/bin/activate
    cd 04-deployment/batch-s3-mlflow-airflow
    ```
2. **Set environment variables:**
    ```bash
    export AIRFLOW_HOME=$(pwd)/airflow
    export AIRFLOW__CORE__LOAD_EXAMPLES=False
    export AIRFLOW__CORE__AUTH_MANAGER="airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager"
    ```
3. **Initialize Airflow and create an admin user:**
    ```bash
    airflow db migrate
    airflow users create \
      --username admin --password admin \
      --firstname Admin --lastname User \
      --role Admin --email admin@example.com
    ```
4. **Start Airflow:**
    ```bash
    airflow standalone
    ```
    Open http://localhost:8080 and log in with admin / admin.

### 2. Configure and Run the Airflow DAG

1. Use the provided DAG: `airflow/dags/airflow_batch_scoring_dag.py`
2. Edit the DAG to set your date range, taxi type, and run ID as needed.
3. Ensure your Airflow environment has all dependencies from `requirements.txt` installed.
4. Set up AWS credentials in your Airflow environment.
5. Trigger the DAG from the Airflow UI or set a schedule for regular runs.

**What does the Airflow DAG do?**

- For each month in the configured range, triggers a batch scoring job using your MLflow model and the public NYC taxi data for that month.
- Downloads the input data from the public CloudFront URL (no AWS credentials needed for input)
- Loads the model from MLflow using the specified run ID
- Saves the results to your S3 output bucket in the format:
  ```
  s3://nyc-duration-prediction-xabi/taxi_type=<taxi_type>/year=<year>/month=<month>/<run_id>.parquet
  ```

---

## (Optional) Manual Batch Scoring (Script/Notebook)

> For testing or one-off jobs only. Use Airflow for production and backfill.

- **Notebook:** Open `score.ipynb` and run all cells for a single month.
- **Script:**
  ```bash
  python score.py <taxi_type> <year> <month> <run_id>
  # Example:
  python score.py green 2023 3 71896568911f44db8650b2f4d112ee71
  ```

This will:
- Download the input file from the public CloudFront URL (no AWS credentials needed for input)
- Load the model from MLflow using the specified run ID
- Save the results to your S3 output bucket

