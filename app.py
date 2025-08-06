#!/usr/bin/env python3
"""
OptiBin AI Flask REST API with Intelligent Agent
Provides endpoints for bin data and intelligent route optimization (JSON only)
"""
import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from agent import RouteSelectionAgent # Import the new agent

app = Flask(__name__)
CORS(app)


# --- HELPER FUNCTION ---

def load_bins_data():
    """Loads bin data from the JSON file."""
    try:
        with open('bins.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: bins.json not found. Please run data_server.py first.")
        return []


# --- API ENDPOINTS ---

@app.route('/api/bins', methods=['GET'])
def get_all_bins():
    """Returns all bin data."""
    bins_data = load_bins_data()
    if not bins_data:
        return jsonify({"error": "Could not load bin data."}), 500
    return jsonify(bins_data)


@app.route('/api/agent/get-route', methods=['POST'])
def get_agent_route():
    """
    The main AI Agent endpoint.
    Selects the most critical bins and returns an optimized route.
    """
    try:
        data = request.get_json() or {}
        fill_threshold = data.get('fill_threshold', 75)
        max_bins_in_route = data.get('max_bins', 10)

        all_bins = load_bins_data()
        if not all_bins:
            return jsonify({"error": "Bin data is not available."}), 500

        # Initialize the agent and get the selected bins
        agent = RouteSelectionAgent(all_bins)
        selected_bins = agent.select_bins_to_service(
            threshold=fill_threshold,
            max_bins=max_bins_in_route
        )

        if not selected_bins:
            return jsonify({
                "message": "No bins meet the current criteria for a collection route.",
                "bins_serviced": [],
                "optimized_route_coords": [],
                "total_distance_km": 0
            }), 200

        # Get the optimized route for these selected bins
        route_info = agent.optimize_route_for_selected_bins(selected_bins)

        # Prepare the comprehensive response
        response = {
            "message": f"Optimized route for {len(selected_bins)} critical bins.",
            "bins_serviced": selected_bins,
            "optimized_route_coords": route_info["optimized_route_coords"],
            "total_distance_km": route_info["total_distance_km"]
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    if not os.path.exists('bins.json'):
        print("Warning: bins.json not found. Please run data_server.py first.")
    app.run(debug=True, port=5000)