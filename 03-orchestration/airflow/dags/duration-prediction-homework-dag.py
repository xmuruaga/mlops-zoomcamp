"""
duration-prediction-dag.py
Runs duration-prediction.py once a month, training on the same month
one year earlier.
"""
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="duration_prediction_homework",
    description="Train a Linear Regression model to predict Yellow NYC-taxi duration",
    start_date=datetime(2023, 1, 1),
    schedule="0 0 2 * *",      # 02:00 on the 2nd of every month
    catchup=False,
    max_active_runs=1,
    tags=["mlops-zoomcamp"],
):

    # Run for March 2023 to answer the homework questions (Q3 and Q4)
    run_model = BashOperator(
        task_id="train_lr_model",
        bash_command="""
        python /workspaces/mlops-zoomcamp/03-orchestration/homework/duration-prediction-homework.py \
          --year 2023 \
          --month 03
        """,
    )
