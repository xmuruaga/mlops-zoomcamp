import os
import mlflow
from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from fastapi.responses import JSONResponse
from typing import Union

# --- CONFIGURATION ---
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
RUN_ID = os.getenv("RUN_ID", "cc5fd8535d3e44ba98960760940efcac") # Default to your latest run

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# --- MODEL LOADING ---
logged_model = f'runs:/{RUN_ID}/model'

print(f"[INFO] Loading model from MLflow: {logged_model}")
print(f"[INFO] Tracking URI: {MLFLOW_TRACKING_URI}")

try:
    model = mlflow.pyfunc.load_model(logged_model)
    print("[INFO] Model loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load model for RUN_ID={RUN_ID} from MLflow at {MLFLOW_TRACKING_URI}.")
    print(f"[ERROR] Exception: {e}")
    raise RuntimeError(f"Failed to load model for RUN_ID={RUN_ID} from MLflow at {MLFLOW_TRACKING_URI}: {e}")

# --- API DEFINITION ---
app = FastAPI()

class RideRequest(BaseModel):
    PULocationID: Union[str, int]
    DOLocationID: Union[str, int]
    trip_distance: float

    @field_validator('PULocationID', 'DOLocationID', mode='before')
    @classmethod
    def convert_to_str(cls, v):
        return str(v)

def prepare_features(ride: RideRequest):
    return {
        'PU_DO': f"{ride.PULocationID}_{ride.DOLocationID}",
        'trip_distance': ride.trip_distance,
    }

@app.post("/predict")
def predict_endpoint(ride: RideRequest):
    features = prepare_features(ride)
    preds = model.predict([features])
    return {
        'duration': float(preds[0]),
        'model_version': RUN_ID
    }
