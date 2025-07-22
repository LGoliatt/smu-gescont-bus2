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

key = "1rCp6RqilhvGhFNh_iZcesXwgUcR_Cc_kHAU117hV4zQ"
#key="1EYGny7QH-49pTEkS-bIiFC3W_NzcFcVE6eksDd09CUM" # teste richard
link='https://docs.google.com/spreadsheet/ccc?key='+key+'&output=csv'
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
        
        coordinates = [(float(stop['stop_lat']), float(stop['stop_lon'])) for stop in stops]
        
        
        
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