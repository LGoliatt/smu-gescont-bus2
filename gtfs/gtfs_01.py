import gtfs_kit as gk

# Carregar GTFS
poa = gk.read_feed("https://dadosabertos.poa.br/dataset/1fe9c2c1-9fbe-48ea-841b-61e30597ecd6/resource/b3bce61f-78ee-49eb-be57-6236d82bd5e0/download/arquivo-gtfs.zip", dist_units="km")
#%%
feed = gk.read_feed('./sample-feed-1.zip', dist_units='km')

# Ver paradas
print(feed.stops.head())

# Ver rotas
print(feed.routes.head())

# Ver viagens de uma rota
trips = feed.get_trips(route_id='AB')
#%%