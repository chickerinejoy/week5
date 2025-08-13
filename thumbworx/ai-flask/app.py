import os, json, math
from flask import Flask, jsonify, request
import requests
import redis
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String, DateTime
from datetime import datetime
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Environment configs
TRACCAR_BASE = os.getenv("TRACCAR_BASE_URL")
TRACCAR_USER = os.getenv("TRACCAR_USER")
TRACCAR_PASS = os.getenv("TRACCAR_PASS")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DB_URL = f"postgresql://postgres:4738@localhost:5432/thumbworx"

# Redis + Database setup
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

# Geocoding setup
geolocator = Nominatim(user_agent="eco_route_app")

def traccar_auth():
    return (TRACCAR_USER, TRACCAR_PASS)

def geocode_address(address):
    """Convert address to latitude and longitude"""
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula"""
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# =====================
# Traccar endpoints
# =====================
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

# =====================
# Lat/Lng ETA calculation
# =====================
@app.route("/api/predict_eta", methods=["POST"])
def predict_eta():
    payload = request.json
    a = (payload['current_lat'], payload['current_lng'])
    b = (payload['dropoff_lat'], payload['dropoff_lng'])
    km = geodesic(a, b).km
    return jsonify({"eta_minutes": round(km * 3, 2)})

# =====================
# Address-based ETA calculation
# =====================
@app.route("/api/predict_eta_address", methods=["POST"])
def predict_eta_address():
    data = request.get_json()
    pickup_address = data.get('pickup_address')
    dropoff_address = data.get('dropoff_address')

    if not pickup_address or not dropoff_address:
        return jsonify({"error": "Both pickup_address and dropoff_address are required"}), 400

    pickup_lat, pickup_lon = geocode_address(pickup_address)
    dropoff_lat, dropoff_lon = geocode_address(dropoff_address)

    if pickup_lat is None or dropoff_lat is None:
        return jsonify({"error": "Unable to geocode one or both addresses"}), 400

    distance_km = calculate_distance(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
    eta_minutes = round(distance_km * 3, 2)

    return jsonify({
        "pickup": {"address": pickup_address, "lat": pickup_lat, "lon": pickup_lon},
        "dropoff": {"address": dropoff_address, "lat": dropoff_lat, "lon": dropoff_lon},
        "distance_km": round(distance_km, 2),
        "eta_minutes": eta_minutes
    })

# =====================
# Route submission & retrieval
# =====================
@app.route("/submit-route", methods=["POST"])
def submit_route():
    """Save a route to Redis"""
    data = request.get_json()
    origin = data.get("origin")
    destination = data.get("destination")

    if not origin or not destination:
        return jsonify({"error": "Both origin and destination are required"}), 400

    # Store routes as a list in Redis
    route_entry = {"origin": origin, "destination": destination, "time": datetime.utcnow().isoformat()}
    existing_routes = json.loads(r.get("latest_routes") or "[]")
    existing_routes.insert(0, route_entry)  # newest first
    existing_routes = existing_routes[:10]  # keep only last 10
    r.set("latest_routes", json.dumps(existing_routes))

    return jsonify({"status": "success", "route": route_entry})

@app.route("/latest-routes", methods=["GET"])
def latest_routes():
    """Get the last saved routes from Redis"""
    routes = json.loads(r.get("latest_routes") or "[]")
    return jsonify(routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
