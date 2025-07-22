
import pandas as pd
import requests
import json
import folium


# === 1. Função para obter rota via API do OSRM ===
def get_osrm_route(points):
    """
    Calcula uma rota entre pontos usando a API pública do OSRM e retorna o GeoJSON da geometria.

    Args:
        points (list): Lista de [lat, lon], ex: [[-21.76, -43.34], ...]

    Returns:
        dict: GeoJSON com a linha da rota calculada
    """
    if len(points) < 2:
        return None

    # Ajustar formato para API: "lon,lat"
    coordinates = ";".join([f"{point[1]},{point[0]}" for point in points])

    url = f"http://router.project-osrm.org/route/v1/driving/{coordinates}?overview=full&geometries=geojson"
    response = requests.get(url)
    data = response.json()

    if not data.get("routes"):
        print("❌ Erro ao calcular rota com OSRM:", data)
        return None

    route_geometry = data["routes"][0]["geometry"]

    geojson_feature = {
        "type": "Feature",
        "properties": {
            "summary":''
        },
        "geometry": route_geometry
    }

    return {
        "type": "FeatureCollection",
        "features": [geojson_feature]
    }

import pandas as pd

def extrair_rotas_csv(caminho_csv):
    # Ler CSV
    df = pd.read_csv(caminho_csv, on_bad_lines='skip')
    
    # Converter colunas relevantes para tipos corretos
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
    detectou_inicio_B_C = False  # Flag para evitar adicionar o ponto inicial em B-C

    # Percorrer linhas do CSV
    for i in range(1, len(df)):
        linha = df.iloc[i]
        stopname = linha['stopname']
        stopsequence = linha['stopsequence']
        lat = linha['stop_lat']
        lon = linha['stop_lon']

        # === Detectar mudança de direção ===
        if not detectou_inicio_B_C:
            if stopsequence > sequencia_anterior:
                # Continuar Centro-Bairro
                direcao_atual = "C-B"
            elif stopsequence == 1:
                # Início da rota de volta (Bairro-Centro)
                direcao_atual = "B-C"
                detectou_inicio_B_C = True
                rota_BC.append([lat, lon])  # Adicionar primeiro ponto da rota B-C
            else:
                # Caso sequência não cresça mas ainda não reiniciou
                direcao_atual = "C-B"
        else:
            # Já está na rota B-C
            direcao_atual = "B-C"

        # === Adicionar ponto à rota correspondente ===
        if direcao_atual == "C-B" and not detectou_inicio_B_C:
            rota_CB.append([lat, lon])
        elif direcao_atual == "B-C" and detectou_inicio_B_C:
            rota_BC.append([lat, lon])

        # Atualizar sequência anterior
        sequencia_anterior = stopsequence

        # === Finalizar se voltou ao ponto inicial ===
        if stopname == primeira_parada and i > 10:
            print(f"✅ Ponto inicial '{primeira_parada}' encontrado novamente. Processo finalizado.")
            break

    return rota_CB, rota_BC

# === 2. Carregar CSV e extrair latlongs_CB e latlongs_BC ===
fn = '../data_stops/722.csv'
df = pd.read_csv(fn, on_bad_lines='skip')
df['stopsequence'] = df['stopsequence'].astype(int)

# 
rota_CB, rota_BC = extrair_rotas_csv(fn)


# === 3. Calcular rotas com OSRM e salvar GeoJSON ===
def save_geojson(route_list, prefix="rota"):
    """Calcula a rota OSRM e salva como GeoJSON"""
    results = []
    for idx, points in enumerate(route_list):
        geojson = get_osrm_route(points)
        if geojson:
            filename = f"{prefix}_{idx + 1}.geojson"
            with open(filename, 'w') as f:
                json.dump(geojson, f, indent=2)
            print(f"✅ Arquivo salvo: {filename}")
            results.append((filename, geojson))
    return results

print("\n🔁 Calculando rotas Centro-Bairro (C-B)...")
cb_results = save_geojson([rota_CB], prefix="rota_CB")

print("\n🔁 Calculando rotas Bairro-Centro (B-C)...")
bc_results = save_geojson([rota_BC], prefix="rota_BC")



# === 1. Função para criar GeoJSON com ambas as rotas ===
def create_combined_geojson(cb_routes, bc_routes):
    """
    Recebe listas de rotas do tipo [(filename, geojson)] e cria um GeoJSON combinado.
    """
    features = []

    # Adicionar rotas Centro-Bairro (C-B) - vermelho
    for filename, geojson in cb_routes:
        for feature in geojson["features"]:
            feature["properties"]["route_type"] = "Centro-Bairro"
            feature["properties"]["color"] = "magenta"
            feature["properties"]["direction"] = "magenta"
            features.append(feature)

    # Adicionar rotas Bairro-Centro (B-C) - azul
    for filename, geojson in bc_routes:
        for feature in geojson["features"]:
            feature["properties"]["route_type"] = "Bairro-Centro"
            feature["properties"]["color"] = "blue"
            feature["properties"]["direction"] = "blue"
            features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }

# Exemplo de uso (assumindo que cb_results e bc_results já estão definidos)
# cb_results = [('rota_CB_1.geojson', geojson_cb), ...]
# bc_results = [('rota_BC_1.geojson', geojson_bc), ...]

combined_geojson = create_combined_geojson(cb_results, bc_results)

# Salvar como arquivo GeoJSON
geojson_output_file = "rotas_combinadas.geojson"
with open(geojson_output_file, "w") as f:
    json.dump(combined_geojson, f, indent=2)

print(f"\n✅ Arquivo GeoJSON salvo como: {geojson_output_file}")


# === 2. Visualizar o GeoJSON no mapa ===
def visualize_geojson(geojson_data, output_html="mapa_rotas_geojson.html"):
    """
    Visualiza o GeoJSON com:
    - Linhas das rotas com cores diferentes por tipo (C-B = vermelho, B-C = azul)
    - Pontos individuais da geometria com a mesma cor da rota
    - Tooltip mostrando 'radius_meters' em cada ponto, se disponível
    """

    # Obter centro médio aproximado das rotas
    all_coords = []
    for feature in geojson_data["features"]:
        coords = feature["geometry"]["coordinates"]
        all_coords.extend(coords)

    if not all_coords:
        raise ValueError("GeoJSON não contém coordenadas válidas.")

    center_lat = sum([c[1] for c in all_coords]) / len(all_coords)
    center_lon = sum([c[0] for c in all_coords]) / len(all_coords)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

    # === Mapear direções para cores ===
    direction_colors = {
        "C-B": "red",
        "B-C": "blue"
    }

    # === Adicionar camadas dinamicamente com cores e tooltips ===
    for feature in geojson_data["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]
        direction = props.get("direction", "unknown")
        route_type = feature["properties"].get("route_type", "Desconhecido")
        #color = direction_colors.get(direction, "black")
        color = feature["properties"].get("color", "black")

        # === Adicionar linha da rota ===
        folium.GeoJson(
            feature,
            name=f"Rota {direction}",
            style_function=lambda x, color=color: {"color": color, "weight": 3}
        ).add_to(m)

        # === Adicionar pontos com tooltip de raio de curvatura (se existir) ===
        radii_dict = {}
        if "radii" in props:
            # Criar dicionário: index -> radius_meters
            for r in props["radii"]:
                segment_idx = r["segment"] + 1  # O ponto central está no índice do segmento +1
                radii_dict[segment_idx] = r["radius_meters"]

        for point_idx, (lon, lat) in enumerate(coords):
            radius = radii_dict.get(point_idx, None)

            # Montar texto do tooltip
            tooltip_text = f"Ponto {point_idx + 1}"
            if radius is not None:
                tooltip_text += f"<br>Raio de curvatura: {radius:.2f} m"
            
            # Definir cor do marcador com base no raio
            if radius is not None:
                if radius < 9:
                    point_color = "red"
                elif 10 <= radius < 25:
                    point_color = "orange"
                else:
                    point_color = "green"
            else:
                point_color = "gray"  # Sem dados de curvatura

            folium.CircleMarker(
                location=[lat, lon],
                radius=3,
                color=point_color,
                fill=True,
                fill_color=point_color,
                fill_opacity=0.7,
                tooltip=folium.Tooltip(tooltip_text, sticky=True),
                popup=f"{tooltip_text}<br>Coordenadas: ({lat:.6f}, {lon:.6f})"
            ).add_to(m)

    # === Adicionar controle de camadas ===
    folium.LayerControl(collapsed=False).add_to(m)

    # Salvar mapa
    m.save(output_html)
    print(f"\n🗺️ Mapa salvo como: {output_html}")
    
    
visualize_geojson(combined_geojson, output_html="mapa_rotas_geojson.html")

#%%

import numpy as np
from pyproj import Transformer

def latlon_to_xy(lat, lon, crs="EPSG:4326", target_crs="EPSG:3857"):
    """
    Converte latitude e longitude para coordenadas em metros (Web Mercator por padrão).
    """
    transformer = Transformer.from_crs(crs, target_crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    return np.array([x, y])

def calculate_curvature_radius(p1_latlon, p2_latlon, p3_latlon):
    # Converte para coordenadas planas (em metros)
    p1 = latlon_to_xy(*p1_latlon)
    p2 = latlon_to_xy(*p2_latlon)
    p3 = latlon_to_xy(*p3_latlon)

    # Lados do triângulo
    a = np.linalg.norm(p2 - p1)
    b = np.linalg.norm(p3 - p2)
    c = np.linalg.norm(p1 - p3)

    # Semiperímetro
    s = (a + b + c) / 2

    # Área do triângulo com fórmula de Heron
    try:
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        if area == 0:
            return float('inf')
        # Raio do círculo circunscrito
        R = (a * b * c) / (4 * area)
        return R
    except:
        return float('inf')

# === Exemplo ===
p1 = (-21.761, -43.349)  # lat, lon
p2 = (-21.762, -43.348)
p3 = (-21.763, -43.349)

raio = calculate_curvature_radius(p1, p2, p3)
print(f"Raio de curvatura: {raio:.2f} metros")


def calcular_raios_geometria(geojson_data):
    """
    Recebe um GeoJSON FeatureCollection com LineStrings
    e calcula o raio de curvatura para cada segmento.
    
    Modifica o GeoJSON in-place adicionando 'radii' nas propriedades.
    """

    for feature in geojson_data.get("features", []):
        geometry = feature.get("geometry", {})
        coords = geometry.get("coordinates", [])

        if geometry.get("type") != "LineString" or len(coords) < 3:
            continue  # Só calcula se tiver pelo menos 3 pontos

        # Inicializar lista de raios
        raios = []

        # Calcular raio para cada trio de pontos consecutivos
        for i in range(1, len(coords) - 1):
            p1 = coords[i - 1]  # (lon, lat)
            p2 = coords[i]
            p3 = coords[i + 1]

            # Converter para (lat, lon) -> ([1], [0])
            lat1, lon1 = p1[1], p1[0]
            lat2, lon2 = p2[1], p2[0]
            lat3, lon3 = p3[1], p3[0]

            radius = calculate_curvature_radius((lat1, lon1), (lat2, lon2), (lat3, lon3))

            raios.append({
                "segment": i,
                "radius_meters": round(radius, 2)
            })

        # Adicionar ao GeoJSON
        feature["properties"]["radii"] = raios
        r=[i['radius_meters'] for i in raios]
        
    return geojson_data, min(r)


# Exemplo: calcular raios e atualizar GeoJSON
geojson_com_raios, _ = calcular_raios_geometria(combined_geojson)

# Salvar como arquivo JSON
with open("rotas_com_raios.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson_com_raios, f, indent=2)

print("✅ Arquivo com raios salvo como 'rotas_com_raios.geojson'")

visualize_geojson(geojson_com_raios, output_html="rotas_com_raios.html")

#%%

# import os
# import glob

# # Pasta onde estão os CSVs
# folder_path = "../data_stops/"

# # Listar e ler todos os CSVs
# csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
# csv_files.sort()

# print(f"📄 Encontrados {len(csv_files)} arquivos CSV na pasta '{folder_path}':")
# for f in csv_files:
#     fg=f.split('/')[-1].replace('.csv','.html')
#     #print(" -", fg)
#     df = pd.read_csv(f, on_bad_lines='skip')
#     df['stopsequence'] = df['stopsequence'].astype(int)    
#     # 
#     rota_CB, rota_BC = extrair_rotas_csv(f  )
#     cb_results = save_geojson([rota_CB], prefix="rota_CB")    
#     bc_results = save_geojson([rota_BC], prefix="rota_BC")
#     combined_geojson = create_combined_geojson(cb_results, bc_results)
#     geojson_com_raios, rmin = calcular_raios_geometria(combined_geojson)
#     visualize_geojson(geojson_com_raios, output_html=fg)
#     print(" -", fg, rmin)
