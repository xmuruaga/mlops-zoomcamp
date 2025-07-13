

# Batch Inference Homework Instructions

This guide explains how to set up, run, and test the batch inference pipeline for the NYC Yellow Taxi trip duration model, following the homework steps.

---

## 1. Run the Notebook (Q1)

Start with the provided notebook (`starter.ipynb`). Run it for March 2023 data:

- What is the standard deviation of the predicted duration?

np.float64(6.247488852238704)


## 2. Prepare the Output (Q2)

Update your code to create a DataFrame with `ride_id` and predictions, then save it as a parquet file using the following snippet:

```python
df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
df_result = pd.DataFrame()
df_result['ride_id'] = df['ride_id']
df_result['predicted_duration'] = y_pred
df_result.to_parquet(
    output_file,
    engine='pyarrow',
    compression=None,
    index=False
)
```

- What is the size of the output file?

total 66M

## 3. Create the Scoring Script (Q3)

Convert the notebook to a script:

```bash
jupyter nbconvert --to script starter.ipynb
```

---

## 4. Set Up the Virtual Environment (Q4)

Install all required libraries in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- What is the first hash for the Scikit-Learn dependency in `Pipfile.lock`? (If using pipenv)

We are not using Pipfile, as we are using venv and requirements.txt.

## 5. Parametrize the Script (Q5)

Make the script configurable via CLI arguments for year and month:

```bash
cd 04-deployment/homework
python batch.py 2023 4
```

- What is the mean predicted duration for April 2023?

predicted mean duration: 14.292282936862437

## 6. Dockerize the Script (Q6)

Build and run the script in a Docker container:

```bash
docker build -t batch-inference .
docker run --rm -v $(pwd)/output:/app/output batch-inference 2023 5
```

- This will save the output file in your local `output/` directory.

- What is the mean predicted duration for May 2023?
predicted mean duration: 14.242595513316317






