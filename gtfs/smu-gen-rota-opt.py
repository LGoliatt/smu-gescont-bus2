import requests
import numpy as np
import folium
import folium
import requests
import polyline
import numpy as np    
import requests
import numpy as np
      
import numpy as np
import pulp


from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def get_valhalla_distance_matrix(coordinates, fixed_speed=14):
    """Create an asymmetric distance matrix using Valhalla API."""
    n = len(coordinates)
    # Initialize matrix with zeros
    distance_matrix = np.zeros((n, n))
    
    # Prepare JSON payload for Valhalla API
    sources = [{"lat": lat, "lon": lon} for lat, lon in coordinates]
    targets = [{"lat": lat, "lon": lon} for lat, lon in coordinates]
    payload = {
        "sources": sources,
        "targets": targets,
        "costing": "bus",
        "costing_options": {
            "bus": {
                "fixed_speed": fixed_speed  # Set fixed speed in km/h
            }
        },
        "units": "meters"
    }
    
    # Valhalla API endpoint
    url = "https://valhalla1.openstreetmap.de/sources_to_targets"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract distances from response
        for i, source in enumerate(data.get("sources_to_targets", [])):
            for j, target in enumerate(source):
                distance = target.get("distance", float('inf'))
                distance_matrix[i][j] = distance * 1000  # Convert kilometers to meters
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching distance matrix: {e}")
        return np.full((n, n), float('inf'))  # Return matrix with infinities on error
    
    # Set diagonal to 0 (distance from a point to itself)
    np.fill_diagonal(distance_matrix, 0)
    
    return distance_matrix



def solve_tsp_asymmetric(distance_matrix):
    """
    Resolve o problema do Caixeiro Viajante (TSP) para uma matriz de distâncias assimétrica.
    
    Args:
        distance_matrix (list of list of float): Matriz assimétrica de distâncias entre os pontos.
    
    Returns:
        list: A rota ótima encontrada.
        int: O custo total da rota ótima.
    """
    # Número de nós (pontos)
    num_nodes = len(distance_matrix)

    # Cria o gerenciador de índices de nós
    manager = pywrapcp.RoutingIndexManager(num_nodes, 1, 0)  # 1 veículo, nó inicial/final é o índice 0

    # Cria o modelo de roteamento
    routing = pywrapcp.RoutingModel(manager)

    # Define a função de custo (distância entre os nós)
    def distance_callback(from_index, to_index):
        """Retorna a distância entre dois nós."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Define as opções de busca para encontrar a solução
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Resolve o problema
    solution = routing.SolveWithParameters(search_parameters)

    # Extrai a rota ótima
    if solution:
        index = routing.Start(0)
        route = []
        total_cost = 0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            total_cost += routing.GetArcCostForVehicle(previous_index, index, 0)
        route.append(manager.IndexToNode(index))  # Adiciona o nó final (que é o nó inicial)
        return route, total_cost
    else:
        raise ValueError("Nenhuma solução foi encontrada.")



def solve_asymmetric_tsp(distance_matrix):
    n = len(distance_matrix)
    
    # Define o problema
    prob = pulp.LpProblem("Asymmetric_TSP", pulp.LpMinimize)

    # Variáveis de decisão: x[i][j] = 1 se o caminho vai de i para j
    x = [[pulp.LpVariable(f"x_{i}_{j}", cat='Binary') for j in range(n)] for i in range(n)]

    # Variáveis auxiliares para sub-tour elimination (MTZ)
    u = [pulp.LpVariable(f"u_{i}", lowBound=0, upBound=n-1, cat='Integer') for i in range(n)]

    # Função objetivo
    prob += pulp.lpSum(distance_matrix[i][j] * x[i][j] for i in range(n) for j in range(n) if i != j)

    # Restrições de entrada única
    for j in range(n):
        prob += pulp.lpSum(x[i][j] for i in range(n) if i != j) == 1

    # Restrições de saída única
    for i in range(n):
        prob += pulp.lpSum(x[i][j] for j in range(n) if i != j) == 1

    # Sub-tour elimination (restrições de Miller–Tucker–Zemlin)
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                prob += u[i] - u[j] + (n - 1) * x[i][j] <= n - 2

    # Resolver
    solver = pulp.PULP_CBC_CMD(msg=0)
    prob.solve(solver)

    # Resultado
    tour = []
    current = 0
    visited = set([0])
    while len(visited) < n:
        for j in range(n):
            if j != current and pulp.value(x[current][j]) == 1:
                tour.append((current, j))
                current = j
                visited.add(j)
                break
    tour.append((current, 0))  # retorna à origem

    total_distance = pulp.value(prob.objective)
    return tour, total_distance



def plot_tsp_route(coordinates, tour, zoom_start=16):
    """
    Plota a rota ótima do TSP em um mapa Leaflet usando OSRM para trajetos reais.
    
    Parâmetros:
    - coordinates: lista de tuplas (lat, lon)
    - tour: lista de pares (origem, destino) indicando a sequência do TSP
    - zoom_start: nível inicial de zoom do mapa

    Retorno:
    - Objeto folium.Map com a rota plotada
    """
    
    def format_coords(c):
        return f"{c[1]},{c[0]}"  # Formato lon,lat exigido pelo OSRM

    # Reconstrói a ordem dos pontos visitados a partir do tour
    ordered_points = [tour[0][0]]  # começa pelo ponto inicial
    for origem, destino in tour:
        ordered_points.append(destino)

    # Inicializa o mapa no primeiro ponto
    m = folium.Map(location=coordinates[ordered_points[0]], zoom_start=zoom_start, control_scale=True)

    # Adiciona marcadores com ordem da visita
    for ordem, idx in enumerate(ordered_points):
        lat, lon = coordinates[idx]
        folium.Marker(
            location=(lat, lon),
            popup=f"Ponto {idx} (Ordem {ordem + 1})",
            tooltip=f"Ordem {ordem + 1}: Ponto {idx}",
            icon=folium.Icon(color="green" if ordem == 0 else "blue", icon="info-sign")
        ).add_to(m)

    # Adiciona linhas da rota usando OSRM
    for origem, destino in tour:
        start = format_coords(coordinates[origem])
        end = format_coords(coordinates[destino])
        
        url = f"http://router.project-osrm.org/route/v1/driving/{start};{end}?overview=full&geometries=geojson"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            route_coords = data['routes'][0]['geometry']['coordinates']
            route_coords_latlon = [(lat, lon) for lon, lat in route_coords]
            
            folium.PolyLine(
                locations=route_coords_latlon,
                color='red',
                weight=4,
                opacity=0.8
            ).add_to(m)
        else:
            print(f"Erro na requisição OSRM: {origem} → {destino}")

    return m



def create_tsp_map_osrm(coordinates, tour):
    """
    Create a Folium map with markers and OSRM-calculated route for the TSP tour.
    
    Args:
        coordinates: List of [lat, lon] coordinates.
        tour: List of indices representing the TSP tour (closed route).
    
    Returns:
        Folium map object.
    """
    # Calculate map center (average of coordinates)
    avg_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
    avg_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
    
    # Initialize Folium map
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=15, tiles='OpenStreetMap')
    
    # Add markers with popups
    for idx, coord in enumerate(coordinates):
        tour_pos = tour.index(idx) if idx in tour else -1
        folium.Marker(
            location=coord,
            popup=f'Point {idx}<br>Tour position: {tour_pos}',
            icon=folium.Icon(color='blue' if idx != tour[0] else 'red')  # Highlight starting point
        ).add_to(m)
    
    # Fetch routes from OSRM for each segment of the tour
    for i in range(len(tour) - 1):
        start_idx = tour[i]
        end_idx = tour[i + 1]
        start_coord = coordinates[start_idx]
        end_coord = coordinates[end_idx]
        
        # OSRM API request
        url = f"http://router.project-osrm.org/route/v1/driving/{start_coord[1]},{start_coord[0]};{end_coord[1]},{end_coord[0]}?overview=full&geometries=polyline"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("code") != "Ok":
                print(f"Error fetching route from {start_coord} to {end_coord}: {data.get('message', 'Unknown error')}")
                continue
            
            # Decode polyline from OSRM response
            encoded_polyline = data["routes"][0]["geometry"]
            route_coords = polyline.decode(encoded_polyline, 5)  # OSRM uses precision 5
            
            # Add polyline to map
            folium.PolyLine(
                locations=route_coords,
                color='blue',
                weight=4
            ).add_to(m)
            
        except (requests.RequestException, KeyError) as e:
            print(f"Error fetching route from {start_coord} to {end_coord}: {e}")
            continue
    
    # Fit map to bounds
    bounds = [[min(coord[0] for coord in coordinates), min(coord[1] for coord in coordinates)],
              [max(coord[0] for coord in coordinates), max(coord[1] for coord in coordinates)]]
    m.fit_bounds(bounds, padding=(50, 50))
    
    return m

#%%


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

coordinates = [
    (-21.71004404754758, -43.41511321637027),
    (-21.70809034249162, -43.41615391337419),
    (-21.7082897013655, -43.417055135521906),
    (-21.706993863748973, -43.4182567650522),
    (-21.70971510926749, -43.41924381788065),
    (-21.707651751996988, -43.41923308904556),
    (-21.710353049489413, -43.42050982042148),
    (-21.705499734435726, -43.42062377765296),
    (-21.708978569768526, -43.421911237863995),
    (-21.70612772521326, -43.42296266385977),
    (-21.703785205818367, -43.42152499995746),
    (-21.704094221197877, -43.421900509185676),
    (-21.703127299897563, -43.42364930930565),
    (-21.701093753460132, -43.42546248253875),
    (-21.702439485947824, -43.42666411222967),
    (-21.705021263396446, -43.42730784236132),
    (-21.70510100867956, -43.427340028866595),
    (-21.706666000919377, -43.42502260048675),
    (-21.707842225924153, -43.42430376853561),
    (-21.709457027645637, -43.425966737974846),
    (-21.71065316544221, -43.423788784436674),
    (-21.71179945478128, -43.423670767250655),
    (-21.71180942247461, -43.42600965330069),
    (-21.71079271419774, -43.426953790788765),
    (-21.712198161976122, -43.426814315932575),
    (-21.712875961734717, -43.42312359667937),
    (-21.71384281753957, -43.42451834524132),
    (-21.714670121987467, -43.4249367698099),
    (-21.71029432515078, -43.427983759039854),
    (-21.706636096762452, -43.42777991116053),
    (-21.705938331478865, -43.428284166409846)
]



# Generate and print the distance matrix
distance_matrix = get_valhalla_distance_matrix(coordinates)
print("Asymmetric Distance Matrix (in meters):")
np.set_printoptions(precision=2, suppress=True)
print(distance_matrix)   


# Chama a função para resolver o TSP
#optimal_route, total_distance = solve_asymmetric_tsp(distance_matrix)
optimal_route, total_distance = solve_tsp_asymmetric(distance_matrix)
#print("Distância total:", total)

# Imprime os resultados
print("Rota Ótima:", optimal_route)
print("Distância Total:", total_distance) 


# Tour ótimo (índices)
#m = plot_tsp_route(coordinates, optimal_route)

# m.save("rota_tsp_leaflet.html")

   
# Optimal tour from previous context

# Create map
m = create_tsp_map_osrm(coordinates, optimal_route)

# Save map to HTML for testing
m.save('rota_tsp_leaflet.html')
print("Map saved as 'rota_tsp_leaflet.html' for testing.")

#%%    

