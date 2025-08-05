#!/usr/bin/env python3
"""
OptiBin AI Flask REST API
Provides endpoints for bin data and route optimization (JSON only)
"""

import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import math
from python_tsp.heuristics import solve_tsp_simulated_annealing
import numpy as np

app = Flask(__name__)
CORS(app)


# --- HELPER FUNCTIONS (UNCHANGED) ---

def load_bins_data():
    try:
        with open('bins.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "bins.json file not found."}


def haversine_distance(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat, dlng = lat2 - lat1, lng2 - lng1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return c * 6371


def create_distance_matrix(coordinates):
    n = len(coordinates)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                p1, p2 = coordinates[i], coordinates[j]
                matrix[i][j] = haversine_distance(p1['lat'], p1['lng'], p2['lat'], p2['lng'])
    return matrix


# --- API ENDPOINTS ---

@app.route('/api/bins', methods=['GET'])
def get_all_bins():
    bins_data = load_bins_data()
    if "error" in bins_data:
        return jsonify(bins_data), 500
    return jsonify(bins_data)


@app.route('/api/optimize-route', methods=['POST'])
def optimize_route():
    try:
        data = request.get_json()
        bins_to_service = data.get('bins_to_service', [])
        if not bins_to_service:
            return jsonify({"error": "bins_to_service list cannot be empty"}), 400

        avg_lat = np.mean([b['location']['lat'] for b in bins_to_service])
        avg_lng = np.mean([b['location']['lng'] for b in bins_to_service])
        depot_location = {'lat': avg_lat, 'lng': avg_lng}

        coordinates = [depot_location] + [b['location'] for b in bins_to_service]
        distance_matrix = create_distance_matrix(coordinates)
        permutation, distance = solve_tsp_simulated_annealing(distance_matrix)

        ordered_coords = [coordinates[i] for i in permutation]
        start_index = ordered_coords.index(depot_location)
        final_ordered_coords = ordered_coords[start_index:] + ordered_coords[:start_index]
        final_ordered_coords.append(depot_location)

        # --- SIMPLIFIED RESPONSE: NO MORE IMAGE URL ---
        response = {
            "optimized_route_coords": final_ordered_coords,
            "total_distance_km": round(distance, 2)
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    if not os.path.exists('bins.json'):
        print("Warning: bins.json not found. Please run data_server.py first.")
    app.run(debug=True, port=5000)