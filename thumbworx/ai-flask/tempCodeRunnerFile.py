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
