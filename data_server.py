#!/usr/bin/env python3
"""
Simplified Data Generation Server for OptiBin AI

This server generates random bin locations for a landlocked city (Kansas City)
without needing complex geographic checks.
"""
import json
import random

def generate_landlocked_city_bins():
    """
    Generates 100 bin locations within a square area representing Kansas City, MO.
    """
    print("Generating 100 bin locations for Kansas City, MO...")

    # --- Define the new location: Kansas City, MO ---
    # Base coordinates (approximate center of the city)
    base_lat = 39.0997
    base_lng = -94.5786

    # Define a simple bounding box (e.g., +/- 0.1 degrees, approx. 14x11 miles)
    # This creates a rectangular service area without any large bodies of water.
    lat_range = 0.1
    lng_range = 0.15 # Make it a bit wider than it is tall for a more realistic shape

    min_lat = base_lat - lat_range
    max_lat = base_lat + lat_range
    min_lng = base_lng - lng_range
    max_lng = base_lng + lng_range

    bins = []
    # Since we are no longer rejecting points, a simple for loop is cleaner.
    for i in range(1, 101):
        # Generate a random point within the defined bounding box
        lat = random.uniform(min_lat, max_lat)
        lng = random.uniform(min_lng, max_lng)

        fill_level = random.randint(0, 100)
        bins.append({
            "id": i,
            "location": {"lat": lat, "lng": lng},
            "fill_level": fill_level
        })
        if i % 10 == 0:
            print(f"  -> Generated {i} bins...")

    # Save the valid bins to a file
    with open('bins.json', 'w') as f:
        json.dump(bins, f, indent=2)

    print("\nSuccessfully generated and saved 100 bins for Kansas City to bins.json.")
    print("You can now start the main Flask server.")

if __name__ == '__main__':
    generate_landlocked_city_bins()