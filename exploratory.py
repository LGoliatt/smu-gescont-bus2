import pandas as pd
import folium
import pandas as pd
import folium
from folium.plugins import HeatMap
import glob
import os


# Step 0: 
csv_file = "sobe_desce_jf.csv"  # Replace with the actual file path
csv_file = 'sobe_desce_jf_horarios.csv'
#df = pd.read_csv(csv_file)
for s,df1 in df.groupby('routeshortname'):
    df1.to_csv(f'./data_stops/{s}.csv', index=False)    

data=df[df['routeshortname']==100]
#%%

# 1. Carregar todos os CSVs da pasta "./data_stops"
lista_arquivos = glob.glob(os.path.join("data_stops", "*.csv"))
df = pd.concat((pd.read_csv(arquivo) for arquivo in lista_arquivos), ignore_index=True)


col='boarding'
# 2. Agregar por latitude e longitude, somando a quantidade de embarques
agrupado = df.groupby(['stop_lat', 'stop_lon'], as_index=False)[col].sum()

# 3. Normalizar a coluna 'boarding' para o intervalo 0-100
min_b = agrupado[col].min()
max_b = agrupado[col].max()
agrupado['intensidade'] = 100 * (agrupado[col] - min_b) / (max_b - min_b)**1

#%%
# 4. Criar um mapa centralizado no ponto médio
mapa = folium.Map(location=[agrupado['stop_lat'].mean(), agrupado['stop_lon'].mean()], zoom_start=13)

# 5. Adicionar círculos ao mapa
for _, row in agrupado.iterrows():
    folium.CircleMarker(
        location=[row['stop_lat'], row['stop_lon']],
        radius=0 + (row['intensidade'] / 5),  # tamanho proporcional
        color='blue',
        fill=True,
        fill_opacity=0.1,
        popup=f"{col}: {row[col]}, Intensidade: {row['intensidade']:.1f}"
    ).add_to(mapa)

# 6. Salvar o mapa
mapa.save("mapa_interativo.html")
print("Mapa salvo como mapa_interativo.html")

#%%
import pandas as pd
import folium
from folium.plugins import HeatMap

# Caminho do CSV
#caminho_csv = "100.csv"  # altere se necessário

# 4. Criar o mapa base
mapa = folium.Map(location=[agrupado['stop_lat'].mean(), agrupado['stop_lon'].mean()], zoom_start=12)

# 5. Adicionar camada de HeatMap
heat_data = [[row['stop_lat'], row['stop_lon'], row['intensidade']] for _, row in agrupado.iterrows()]
HeatMap(heat_data, min_opacity=0.2, max_val=100, radius=15, blur=5).add_to(mapa)

# 6. Salvar o mapa como HTML
mapa.save("mapa_heatmap.html")
print("Heatmap salvo como mapa_heatmap.html")

#%%
