#!/usr/bin/env python3
"""
Smarter Data Generation Server for OptiBin AI

This server generates random bin locations that are guaranteed to be
on the landmass of San Francisco, not in the ocean.
"""
import json
import random
from shapely.geometry import Point, Polygon

def generate_land_based_bins():
    """
    Generates 100 bin locations within the land area of San Francisco.
    """
    print("Generating 100 geographically accurate bin locations...")

    # A GeoJSON-like polygon defining the landmass of San Francisco.
    # This prevents bins from being generated in the water.
    sf_polygon = Polygon([
        [-122.45, 37.81], [-122.40, 37.81], [-122.39, 37.78],
        [-122.38, 37.74], [-122.40, 37.70], [-122.43, 37.70],
        [-122.48, 37.71], [-122.51, 37.74], [-122.52, 37.78],
        [-122.49, 37.80], [-122.45, 37.81]
    ])

    # A simple bounding box to generate initial random points.
    min_lng, min_lat, max_lng, max_lat = sf_polygon.bounds

    bins = []
    count = 0
    while count < 100:
        # Generate a random point within the bounding box
        lng = random.uniform(min_lng, max_lng)
        lat = random.uniform(min_lat, max_lat)
        point = Point(lng, lat)

        # THE CRITICAL CHECK: Is the point inside the San Francisco polygon?
        if sf_polygon.contains(point):
            count += 1
            fill_level = random.randint(0, 100)
            bins.append({
                "id": count,
                "location": {"lat": lat, "lng": lng},
                "fill_level": fill_level
            })
            print(f"  -> Generated bin #{count} on land.")

    # Save the valid bins to a file
    with open('bins.json', 'w') as f:
        json.dump(bins, f, indent=2)

    print("\nSuccessfully generated and saved 100 land-based bins to bins.json.")
    print("You can now start the main Flask server (`flask --app app run`).")

if __name__ == '__main__':
    generate_land_based_bins()