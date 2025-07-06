from datetime import datetime
from airflow import DAG
from airflow.decorators import task

with DAG(
    dag_id="hello_world",
    description="The tiniest possible Airflow DAG",
    start_date=datetime(2025, 1, 1),  # any time in the past
    schedule=None,                    # run only when triggered
    catchup=False,
    tags=["tutorial"],
):

    @task
    def say_hello():
        print("Hello, world! 👋")

    say_hello()