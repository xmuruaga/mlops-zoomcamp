# FastAPI MLflow Model Deployment

This project demonstrates how to serve a machine learning model tracked with MLflow using a FastAPI web service. The service loads a model from the MLflow tracking server and exposes a `/predict` endpoint for real-time predictions.

---

## What the Code Does
- **Model Training & Logging:**
  - The script `/workspaces/mlops-zoomcamp/03-orchestration/homework/duration-prediction.py` trains a model and logs (saves) it as an artifact to the MLflow tracking server. Each run creates a unique run ID.
- **Model Loading & Serving:**
  - The FastAPI service (`predict.py`) loads the model artifact from MLflow at startup, using the specified `RUN_ID` and `MLFLOW_TRACKING_URI`.
  - The `/predict` endpoint accepts a JSON payload and returns a prediction using the loaded model.
- **Testing:**
  - A test script (`test.py`) is provided to send a sample request to the API.

---

## Step-by-Step Usage

### 1. Start the MLflow Tracking Server
```bash
source .venv/bin/activate
cd 04-deployment/web-service-fastapi-mlflow/
mlflow server --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0
```
- The MLflow UI will be available at http://localhost:5000
- If port 5000 is in use, stop the process using:
  ```bash
  lsof -i :5000
  kill -9 <PID>
  ```



### 2. Train and Log Model Artifacts (if not already done)
In a new terminal, run this step to train the model in session 03 and save it to MLflow as a pipeline:
```bash
python /workspaces/mlops-zoomcamp/03-orchestration/homework/duration-prediction.py --year 2023 --month 03
```
- This creates a new MLflow run and logs the trained pipeline (DictVectorizer + XGBoost) as a single artifact under `model`.
- **Find the run ID** in the MLflow UI (http://localhost:5000) and update the `RUN_ID` variable in `predict.py` if needed.

> **Note:** The FastAPI service will load this pipeline artifact from MLflow at startup, using the run ID you specify. The service expects the artifact path to be `model`.

### 3. Install Dependencies
```bash
pip install fastapi uvicorn mlflow scikit-learn boto3
```

### 4. Start the FastAPI Service (Locally)
```bash
uvicorn predict:app --host 0.0.0.0 --port 9696
```
- The service will load the model from MLflow as soon as it starts.

### 5. Test the Service
```bash
python test.py
```
Or with curl:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"PULocationID": "130", "DOLocationID": "205", "trip_distance": 3.66}' \
  http://localhost:9696/predict
```

---

## Running with Docker

### 1. Build the Docker Image
```bash
docker build --no-cache -t duration-prediction-service .
```

### 2. Run the Docker Container
Update the RUN_ID

```bash
docker run -it --rm -p 9696:9696 \
  --add-host=host.docker.internal:host-gateway \
  -e RUN_ID="cc5fd8535d3e44ba98960760940efcac" \
  duration-prediction-service
```

### 3. Test the Service
Use the same test script or curl command as above.

---

## Notes
- The MLflow server must be running and accessible from the container or local environment.
- The `RUN_ID` in `predict.py` and in `docker run ...` determines which model artifact is loaded at service startup.
- The service uses FastAPI and loads the pipeline directly from MLflow at startup—no need to manually download the model artifact or handle feature transformation.
- Use the MLflow UI to inspect runs, artifacts, and to find the correct run ID.

---

**You're ready to deploy and test your ML prediction service!**