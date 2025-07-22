import requests
import json
import time
import pandas as pd

def get_neighborhood_locations(city="Juiz de Fora", state="Minas Gerais", country="Brasil"):
    """
    Busca a latitude e longitude de uma lista de bairros em uma cidade/estado/país especificados.
    Utiliza a API pública do OpenStreetMap Nominatim.

    Args:
        city (str): Nome da cidade.
        state (str): Nome do estado.
        country (str): Nome do país.

    Returns:
        pandas.DataFrame: Um DataFrame com o nome do bairro, latitude e longitude,
                          ou None em caso de erro.
    """
    # Lista de bairros de Juiz de Fora (extraída da Wikipédia para demonstração)
    # Esta lista pode ser expandida ou carregada de uma fonte externa.
    
    
    neighborhoods = [
        "Aeroporto", "Alto dos Passos", "Barão do Retiro", "Benfica", "Boa Vista",
        "Bom Pastor", "Borboleta", "Cascatinha", "Centro", "Floresta",
        "Granbery", "Jardim Glória", "Manoel Honório", "Mariano Procópio", "Martelos",
        "Nossa Senhora Aparecida", "Nossa Senhora de Lourdes", "Nova Era",
        "Poço Rico", "Progresso", "Sagrado Coração de Jesus", "Salvaterra",
        "Santa Helena", "São Mateus", "São Pedro", "Vila Ideal",
        "São Geraldo", "Santa Luzia", "Industrial", "Linhares", "Monte Castelo",
        "Bairros expandidos:",
        "Aracy", "Bandeirantes", "Baviera", "Bela Aurora", "Caiçaras",
        "Carlos Chagas", "Cerâmica", "Cidade Alta", "Cruzeiro do Sul", "Eldorado",
        "Fábrica", "Francisco Bernardino", "Grajaú", "Graminha", "Jardim Primavera",
        "Jardim São João", "Jóquei Clube", "Lagoa", "Milho Branco", "Morro da Glória",
        "Mundo Novo", "Nova Califórnia", "Novo Horizonte", "Parque Guarani", "Retiro",
        "Santa Cecília", "Santa Cruz", "Santa Efigênia", "Santa Rita de Cássia",
        "Santa Terezinha", "Santo Antônio", "São Benedito", "São Judas Tadeu",
        "Teixeiras", "Vale do Ipê", "Vila Ozanan", "Vitorino Braga"
    ]
    neighborhoods = [        
        "Benfica","Nova Era","Nova Era I","Nova Era II","Nova Era III",
        'Nova Benfica','Cidade do Sol',
        'Jóquei Clube',
         'Vila Esperança', 'Vila Esperança II',
        'Ponte Preta', 'Distrito Industrial', 'Santa Lúcia',
        #
        'Barreira do Triunfo','Náutico', 'Nautico', 'Novo Triunfo','Miguel Marinho',
        'Jóquei Clube II', 'Jóquei Clube III','Barbosa Lage',
        'Bairro Industrial','Bairro Araújo','Araújo',
        #
        'Linhares', 'Bom Jardim',
        #
        "Grama", 'Vila Montanhesa','Parque Guarani', 'Granjas Bethânia',
        'Granjas Bethanea','Granjas Betânea','Granjas Bethanea',
        'Parque Independência', 'Nova Suissa', 'Nova Suiça', 
        'Vivendas da Serra','Recanto dos Lagos',
        #    
        'Filgueiras', 'Granjas Triunfo',
        #
        "Aeroporto", "Salvaterra", "Teixeiras",
        #
        "Sagrado Coração de Jesus", "São Geraldo", "Santa Luzia",
        'Bela Aurora', 'Ipiranga','Santa Efigênia','Santa Efigenia', 
        'Cidade Nova', 'Vale Verde', 'Arco-íris', 'Jardim de Alá',
        'Previdenciários', 
        'Jardim Gaúcho',
        #
        "São Judas Tadeu", 'Santa Cruz',
        #
        'Monte Castelo', 'Carlos Chagas', 'Jardim Natal', 'Milho Branco',
        'Amazônia', 'Francisco Bernardino',
        #
        'Floresta', 'Barão do Retiro', 'Usina 4', 'Caetés', 'Retiro', 
        'Parque das Palmeiras', 'Granjas Bethel',
        #
        'Monte Verde de Minas', 'Torreões','Paula Lima', 'Torreões',
        #
        "Alto dos Passos", "Barão do Retiro", "Boa Vista",
        "Bom Pastor", "Borboleta", "Cascatinha", "Centro", "Floresta",
        "Granbery", "Jardim Glória", "Manoel Honório", "Mariano Procópio", "Martelos",
        "Nossa Senhora Aparecida", "Nossa Senhora de Lourdes", 
        "Poço Rico", "Progresso",
        "Santa Helena", "São Mateus", "São Pedro", "Vila Ideal",
        "Monte Castelo",
        "Aracy", "Bandeirantes", "Baviera", "Caiçaras",
        "Carlos Chagas", "Cerâmica", "Cidade Alta", "Cruzeiro do Sul", "Eldorado",
        "Fábrica", "Francisco Bernardino", "Grajaú", "Graminha", "Jardim Primavera",
        "Jardim São João", "Jóquei Clube", "Lagoa", "Milho Branco", "Morro da Glória",
        "Mundo Novo", "Nova Califórnia", "Novo Horizonte", "Parque Guarani", "Retiro",
        "Santa Cecília", "Santa Cruz", "Santa Efigênia", "Santa Rita de Cássia",
        "Santa Terezinha", "Santo Antônio", "São Benedito", "São Judas Tadeu",
        "Teixeiras", "Vale do Ipê", "Vila Ozanan", "Vitorino Braga"
    ]

    base_url = "https://nominatim.openstreetmap.org/search"
    results = []

    print(f"Buscando localizações para bairros em {city}, {state}, {country}...")

    for neighborhood in neighborhoods:
        query = f"{neighborhood}, {city}, {state}, {country}"
        params = {
            "q": query,
            "format": "json",
            "limit": 1,  # Pega o melhor resultado
            "addressdetails": 0 # Não precisamos de detalhes completos do endereço aqui
        }
        headers = {
            "User-Agent": "NeighborhoodGeocodingApp/1.0 (your_email@example.com)" # Substitua pelo seu email ou nome da aplicação
        }

        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status() # Levanta um erro para status de resposta HTTP ruins (4xx ou 5xx)

            data = response.json()

            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                results.append({
                    "Bairro": neighborhood,
                    "Latitude": lat,
                    "Longitude": lon
                })
                print(f"Encontrado: {neighborhood} (Lat: {lat:.6f}, Lon: {lon:.6f})")
            else:
                results.append({
                    "Bairro": neighborhood,
                    "Latitude": None,
                    "Longitude": None
                })
                print(f"Não encontrado: {neighborhood}")

        except requests.exceptions.RequestException as e:
            print(f"Erro de requisição para {neighborhood}: {e}")
            results.append({"Bairro": neighborhood, "Latitude": None, "Longitude": None})
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON para {neighborhood}: {e}")
            print(f"Resposta bruta: {response.text}")
            results.append({"Bairro": neighborhood, "Latitude": None, "Longitude": None})
        except Exception as e:
            print(f"Ocorreu um erro inesperado para {neighborhood}: {e}")
            results.append({"Bairro": neighborhood, "Latitude": None, "Longitude": None})

        time.sleep(1.5) # Pausa para respeitar a política de uso justo do Nominatim (1 requisição/segundo)

    return pd.DataFrame(results)

# --- Exemplo de Uso da Função ---
if __name__ == "__main__":
    neighborhood_df = get_neighborhood_locations(city="Juiz de Fora", state="Minas Gerais", country="Brasil")
    
    neighborhood_df.to_csv('bairros_jf.csv', sep=';', index=False)

    if neighborhood_df is not None:
        print("\n--- Localização dos Bairros de Juiz de Fora ---")
        print(neighborhood_df.to_string(index=False))
    else:
        print("\nNão foi possível obter a lista de bairros.")
        


#%%
    import overpy
    
    api = overpy.Overpass()
    
    query = """
        area["name"="Juiz de Fora"]["admin_level"="8"];
        node["place"="suburb"](area);
        out body;
    """
    
    result = api.query(query)
    
    bairros = []
    
    for node in result.nodes:
        nome_bairro = node.tags.get("name", "Sem Nome")
        lat = node.lat
        lon = node.lon
        bairros.append({"Bairro": nome_bairro, "Latitude": lat, "Longitude": lon})
    
    # Salvar CSV
    import pandas as pd
    df = pd.DataFrame(bairros)
    df.to_csv("bairros_jf_osm.csv", index=False, sep=";", decimal=",")
    print("✅ Arquivo 'bairros_jf_osm.csv' gerado com sucesso!")
    print(df.head())

