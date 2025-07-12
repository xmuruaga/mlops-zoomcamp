
# This script was converted from a Jupyter notebook (duration-prediction.ipynb) to a Python script.
# jupyter nbconvert --to=script duration-prediction.ipynb

# Key changes made during conversion:
# 1. Removed notebook cell structure and markdown explanations; only code is retained.
# 2. Added a main guard (`if __name__ == "__main__":`) to allow command-line execution.
# 3. Introduced argparse to accept year and month as command-line arguments instead of hardcoding or using notebook cells.
# 4. Removed any interactive display or plotting code specific to notebooks.
# 5. Added code to write the MLflow run_id to a file (run_id.txt) for automation.
# 6. Consolidated all imports at the top of the script.
# 7. Organized code into functions for modularity and reusability.
# 8. Ensured the script is self-contained and can be run independently from the command line.

# Execute it: python duration-prediction.py --year=2023 --month=03

#!/usr/bin/env python
# coding: utf-8

import pickle
from pathlib import Path
import pandas as pd
import xgboost as xgb
import mlflow

from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor


mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("nyc-taxi-experiment")

models_folder = Path('models')
models_folder.mkdir(exist_ok=True)



def read_dataframe(year, month):
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet'
    df = pd.read_parquet(url)

    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)

    df = df[(df.duration >= 1) & (df.duration <= 60)]

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




def train_model(X_train, y_train, X_val, y_val, dv, dicts_train, dicts_val):
    with mlflow.start_run() as run:
        # Build pipeline
        pipe = Pipeline([
            ("dv", DictVectorizer(sparse=True)),
            ("xgb", XGBRegressor(
                n_estimators=30,
                learning_rate=0.09585355369315604,
                max_depth=30,
                min_child_weight=1.060597050922164,
                reg_alpha=0.018060244040060163,
                reg_lambda=0.011658731377413597,
                objective="reg:squarederror",
                seed=42,
                n_jobs=-1
            ))
        ])

        # Fit pipeline on raw dicts
        pipe.fit(dicts_train, y_train)
        y_pred = pipe.predict(dicts_val)
        rmse = root_mean_squared_error(y_val, y_pred)
        mlflow.log_metric("rmse", rmse)

        mlflow.sklearn.log_model(
            sk_model=pipe,
            artifact_path="model"
        )

        return run.info.run_id



def run(year, month):
    df_train = read_dataframe(year=year, month=month)
    next_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1
    df_val = read_dataframe(year=next_year, month=next_month)

    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts_train = df_train[categorical + numerical].to_dict(orient='records')
    dicts_val = df_val[categorical + numerical].to_dict(orient='records')

    target = 'duration'
    y_train = df_train[target].values
    y_val = df_val[target].values

    # dv is not needed anymore, but kept for compatibility
    X_train, dv = create_X(df_train)
    X_val, _ = create_X(df_val, dv)

    run_id = train_model(X_train, y_train, X_val, y_val, dv, dicts_train, dicts_val)
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