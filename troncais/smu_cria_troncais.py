import folium
import requests
import polyline
import pandas as pd

# === 1. Definir Rotas com Multiplos Waypoints e Nome dos Pontos ===
csv_file_path = './bairros_jf.csv'
df_bairros = pd.read_csv(csv_file_path, sep=';', encoding='utf-8')
df_bairros.columns=['Bairro', 'lat', 'lon']
bairros_dict = df_bairros.set_index('Bairro')[['lat', 'lon']].apply(tuple, axis=1).to_dict()

rotas = [
    { "nome": "Troncal Santa Cruz",
     "pontos": [
             ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
             ("Rodoviária de Juiz de Fora", -21.7382049560547,-43.3742561340332),
             ("Terminal Santa Cruz",  -21.7027606964111, -43.4294929504395),
          ],
     "atendimento": [
            "São Judas Tadeu", 'Santa Cruz',
          ],
       "color": "#FFD700"
     },
    { "nome": "Troncal Acesso Norte",
     "pontos": [
         ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
         ("Rodoviária de Juiz de Fora", -21.7382049560547,-43.3742561340332),
         ("Estação Bairro Industrial", -21.7325706481934,-43.3891258239746),
         ("Estação Barbosa Lage", -21.7178344726563,-43.3980751037598),
         ("Estação Jóquei Clube III",-21.7117805480957,-43.4091110229492),
         ("Estação Benfica",-21.692512512207,-43.4318466186523),
         ("Estação Miguel Marinho",-21.6772365570068,-43.4326438903809),
         ("Estação Barreira do Triunfo",  -21.6570682525635,-43.4319686889648),
          ],
     "atendimento": [
             'Barreira do Triunfo','Náutico', 'Novo Triunfo',#'Miguel Marinho',
             'Jóquei Clube II', 'Jóquei Clube III','Barbosa Lage',
             'Bairro Industrial',
          ],
       "color": "#4B0082"
     },
    {
        "nome": "Troncal JK",
        "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Estação Jóquei Clube",   -21.7271518707275,-43.3960990905762),
            ("Estação Barbosa Lage", -21.7188282012939,-43.4002532958984),
            ("Estação Nova Era 1", -21.710018009702235,-43.41478764275406),
            ("Estação Nova Era 2",  -21.6999034881592,-43.423454284668),
            ("Estação Benfica",   -21.6900444030762,-43.4328117370605),
            ("Terminal Distrito Industrial", -21.6796836853027,-43.4445381164551),
        ],
        "atendimento":[
            "Benfica","Nova Era","Nova Era II","Nova Era III",
            'Nova Benfica','Cidade do Sol','Jóquei Clube',"Nova Era I",
             'Vila Esperança', 'Vila Esperança II','Ponte Preta',
             'Distrito Industrial', # 'Santa Lúcia',
        ],
        "color": "red"
    },
    {
        "nome": "Troncal Diva Garcia",
        "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Estação Vitorino Braga",  -21.7501430511475,-43.3422813415527),
            ("Estação Vila Real", -21.735239371454462, -43.329316383861475),
        ],
        "atendimento":[
            'Linhares', 'Bom Jardim',
        ],
        "color": "#708090"
    },
    {
        "nome": "Troncal Filgueiras",
        "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Estação Paracatú", -21.7307987213135,-43.3567276000977),
            ("Estação Grama",   -21.690417494684006,-43.34966653504202),
            ("Estação Filgueiras",  -21.666243464981452, -43.30497229782887),
        ],
        "atendimento":[
            #'Filgueiras',
            'Granjas Triunfo',
        ],
        "color": "#8B4513"
    },
    {
        "nome": "Troncal Grama",
        "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Estação Paracatú", -21.7307987213135,-43.3567276000977),
            ("Estação Parque Guarani",  -21.71793954985861, -43.35085020954209),
            ("Estação Granjas Bethanea", -21.709040995702303, -43.35863934441445),
            ("Estação Recanto dos Lagos", -21.702750834801645, -43.35822219317341),
            ("Estação Grama",   -21.690417494684006,-43.34966653504202),
        ],
        "atendimento":[
            "Grama", 'Vila Montanhesa','Parque Guarani', 'Granjas Bethânia',
            'Granjas Bethanea','Granjas Betânea','Granjas Bethanea',
            'Parque Independência', 'Nova Suissa', 'Nova Suiça',
            'Vivendas da Serra','Recanto dos Lagos','Muçunge da Grama',
        ],
        "color": "green"
    },
    {
         "nome": "Troncal Rio Branco",
         "pontos": [
             ("Estação Belmiro Braga", -21.78004975789712,-43.344867825508125),
             ("Estação Paracatú", -21.7307987213135,-43.3567276000977),
         ],
         "atendimento":[
             "Aeroporto",
         ],
         "color": "darkcyan"
    },
    {
         "nome": " Troncal Deusdedith Salgado",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
 		        ("Estação Parque da Lajinha", -21.7932777404785,-43.3667030334473),
 		        ("Estação Salvaterra", -21.8170642852783,-43.3787803649902),
         ],
         "atendimento":[
             "Aeroporto", "Salvaterra", "Teixeiras",'Santa Cecília',
         ],
         "color":'#FF00FF'
     },

    {
         "nome": "Troncal São Pedro",
         "pontos": [
             ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
             ("Estação São Pedro", -21.759604315763312, -43.38941931724549),
         ],
         "atendimento":[
            'São Pedro','Condomínio Neo Residencial','Caiçaras', 'Santana',
            'Vina del Mar', 'Alphaville', 'Recanto dos Brugger',
            'Nossa Senhora de Fátima', 'Nova Germânia',
         ],
         "color":'#C04000'
     },
    {
         "nome": "Troncal Borboleta",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
             ("Estação Vale do Ipê", -21.751681197157303, -43.36150077660804),
             ("Estação Borboleta",   -21.75533891326005, -43.376463143983166),
             ("Terminal Nova Germânia", -21.75402855253621, -43.38567921438043),
         ],
         "atendimento":[
            'São Pedro', 'Nova Germânia', 'Borboleta', 'Vale do Ipê', 'Democrata',
         ],
         "color":'#045D5D'
     },
     {
         "nome": "Troncal Darcy Vargas",
         "pontos": [
             ("Terminal Renascença", -21.8052406311035,-43.3407554626465),
             ("Estação Previdenciários", -21.8013553619385,-43.3432579040527),
             ("Estação Vale Verde", -21.7981224060059,-43.3470344543457),
             ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),             
         ],
         "atendimento":[
              "São Geraldo", "Santa Luzia",
             'Bela Aurora', 'Ipiranga',  'Jardim de Alá',
             #'Arco-íris',
             #'Previdenciários',
         ],
         "color": 'purple'
     },
     {
         "nome": "Troncal Bady Geara",
         "pontos": [
             ("Terminal Bady Geara", -21.799655567909312,-43.354883193969734),
             ("Estação Bela Aurora", -21.7894611358643,-43.3535766601563),
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
         ],
         "atendimento":[
             'Santa Efigênia','Santa Efigenia', 'Jardim Gaúcho',
             'Cidade Nova', 'Vale Verde',"Sagrado Coração de Jesus",
         ],
         "color":  '#0000FF'
     },
         {
         "nome": "Troncal Santa Luzia",
         "pontos": [
             ("Estação Andradas", -21.75414493345917, -43.35208414970079),
             ("Estação Chácara", -21.784553527832,-43.3452835083008)
         ],
         "atendimento":[
              "Santa Luzia"
             #'Bela Aurora', 'Ipiranga',  'Jardim de Alá',
             #'Arco-íris',
             #'Previdenciários',
         ],
         "color": '#DA70D6'
     },

     {
         "nome": "Troncal Rodoviária",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Estação Rodoviária",-21.7375545501709,-43.3748817443848),
         ],
         "atendimento":[
             'Monte Castelo', 'Carlos Chagas', 'Jardim Natal', 'Milho Branco',
             'Amazônia', 'Francisco Bernardino', 'Esplanada','Fontesville',
         ],
         "color":  '#4F4F4F'
     },

    {
         "nome": "Troncal Monte Castelo",
         "pontos": [
            ("Estação Eduardo Weiss",-21.740646920440675, -43.37658291672075),
            ("Estação Democrata",-21.750348985465614, -43.363640288865504),
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
         ],
         "atendimento":[
             'Monte Castelo', 'Carlos Chagas', 'Esplanada',
         ],
         "color":  '#BC8F8F'
     },

     {
         "nome": "Troncal Retiro",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ('Estação Graminha', -21.790789559144446, -43.32536224269704),
            ('Estação Granjas Bethel', -21.791048302129937, -43.30266968592235),
            #("Estação Retiro",-21.773151041221855, -43.29154588962496),
            ("Terminal Retiro",-21.773151041221855, -43.29154588962496),
         ],
         "atendimento":[
             'Floresta', 'Barão do Retiro', 'Usina 4', 'Caetés', 'Retiro',
             'Parque das Palmeiras',
         ],
         "color":  '#CD853F'
     },

     {
         "nome": "Troncal Nova Califórnia",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Estação Parque da Lajinha", -21.7932777404785,-43.3667030334473),
            ('Estação Santos Dumont', -21.779908031022035, -43.3846345959347),
            ('Estação Marilândia', -21.784647028368102, -43.3916779702871),
            ("Terminal Nova Califórnia",-21.797691292131322, -43.40160115463466),
         ],
         "atendimento":[
             'Santos Dumont', 'Nova Califórnia', 'Marilândia','Novo Horizonte',
         ],
         "color":  '#2F4F4F'
     },

     # Zona Rural
     {
         "nome": "ZR Sarandira",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Sarandira",-21.83062357166665, -43.18820574318265),
         ],
         "atendimento":[
             'Sarandira',
         ],
         "color":  '#4169E1'
     },

     {
         "nome": "ZR Torreões",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Torreões",-21.863094329834,-43.5416946411133),
         ],
         "atendimento":[
             'Torreões',
         ],
         "color":  '#4169E1'
     },

     {
         "nome": "ZR Humaitá",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Humaitá",-21.76935990406484, -43.49035121215151),
         ],
         "atendimento":[
             'Humaitá',
         ],
         "color":  '#4169E1'
     },

     {
         "nome": "ZR Paula Lima",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Paula Lima",-21.58199835857271, -43.48698781282178),
         ],
         "atendimento":[
             'Paula Lima',
         ],
         "color":  '#4169E1'
     },

      {
         "nome": "ZR Monte Verde",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Monte Verde", -21.9175662994385,-43.518726348877),
         ],
         "atendimento":[
             'Monte Verde',
         ],
         "color":  '#4169E1'
     },

      {
         "nome": "ZR Lagoa",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Lagoa", -21.779202651256885,-43.439609112191576),
         ],
         "atendimento":[
             'Lagoa',
         ],
         "color":  '#4169E1'
     },

      {
         "nome": "ZR Santa Córdula",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Santa Córdula", -21.8836460113525,-43.3945007324219),
         ],
         "atendimento":[
             'Santa Córdula',
         ],
         "color":  '#4169E1'
     },

      {
         "nome": "ZR Dias Tavares",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Dias Tavares", -21.6478614807129,-43.4541473388672),
         ],
         "atendimento":[
             'Dias Tavares',
         ],
         "color":  '#4169E1'
     },

      {
         "nome": "ZR Chapéu D'uvas",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Chapéu D'uvas", -21.5932941436768,-43.5080909729004),
         ],
         "atendimento":[
             'Chapéu D´uvas',
         ],
         "color":  '#4169E1'
     },

      {
         "nome": "ZR Igrejinha",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Igrejinha", -21.7086601257324,-43.4878044128418),
         ],
         "atendimento":[
             'Igrejinha',
         ],
         "color":  '#4169E1'
     },

      {
         "nome": "ZR BR040",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal BR040", -21.55302425226195,-43.508031967199294),
         ],
         "atendimento":[
             'BR040',
         ],
         "color":  '#4169E1'
     },

      {
         "nome": "ZR Valadares",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Valadares", -21.760794908761433,-43.60123872756959),
         ],
         "atendimento":[
             'Valadares',
         ],
         "color":  '#4169E1'
     },

      {
         "nome": "ZR Rosário de Minas",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Rosário de Minas", -21.7070465087891,-43.619384765625),
         ],
         "atendimento":[
             'Rosário de Minas',
         ],
         "color":  '#4169E1'
     },

      {
         "nome": "ZR Toledos",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Toledos", -21.7919406890869,-43.5877914428711),
         ],
         "atendimento":[
             'Toledos',
         ],
         "color":  '#4169E1'
     },

      {
         "nome": "ZR Palmital",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Palmital", -21.7260360717773,-43.6502723693848),
         ],
         "atendimento":[
             'Palmital',
         ],
         "color":  '#4169E1'
     },

      {
         "nome": "ZR Cicular BR267",
         "pontos": [
            ("Terminal  Getúlio Vargas", -21.760425567627,-43.3462677001953),
            ("Terminal Cicular BR267",  -21.7747287750244,-43.619800567627),
         ],
         "atendimento":[
             'Cicular BR267',
         ],
         "color":  '#4169E1'
     },
]

# === 2. Criar Mapa Base ===
mapa = folium.Map(location=[-21.75, -43.38], zoom_start=13)

# === 3. Função para Buscar Rota via OSRM API com Múltiplos Waypoints ===
def rota_osrm(pontos):
    """
    Retorna uma lista de coordenadas da rota através de vários pontos.
    """
    coords = ";".join([f"{lon},{lat}" for _, lat, lon in pontos])
    url = f"http://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=polyline"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            geometry = r.json()["routes"][0]["geometry"]
            return polyline.decode(geometry)
        else:
            print(f"Erro na rota: {r.status_code}")
            return []
    except Exception as e:
        print(f"Falha ao obter rota OSRM: {e}")
        return []



    
# === 4. Adicionar Rotas e Marcadores ao Mapa com Controle de Camadas ===
for rota in rotas:
    coords_rota = rota_osrm(rota["pontos"])

    if coords_rota:
        # Criar grupo de feições para essa rota
        feature_group = folium.FeatureGroup(name=rota["nome"])

        # Adicionar linha da rota ao grupo
        feature_group.add_child(folium.PolyLine(
            locations=coords_rota,
            color=rota["color"],
            weight=5,
            popup=rota["nome"]
        ))

        # Marcar início (verde), fim (vermelho) e waypoints intermediários (azul)
        nome_inicio, lat_inicio, lon_inicio = rota["pontos"][0]
        feature_group.add_child(folium.Circle(
            location=(lat_inicio, lon_inicio),
            radius=100,
            color='grey',
            fill=True,
            fill_color=rota['color'],
            fill_opacity=0.99,
            popup=f"{rota['nome']}: {nome_inicio}"
        ))

        nome_fim, lat_fim, lon_fim = rota["pontos"][-1]
        feature_group.add_child(folium.Circle(
            location=(lat_fim, lon_fim),
            radius=100,
            color='grey',
            fill=True,
            fill_color=rota['color'],
            fill_opacity=0.99,
            popup=f"{rota['nome']}: {nome_fim}"
        ))

        for i, (nome_wp, lat_wp, lon_wp) in enumerate(rota["pontos"][1:-1], start=1):
            feature_group.add_child(folium.Circle(
                location=(lat_wp, lon_wp),
                radius=80,
                color='grey',
                fill=True,
                fill_color=rota['color'],
                fill_opacity=0.99,
                popup=f"{rota['nome']}: {nome_wp}"
            ))

        for i, nome_ap in enumerate(rota["atendimento"]):
            try:
                (lat_ap, lon_ap) = bairros_dict[nome_ap]
                feature_group.add_child(folium.Circle(
                    location=(lat_ap, lon_ap),
                    radius=300,
                    color=rota['color'],
                    fill=True,
                    fill_color=rota['color'],
                    fill_opacity=0.15,
                    popup=f"{rota['nome']}: {nome_ap}"
                ))
            except:
                pass

        # Adicionar grupo ao mapa
        mapa.add_child(feature_group)

# === Adicionar Controle de Camadas ===
folium.LayerControl().add_to(mapa)

# === 5. Salvar e Mostrar Mapa ===
mapa.save("mapa_rotas_multiplos_waypoints.html")
print("🗺️ Mapa salvo como 'mapa_rotas_multiplos_waypoints.html'")

