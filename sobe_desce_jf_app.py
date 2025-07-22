import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium, folium_static
import os
import plotly.express as px
import numpy as np
import math

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to calculate Haversine distance
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two points on the Earth.
    :param lat1, lon1: Latitude and Longitude of point 1 (in decimal degrees)
    :param lat2, lon2: Latitude and Longitude of point 2 (in decimal degrees)
    :return: Distance in kilometers
    """
    R = 6371  # Earth radius in kilometers

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Differences
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    return R * c

# Function to snap newer points to the closest older points
def snap_newer_to_older(df):
    """
    Snap newer points to the closest older points in the DataFrame.
    :param df: DataFrame with 'stop_lat' and 'stop_lon' columns
    :return: Modified DataFrame where newer points are replaced by the closest older points
    """
    # Create a copy of the DataFrame to modify
    snapped_df = df.copy()

    # Iterate through each row starting from the second point (newer points)
    for i in range(1, len(snapped_df)):
        min_distance = float(15/1000.)  # Initialize minimum distance to infinity
        closest_index = i  # To store the index of the closest older point

        # Compare the current point with all older points
        for j in range(i):
            distance = haversine_distance(
                snapped_df.loc[i, 'stop_lat'], snapped_df.loc[i, 'stop_lon'],
                snapped_df.loc[j, 'stop_lat'], snapped_df.loc[j, 'stop_lon']
            )
            if distance < min_distance:
                min_distance = distance
                closest_index = j
                

        # Replace the newer point's coordinates with the closest older point's coordinates
        snapped_df.loc[i, 'stop_lat'] = snapped_df.loc[closest_index, 'stop_lat']
        snapped_df.loc[i, 'stop_lon'] = snapped_df.loc[closest_index, 'stop_lon']

    return snapped_df

def recomendar_onibus_por_demanda(df, frequencia=1):
    """
    Recomenda tipos de ônibus com base na demanda horária de embarque (boarding).
    
    Parâmetros:
    - df: DataFrame com colunas 'hour' e 'boarding'
    - frequencia: número de viagens por hora (pode ser float, ex: 2.0 = a cada 30 min)
                  ou uma lista/Series com frequência por hora
    
    Retorna:
    - DataFrame com colunas: hour, boarding, frequencia, passageiros_por_viagem, tipos_recomendados
    """
    
    # Definir tipos de ônibus e suas capacidades mínimas (reais típicas)
    tipos_onibus = [
        {'tipo': 'Micro-ônibus M2/M3', 'min': 16, 'max': 20},
        {'tipo': 'Miniônibus',        'min': 21, 'max': 35},
        {'tipo': 'Midiônibus',        'min': 40, 'max': 60},
        {'tipo': 'Ônibus Básico',     'min': 70, 'max': 80},
        {'tipo': 'Ônibus Padron',     'min': 80, 'max': 90},
        {'tipo': 'Articulado',        'min': 100, 'max': 140},
        {'tipo': 'Biarticulado',      'min': 160, 'max': 200}
    ]
    
    # Criar cópia do DataFrame
    resultado = df.copy()
    
    # Calcular frequência (se for escalar, repete para todos)
    if isinstance(frequencia, (int, float)):
        resultado['frequencia'] = frequencia
    elif isinstance(frequencia, (list, pd.Series)):
        resultado['frequencia'] = pd.Series(frequencia).values
    else:
        raise ValueError("Frequência deve ser número, lista ou série.")
    
    # Calcular passageiros por viagem
    resultado['passageiros_por_viagem'] = resultado['boarding'] / resultado['frequencia']
    
    # Função interna para recomendar tipos com base na demanda por viagem
    def escolher_tipos(demanda):
        tipos = []
        for t in tipos_onibus:
            # Considerar 85% da capacidade como limite seguro
            capacidade_efetiva = t['max'] * 0.85
            if demanda <= capacidade_efetiva:
                tipos.append(t['tipo'])
        # Retorna os tipos que atendem, do menor para o maior
        return ", ".join(tipos) if tipos else tipos_onibus[-1]['tipo']
    
    resultado['tipos_recomendados'] = resultado['passageiros_por_viagem'].apply(escolher_tipos)
    
    return resultado[[
        'hour', 'boarding', 'frequencia', 
        'passageiros_por_viagem', 'tipos_recomendados'
    ]]


import pandas as pd
import numpy as np
import plotly.graph_objects as go

def analise_frota_onibus_plotly(df, frequencia=None):
    """
    Analisa frota necessária e retorna um DataFrame e um gráfico Plotly interativo.
    
    Parâmetros:
    - df: DataFrame com colunas 'hour' e 'boarding'
    - frequencia: escalar, lista ou série com frequência de viagens por hora
    
    Retorna:
    - df_result: DataFrame com análise detalhada
    - fig: objeto plotly.graph_objects.Figure
    """
    
    cap = [20, 35, 60, 80, 90, #140, 200
           ]
    
    # Capacidades de ônibus (85% de ocupação segura)
    frota = pd.DataFrame({
        'tipo': [
            'Micro-ônibus M2/M3',
            'Miniônibus',
            'Midiônibus',
            'Ônibus Básico',
            'Ônibus Padron',
            #'Articulado',
            #'Biarticulado'
        ],
        'capacidade_nominal': cap,
        'capacidade_util': [int(i * 0.95) for i in cap],
    })

    # Mapeamento de cores por tipo
    cores = {
        'Micro-ônibus M2/M3': '#FF9999',
        'Miniônibus': '#FFD700',
        'Midiônibus': '#66BB6A',
        'Ônibus Básico': '#42A5F5',
        'Ônibus Padron': '#1E88E5',
        #'Articulado': '#8E24AA',
        #'Biarticulado': '#3E2723'
    }

    # Preparar dados
    df_work = df.copy()
    if 'hour' not in df_work.columns:
        raise ValueError("DataFrame must have a 'hour' column.")
    if frequencia is None:
        df_work['frequencia'] = 1.0
    elif isinstance(frequencia, (int, float)):
        df_work['frequencia'] = frequencia
    else:
        df_work['frequencia'] = pd.Series(frequencia).values

    # Garantir que 'hour' seja string no formato HH:MM
    df_work['hour'] = df_work['hour'].astype(str).str.split().str[-1]  # extrai HH:MM se tiver data
    df_work['hour_dt'] = pd.to_datetime(df_work['hour'], format='%H:%M', errors='coerce')
    df_work = df_work.sort_values('hour_dt').reset_index(drop=True)

    resultados = []

    for _, row in df_work.iterrows():
        hora = row['hour']
        demanda = row['boarding']  # assumindo que a coluna se chama 'boarding'
        freq = row['frequencia']
        pass_por_viagem = demanda / freq

        # Calcular frota necessária para cada tipo
        frota_req = frota.copy()
        frota_req['onibus_necessarios'] = np.ceil(demanda / frota_req['capacidade_util']).astype(int)

        # Encontrar tipo mais racional
        frota_viavel = frota_req[frota_req['capacidade_util'] >= pass_por_viagem]
        if not frota_viavel.empty:
            tipo_recomendado = frota_viavel.iloc[0]  # Menor tipo que atende 1 viagem
        else:
            tipo_recomendado = frota_req.loc[frota_req['onibus_necessarios'].idxmin()]

        # Alternativas com mesmo número de veículos
        alternativas = frota_req[frota_req['onibus_necessarios'] == tipo_recomendado['onibus_necessarios']]['tipo'].tolist()

        resultados.append({
            'hora': hora,
            'demanda_hora': round(demanda, 2),
            'frequencia': freq,
            'pass_por_viagem': round(pass_por_viagem, 2),
            'tipo_recomendado': tipo_recomendado['tipo'],
            'capacidade_util': tipo_recomendado['capacidade_util'],
            'onibus_necessarios': tipo_recomendado['onibus_necessarios'],
            'alternativas': ", ".join(alternativas),
            'cor': cores[tipo_recomendado['tipo']]
        })

    df_result = pd.DataFrame(resultados)

    # === CRIAR GRÁFICO PLOTLY (sem exibir, apenas retornar) ===
    fig = go.Figure()

    for _, row in df_result.iterrows():
        fig.add_trace(go.Bar(
            x=[row['hora']],
            y=[row['demanda_hora']],
            marker_color=row['cor'],
            name=row['tipo_recomendado'],  # para legenda
            hovertemplate=(
                f"<b>Hora:</b> {row['hora']}<br>"
                f"<b>Demanda/h:</b> {row['demanda_hora']} pax<br>"
                f"<b>Tipo:</b> {row['tipo_recomendado']}<br>"
                f"<b>Quantidade:</b> {row['onibus_necessarios']} veículo(s)<br>"
                f"<b>Capacidade útil:</b> {row['capacidade_util']} pax/viagem<br>"
                f"<b>Passageiros/viagem:</b> {row['pass_por_viagem']:.1f}<br>"
                f"<b>Alternativas:</b> {row['alternativas']}"
            ),
            showlegend=False,
            text=f"{row['onibus_necessarios']}×<br>{row['tipo_recomendado'].split()[0]}",
            textposition="outside",
            textfont=dict(size=10)
        ))

    # Layout
    fig.update_layout(
        title={
            'text': "Demanda Horária e Frota Recomendada<br><sup>Número e Tipo de Ônibus por Hora</sup>",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Hora do Dia",
        yaxis_title="Passageiros por Hora",
        xaxis=dict(tickmode='linear'),
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        hovermode="x unified",
        height=600,
        template="plotly_white",
        margin=dict(t=100, b=100, l=60, r=60)
    )

    # Não usar fig.show() — retorna para o Streamlit
    return df_result, fig

    
st.set_page_config(layout="wide")

# Step 1: Load the CSV file
# Define the folder path
folder_path = "data_stops"

# Initialize an empty list to store the cleaned filenames
file_list = []

# Iterate through all files in the folder
for file_name in os.listdir(folder_path):
    # Check if the file has a .csv extension
    if file_name.endswith(".csv"):
        # Remove the .csv suffix
        cleaned_name = file_name[:-4]  # Removes the last 4 characters (".csv")
        # Append the cleaned name to the list
        file_list.append(cleaned_name)

file_list.sort()


# Sidebar filters
st.sidebar.title("Filters")

# Route selector
route_options = file_list
selected_routes = st.sidebar.multiselect(
    "Select Route(s):",
    options=route_options,
    #default=None
    default=[route_options[0]] if len(route_options) > 0 else None
    #default=['100', '101', '102', '103', '104', '105',]
)

# Time selector for the selected route
#time_options = data['hour'].unique()
time_options=[#'01', '03', '04', 
              '05', '06', '07', '08', '09', '10', '11', '12',
              '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
time_options=[i+':00' for i in time_options]
time_options.sort()
selected_times = st.sidebar.multiselect(
        "Select Departure Time(s):",
        options=time_options,
        #default=[time_options[1]] if len(time_options) > 0 else None
        default=time_options
    )

selected_days = st.sidebar.multiselect(
        "Select Day(s) of Week:",
        options=['Monday', 'Tuesday', 'Wednesday',  'Thursday', 'Friday', 'Saturday', 'Sunday'],
        default=['Monday', 'Tuesday', 'Wednesday',  'Thursday', 'Friday', ]
    )


# # Day type selector
# day_type = st.sidebar.radio(
#     "Select Day Type to Visualize:",
#     options=['weekday', 'saturday', 'sunday']
# )

# Data type selector
data_type = st.sidebar.radio(
    "Select Data to Visualize:",
    options=['boarding', 'landing', 'occupation']
)

# # Hide line
# show_polyline = st.sidebar.radio(
#     "Show polyline:",
#     options=['No', 'Yes', ]
# )


# # Hide line
# show_markers = st.sidebar.radio(
#     "Show markers:",
#     options=['No', 'Yes', ]
# )
#%%
#selected_routes = route_options[:10]
#selected_times= time_options[0:10]
#%%
data=pd.DataFrame()
for selected_route in selected_routes:
    aux=pd.read_csv(f'./data_stops/{selected_route}.csv')
    data=pd.concat([data,aux], axis=0)

data['stop_lat'] = data['stop_lat'].round(4)
data['stop_lon'] = data['stop_lon'].round(4)
data['date'] = pd.to_datetime(data['day'])

def classify_day(date):
    # Monday=0, Sunday=6
    if date.dayofweek < 5:  # Weekdays are Monday (0) to Friday (4)
        return 'weekday'
    else:  # Saturday (5) and Sunday (6) are weekends
        #return 'weekend'
        return 'saturday' if date==5 else 'sunday'

data['day_type'] = data['date'].apply(classify_day)
data['hour'] = [i.split(':')[0]+':00' for i in data['departuretime']]
data['day_of_week'] = data['date'].dt.day_name()
data['day_of_week_number'] = data['date'].dt.dayofweek
#%%
# Filter data based on selections
df=data.copy()
filtered_df = df[
    (df['routeshortname'].isin([int(i) for i in selected_routes])) & 
    (df['hour'].isin([i for i in selected_times])) &
    #(df['departuretime'].isin([i for i in selected_times])) &
    (df['day_of_week'].isin([i for i in selected_days])) 
]

for c in ['routeshortname', 'hour', 'day_of_week']:
    print(c,':',filtered_df[c].unique()) 
#%%
numeric_columns = filtered_df.select_dtypes(include=['number']).columns
non_numeric_columns = filtered_df.select_dtypes(exclude=['number']).columns
#print("Numeric Columns:", numeric_columns)
#print("Non-Numeric Columns:", non_numeric_columns)
#filtered_df['hour'] = pd.to_datetime(filtered_df['hour'], format='%H:%M').dt.time

#df1 = filtered_df.groupby(['routeshortname','hour','stop_lon', 'stop_lat','stopname']).aggregate(lambda x: x.astype(float).mean())
df1 = filtered_df.groupby(['routeshortname', 'hour', 'stop_lon', 'stop_lat', 'stopname'], as_index=False).mean(numeric_only=True)

df1.reset_index(inplace=True)
#%%
#df2=df1.groupby(['stop_lon', 'stop_lat',]).aggregate(sum)
#df2 = df1.groupby(['stop_lon', 'stop_lat','stopname']).aggregate(sum)
df2 = df1.groupby(['stop_lon', 'stop_lat','stopname'], as_index=False).sum(numeric_only=True)
df2.reset_index(inplace=True)
#%%
#df3 = df1.groupby(['routeshortname','hour',]).aggregate(sum)
df3 = df1.groupby(['routeshortname','hour',], as_index=False).sum(numeric_only=True)
aux=df1.groupby(['routeshortname','hour',]).aggregate(np.max)
df3['occupation'] = aux['occupation'].values
df3.reset_index(inplace=True)
#%%
filtered_df=df2.copy()
# n_seq=len(filtered_df['routeshortname'].unique())==1
# if n_seq==1:
#     filtered_df.sort_values(by='stopsequence', inplace=True)

# Create two tabs

#tab1, tab2, tab3, tab4,  = st.tabs(["Routes Heatmap", "Bus Boarding/Time", "Bus Boarding/Time Acummulated", "Board-Landing"])
#tab1, tab2, tab3,   = st.tabs(["Routes Heatmap", "Bus Boarding/Time", "Bus Boarding/Time Acummulated", ])
tab1, tab2, tab3, tab4  = st.tabs(["Routes Heatmap", "Bus Boarding/Time", "Bus Boarding/Time Acummulated", "Bus Fleet"])

# Tab 1: Routes Heatmap
with tab1:
    #st.header("Routes Heatmap")
    st.write("This tab displays a heatmap of bus routes based on location intensity.")
    
    # Create map centered on the route stops
    if not filtered_df.empty:
        
        #st.title(f"Routes Heatmap")
        #toggle_circles = st.checkbox("Circles")
        #toggle_markers = st.checkbox("Markers")
        toggle_heatmap = st.checkbox("Heatmap")
    
        
        map_center = [filtered_df['stop_lat'].mean(), filtered_df['stop_lon'].mean()]
        m = folium.Map(location=map_center, zoom_start=14)
    
        # Prepare heatmap data
        #aux=snap_newer_to_older(filtered_df[['stop_lat', 'stop_lon']])
        #filtered_df['stop_lat'] = aux['stop_lat'].values
        #filtered_df['stop_lon'] = aux['stop_lon'].values
        #filtered_df=filtered_df.groupby(['stop_lon', 'stop_lat',]).aggregate(sum)
        #filtered_df.reset_index(inplace=True)   
        
        #if toggle_circles:
        #map_center = [filtered_df['stop_lat'].mean(), filtered_df['stop_lon'].mean()]
        #m = folium.Map(location=map_center, zoom_start=14)
    
        min_val = filtered_df[data_type].min()
        max_val = filtered_df[data_type].max()
        for _, row in filtered_df.iterrows():
            if row[data_type] > 0:
                folium.CircleMarker(
                    location=[row['stop_lat'], row['stop_lon']],
                    radius=(row[data_type] - min_val) / (max_val - min_val)*25,
                    #popup=f"{data_type}: {int(row[data_type])}",
                    popup=f"{row['stopname']}<br>data_type: {int(row[data_type])}",
                    color='blue',
                    fill=True,
                    fill_color='blue',
                    fill_opacity=0.6
                ).add_to(m)
        
        if toggle_heatmap:        
            # Add heatmap
            heat_data = filtered_df[['stop_lat', 'stop_lon', data_type]].values.tolist()
            HeatMap(heat_data,
                    #radius=15,
                    #blur=0,
                    #max_zoom=14,
                    #gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}
                   ).add_to(m)
        
        # if toggle_markers:
        #     marker_cluster = MarkerCluster().add_to(m)
        #     for idx, row in filtered_df.iterrows():
        #         for kk in range(math.ceil(row[data_type])):
        #             folium.CircleMarker(
        #                 location=[row['stop_lat'], row['stop_lon']],
        #                 #radius=row['radius'],  # Size of the circle
        #                 #color="blue",         # Border color
        #                 #fill=True,
        #                 #fill_color="blue",    # Fill color
        #                 #fill_opacity=0.6,
        #                 popup=f"{data_type}: {row[data_type]}",  # Popup text
        #             ).add_to(marker_cluster)
           
        # for idx, row in filtered_df.iterrows():
        #     # folium.CircleMarker(
        #     #     location=[row['stop_lat'], row['stop_lon']],
        #     #     radius=3,
        #     #     color='grey',
        #     #     fill=True,
        #     #     fill_color='white',
        #     #     fill_opacity=0.7,
        #     #     popup=f"Stop: {row['stopname']}<br>{data_type}: {row[data_type]}<br>Sequence: {row['stopsequence']}"
        #     # ).add_to(m)
        #     folium.CircleMarker(
        #             location=[row['stop_lat'], row['stop_lon']],
        #             radius=5,
        #             #color=color_palette[route_idx],
        #             fill=True,
        #             #fill_color=color_palette[route_idx],
        #             fill_opacity=0.7,
        #             #popup=f"""
        #             #    Route: {row['routeshortname']}<br>
        #             #    Time: {row['departuretime']}<br>
        #             #    Stop: {row['stopname']}<br>
        #             #    {data_type}: {row[data_type]}<br>
        #             #    Sequence: {row['stopsequence']}
        #             #"""
        #             popup=f"""
        #                 {data_type}: {row[data_type]}<br>
        #             """
        #         ).add_to(m)
        
        # if show_polyline=='Yes':
        # if n_seq==1:
        #     # Add route line
        #     folium.PolyLine(
        #         locations=filtered_df[['stop_lat', 'stop_lon']].values,
        #         color='grey',
        #         weight=1,
        #         opacity=0.5
        #     ).add_to(m)
    
        # Display the map
        #st.title(f"Route {selected_route} at {selected_time} - {data_type.capitalize()} Heatmap")
        #st_folium(m, width=700, height=500)
        
        # Show data table
        #st.subheader("Route Data")
        #st.dataframe(filtered_df[['stopsequence', 'stopname', 'boarding', 'landing', 'occupation']])
        #st_folium(m, width=1100, height=900)
        folium_static(m, width=1000, height=800)
        
    else:
        st.warning("No data available for the selected filters.")
   
# Tab 2: Bus Occupation
with tab2:
    #st.header("Bus Occupation")
    st.write("This tab shows the occupation percentage of buses on different routes.")
    filtered_df = df3.copy()
    filtered_df.sort_values(by=['hour','routeshortname'],inplace=True)
    if not filtered_df.empty:    
        fig = px.line(
            filtered_df.sort_values(by=['hour','routeshortname']),
            x='hour',
            y=data_type,
            color='routeshortname',
            #line_group='hour',
            hover_name='routeshortname',
            hover_data=['hour', data_type],
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Plotly,
            #template='plotly_white',
            height=600
        )
        
        # Customize layout
        fig.update_layout(
            xaxis_title='Hour',
            yaxis_title=data_type.capitalize(),
            legend_title='Route',
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20),
            font=dict(
                family="Arial",
                size=18,       # Global font size
                color="black"
            ),
            legend=dict(
                font=dict(size=16)
            ),
            xaxis=dict(
                title_font=dict(size=20),
                tickfont=dict(size=18)
            ),
            yaxis=dict(
                title_font=dict(size=20),
                tickfont=dict(size=18)
            )            
        )
        
        # Add annotations for peaks
        max_val = filtered_df[data_type].max()
        if max_val > 0:
            max_stop = filtered_df[filtered_df[data_type] == max_val].iloc[0]
            fig.add_annotation(
                x=max_stop['hour'],
                y=max_val,
                text=f"Max {data_type}: {max_val:.0f}",
                showarrow=True,
                arrowhead=1,
                ax=0,
                ay=-40,
                font=dict(size=18),
            )
        
        #fig.update_xaxes(title_font_size=18, tickfont_size=18)
        #fig.update_yaxes(title_font_size=18, tickfont_size=18)
        fig.update_traces(line=dict(width=4))
        fig.update_traces(marker=dict(size=12))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")
         
# tab 3: Bus Boarding/Time Acummulated        
with tab3:
    # st.header("Bus Occupation")
    st.write("This tab shows the accumulated occupation percentage of buses across all routes over time.")
    
    # Make a copy of the dataframe and filter if needed
    filtered_df = df3.copy()
    #print(filtered_df)
    if not filtered_df.empty:
        # Group by 'hour' and sum the selected data_type across all routes
        accumulated_df = filtered_df.groupby('hour')[data_type].sum().reset_index()
    
        # Plot the accumulated values
        fig = px.line(
            accumulated_df,
            x='hour',
            y=data_type,
            hover_data=['hour', data_type],
            markers=True,
            color_discrete_sequence=["#007BFF"],  # Single color for the line
            height=600
        )
    
        # Customize layout
        fig.update_layout(
            xaxis_title='Hour',
            yaxis_title=f'Total {data_type.capitalize()}',
            legend_title='Accumulated',
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20),
            font=dict(
                family="Arial",
                size=18,
                color="black"
            ),
            xaxis=dict(
                title_font=dict(size=20),
                tickfont=dict(size=18)
            ),
            yaxis=dict(
                title_font=dict(size=20),
                tickfont=dict(size=18)
            )
        )
    
        # Style the line and markers
        fig.update_traces(line=dict(width=4), marker=dict(size=12))
    
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("No data available for the selected filters.")    

      
# tab 4: Bus Fleet
with tab4:
    st.write("This tab shows the recommended bus fleet size and type per hour based on demand.")

    filtered_df = df3.copy()

    if not filtered_df.empty:
        # Certifique-se de que a coluna 'boarding' existe e 'hour' está formatada
        if 'boarding' not in filtered_df.columns:
            st.error("Column 'boarding' not found in data.")
        else:
            # Agrupar por hora
            accumulated_df = filtered_df.groupby('hour', as_index=False)['boarding'].sum()

            # Chamar função
            resultado, fig = analise_frota_onibus_plotly(accumulated_df, frequencia=1)

            # Opcional: ajustar estilo
            fig.update_traces(marker_line_color='rgb(8,48,107)', marker_line_width=1)

            # Exibir no Streamlit
            st.plotly_chart(fig, use_container_width=True)

            # (Opcional) Mostrar tabela
            with st.expander("View detailed fleet analysis"):
                st.dataframe(resultado)

    else:
        st.warning("No data available for the selected filters.") 

# with tab4:
    
#     # Upload do arquivo CSV
#     uploaded_file = st.file_uploader("Envie o arquivo CSV com os dados de transporte", type="csv")
    
#     if uploaded_file:
#         df = pd.read_csv(uploaded_file)
#         df.fillna(0, inplace=True)
    
#         # Pré-processamento
#         df['day'] = pd.to_datetime(df['day'])
#         df['departuretime'] = pd.to_datetime(df['departuretime'], format='%H:%M').dt.time
#         df['trip_id'] = df['routeshortname'].astype(str) + '_' + df['day'].astype(str) + '_' + df['departuretime'].astype(str)
    
#         # Seleção de viagem
#         viagens_disponiveis = df['trip_id'].unique()
#         viagem_selecionada = st.selectbox("Selecione uma viagem", viagens_disponiveis)
    
#         # Filtrar a viagem selecionada
#         df_viagem = df[df['trip_id'] == viagem_selecionada].copy()
#         df_viagem.sort_values(by='stopsequence', inplace=True)
    
#         # Gráfico sobe-desce com Plotly
#         fig = px.line(df_viagem,
#                       x='stopname',
#                       y= data_type,
#                       markers=True,
#                       title=f'Ocupação ao Longo da Rota - Viagem {viagem_selecionada}',
#                       labels={data_type: '', 'stopname': 'Parada'},
#                       height=700,
#                     )
    
#         #fig.update_layout(xaxis_tickangle=-90)
#         # Customize layout
#         fig.update_layout(
#                 #xaxis_title='Hour',
#                 yaxis_title=data_type.capitalize(),
#                 #legend_title='Route',
#                 hovermode='x unified',
#                 plot_bgcolor='rgba(0,0,0,0)',
#                 xaxis_tickangle=-90,
#                 margin=dict(l=20, r=20, t=30, b=20)
#             )
#         st.plotly_chart(fig)
    
#         # Mostrar tabela da viagem
#         with st.expander("Ver dados da viagem"):
#             st.dataframe(df_viagem[['stopsequence', 'stopname', 'boarding', 'landing', 'occupation']])
            
# Instructions
st.sidebar.markdown("""
**Instructions:**
1. Select a route from the dropdown
2. Choose a departure time
3. Select which data to visualize
4. The heatmap will update automatically
""")    