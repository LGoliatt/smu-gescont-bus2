import folium
from folium.plugins import TimestampedGeoJson
import requests
import datetime
from shapely.geometry import LineString
import numpy as np

# === DADOS DE ENTRADA ===
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

# Sequência de índices (ciclo fechado)
sequence = [0, 8, 6, 5, 4, 3, 7, 2, 1, 0]
edges = [(sequence[i], sequence[i+1]) for i in range(len(sequence)-1)]

# OSRM API (público - pode ser limitado; use seu próprio servidor para produção)
OSRM_URL = "http://router.project-osrm.org/route/v1/driving/"

# === Função para obter rota entre dois pontos ===
def get_route_osrm(coord1, coord2):
    """
    Retorna geometria (polyline), distância (m) e duração (s) entre dois pontos.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    url = f"{OSRM_URL}{lon1},{lat1};{lon2},{lat2}?geometries=geojson&overview=full"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Erro na API OSRM: {response.status_code}")
    
    data = response.json()
    route = data['routes'][0]
    geometry = route['geometry']['coordinates']  # Lista de [lon, lat]
    distance = route['distance']  # em metros
    duration = route['duration']  # em segundos
    return geometry, distance, duration

# === Calcular todas as rotas do ciclo ===
print("Calculando rotas com OSRM...")
full_geometry = []  # Coordenadas da rota completa [[lon, lat], ...]
total_duration_original = 0  # duração total em segundos
segments = []

for i, (idx1, idx2) in enumerate(edges):
    coord1 = coordinates[idx1]
    coord2 = coordinates[idx2]
    try:
        geom, dist, dur = get_route_osrm(coord1, coord2)
        full_geometry.extend(geom)
        segments.append({
            'from': idx1,
            'to': idx2,
            'geometry': geom,
            'distance': dist,
            'duration': dur
        })
        total_duration_original += dur
        print(f"Rota {idx1} → {idx2}: {dist:.0f}m, {dur/60:.1f}min")
    except Exception as e:
        print(f"Erro na rota {idx1} → {idx2}: {e}")

print(f"Duração total original do ciclo: {total_duration_original/60:.2f} min")

# === Ajustar duração para 20 minutos (1200 segundos) ===
TARGET_DURATION = 20 * 60  # 20 minutos em segundos
scale_factor = TARGET_DURATION / total_duration_original
print(f"Fator de escala para duração: {scale_factor:.3f}")

# Aplicar fator de escala nas durações
for seg in segments:
    seg['scaled_duration'] = seg['duration'] * scale_factor

# === Gerar pontos ao longo do tempo ===
# === GERAR MAIS PONTOS (maior "FPS") ===
features = []
current_time = datetime.datetime(2025, 8, 3, 5, 0, 0)  # 05:00
end_time = datetime.datetime(2025, 8, 3, 11, 0, 0)     # 23:00
cycle_count = 0

# ⚙️ Configuração: gere um ponto a cada 0.5 segundos (mais suave)
TIME_STEP = 0.5  # segundos entre cada ponto (quanto menor, mais suave)

while current_time < end_time:
    print(f"Iniciando ciclo {cycle_count + 1} às {current_time.strftime('%H:%M:%S')}")

    for seg in segments:
        duration_sec = seg['scaled_duration']
        num_points = max(2, int(duration_sec / TIME_STEP))  # Mais pontos!
        line = LineString(seg['geometry'])
        start_time = current_time
        end_time_seg = start_time + datetime.timedelta(seconds=duration_sec)

        for i in range(num_points):
            frac = i / (num_points - 1) if num_points > 1 else 0
            point = line.interpolate(frac * line.length, normalized=True)
            t = start_time + datetime.timedelta(seconds=frac * duration_sec)

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [point.x, point.y],  # [lon, lat]
                },
                "properties": {
                    "time": t.strftime("%Y-%m-%dT%H:%M:%S"),
                    "popup": f"Veículo - {t.strftime('%H:%M:%S')}",
                    "icon": "circle",
                    "iconstyle": {
                        "fillColor": "red",
                        "fillOpacity": 0.9,
                        "stroke": "true",
                        "radius": 6
                    },
                    # Adicionado para suavizar animação
                    "tooltip": f"{t.strftime('%H:%M:%S')}"
                }
            })

        current_time = end_time_seg

    cycle_count += 1

# === CRIAR MAPA COM ANIMAÇÃO RÁPIDA E SUAVE ===
center_lat = np.mean([coord[0] for coord in coordinates])
center_lon = np.mean([coord[1] for coord in coordinates])

m = folium.Map(location=[center_lat, center_lon], zoom_start=15)

# Adicionar rota (opcional)
polyline = [(point[1], point[0]) for point in full_geometry]  # (lat, lon)
folium.PolyLine(polyline, color="blue", weight=2, opacity=0.5, tooltip="Rota do veículo").add_to(m)

# 🚀 Configuração de alta velocidade e FPS
TimestampedGeoJson(
    {"type": "FeatureCollection", "features": features},
    period=f"PT{int(TIME_STEP)}S",        # Ex: "PT0S" não funciona, então usamos "PT1S", mas geramos a cada 0.5s
    add_last_point=True,
    auto_play=True,                       # Começa automático
    loop=True,
    loop_button=True,
    date_options="HH:mm:ss",
    time_slider_drag_update=True,
    duration=None,                        # Sem duração fixa
    transition_time=200,                  # Tempo entre quadros em ms (quanto menor, mais rápido)
    max_speed=10,                         # Botão de "x10" velocidade
).add_to(m)

m.save("veiculo_simulacao_alta_velocidade.html")
print("Mapa de alta velocidade salvo como 'veiculo_simulacao_alta_velocidade.html'")