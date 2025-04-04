from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import numpy as np
from scipy.spatial.distance import cosine
from fastapi.middleware.cors import CORSMiddleware  # Add this import
import json
from pathlib import Path

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load existing data from JSON file
DATABASE_PATH = "balanced_dataset.json"
database = []

def load_database():
    global database
    try:
        with open("fixed_dataset.json", "r") as f:
            database = [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        print("Warning: fixed_dataset.json not found, starting with empty database")
        database = []

def save_to_database(entry: Dict):
    with open("fixed_dataset.json", "a") as f:
        f.write(json.dumps(entry) + "\n")

# Load data at startup
load_database()

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
    sensor_data: Dict[str, float]  # No label needed for queries

def compute_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute 1 - cosine distance (higher = more similar)"""
    return 1 - cosine(vec1, vec2)

@app.post("/add_data/")
async def add_data(data: SensorData):
    """Add new sensor data to the database."""
    new_entry = data.dict()
    database.append(new_entry)
    save_to_database(new_entry)
    return {"status": "success", "id": len(database) - 1}

@app.post("/query_similar/")
async def query_similar(query: QueryData):
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

    # Return results with similarity scores
    return {"results": [{"similarity": sim, "data": data} for data, sim in top_5]}