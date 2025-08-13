import os, json
from flask import Flask, jsonify, request
import requests
import redis
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String, DateTime
from datetime import datetime
from geopy.distance import geodesic

app = Flask(__name__)

TRACCAR_BASE = os.getenv("TRACCAR_BASE_URL")
TRACCAR_USER = os.getenv("TRACCAR_USER")
TRACCAR_PASS = os.getenv("TRACCAR_PASS")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DB_URL = f"postgresql://postgres:4738@localhost:5432/thumbworx"


r = redis.from_url(REDIS_URL)
engine = create_engine(DB_URL)
metadata = MetaData()
positions = Table('positions', metadata,
    Column('id', Integer, primary_key=True),
    Column('device_id', Integer),
    Column('latitude', Float),
    Column('longitude', Float),
    Column('speed', Float),
    Column('timestamp', DateTime),
    Column('attributes', String),
)
metadata.create_all(engine)

def traccar_auth():
    return (TRACCAR_USER, TRACCAR_PASS)

@app.route("/api/traccar/devices")
def devices():
    res = requests.get(f"{TRACCAR_BASE}/api/devices", auth=traccar_auth())
    return jsonify(res.json())

@app.route("/api/traccar/positions")
def positions_api():
    res = requests.get(f"{TRACCAR_BASE}/api/positions", auth=traccar_auth())
    items = res.json()
    r.set("latest_positions", json.dumps(items), ex=30)
    return jsonify(items)

@app.route("/api/predict_eta", methods=["POST"])
def predict_eta():
    payload = request.json
    a = (payload['current_lat'], payload['current_lng'])
    b = (payload['dropoff_lat'], payload['dropoff_lng'])
    km = geodesic(a, b).km
    return jsonify({"eta_minutes": round(km * 3, 2)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
