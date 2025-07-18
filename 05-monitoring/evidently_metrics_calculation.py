
import datetime
import time
import random
import logging
import uuid
import pytz
import pandas as pd
import io
import psycopg
import joblib

from airflow import DAG
try:
	from airflow.operators.python import PythonOperator  # Airflow <2.8
except ImportError:
	from airflow.providers.common.sql.operators.python import PythonOperator  # Airflow 2.8+

from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10
rand = random.Random()

create_table_statement = """
DROP TABLE IF EXISTS dummy_metrics;
CREATE TABLE dummy_metrics(
	timestamp timestamp,
	prediction_drift float,
	num_drifted_columns integer,
	share_missing_values float
);
"""

begin = datetime.datetime(2022, 2, 1, 0, 0)
num_features = ['passenger_count', 'trip_distance', 'fare_amount', 'total_amount']
cat_features = ['PULocationID', 'DOLocationID']
column_mapping = ColumnMapping(
	prediction='prediction',
	numerical_features=num_features,
	categorical_features=cat_features,
	target=None
)

report = Report(metrics = [
	ColumnDriftMetric(column_name='prediction'),
	DatasetDriftMetric(),
	DatasetMissingValuesMetric()
])

def prep_db():
	with psycopg.connect("host=localhost port=5432 user=postgres password=example", autocommit=True) as conn:
		res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
		if len(res.fetchall()) == 0:
			conn.execute("create database test;")
		with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example") as conn2:
			conn2.execute(create_table_statement)

def calculate_and_store_metrics(i):
	reference_data = pd.read_parquet('data/reference.parquet')
	with open('models/lin_reg.bin', 'rb') as f_in:
		model = joblib.load(f_in)
	raw_data = pd.read_parquet('data/green_tripdata_2022-02.parquet')

	current_data = raw_data[(raw_data.lpep_pickup_datetime >= (begin + datetime.timedelta(i))) &
							(raw_data.lpep_pickup_datetime < (begin + datetime.timedelta(i + 1)))]
	current_data['prediction'] = model.predict(current_data[num_features + cat_features].fillna(0))

	report = Report(metrics=[
		ColumnDriftMetric(column_name='prediction'),
		DatasetDriftMetric(),
		DatasetMissingValuesMetric()
	])
	report.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)
	result = report.as_dict()

	prediction_drift = result['metrics'][0]['result']['drift_score']
	num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
	share_missing_values = result['metrics'][2]['result']['current']['share_of_missing_values']

	with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example", autocommit=True) as conn:
		with conn.cursor() as curr:
			curr.execute(
				"insert into dummy_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values) values (%s, %s, %s, %s)",
				(begin + datetime.timedelta(i), prediction_drift, num_drifted_columns, share_missing_values)
			)

def batch_monitoring_backfill_airflow(**context):
	prep_db()
	last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)
	for i in range(0, 27):
		calculate_and_store_metrics(i)
		new_send = datetime.datetime.now()
		seconds_elapsed = (new_send - last_send).total_seconds()
		if seconds_elapsed < SEND_TIMEOUT:
			time.sleep(SEND_TIMEOUT - seconds_elapsed)
		while last_send < new_send:
			last_send = last_send + datetime.timedelta(seconds=10)
		logging.info(f"data sent for interval {i}")


# Airflow DAG definition
default_args = {
	'owner': 'airflow',
	'depends_on_past': False,
	'retries': 1,
}

with DAG(
	dag_id='batch_monitoring_backfill',
	default_args=default_args,
	description='Batch monitoring backfill with Evidently and PostgreSQL',
	schedule_interval=None,
	start_date=datetime.datetime(2024, 1, 1),
	catchup=False,
) as dag:
	run_batch_monitoring = PythonOperator(
		task_id='run_batch_monitoring',
		python_callable=batch_monitoring_backfill_airflow,
		provide_context=True
	)

# Prevent running as a script
if __name__ == "__main__":
	print("This file is an Airflow DAG and should not be run with 'python ...'. Move it to your Airflow 'dags/' folder and trigger it via the Airflow UI or CLI.")
