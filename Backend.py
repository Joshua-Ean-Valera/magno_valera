from flask import Flask, render_template, jsonify, request
from math import radians, cos, sin, sqrt, atan2
import heapq

app = Flask(__name__)

# Evacuation Centers Data
evacuation_centers = [
    {
        "name": "La Consolacion",
        "lat": 13.454018,
        "lng": 123.366992,
        "is_full": False,
        "safe_for": ["Flood", "Storm"]
    },
    {
        "name": "Rosary School Inc",
        "lat": 13.453114,
        "lng": 123.367909,
        "is_full": True,
        "safe_for": ["Earthquake", "Flood"]
    },
    {
        "name": "Baao Central School",
        "lat": 13.452945,
        "lng": 123.371970,
        "is_full": True,
        "safe_for": ["Storm"]
    },
    {
        "name": "Salvacion Elementary School",
        "lat": 13.460397,
        "lng": 123.373887,
        "is_full": False,
        "safe_for": ["Flood", "Earthquake", "Storm"]
    }
]

# Home Page Route
@app.route("/")
def home():
    return render_template("Home.html")

# Map Page Route
@app.route("/map")
def map_page():
    return render_template("Map.html")

# API to Return Evacuation Centers Data
@app.route("/get_evacuations", methods=["GET"])
def get_evacuations():
    return jsonify(evacuation_centers)

# Haversine Function to Calculate Distance
def calculate_distance(lat1, lng1, lat2, lng2):
    R = 6371  # Earth's radius in kilometers
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Dijkstra's Algorithm for Shortest Path
def find_closest_center(user_lat, user_lng, centers):
    graph = {}
    for idx, center in enumerate(centers):
        graph[idx] = []
        for jdx, neighbor in enumerate(centers):
            if idx != jdx:
                distance = calculate_distance(center["lat"], center["lng"], neighbor["lat"], neighbor["lng"])
                graph[idx].append((jdx, distance))
    
    # Priority queue and Dijkstra logic
    priority_queue = [(0, -1)]  # Distance, Center Index (-1 represents user location)
    distances = {i: float("inf") for i in range(len(centers))}
    distances[-1] = 0  # Distance to user location is 0
    
    while priority_queue:
        current_dist, current_node = heapq.heappop(priority_queue)
        if current_dist > distances[current_node]:
            continue
        
        neighbors = graph[current_node] if current_node != -1 else [(i, calculate_distance(user_lat, user_lng, centers[i]["lat"], centers[i]["lng"])) for i in range(len(centers))]
        
        for neighbor_idx, weight in neighbors:
            distance = current_dist + weight
            if distance < distances[neighbor_idx]:
                distances[neighbor_idx] = distance
                heapq.heappush(priority_queue, (distance, neighbor_idx))
    
    closest_center_idx = min(range(len(centers)), key=lambda i: distances[i])
    return centers[closest_center_idx], round(distances[closest_center_idx], 2)

# API to Find the Closest Evacuation Center
@app.route("/closest_center", methods=["POST"])
def closest_center():
    data = request.json
    user_lat = data["lat"]
    user_lng = data["lng"]

    closest, min_distance = find_closest_center(user_lat, user_lng, evacuation_centers)
    return jsonify({"closest": closest, "distance": min_distance})

if __name__ == "__main__":
    app.run(debug=True)
