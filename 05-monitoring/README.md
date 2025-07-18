# 5. Model Monitoring

## 5.1 Intro to ML monitoring

<a href="https://www.youtube.com/watch?v=SQ0jBwd_3kk&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/SQ0jBwd_3kk">
</a>



## 5.2 Environment setup

<a href="https://www.youtube.com/watch?v=yixA3C1xSxc&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/yixA3C1xSxc">
</a>



## 5.3 Prepare reference and model

<a href="https://www.youtube.com/watch?v=IjNrkqMYQeQ&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/IjNrkqMYQeQ">
</a>



## 5.4 Evidently metrics calculation

<a href="https://www.youtube.com/watch?v=kP3lzh_HfWY&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/kP3lzh_HfWY">
</a>


## 5.5 Evidently Monitoring Dashboard

<a href="https://www.youtube.com/watch?v=zjvYhDPzFlY&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/zjvYhDPzFlY">
</a>


## 5.6 Dummy monitoring

<a href="https://www.youtube.com/watch?v=s3G4PMsOMOA&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/s3G4PMsOMOA">
</a>



## 5.7 Data quality monitoring

<a href="https://www.youtube.com/watch?v=fytrmPbcLhI&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/fytrmPbcLhI">
</a>

> Note: in this video we use Prefect (07:33-11:21). Feel free to skip this part. Also note that Prefect
is not officially supported in the 2024 edition of the course.


## 5.8 Save Grafana Dashboard

<a href="https://www.youtube.com/watch?v=-c4iumyZMyw&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/-c4iumyZMyw">
</a>



## 5.9 Debugging with test suites and reports

<a href="https://www.youtube.com/watch?v=sNSk3ojISh8&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="https://markdown-videos-api.jorgenkh.no/youtube/sNSk3ojISh8">
</a>




# How to Use This Project

## 1. Prerequisites

- Docker and Docker Compose installed
- NYC taxi data and trained model available in the expected locations

## 2. Prepare Data and Model

- Run the notebook `baseline_model_nyc_taxi_data.ipynb` to download datasets, train the model, and create the reference and current data files.
  - This will generate:
    - `data/reference.parquet`
    - `data/green_tripdata_2022-02.parquet`
    - `models/lin_reg.bin`



## 3. Start the Monitoring Stack

From the `05-monitoring` directory, run:
```bash
docker-compose up --build
```
This will start:
- PostgreSQL (metrics storage)
- Adminer (DB UI, http://localhost:8080)
- Grafana (dashboard, http://localhost:3000)
- Airflow webserver (http://localhost:8082)
- Airflow scheduler

### 3a. Initialize Airflow (First Time Only)

Open a new terminal in the same directory and run:
```bash
docker-compose run --rm airflow-webserver airflow db init
docker-compose run --rm airflow-webserver airflow users create \
  --username admin --password admin \
  --firstname Admin --lastname User \
  --role Admin --email admin@example.com
```
You only need to do this once, unless you reset the database.

## 5. Access the UIs

- **Airflow:** [http://localhost:8082](http://localhost:8082) (login: admin / admin)
- **Adminer:** [http://localhost:8080](http://localhost:8080) (DB: postgres, user: postgres, pass: example, host: db)
- **Grafana:** [http://localhost:3000](http://localhost:3000) (login: admin / admin)

## 6. Run Monitoring

- In Airflow UI, find the DAG `batch_monitoring_backfill`.
- Turn it on and trigger it manually (play button).
- The DAG will calculate metrics and store them in the `dummy_metrics` table in Postgres.

## 7. View Metrics in Grafana

- Open Grafana and use the preconfigured dashboard to view drift and missing value metrics.

## 8. (Optional) Manual Monitoring

- Run `python evidently_metrics_calculation.py` to simulate batch monitoring and send metrics to the database.
- For ad-hoc debugging, run `debugging_nyc_taxi_data.ipynb` to use Evidently TestSuites and Reports.

## 9. Stop All Services

To stop all services, run:
```bash
docker-compose down
```
  - `data/green_tripdata_2022-02.parquet`
  - `models/lin_reg.bin`


### 4. Airflow Setup & Launch


#### Airflow Setup & Launch (with Docker Compose)

**Step 1: Start All Services**

From the `05-monitoring` directory, run:
```bash
docker-compose up --build
```
This will start:
- PostgreSQL (metrics storage)
- Adminer (DB UI, http://localhost:8080)
- Grafana (dashboard, http://localhost:3000)
- Airflow webserver (http://localhost:8082)
- Airflow scheduler

**Step 2: Initialize Airflow (First Time Only)**

Open a new terminal in the same directory and run:
```bash
docker-compose run --rm airflow-webserver airflow db init
docker-compose run --rm airflow-webserver airflow users create \
  --username admin --password admin \
  --firstname Admin --lastname User \
  --role Admin --email admin@example.com
```
You only need to do this once, unless you reset the database.

**Step 3: Access Airflow**

Go to [http://localhost:8082](http://localhost:8082) and log in with:
- Username: `admin`
- Password: `admin`

---

## Monitoring with Airflow

> **Recommended:** Use Airflow to orchestrate monitoring and backfill. Manual script/notebook runs are for testing or one-off jobs only.

### 1. Configure and Run the Airflow DAG

1. Use the provided DAG: `airflow/dags/evidently_metrics_calculation.py`
2. Edit the DAG to set your date range or data/model paths as needed.
3. Ensure your Airflow environment has all dependencies from `requirements.txt` installed.
4. Trigger the DAG from the Airflow UI or set a schedule for regular runs.

**What does the Airflow DAG do?**

- For each day in the configured range, computes drift and missing value metrics using Evidently.
- Loads the reference and current data, and the trained model.
- Stores the computed metrics in a PostgreSQL table (`dummy_metrics`).

---

## (Optional) Manual Monitoring (Script/Notebook)

> For testing or one-off jobs only. Use Airflow for production and backfill.

- **Notebook:** Open `baseline_model_nyc_taxi_data.ipynb` or `debugging_nyc_taxi_data.ipynb` and run all cells for a single period.
- **Script:**  
  You can adapt the code in `evidently_metrics_calculation.py` to run as a standalone script for quick tests.

---

## Output

- Metrics are stored in the PostgreSQL table `dummy_metrics` for further analysis, dashboarding, or alerting.

---

## Notes

- Ensure your PostgreSQL instance is running and accessible before triggering the DAG.
- You can customize the DAG to monitor different time periods, data files, or models as needed.



---

## How to Run the Monitoring Stack (Step by Step)

### 1. Build and Start All Services

From the `05-monitoring` directory, run:

```bash
docker-compose up --build
```
This will start:
- PostgreSQL (metrics storage)
- Adminer (DB UI, http://localhost:8080)
- Grafana (dashboard, http://localhost:3000)
- Airflow webserver (http://localhost:8082)
- Airflow scheduler

### 2. Initialize Airflow and Create Admin User (First Time Only)

Open a new terminal in `05-monitoring` and run:

```bash
docker-compose run --rm airflow-webserver airflow db init
docker-compose run --rm airflow-webserver airflow users create \
  --username admin --password admin \
  --firstname Admin --lastname User \
  --role Admin --email admin@example.com
```

### 3. Prepare Data and Model

- Place your reference data in `05-monitoring/data/reference.parquet`
- Place your current data in `05-monitoring/data/green_tripdata_2022-02.parquet`
- Place your trained model in `05-monitoring/models/lin_reg.bin`

These folders are mounted into the Airflow containers by default. If you add new data/models, restart Airflow containers.

### 4. Access the UIs

- **Airflow:** [http://localhost:8082](http://localhost:8082) (login: admin / admin)
- **Adminer:** [http://localhost:8080](http://localhost:8080) (DB: postgres, user: postgres, pass: example, host: db)
- **Grafana:** [http://localhost:3000](http://localhost:3000) (login: admin / admin)

### 5. Trigger the Monitoring DAG

1. In Airflow UI, find the DAG `batch_monitoring_backfill`.
2. Turn it on and trigger it manually (play button).
3. The DAG will calculate metrics and store them in the `dummy_metrics` table in Postgres.

### 6. View Metrics in Grafana

- Open Grafana and use the preconfigured dashboard to view drift and missing value metrics.

### 7. Stop All Services

```bash
docker-compose down
```

---

## Troubleshooting & Tips

- If you change DAGs, data, or models, restart the Airflow containers.
- If you get permission errors, ensure the `airflow` folders are owned by your user or fix permissions with `chmod -R 777 airflow` (for local dev only).
- If you need to debug, use `docker-compose exec airflow-webserver bash` to get a shell inside the Airflow container.
- All logs are in `airflow/logs`.

---

## Folder Structure Overview

- `airflow/` - Airflow configs, DAGs, logs
- `data/` - Input parquet files
- `models/` - Trained model binaries
- `config/` - Grafana and other service configs
- `dashboards/` - Grafana dashboards
- `docker-compose.yml` - Service orchestration
- `requirements.txt` - Python dependencies
- `README.md` - This guide

---

## What Happens?
- Airflow orchestrates batch monitoring jobs using Evidently.
- Metrics are written to Postgres and visualized in Grafana.
- Adminer lets you inspect the database directly.

---

For more details, see the comments in each DAG and the configuration files.
