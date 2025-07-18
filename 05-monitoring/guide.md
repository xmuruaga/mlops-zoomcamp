
# Step-by-Step Guide: Running the Monitoring Project (2025 Minimal Edition)

## Prerequisites

- Docker and Docker Compose installed
- Data and model files in place:
  - `data/reference.parquet`
  - `data/green_tripdata_2022-02.parquet`
  - `models/lin_reg.bin`

## 1. Build and Start All Services

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

## 2. Initialize Airflow Database (First Time Only)

In a new terminal, run:

```bash
docker-compose run --rm airflow-webserver airflow db init
```

## 3. Airflow Authentication

- Airflow uses SimpleAuthManager.
- The password file is at `airflow/simple_auth_manager_passwords.json.generated` and should contain:

```json
{"admin": "KuhBwkT96HnVNCry"}
```

- Login at [http://localhost:8082](http://localhost:8082) with:
  - Username: `admin`
  - Password: `KuhBwkT96HnVNCry`

## 4. Access Other UIs

- **Adminer:** [http://localhost:8080](http://localhost:8080) (user: `postgres`, pass: `example`, host: `db`)
- **Grafana:** [http://localhost:3000](http://localhost:3000) (user: `admin`, pass: `admin`)

## 5. Run Monitoring

- In Airflow UI, find the DAG `batch_monitoring_backfill`.
- Turn it on and trigger it manually.
- Metrics will be written to the `dummy_metrics` table in Postgres.

## 6. View Metrics

- Open Grafana and use the preconfigured dashboard.

## 7. Stop All Services

```bash
docker-compose down
```

---

## Troubleshooting

- If you change DAGs, data, or models, restart Airflow containers.
- If login fails, check the password file and restart containers.
- If you get DB errors, re-run the Airflow DB init step.

---

**No Dockerfile, entrypoint, or SQL init scripts are needed. Everything runs from the official images.**
