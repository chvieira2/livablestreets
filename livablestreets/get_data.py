from osm_query import query_params_osm

public_transport = {
                   'highway':['bus_stop','platform'],
                   }

data = query_params_osm(public_transport)
print(data)
