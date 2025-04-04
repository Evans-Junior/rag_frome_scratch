from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Dict
import numpy as np
from scipy.spatial.distance import cosine
import json

app = FastAPI()

# ======================
# CORS Configuration
# ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-flutter-web-app.com",  # Replace with your actual domain
        "http://localhost",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["X-API-KEY", "Content-Type"],
)

# ======================
# API Key Authentication
# ======================
API_KEY = "your-secret-api-key"  # Store in environment variables in production!
API_KEY_NAME = "X-API-KEY"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# ======================
# Data Models
# ======================
class SensorData(BaseModel):
    sensor_1: float
    sensor_2: float
    sensor_3: float
    sensor_4: float
    sensor_5: float
    sensor_6: float
    sensor_7: float
    sensor_8: float
    label: str

class QueryData(BaseModel):
    sensor_data: Dict[str, float]

# ======================
# Database Setup
# ======================
DATABASE_PATH = "fixed_dataset.json"
database = []

def load_database():
    global database
    try:
        with open(DATABASE_PATH, "r") as f:
            database = [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Warning: {DATABASE_PATH} not found, starting with empty database")
        database = []

def save_to_database(entry: Dict):
    with open(DATABASE_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

# Load data at startup
load_database()

# ======================
# Helper Functions
# ======================
def compute_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute 1 - cosine distance (higher = more similar)"""
    return 1 - cosine(vec1, vec2)

# ======================
# API Endpoints
# ======================
@app.post("/add_data/")
async def add_data(data: SensorData, api_key: str = Depends(get_api_key)):
    """Add new sensor data to the database."""
    new_entry = data.dict()
    database.append(new_entry)
    save_to_database(new_entry)
    return {"status": "success", "id": len(database) - 1}

@app.post("/query_similar/")
async def query_similar(
    query: QueryData,
    api_key: str = Depends(get_api_key)  # API key required
):
    """Find top 5 similar entries in the database."""
    if not database:
        raise HTTPException(status_code=404, detail="Database is empty")

    query_vec = list(query.sensor_data.values())
    similarities = []

    for entry in database:
        entry_vec = [v for k, v in entry.items() if k.startswith("sensor_")]
        sim = compute_cosine_similarity(query_vec, entry_vec)
        similarities.append((entry, sim))

    # Sort by similarity (descending) and get top 5
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_5 = similarities[:5]

    return {"results": [{"similarity": sim, "data": data} for data, sim in top_5]}