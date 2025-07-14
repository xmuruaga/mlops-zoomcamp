from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# Ensure the batch scoring script is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import score

def airflow_batch_scoring(ti, taxi_type, year, month, run_id):
    from datetime import datetime
    score.ride_duration_prediction(
        taxi_type=taxi_type,
        run_id=run_id,
        run_date=datetime(year=year, month=month, day=1)
    )

def generate_run_id():
    # Optionally, generate or fetch a run_id here
    return os.getenv('RUN_ID', '71896568911f44db8650b2f4d112ee71')

def_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'nyc_taxi_batch_scoring',
    default_args=def_args,
    description='Batch scoring for NYC taxi duration prediction using MLflow and S3',
    schedule=None,  # Set your schedule here
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

run_id = generate_run_id()


# Backfill: configure your range here
taxi_type = 'green'
run_id = generate_run_id()
start_year, start_month = 2022, 1
end_year, end_month = 2022, 12

from dateutil.relativedelta import relativedelta
from datetime import date

def month_range(start_year, start_month, end_year, end_month):
    start = date(start_year, start_month, 1)
    end = date(end_year, end_month, 1)
    current = start
    while current <= end:
        yield current.year, current.month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

for year, month in month_range(start_year, start_month, end_year, end_month):
    PythonOperator(
        task_id=f'batch_scoring_{year}_{month:02d}',
        python_callable=airflow_batch_scoring,
        op_kwargs={
            'taxi_type': taxi_type,
            'year': year,
            'month': month,
            'run_id': run_id,
        },
        dag=dag,
    )
