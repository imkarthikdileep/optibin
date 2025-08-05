<img width="804" height="274" alt="cropped" src="https://github.com/user-attachments/assets/bb105cab-9db8-4a6d-9e20-0e52d2e2e968" />

# OptiBin AI 

This is the core logic engine for the OptiBin AI project. It's a lightweight REST API built with Flask (Python) that serves bin data and performs the route optimization calculations.

## Core Technologies

-   **Framework:** [Flask](https://flask.palletsprojects.com/)
-   **Optimization Library:** [Python-TSP](https://pypi.org/project/python-tsp/) (using a Simulated Annealing heuristic)
-   **Geographic Library:** [Shapely](https://pypi.org/project/Shapely/) (for ensuring generated data is on land)
-   **Numerical Operations:** [NumPy](https://numpy.org/)

## Project Structure

```
backend/
├── app.py             # Main Flask application with API endpoint logic.
├── data_server.py     # Utility script to generate realistic, land-based dummy data.
├── bins.json          # The generated data file acting as our simple database.
└── requirements.txt   # List of Python dependencies.
```

## Key Concepts & Logic Flow

1.  **Geographically-Aware Data Generation:** The `data_server.py` script is more than a simple random number generator. It uses a `Polygon` from the **Shapely** library that defines the landmass of San Francisco. When generating dummy data, it creates points within a bounding box and then checks if each point is `within` the polygon, discarding any points that fall into the water. This ensures the data is realistic and usable.

2.  **Dynamic Depot Calculation:** The `/api/optimize-route` endpoint does not require a fixed depot location. It dynamically calculates the geometric center (mean latitude and longitude) of all the bins that require service and uses that point as the starting and ending depot for the route. This makes the system robust and adaptable to any cluster of full bins.

3.  **Route Optimization (TSP):** The core "AI" of the project. When a request is received, the backend:
    *   Creates a distance matrix for all points (depot + bins) using the **Haversine formula** to accurately calculate distances on a sphere.
    *   Feeds this matrix into the `solve_tsp_simulated_annealing` function from the `python-tsp` library. This is a powerful heuristic that finds a near-optimal solution to the Traveling Salesperson Problem very quickly.
    *   Returns the ordered list of coordinates and the total route distance.

## API Contract

The API exposes two endpoints:

### 1. Get All Bins

-   **Endpoint:** `GET /api/bins`
-   **Description:** Fetches the complete list of all 100 bins from `bins.json`.
-   **Success Response (200 OK):**
    ```json
    [
      {
        "id": 1,
        "location": {"lat": 37.7749, "lng": -122.4194},
        "fill_level": 85
      },
      ...
    ]
    ```

### 2. Optimize Collection Route

-   **Endpoint:** `POST /api/optimize-route`
-   **Description:** Calculates the most efficient route to service a given list of bins.
-   **Request Body:**
    ```json
    {
      "bins_to_service": [
        {"id": "BIN1", "location": {"lat": 37.77, "lng": -122.42}, ...},
        {"id": "BIN25", "location": {"lat": 37.75, "lng": -122.44}, ...}
      ]
    }
    ```
-   **Success Response (200 OK):**
    ```json
    {
      "optimized_route_coords": [
        {"lat": 37.76, "lng": -122.43}, // Depot start
        {"lat": 37.77, "lng": -122.42}, // First bin
        {"lat": 37.75, "lng": -122.44}, // Second bin
        ...,
        {"lat": 37.76, "lng": -122.43}  // Depot end
      ],
      "total_distance_km": 51.81
    }
    ```
-   **Error Response (400 Bad Request):** Occurs if `bins_to_service` array is empty.

## Setup and Running

1.  **Create Virtual Environment:**
    Navigate to the `backend` directory and run:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Generate Data (Run Once):**
    Before starting the server for the first time, you must generate the data file.
    ```bash
    python data_server.py
    ```

4.  **Run the Flask Server:**
    ```bash
    flask --app app run
    ```
    The API will be available at `http://localhost:5000`.
