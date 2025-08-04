import folium
from folium.plugins import TimestampedGeoJson
import requests
import polyline
from datetime import datetime, timedelta
import time
import json

# List of coordinates (latitude, longitude)
coordinates = [
    (-21.71425604282143, -43.40818129073404),
    (-21.714714548171766, -43.40778432378551),
    (-21.71697724990115, -43.408590499730664),
    (-21.720279521514225, -43.41024149647037),
    (-21.720145420590548, -43.40841908476862),
    (-21.718921743886302, -43.40726428923483),
    (-21.718720590555066, -43.406073406340624),
    (-21.719036688643843, -43.41020128503543),
    (-21.717417010782437, -43.40704164270194)
]

# Sequence of points (indices of coordinates)
sequence = [(0, 8), (8, 6), (6, 5), (5, 4), (4, 3), (3, 7), (7, 2), (2, 1), (1, 0)]

# OSRM public API URL
OSRM_URL = "http://router.project-osrm.org/route/v1/driving/"

# Function to calculate distance and get polyline using OSRM API
def osrm_route(lon1, lat1, lon2, lat2):
    url = f"{OSRM_URL}{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=polyline"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["code"] != "Ok":
            print(f"Error in OSRM response for ({lat1}, {lon1}) to ({lat2}, {lon2}): {data['message']}")
            return None, None
        distance = data["routes"][0]["distance"]  # Distance in meters
        route_polyline = data["routes"][0]["geometry"]  # Encoded polyline
        return distance, route_polyline
    except requests.exceptions.RequestException as e:
        print(f"Error fetching route for ({lat1}, {lon1}) to ({lat2}, {lon2}): {e}")
        return None, None

# Calculate distances and polylines for each segment
distances = []
polylines = []
for start_idx, end_idx in sequence:
    lat1, lon1 = coordinates[start_idx]
    lat2, lon2 = coordinates[end_idx]
    distance, route_polyline = osrm_route(lon1, lat1, lon2, lat2)
    if distance is None or route_polyline is None:
        print(f"Failed to calculate route for segment {start_idx} to {end_idx}. Exiting.")
        exit(1)
    distances.append(distance)
    polylines.append(route_polyline)
    time.sleep(1)  # Respect OSRM public API rate limit (1 request per second)

total_distance = sum(distances)  # Total cycle distance in meters
cycle_time = 20 * 60  # 20 minutes in seconds
num_segments = len(sequence)

# Calculate time per segment (assuming equal time distribution)
time_per_segment = cycle_time / num_segments  # seconds
speeds = [distance / time_per_segment * 3.6 for distance in distances]  # Convert m/s to km/h

# Print distances and speeds
print(f"Total cycle distance: {total_distance:.2f} meters")
print("Distances and speeds per segment:")
for i, (dist, speed) in enumerate(zip(distances, speeds)):
    print(f"Segment {sequence[i]}: Distance = {dist:.2f} m, Speed = {speed:.2f} km/h")

# Simulation parameters
start_time = datetime(2025, 8, 3, 5, 0)  # 5:00 AM
end_time = datetime(2025, 8, 3, 23, 0)  # 11:00 PM
cycle_duration = timedelta(minutes=20)

# Generate GeoJSON features
features = []
current_time = start_time
while current_time <= end_time:
    for i, (start_idx, end_idx) in enumerate(sequence):
        # Add point feature for start of segment
        lat, lon = coordinates[start_idx]
        point_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
            "properties": {
                "time": current_time.isoformat(),
                "popup": f"Vehicle at point {start_idx}, Speed: {speeds[i]:.2f} km/h",
                "icon": "circle",
                "iconstyle": {
                    "fillColor": "blue",
                    "fillOpacity": 0.8,
                    "stroke": "true",
                    "radius": 5
                }
            }
        }
        features.append(point_feature)
        
        # Add polyline feature for the route
        decoded_polyline = polyline.decode(polylines[i])  # Decode OSRM polyline
        polyline_feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[lon, lat] for lat, lon in decoded_polyline],
            },
            "properties": {
                "time": current_time.isoformat(),
                "popup": f"Route from {start_idx} to {end_idx}, Distance: {distances[i]:.2f} m",
                "style": {
                    "color": "red",
                    "weight": 4,
                    "opacity": 0.6
                }
            }
        }
        features.append(polyline_feature)
        
        current_time += timedelta(seconds=time_per_segment)
    
    if current_time > end_time:
        break
    # Add point feature for the start of the next cycle (index 0)
    lat, lon = coordinates[0]
    point_feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat],
        },
        "properties": {
            "time": current_time.isoformat(),
            "popup": f"Vehicle at point 0, Starting new cycle",
            "icon": "circle",
            "iconstyle": {
                "fillColor": "blue",
                "fillOpacity": 0.8,
                "stroke": "true",
                "radius": 5
            }
        }
    }
    features.append(point_feature)

# Create Folium map
center_lat = sum(lat for lat, _ in coordinates) / len(coordinates)
center_lon = sum(lon for _, lon in coordinates) / len(coordinates)
m = folium.Map(location=[center_lat, center_lon], zoom_start=15)

# Add animation
TimestampedGeoJson({
    "type": "FeatureCollection",
    "features": features,
}, period="PT10S", add_last_point=True, transition_time=200).add_to(m)

# Save map
m.save("vehicle_simulation_map_osrm.html")