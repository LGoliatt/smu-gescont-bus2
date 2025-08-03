import pandas as pd
import numpy as np
import os
import uuid
from datetime import datetime, timedelta

# === Dados de entrada ===
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

# === Parâmetros da rota ===
AGENCY_ID = "f3f3d69e-827e-4776-a70d-3f47c43285a0"
AGENCY_NAME = "Empresa de Ônibus Local"
AGENCY_URL = "http://exemplo.com"
AGENCY_TIMEZONE = "America/Sao_Paulo"

ROUTE_ID = "ROUTE_circular_01"  # Must start with ROUTE_ like in files
ROUTE_SHORT_NAME = "Linha Circular"
ROUTE_LONG_NAME = "Linha Circular - Bairro A"
ROUTE_TYPE = 3
ROUTE_URL = f"{AGENCY_URL}/tarifas"

SERVICE_ID = "service_1"
TRIP_ID_PREFIX = "TRIP_circular"
HEADSIGN = "Circular Completa"
DIRECTION_ID = 0

START_TIME = "06:00:00"
HEADWAY_MINUTES = 30
SECONDS_PER_SEGMENT = 60
WEEKDAYS = [1, 1, 1, 1, 1, 1, 1]  # Seg a Dom

# === Helper: UUID-style ID generator ===
def generate_uuid():
    return str(uuid.uuid4())

# === Passo 1: Encontrar a melhor rota circular (TSP com vizinho mais próximo) ===
def haversine_distance_matrix(coords):
    from sklearn.metrics import DistanceMetric
    coords_rad = np.radians(coords)
    dist = DistanceMetric.get_metric("haversine")
    distance_matrix_km = dist.pairwise(coords_rad) * 6371
    return distance_matrix_km

def solve_tsp_nn(coords):
    n = len(coords)
    unvisited = set(range(1, n))
    tour = [0]
    current = 0
    dist_matrix = haversine_distance_matrix(coords)
    while unvisited:
        nearest = min(unvisited, key=lambda x: dist_matrix[current][x])
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    return tour

tour_indices = solve_tsp_nn(coordinates)
ordered_coords = [coordinates[i] for i in tour_indices]

# === Output directory ===
output_dir = "gtfs_circular_route"
os.makedirs(output_dir, exist_ok=True)

# === 1. stops.txt (match structure from uploaded file) ===
stops_data = []
stop_ids = []

for i, (lat, lon) in enumerate(ordered_coords):
    stop_id = f"STOP_{generate_uuid()}"
    stop_name = f"Parada {i+1}"
    stops_data.append({
        "stop_id": stop_id,
        "stop_code": "",
        "stop_name": stop_name,
        "stop_desc": "",
        "stop_lat": lat,
        "stop_lon": lon,
        "zone_id": "",
        "stop_url": "",
        "location_type": 0,
        "parent_station": "",
        "stop_timezone": "",
        "wheelchair_boarding": 0
    })
    stop_ids.append(stop_id)

# Column order must match uploaded stops.txt
stops_df = pd.DataFrame(stops_data)[[
    "stop_id", "stop_code", "stop_name", "stop_desc", "stop_lat", "stop_lon",
    "zone_id", "stop_url", "location_type", "parent_station", "stop_timezone", "wheelchair_boarding"
]]
stops_df.to_csv(os.path.join(output_dir, "stops.txt"), index=False)

# === 2. agency.txt (use provided structure) ===
agency_df = pd.DataFrame([{
    "agency_id": AGENCY_ID,
    "agency_name": AGENCY_NAME,
    "agency_url": AGENCY_URL,
    "agency_timezone": AGENCY_TIMEZONE,
    "agency_lang": "pt",
    "agency_phone": "555-1234",
    "agency_fare_url": ROUTE_URL
}])
# Ensure column order
agency_df = agency_df[[
    "agency_id", "agency_name", "agency_url", "agency_timezone",
    "agency_lang", "agency_phone", "agency_fare_url"
]]
agency_df.to_csv(os.path.join(output_dir, "agency.txt"), index=False)

# === 3. routes.txt (match uploaded format) ===
routes_df = pd.DataFrame([{
    "agency_id": AGENCY_ID,
    "route_id": ROUTE_ID,
    "route_short_name": ROUTE_SHORT_NAME,
    "route_long_name": ROUTE_LONG_NAME,
    "route_desc": "",
    "route_type": ROUTE_TYPE,
    "route_url": ROUTE_URL,
    "route_color": "FF6600",
    "route_text_color": "FFFFFF"
}])
# Column order from uploaded file
routes_df = routes_df[[
    "agency_id", "route_id", "route_short_name", "route_long_name",
    "route_desc", "route_type", "route_url", "route_color", "route_text_color"
]]
routes_df.to_csv(os.path.join(output_dir, "routes.txt"), index=False)

# === 4. calendar.txt (from uploaded) ===
today = datetime.now()
start_date = today.strftime("%Y%m%d")
end_date = (today + timedelta(days=365)).strftime("%Y%m%d")

calendar_df = pd.DataFrame([{
    "service_id": SERVICE_ID,
    "monday": WEEKDAYS[0],
    "tuesday": WEEKDAYS[1],
    "wednesday": WEEKDAYS[2],
    "thursday": WEEKDAYS[3],
    "friday": WEEKDAYS[4],
    "saturday": WEEKDAYS[5],
    "sunday": WEEKDAYS[6],
    "start_date": start_date,
    "end_date": end_date
}])
calendar_df.to_csv(os.path.join(output_dir, "calendar.txt"), index=False)

# === 5. trips.txt (match uploaded format) ===
trips_data = []
trip_ids = []

for trip_num in range(24 * 60 // HEADWAY_MINUTES):
    trip_id = f"TRIP_{generate_uuid()}"
    trip_ids.append(trip_id)

    trips_data.append({
        "route_id": ROUTE_ID,
        "service_id": SERVICE_ID,
        "trip_id": trip_id,
        "trip_headsign": HEADSIGN,
        "trip_short_name": "",
        "direction_id": DIRECTION_ID,
        "block_id": "",
        "shape_id": "",
        "wheelchair_accessible": 0,
        "bikes_allowed": 0
    })

trips_df = pd.DataFrame(trips_data)[[
    "route_id", "service_id", "trip_id", "trip_headsign", "trip_short_name",
    "direction_id", "block_id", "shape_id", "wheelchair_accessible", "bikes_allowed"
]]
trips_df.to_csv(os.path.join(output_dir, "trips.txt"), index=False)

# === 6. stop_times.txt ===
def time_to_seconds(t):
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s

def seconds_to_time(seconds):
    h, s = divmod(seconds, 3600)
    m, s = divmod(s, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

start_seconds = time_to_seconds(START_TIME)
stop_times_data = []

for trip_id in trip_ids:
    current_time = start_seconds + (int(trip_id.split('_')[-1][:6], 16) % (HEADWAY_MINUTES * 60))
    for seq, stop_id in enumerate(stop_ids):
        arrival_time = current_time + seq * SECONDS_PER_SEGMENT
        departure_time = arrival_time  # no dwell time
        stop_times_data.append({
            "trip_id": trip_id,
            "arrival_time": seconds_to_time(arrival_time),
            "departure_time": seconds_to_time(departure_time),
            "stop_id": stop_id,
            "stop_sequence": seq + 1,
            "stop_headsign": HEADSIGN,
            "pickup_type": 0,
            "drop_off_type": 0,
            "shape_dist_traveled": "",
            "timepoint": 0
        })

stop_times_df = pd.DataFrame(stop_times_data)[[
    "trip_id", "arrival_time", "departure_time", "stop_id",
    "stop_sequence", "stop_headsign", "pickup_type",
    "drop_off_type", "shape_dist_traveled", "timepoint"
]]
stop_times_df.to_csv(os.path.join(output_dir, "stop_times.txt"), index=False)

print(f"✅ Arquivos GTFS gerados em: ./{output_dir}/")
print(f"   - {len(stop_ids)} paradas (com IDs UUID)")
print(f"   - {len(trip_ids)} viagens (TRIP_xxx)")
print(f"   - Arquivos alinhados com o formato dos arquivos fornecidos.")