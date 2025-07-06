

## Disclaimer (2025)

**Note:** In 2025, there is no requirement to use Mage for this homework. I have used Airflow instead of Mage to build the orchestration pipeline. The following instructions and questions have been adapted to reflect the use of Airflow. Please disregard any references to Mage, Docker Compose, or Mage-specific code blocks. All orchestration, scheduling, and pipeline logic is implemented using Airflow DAGs and Python scripts.

---

---

## Homework (Airflow Version)

The goal of this homework is to create a simple ML pipeline, use MLflow to track experiments, and register the best model, using Airflow for orchestration.

We'll use [the same NYC taxi dataset](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page), the **Yellow** taxi data for March, 2023.

## Question 1. Run Airflow

First, set up and run Airflow. You can use a local installation with pip.

What version of Airflow are you running? (You can check with `airflow version`.)



## Question 2. Creating a DAG

Create a new Airflow DAG for this homework (e.g., `airflow/dags/duration-prediction-dag.py`).

How many tasks are defined in your DAG (including data ingestion, preparation, training, and model registration)?


## Question 3. Data Ingestion Task

Create a data ingestion task in your Airflow DAG. In this task, read the March 2023 Yellow taxi trips data.

How many records did you load?

- 3,003,766
- 3,203,766
- **3,403,766**
- 3,603,766

## Question 4. Data Preparation Task

Use the same logic for preparing the data as in previous homeworks. Implement this as a separate task in your Airflow DAG.

This is what we used (adjusted for yellow dataset):

```python
def read_dataframe(filename):
    df = pd.read_parquet(filename)

    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    

    return df
```

Apply this function to the data loaded in the ingestion task. What is the size of the resulting DataFrame?

- 2,903,766
- 3,103,766
- **3,316,216**
- 3,503,766

## Question 5. Train a Model Task

Train a linear regression model using the same code as in homework 1. Implement this as a separate task in your Airflow DAG.

- Fit a dict vectorizer.
- Train a linear regression with default parameters.
- Use pick up and drop off locations separately, don't create a combination feature.

What is the intercept of the model? (Print the `intercept_` field in your code.)

- 21.77
- 24.77
- **27.77**
- 31.77

## Question 6. Register the Model Task


After training, save the model with MLflow. Implement this as a separate task in your Airflow DAG.

- Log the model (linear regression)
- Save and log the artifact (dict vectorizer)

Find the logged model, and check the MLModel file. What is the size of the model? (`model_size_bytes` field):

- 14,534
- 9,534
- **4,534**
- 1,534



## Submit the results

- Submit your results here: https://courses.datatalks.club/mlops-zoomcamp-2024/homework/hw3
- If your answer doesn't match options exactly, select the closest one.






