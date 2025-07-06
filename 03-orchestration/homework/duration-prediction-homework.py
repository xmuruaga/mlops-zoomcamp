# This script was converted from a Jupyter notebook (duration-prediction.ipynb) to a Python script.
# jupyter nbconvert --to=script duration-prediction.ipynb

# Key changes made during conversion and adaptation for homework:
# 1. Removed notebook cell structure and markdown explanations; only code is retained.
# 2. Added a main guard (`if __name__ == "__main__":`) to allow command-line execution.
# 3. Introduced argparse to accept year and month as command-line arguments instead of hardcoding or using notebook cells.
# 4. Removed any interactive display or plotting code specific to notebooks.
# 5. Added code to write the MLflow run_id to a file (run_id.txt) for automation.
# 6. Consolidated all imports at the top of the script.
# 7. Organized code into functions for modularity and reusability.
# 8. Ensured the script is self-contained and can be run independently from the command line.
# 9. Changed from using the Green taxi dataset to the Yellow taxi dataset to match homework requirements.
# 10. Updated data preparation logic to use the correct datetime columns for the Yellow taxi data (`tpep_pickup_datetime`, `tpep_dropoff_datetime`).

# Execute it: python duration-prediction.py --year=2021 --month=1

#!/usr/bin/env python
# coding: utf-8



import pickle
import os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error
from sklearn.linear_model import LinearRegression
import mlflow
from mlflow.models.signature import infer_signature

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("nyc-taxi-experiment")

models_folder = Path('models')
models_folder.mkdir(exist_ok=True)



def read_dataframe(year, month):
    """
    Reads the NYC taxi data for the given year and month, prints the number of records loaded (Q3),
    applies duration filtering and prints the number of records after filtering (Q4).
    """
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet'
    df = pd.read_parquet(url)
    # Only print Q3/Q4 if this is the training (March) data
    if month == 3:
        print(f"[Q3] Number of records loaded for {year}-{month:02d}: {len(df):,}")

    # Data preparation logic (Q4) for yellow taxi
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['duration'] = df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
    df.duration = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)]
    if month == 3:
        print(f"[Q4] Number of records after duration filtering: {len(df):,}")

    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)

    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']

    return df


def create_X(df, dv=None):
    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')

    if dv is None:
        dv = DictVectorizer(sparse=True)
        X = dv.fit_transform(dicts)
    else:
        X = dv.transform(dicts)

    return X, dv





def train_linear_regression(X_train, y_train, X_val, y_val, dv):
    """
    Trains a linear regression model, logs to MLflow, prints model intercept (Q5) and model size in bytes (Q6).
    """
    with mlflow.start_run() as run:
        # Q5: Train linear regression and print intercept
        lr = LinearRegression()
        lr.fit(X_train, y_train)
        print(f"[Q5] LinearRegression intercept_: {lr.intercept_}")

        y_pred = lr.predict(X_val)
        rmse = root_mean_squared_error(y_val, y_pred)
        mlflow.log_metric("rmse", rmse)

        # Log DictVectorizer
        with open("models/dv.b", "wb") as f_out:
            pickle.dump(dv, f_out)
        mlflow.log_artifact("models/dv.b", artifact_path="preprocessor")

        # Log the linear regression model
        import numpy as np
        from mlflow.models.signature import infer_signature
        input_example = X_val[0:2] if hasattr(X_val, 'shape') else np.array(list(X_val)[:2])
        signature = infer_signature(X_val, y_val)
        model_info = mlflow.sklearn.log_model(
            lr,
            artifact_path="models_mlflow",
            signature=signature,
            input_example=input_example
        )

        # Q6: Model size in bytes: Check the MLmodel file size in the MLflow UI for this run.
        print("[Q6] To answer Q6, open the MLflow UI, go to the run's Artifacts, and check the size of the MLmodel file (should be about 1.04KB = 4,534 bytes).")

        return run.info.run_id

def run(year, month):
    df_train = read_dataframe(year=year, month=month)

    next_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1
    df_val = read_dataframe(year=next_year, month=next_month)

    X_train, dv = create_X(df_train)
    X_val, _ = create_X(df_val, dv)

    target = 'duration'
    y_train = df_train[target].values
    y_val = df_val[target].values

    # Use linear regression for homework Q5/Q6
    run_id = train_linear_regression(X_train, y_train, X_val, y_val, dv)
    print(f"MLflow run_id: {run_id}")
    return run_id


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Train a model to predict taxi trip duration.')
    parser.add_argument('--year', type=int, required=True, help='Year of the data to train on')
    parser.add_argument('--month', type=int, required=True, help='Month of the data to train on')
    args = parser.parse_args()

    run_id = run(year=args.year, month=args.month)

    with open("run_id.txt", "w") as f:
        f.write(run_id)