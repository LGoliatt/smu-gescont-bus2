"""
Script para processar rotas de Ã´nibus a partir de um CSV:
- Detecta direÃ§Ã£o da rota: Centro-Bairro (C-B) ou Bairro-Centro (B-C)
- Gera GeoJSON com raios de curvatura por trecho
- Visualiza rotas num mapa interativo

Arquivo de entrada: 'rotas.csv'
SaÃ­das geradas:
- 'rotas.geojson': GeoJSON com geometrias e propriedades das rotas
- 'mapa_rotas.html': Mapa interativo com rotas C-B e B-C
"""

import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import json
import folium

def default(o):
    """
    FunÃ§Ã£o auxiliar para lidar com tipos numpy na serializaÃ§Ã£o JSON.
    """
    if isinstance(o, np.integer):
        return int(o)
    elif isinstance(o, np.floating):
        return float(o)
    elif isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")
    
def convert_numpy_types(data):
    """
    Converte tipos numpy (como int64, float64) para tipos nativos do Python.
    Ãtil para tornar o dicionÃ¡rio compatÃ­vel com json.dumps().
    """
    if isinstance(data, dict):
        return {key: convert_numpy_types(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types(item) for item in data]
    elif isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.floating):
        return float(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    else:
        return data
    
def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula a distÃ¢ncia entre dois pontos geogrÃ¡ficos usando a fÃ³rmula de Haversine (em metros).
    """
    R = 6371e3  # Raio da Terra em metros
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def calculate_radius(p1, p2, p3):
    """
    Calcula o raio de curvatura dado trÃªs pontos consecutivos (p1, p2, p3).
    Retorna o raio em metros.
    """
    def dist(a, b):
        return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    d1 = dist(p1, p2)
    d2 = dist(p2, p3)
    d3 = dist(p1, p3)

    if d1 == 0 or d2 == 0:
        return float('inf')  # Linha reta

    angle = np.arccos((d1**2 + d2**2 - d3**2) / (2 * d1 * d2))
    if angle == 0:
        return float('inf')  # Linha reta

    radius = d2 / (2 * sin(angle))
    return abs(radius)  # Em unidades dos pontos (metros ou graus?)



def extrair_rotas_csv(caminho_csv):
    # Ler CSV
    df = pd.read_csv(caminho_csv, on_bad_lines='skip')
    
    # Converter stopsequence para inteiro
    df['stopsequence'] = df['stopsequence'].astype(int)

    # Primeira parada para identificar reinício da rota
    primeira_parada = df.iloc[0]['stopname']
    ponto_inicial_lat = df.iloc[0]['stop_lat']
    ponto_inicial_lon = df.iloc[0]['stop_lon']

    # Listas para armazenar rotas
    rota_CB = [[ponto_inicial_lat, ponto_inicial_lon]]  # Rota Centro-Bairro
    rota_BC = []  # Rota Bairro-Centro

    # Variáveis temporárias
    direcao_atual = "C-B"
    sequencia_anterior = df.iloc[0]['stopsequence']

    # Percorrer linhas do CSV
    for i in range(1, len(df)):
        linha = df.iloc[i]
        stopname = linha['stopname']
        stopsequence = linha['stopsequence']
        lat = linha['stop_lat']
        lon = linha['stop_lon']

        # Detectar mudança de direção
        if stopsequence > sequencia_anterior:
            nova_direcao = "C-B"
        elif stopsequence == 1:
            nova_direcao = "B-C"
        else:
            nova_direcao = "B-C"

        # Adicionar à rota atual
        if nova_direcao == "C-B":
            rota_CB.append([lat, lon])
        elif nova_direcao == "B-C":
            rota_BC.append([lat, lon])

        # Atualizar direção e sequência
        sequencia_anterior = stopsequence
        direcao_atual = nova_direcao

        # Se voltou ao ponto inicial, encerrar
        if stopname == primeira_parada and i > 10:
            print(f"✅ Ponto inicial '{primeira_parada}' encontrado novamente. Processo finalizado.")
            break

    return rota_CB, rota_BC


#%%
# Carregar dados do CSV
fn = '../data_stops/209.csv'
df = pd.read_csv(fn, on_bad_lines='skip')

# Converter stopsequence para inteiro
df['stopsequence'] = df['stopsequence'].astype(int)

# Armazenar rotas como FeatureCollection
geojson_routes = []

# Nome da primeira parada para detectar reinÃ­cio da rota
first_stop_name = df.iloc[0]['stopname']

# VariÃ¡veis temporÃ¡rias para agrupar rotas
current_route_points = []
direction = "C-B"
prev_seq = 0

for i in range(len(df)):
    row = df.iloc[i]
    
    current_seq = row['stopsequence']
    current_point = {
        "lon": row['stop_lon'],
        "lat": row['stop_lat'],
        "properties": {
            "stopname": row['stopname'],
            "boarding": int(row['boarding']),
            "landing": int(row['landing']),
            "occupation": int(row['occupation']),
            "timestamp": f"{row['day']} {row['departuretime']}"
        }
    }

    # Detectar mudanÃ§a de direÃ§Ã£o (stopsequence nÃ£o cresce mais)
    if i > 0 and current_seq <= prev_seq:
        # Finalizar rota anterior se tiver ao menos 2 pontos
        if len(current_route_points) >= 2:
            coords = [(pt["lon"], pt["lat"]) for pt in current_route_points]

            line_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
                },
                "properties": {
                    "route": row['routeshortname'],
                    "direction": direction,
                    "start_time": current_route_points[0]["properties"]["timestamp"],
                    "stops_count": len(coords),
                    "radii": []
                }
            }

            # Calcular raios de curvatura entre pontos consecutivos
            for j in range(1, len(coords) - 1):
                p1 = coords[j - 1]
                p2 = coords[j]
                p3 = coords[j + 1]
                radius = calculate_radius(p1, p2, p3)
                line_feature["properties"]["radii"].append({
                    "segment": j,
                    "radius_meters": round(radius, 2)
                })

            geojson_routes.append(line_feature)

        # Reiniciar nova rota
        current_route_points = [current_point]
        direction = "B-C" if current_seq < prev_seq else "C-B"
    else:
        current_route_points.append(current_point)

    prev_seq = current_seq

    # Se voltou ao ponto inicial, finalizar a rota
    if row['stopname'] == first_stop_name and i > 10:
        if len(current_route_points) >= 2:
            coords = [(pt["lon"], pt["lat"]) for pt in current_route_points]

            line_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
                },
                "properties": {
                    "route": row['routeshortname'],
                    "direction": direction,
                    "start_time": current_route_points[0]["properties"]["timestamp"],
                    "stops_count": len(coords),
                    "radii": []
                }
            }

            # Calcular raios de curvatura entre pontos
            for j in range(1, len(coords) - 1):
                p1 = coords[j - 1]
                p2 = coords[j]
                p3 = coords[j + 1]
                radius = calculate_radius(p1, p2, p3)
                line_feature["properties"]["radii"].append({
                    "segment": j,
                    "radius_meters": round(radius, 2)
                })

            geojson_routes.append(line_feature)

        # Reiniciar rota
        current_route_points = []
        direction = "C-B" if direction == "B-C" else "B-C"


# Montar GeoJSON final
geojson_output = {
    "type": "FeatureCollection",
    "features": geojson_routes
}

with open("rotas.geojson", "w") as f:
    json.dump(geojson_output, f, indent=2, default=default)
    
    
print("â
 Arquivo GeoJSON salvo como 'rotas.geojson'")

#%%
geojson_output_clean = convert_numpy_types(geojson_output)

# Visualizar no mapa com Folium
m = folium.Map(location=[-21.74, -43.34], zoom_start=13)

for feature in geojson_output_clean["features"]:
    color = "blue" if feature["properties"]["direction"] == "C-B" else "red"
    folium.GeoJson(
        feature,
        name=f"Rota {feature['properties']['direction']}",
        style_function=lambda x, color=color: {"color": color, "weight": 2.5}
    ).add_to(m)

folium.LayerControl().add_to(m)
m.save("mapa_rotas.html")
print("ðºï¸ Mapa salvo como 'mapa_rotas.html'")
#%%

# Supondo que vocÃª jÃ¡ tenha 'geojson_output_clean' criado anteriormente
# Extraindo rotas C-B e B-C como listas de [lat, lon]

caminho_CB = []
caminho_BC = []

for feature in geojson_output_clean["features"]:
    coords = feature["geometry"]["coordinates"]
    direction = feature["properties"]["direction"]

    # Converter coordenadas GeoJSON (lon, lat) para formato [lat, lon]
    pontos = [[round(lat, 6), round(lon, 6)] for lon, lat in coords]

    if direction == "C-B":
        caminho_CB.extend(pontos)
    elif direction == "B-C":
        caminho_BC.extend(pontos)

# Remover duplicados consecutivos (opcional)
def remove_consecutive_duplicates(seq):
    return [x for i, x in enumerate(seq) if i == 0 or x != seq[i - 1]]

caminho_CB = remove_consecutive_duplicates(caminho_CB)
caminho_BC = remove_consecutive_duplicates(caminho_BC)

# Resultado final:
print("â
 Rota Centro-Bairro (C-B):")
print(caminho_CB)

print("\nâ
 Rota Bairro-Centro (B-C):")
print(caminho_BC)


#%%


import requests
import json

def get_osrm_route(points):
    """
    Recebe uma lista de pontos [lat, lon] e retorna a rota GeoJSON calculada pelo OSRM.
    
    Args:
        points (list): Lista de pontos [[lat1, lon1], [lat2, lon2], ...]
        
    Returns:
        dict: GeoJSON com a geometria da rota calculada
    """
    if len(points) < 2:
        raise ValueError("Ã necessÃ¡rio pelo menos 2 pontos para calcular uma rota.")

    # Ajustar cada ponto usando o endpoint 'nearest'
    adjusted_points = []
    for lat, lon in points:
        url = f"http://router.project-osrm.org/nearest/v1/driving/{lon},{lat}"
        response = requests.get(url)
        data = response.json()

        if not data.get('waypoints'):
            raise Exception(f"Erro ao ajustar o ponto {lat}, {lon}: {data}")

        nearest = data['waypoints'][0]['location']
        adjusted_points.append((nearest[1], nearest[0]))  # (lat, lon) -> (lon, lat) na API

    print(f"â
 Pontos ajustados ao grafo rodoviÃ¡rio: {adjusted_points[:2]}...")

    # Converter pontos ajustados para formato esperado pela API de rota
    coordinates = ";".join([f"{lon},{lat}" for lat, lon in adjusted_points])

    # Calcular rota com overview completo em GeoJSON
    route_url = (
        f"http://router.project-osrm.org/route/v1/driving/{coordinates}"
        "?overview=full&geometries=geojson"
    )
    route_response = requests.get(route_url)
    route_data = route_response.json()

    if not route_data.get('routes'):
        raise Exception(f"Erro ao calcular rota: {route_data}")

    route_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": route_data["routes"][0]["geometry"],
                "properties": {
                    "distance_meters": route_data["routes"][0]["distance"],
                    "duration_seconds": route_data["routes"][0]["duration"],
                    "summary": "Rota calculada via OSRM"
                }
            }
        ]
    }

    return route_geojson

# Supondo que caminho_CB e caminho_BC foram extraÃ­dos anteriormente
geojson_CB = get_osrm_route(caminho_CB)
geojson_BC = get_osrm_route(caminho_BC)

# Salvar como arquivos GeoJSON
with open("rota_CB_osrm.geojson", "w") as f:
    json.dump(geojson_CB, f, indent=2)

with open("rota_BC_osrm.geojson", "w") as f:
    json.dump(geojson_BC, f, indent=2)

print("â
 Rotas OSRM salvas como 'rota_CB_osrm.geojson' e 'rota_BC_osrm.geojson'")

#%%
