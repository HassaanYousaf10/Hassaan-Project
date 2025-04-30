from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import os

app = FastAPI(
    title="Predictive Maintenance API",
    description="Serves processed data for ML model input",
    version="1.0"
)

# Load the data once when the app starts
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/part-00000-a1b35fb2-29b8-45a7-a838-038fe9c5198c-c000.snappy    .parquet")
try:
    df = pd.read_parquet(DATA_PATH)
except Exception as e:
    df = None
    print(f"❌ Failed to load dataset: {e}")

@app.get("/")
def root():
    return {"status": "API is up. Check /docs for Swagger UI."}

@app.get("/predict-ready-data")
def get_data(n: int = 5):
    """
    Returns the top N rows of cleaned data from silver layer.
    """
    if df is None:
        return JSONResponse(status_code=500, content={"error": "Data not loaded."})
    return df.head(n).to_dict(orient="records")
