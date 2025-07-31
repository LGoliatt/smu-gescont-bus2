import pandas as pd
import numpy as np
import os
from sklearn.neighbors import NearestNeighbors
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
AGENCY_NAME = "Empresa de Ônibus Local"
AGENCY_URL = "http://exemplo.com"
AGENCY_TIMEZONE = "America/Sao_Paulo"
ROUTE_SHORT_NAME = "Linha Circular"
ROUTE_LONG_NAME = "Linha Circular - Bairro A"
ROUTE_TYPE = 3  # 3 = ônibus
SERVICE_ID = "service_1"
TRIP_ID = "trip_circular_01"
DIRECTION_ID = 0  # 0 = sentido horário (exemplo)
HEADSIGN = "Circular Completa"

# Horário de início da primeira viagem
START_TIME = "06:00:00"  # HH:MM:SS no formato GTFS
# Intervalo entre ônibus (em minutos)
HEADWAY_MINUTES = 30
# Duração estimada por trecho (em segundos)
SECONDS_PER_SEGMENT = 60  # ajuste conforme necessário
# Dias de operação
WEEKDAYS = [1, 1, 1, 1, 1, 1, 1]  # Seg a Dom (1 = opera)

# === Passo 1: Encontrar a melhor rota circular (TSP com vizinho mais próximo) ===

def haversine_distance_matrix(coords):
    """Calcula matriz de distância haversine (em km)"""
    from sklearn.metrics import DistanceMetric
    coords_rad = np.radians(coords)
    dist = DistanceMetric.get_metric("haversine")
    distance_matrix_km = dist.pairwise(coords_rad) * 6371  # Raio da Terra
    return distance_matrix_km

def solve_tsp_nn(coords):
    """Resolve TSP com heurística do vizinho mais próximo"""
    n = len(coords)
    unvisited = set(range(1, n))  # Começa do ponto 0
    tour = [0]
    current = 0
    dist_matrix = haversine_distance_matrix(coords)

    while unvisited:
        nearest = min(unvisited, key=lambda x: dist_matrix[current][x])
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    return tour

# Obter a melhor rota
tour_indices = solve_tsp_nn(coordinates)
ordered_coords = [coordinates[i] for i in tour_indices]

# === Passo 2: Criar diretório GTFS ===
output_dir = "gtfs_circular_route"
os.makedirs(output_dir, exist_ok=True)

# === Passo 3: stops.txt ===
stops_data = []
stop_ids = []
for i, (lat, lon) in enumerate(ordered_coords):
    stop_id = f"stop_{i+1}"
    stop_name = f"Parada {i+1}"
    stops_data.append({
        "stop_id": stop_id,
        "stop_name": stop_name,
        "stop_lat": lat,
        "stop_lon": lon,
        "location_type": 0,
        "wheelchair_boarding": 0
    })
    stop_ids.append(stop_id)

stops_df = pd.DataFrame(stops_data)
stops_df.to_csv(os.path.join(output_dir, "stops.txt"), index=False)

# === Passo 4: agency.txt ===
agency_df = pd.DataFrame([{
    "agency_id": "0",
    "agency_name": AGENCY_NAME,
    "agency_url": AGENCY_URL,
    "agency_timezone": AGENCY_TIMEZONE,
    "agency_lang": "pt",
    "agency_phone": "555-1234",
    "agency_fare_url": f"{AGENCY_URL}/tarifas"
}])
agency_df.to_csv(os.path.join(output_dir, "agency.txt"), index=False)

# === Passo 5: routes.txt ===
routes_df = pd.DataFrame([{
    "route_id": "route_01",
    "agency_id": "0",
    "route_short_name": ROUTE_SHORT_NAME,
    "route_long_name": ROUTE_LONG_NAME,
    "route_type": ROUTE_TYPE,
    "route_color": "FF6600",
    "route_text_color": "FFFFFF"
}])
routes_df.to_csv(os.path.join(output_dir, "routes.txt"), index=False)

# === Passo 6: calendar.txt ===
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

# === Passo 7: trips.txt e stop_times.txt ===

# Converter horário inicial para segundos
def time_to_seconds(t):
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s

def seconds_to_time(seconds):
    return f"{seconds // 3600:02d}:{(seconds // 60) % 60:02d}:{seconds % 60:02d}"

# Gerar múltiplas viagens com headway
start_seconds = time_to_seconds(START_TIME)
trip_count = 24 * 60 // HEADWAY_MINUTES  # ~1 dia de operação

trips_data = []
stop_times_data = []

for trip_num in range(trip_count):
    trip_id = f"{TRIP_ID}_{trip_num:03d}"
    departure_offset = trip_num * HEADWAY_MINUTES * 60  # em segundos
    current_time = start_seconds + departure_offset

    # Adicionar viagem
    trips_data.append({
        "route_id": "route_01",
        "service_id": SERVICE_ID,
        "trip_id": trip_id,
        "trip_headsign": HEADSIGN,
        "direction_id": DIRECTION_ID
    })

    # Paradas
    for stop_seq, stop_id in enumerate(stop_ids):
        arrival_time = current_time + stop_seq * SECONDS_PER_SEGMENT
        departure_time = arrival_time  # sem espera
        time_str = seconds_to_time(arrival_time)
        stop_times_data.append({
            "trip_id": trip_id,
            "arrival_time": time_str,
            "departure_time": time_str,
            "stop_id": stop_id,
            "stop_sequence": stop_seq + 1,
            "pickup_type": 0,
            "drop_off_type": 0
        })

    # Fechar rota circular (volta ao início)
    # Opcional: adicionar tempo de volta ao ponto inicial
    last_time = current_time + len(stop_ids) * SECONDS_PER_SEGMENT
    # Se quiser que o ônibus volte ao ponto inicial, adicione mais um ponto

trips_df = pd.DataFrame(trips_data)
trips_df.to_csv(os.path.join(output_dir, "trips.txt"), index=False)

stop_times_df = pd.DataFrame(stop_times_data)
stop_times_df.to_csv(os.path.join(output_dir, "stop_times.txt"), index=False)

print(f"✅ Arquivos GTFS gerados em: ./{output_dir}/")
print(f"   - {len(stop_ids)} paradas ordenadas em rota circular.")
print(f"   - {len(trips_data)} viagens geradas (a cada {HEADWAY_MINUTES} min).")