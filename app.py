#!/usr/bin/env python3
"""
OptiBin AI Flask REST API with Intelligent Agent
Provides endpoints for bin data and dynamic, stateful route optimization.
"""
import json
import os
import random  # Import the random library for dynamic updates
from flask import Flask, jsonify, request
from flask_cors import CORS
from agent import RouteSelectionAgent

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
    """Returns the current state of all bin data."""
    bins_data = load_bins_data()
    if not bins_data:
        return jsonify({"error": "Could not load bin data."}), 500
    return jsonify(bins_data)


@app.route('/api/agent/get-route', methods=['POST'])
def get_agent_route():
    """
    The main AI Agent endpoint.
    Selects critical bins, returns an optimized route, and then updates
    the state of all bins for the next cycle.
    """
    try:
        data = request.get_json() or {}
        fill_threshold = data.get('fill_threshold', 75)
        max_bins_in_route = data.get('max_bins', 10)

        current_bins = load_bins_data()
        if not current_bins:
            return jsonify({"error": "Bin data is not available."}), 500

        # 1. AGENT MAKES DECISION BASED ON CURRENT STATE
        agent = RouteSelectionAgent(current_bins)
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

        route_info = agent.optimize_route_for_selected_bins(selected_bins)

        # 2. SIMULATE THE NEXT STATE OF THE WORLD AFTER THE ROUTE IS COMPLETED
        # Get a list of IDs for the bins that were just serviced
        serviced_bin_ids = {b['id'] for b in selected_bins}

        next_state_bins = []
        for bin_data in current_bins:
            if bin_data['id'] in serviced_bin_ids:
                # This bin was emptied, reset its fill level to a low value
                bin_data['fill_level'] = random.randint(0, 10)
            else:
                # This bin was not serviced, so its fill level increases
                increase = random.randint(5, 15)
                bin_data['fill_level'] = min(100, bin_data['fill_level'] + increase)

            next_state_bins.append(bin_data)

        # 3. PERSIST THE NEW STATE by overwriting the JSON file
        with open('bins.json', 'w') as f:
            json.dump(next_state_bins, f, indent=2)

        # 4. PREPARE AND RETURN THE RESPONSE about the action just taken
        response = {
            "message": f"Optimized route for {len(selected_bins)} critical bins. Bin levels have been updated for the next cycle.",
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