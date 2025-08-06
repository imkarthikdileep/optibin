#!/usr/bin/env python3
"""
Intelligent Route Selection Agent for OptiBin AI

This agent determines the most critical bins to service based on their
fill-level and proximity, then generates an optimized route.
"""
import json
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from python_tsp.heuristics import solve_tsp_simulated_annealing
import math

class RouteSelectionAgent:
    """
    An AI agent that selects bins and optimizes the collection route.
    """

    def __init__(self, bins_data):
        """
        Initializes the agent with the current bin data.

        Args:
            bins_data (list): A list of bin dictionaries.
        """
        self.bins_data = bins_data

    def select_bins_to_service(self, threshold=75, max_bins=10):
        """
        Selects the most critical bins to service.

        Args:
            threshold (int): The fill level percentage to consider a bin "full".
            max_bins (int): The maximum number of bins to include in a route.

        Returns:
            list: A list of bin dictionaries that need servicing.
        """
        # Prioritize bins with the highest fill levels
        priority_bins = sorted(
            [b for b in self.bins_data if b['fill_level'] >= threshold],
            key=lambda x: x['fill_level'],
            reverse=True
        )

        # If more bins are over the threshold than our truck can handle,
        # we take the fullest ones.
        return priority_bins[:max_bins]

    def haversine_distance(self, lat1, lng1, lat2, lng2):
        """
        Calculates the Haversine distance between two points on Earth.
        """
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        dlat, dlng = lat2 - lat1, lng2 - lng1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return c * 6371  # Earth radius in kilometers

    def create_distance_matrix(self, coordinates):
        """
        Creates a distance matrix for the given coordinates.
        """
        n = len(coordinates)
        matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    p1, p2 = coordinates[i], coordinates[j]
                    matrix[i][j] = self.haversine_distance(p1['lat'], p1['lng'], p2['lat'], p2['lng'])
        return matrix

    def optimize_route_for_selected_bins(self, bins_to_service):
        """
        Generates an optimized route for the selected bins.

        Args:
            bins_to_service (list): A list of bins to be serviced.

        Returns:
            dict: A dictionary containing the optimized route and total distance.
        """
        if not bins_to_service:
            return {"optimized_route_coords": [], "total_distance_km": 0}

        # The depot is calculated as the geographic center of the selected bins
        avg_lat = np.mean([b['location']['lat'] for b in bins_to_service])
        avg_lng = np.mean([b['location']['lng'] for b in bins_to_service])
        depot_location = {'lat': avg_lat, 'lng': avg_lng, 'id': 'depot'}

        coordinates = [depot_location] + [b['location'] for b in bins_to_service]
        distance_matrix = self.create_distance_matrix(coordinates)

        # Using the Traveling Salesperson Problem solver
        permutation, distance = solve_tsp_simulated_annealing(distance_matrix)

        ordered_coords = [coordinates[i] for i in permutation]
        start_index = ordered_coords.index(depot_location)
        final_ordered_coords = ordered_coords[start_index:] + ordered_coords[:start_index]
        final_ordered_coords.append(depot_location)

        return {
            "optimized_route_coords": final_ordered_coords,
            "total_distance_km": round(distance, 2)
        }