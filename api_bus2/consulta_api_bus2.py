#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# !pip  install numpy   requests --break-system-packages


# curl -X 'GET' \
#   'https://bus2.services/api-b2b/sobe-desce?startDate=2024-11-01&endDate=2024-11-10&routeShortName=105&page=1&limit=20' \
#   -H 'accept: /' \
#   -H 'x-api-key: cb66e329-eaca-4cbb-bc31-914e20c25f86'
  
  
  
import requests
import folium
from folium import PolyLine
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

# Inicializar o geolocalizador com um user_agent válido
geolocator = Nominatim(user_agent="transport-analysis-v1", timeout=10)

# Use um user_agent único e descritivo
#geolocator = Nominatim(user_agent="meu_projeto_transporte_v1", timeout=10)  # timeout maior

def geocode_location(stop_name, max_retries=3):
    """
    Geocodifica um nome de parada com tentativas automáticas em caso de falha.
    """
    for attempt in range(1, max_retries + 1):
        try:
            location = geolocator.geocode(stop_name)
            if location:
                print(f"📍 Geocodificado: '{stop_name}' → ({location.latitude}, {location.longitude})")
                return (location.latitude, location.longitude)
            else:
                print(f"⚠️  Não encontrado (tentativa {attempt}): '{stop_name}'")
        
        except GeocoderTimedOut:
            print(f"⏳ Timeout na tentativa {attempt} para '{stop_name}'. Aguardando...")
        
        except GeocoderServiceError as e:
            print(f"🔧 Erro de serviço (tentativa {attempt}): {e}")
        
        except Exception as e:
            print(f"❌ Erro inesperado na tentativa {attempt}: {e}")
            break

        # Espera exponencial com jitter
        time.sleep(random.uniform(1.0, 2.5))  # entre 1 e 2.5 segundos

    print(f"❌ Falha ao geocodificar após {max_retries} tentativas: '{stop_name}'")
    return None

def fill_missing_stop_coordinates(stops, geocode_func, delay=0.1):
    """
    Preenche coordenadas faltantes em uma lista de paradas usando:
      1. Coordenadas conhecidas de outras ocorrências do mesmo stopid.
      2. Geocodificação por nome (stopname) se não encontradas.

    Parâmetros:
        stops (list): Lista de dicts com dados de paradas (stopid, stop_lat, stop_lon, stopname, etc).
        geocode_func (function): Função que recebe um nome e retorna (lat, lon) ou None.
        delay (float): Tempo de espera entre geocodificações.

    Retorna:
        tuple: (stops_atualizados, stop_coords_map)
    """
    # Passo 1: Construir mapa de coordenadas conhecidas
    stop_coords_map = {}
    for stop in stops:
        stopid = stop['stopid']
        lat = stop.get('stop_lat')
        lon = stop.get('stop_lon')

        if lat is not None and lon is not None and lat != '' and lon != '':
            try:
                lat = float(lat)
                lon = float(lon)
                if stopid not in stop_coords_map:
                    stop_coords_map[stopid] = {'lat': lat, 'lon': lon}
            except (ValueError, TypeError):
                continue

    print("✅ Known coordinates for stopids:")
    for stopid, coords in stop_coords_map.items():
        print(f"  ID {stopid}: ({coords['lat']}, {coords['lon']})")

    # Passo 2: Encontrar paradas com coordenadas faltando
    missing_coords = []
    for i, stop in enumerate(stops):
        if stop['stop_lat'] is None or stop['stop_lon'] is None or stop['stop_lat'] == '' or stop['stop_lon'] == '':
            missing_coords.append({
                'index': i,
                'stopid': stop['stopid'],
                'stopname': stop['stopname']
            })

    # Remover duplicatas por stopid
    seen = set()
    unique_missing = []
    for item in missing_coords:
        stopid = item['stopid']
        if stopid not in seen:
            seen.add(stopid)
            unique_missing.append(item)

    if unique_missing:
        print("\n📍 Filling missing coordinates using geocoding:")
    else:
        print("\n✅ All stopids have coordinates.")
    
    # Passo 3: Tentar geocodificar os que não têm coordenadas
    for item in unique_missing:
        stopid = item['stopid']
        stopname = item['stopname']

        if stopid in stop_coords_map:
            # Já foi preenchido por outra entrada
            continue

        print(f"🔍 Geocoding stopid {stopid}: '{stopname}'")
        try:
            coords = geocode_func(stopname)
            time.sleep(delay)  # Respeitar limite do serviço
            if coords and len(coords) == 2:
                lat, lon = coords
                stop_coords_map[stopid] = {'lat': lat, 'lon': lon}
                print(f"✅ Geocoded: ({lat}, {lon})")
            else:
                print(f"❌ Failed to geocode: {stopname}")
        except Exception as e:
            print(f"❌ Error geocoding '{stopname}': {e}")

    # Passo 4: Atualizar todas as paradas com coordenadas completas
    for stop in stops:
        if stop['stop_lat'] is None or stop['stop_lon'] is None or stop['stop_lat'] == '' or stop['stop_lon'] == '':
            stopid = stop['stopid']
            if stopid in stop_coords_map:
                coords = stop_coords_map[stopid]
                stop['stop_lat'] = str(coords['lat'])
                stop['stop_lon'] = str(coords['lon'])
                print(f"🔄 Filled stopid {stopid} from map: ({coords['lat']}, {coords['lon']})")
            else:
                print(f"❌ Unable to fill stopid {stopid}: no coordinates available")

    return stops, stop_coords_map

def build_stop_coordinates(stops, geocode_fallback=True, delay=0.1):
    """
    Processa uma lista de paradas e retorna um dicionário com:
        stopid -> {'lat': lat, 'lon': lon, 'stopname': name}

    Parâmetros:
        stops (list): Lista de dicts com chaves como 'stopid', 'stop_lat', 'stop_lon', 'stopname'
        geocode_fallback (bool): Se True, tenta geocodificar se coordenadas estiverem faltando
        delay (float): Tempo de espera entre geocodificações (para respeitar políticas do OSM)

    Retorna:
        dict: Mapeamento stopid -> {lat, lon, stopname}
    """
    stop_coords = {}

    for stop in stops:
        stopid = stop['stopid']
        lat = stop.get('stop_lat')
        lon = stop.get('stop_lon')
        stopname = stop.get('stopname', 'Unnamed Stop')

        # Verificar se coordenadas estão ausentes ou inválidas
        if lat is None or lon is None or lat == '' or lon == '':
            if not geocode_fallback:
                print(f"❌ Skipping stopid {stopid}: no coordinates and geocode_fallback=False")
                continue

            print(f"📍 Missing coordinates for stopid {stopid}, geocoding: '{stopname}'...")
            coords = geocode_location(stopname)
            if coords:
                lat, lon = coords
            else:
                print(f"❌ Could not retrieve coordinates for stopid {stopid}")
                continue  # Pula se não conseguir geocodificar
        else:
            # Converter de string para float, se necessário
            try:
                lat = float(lat)
                lon = float(lon)
            except (ValueError, TypeError):
                if not geocode_fallback:
                    print(f"❌ Invalid lat/lon format for stopid {stopid}: ({lat}, {lon})")
                    continue

                print(f"❌ Invalid lat/lon format for stopid {stopid}, geocoding by name: '{stopname}'...")
                coords = geocode_location(stopname)
                if not coords:
                    continue
                lat, lon = coords

        # Armazenar no dicionário
        stop_coords[stopid] = {
            'lat': lat,
            'lon': lon,
            'stopname': stopname
        }

        # Pausa para respeitar os termos de uso do Nominatim
        time.sleep(delay)

    return stop_coords
    
    
key = "1rCp6RqilhvGhFNh_iZcesXwgUcR_Cc_kHAU117hV4zQ"
#key="1EYGny7QH-49pTEkS-bIiFC3W_NzcFcVE6eksDd09CUM" # teste richard
link='https://docs.google.com/spreadsheet/ccc?key='+key
print(link)
link+='&output=csv'
df = pd.read_csv(link, sep=',')


if  'ativa' in df.columns:
    df=df[df['ativa']!='n']

# API URL with query parameters
url = "https://bus2.services/api-b2b/sobe-desce"

# Query parameters
params = {
    "startDate": "2024-12-01",
    "endDate": "2024-12-05",
    "routeShortName": "190",
    "page": 1,
    "limit": 30
}

# Headers
headers = {
    "accept": "*/*",
    "x-api-key": "cb66e329-eaca-4cbb-bc31-914e20c25f86"
}



#curl -X 'GET' \
#  'https://bus2.services/api-b2b/sobe-desce?startDate=2025-01-01&endDate=2025-01-10&routeShortName=105&page=1&limit=20' \
#  -H 'accept: /' \
#  -H 'x-api-key: cb66e329-eaca-4cbb-bc31-914e20c25f86'
  
  
for index, row in df.iterrows():
    params = {
        "startDate": row['startDate'],
        "endDate": row['endDate'],
        "routeShortName": str(row['routeShortName']),
        "page": int(row['page']),
        "limit": int(row['limit'])
    }
    
    print(params)
        
    # Make the GET request
    response = requests.get(url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
    
        # Save to a JSON file
        routeShortName = str(row['routeShortName'])
        filename = f"bus_route_{routeShortName}.json"
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
        #print(f"Success! Data saved to {filename}")
    else:
        print(f"Error: {response.status_code}")
        print("Response text:", response.text)

        
    data= response.json()    
    if len(data['data'])> 0:
        aux = pd.DataFrame(data['data'])
        l=aux['routeshortname'].unique()[0]
        aux.to_csv(f'{l}.csv', sep=',', index=None)    
        print(l, len(data['data']))
        # --- Convert coordinates to float and sort by stopsequence ---
        stops = sorted(data['data'], key=lambda x: x['stopsequence'])
        #print(stops[0]['stop_lat'])
        #stops, stop_coords_map = fill_missing_stop_coordinates(
        #    stops=stops,
        #    geocode_func=geocode_location,  # Sua função de geocodificação
        #    delay=1.0
        #)
        
        #coordinates = [(float(stop['stop_lat']), float(stop['stop_lon'])) for stop in stops]
        coordinates = [
            (float(stop['stop_lat']), float(stop['stop_lon']))
            for stop in stops
            if stop['stop_lat'] is not None 
            and stop['stop_lon'] is not None
            and stop['stop_lat'] != ''
            and stop['stop_lon'] != ''
            and isinstance(stop['stop_lat'], (str, int, float))
            and isinstance(stop['stop_lon'], (str, int, float))
        ]
        
        for s,stop in enumerate(stops):
            print(s, stop['stopid'], stop['stop_lat'], stop['stop_lon'])
        
        
        
        # --- Initialize map centered at first stop ---
        start_lat, start_lon = coordinates[0]
        map_route = folium.Map(location=[start_lat, start_lon], zoom_start=14)
        
        # --- Add stop markers with info ---
        for stop in stops:
            lat = float(stop['stop_lat'])
            lon = float(stop['stop_lon'])
            name = stop['stopname']
            seq = stop['stopsequence']
            occ = stop['occupation']
            popup_text = f"#{seq} - {name}<br>Occupation: {occ}"
            
            folium.Marker(
                location=[lat, lon],
                popup=popup_text,
                icon=folium.Icon(color='blue' if occ == 0 else 'red', icon='bus', prefix='fa')
            ).add_to(map_route)
        
        # --- Add polyline connecting the stops ---
        folium.PolyLine(coordinates, color="blue", weight=3, opacity=0.7).add_to(map_route)
        
        # --- Save and/or show ---
        map_route.save(f"bus_route_{routeShortName}.html")
        

#%%
         
#%%