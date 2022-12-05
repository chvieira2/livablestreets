import requests
from livablestreets.livability_map.create_grid import get_id_deambiguate

overpass_url = "http://overpass-api.de/api/interpreter"
# https://dev.overpass-api.de/overpass-doc/de/full_data/osm_types.html
#example query list:
keys_values_osm = {'amenity':['bbq','cafe']}

# Consider using node(around.indianairports:5000)[‘tourism’=’hotel’]; to search features over the border of countries

def param_nodes(keys):
    '''converts the dict into a string, returns a str'''
    osm_keys = ''
    for k,val in keys.items():
        for v in val:
            osm_keys += f"""node['{k}'='{v}'](area.searchArea);"""
    return osm_keys

def param_ways(keys):
    '''converts the dict into a string, returns a str'''
    osm_keys = ''
    for k,val in keys.items():
        for v in val:
            osm_keys += f"""way['{k}'='{v}'](area.searchArea);"""
    return osm_keys

def param_areas(keys):
    '''converts the dict into a string, returns a str'''
    osm_keys = ''
    for k,val in keys.items():
        for v in val:
            osm_keys += f"""rel['{k}'='{v}'](area.searchArea);"""
    return osm_keys


def query_params_osm(osm_id, keys, features, limit=''):
    '''Adding keys and values as a dictionary, example: keys_values_osm = {'amenity':['bbq','cafe']}
    several values can be added to a same key as a list, returns a dict
    feat = nodes, ways or areas (geometry type)
    limit = number (optional query limit)'''

    location_area = f'area(id:{osm_id})->.searchArea'

    if features == 'ways':
        params = param_ways(dict(keys))
        out_type = 'geom'
    if features == 'areas':
        params = param_areas(dict(keys))
        out_type = 'geom'
    if features == 'nodes':
        params = param_nodes(dict(keys))
        out_type = 'center'

    # [WARNING] do not create multiple lines for the next string: !!!
    overpass_query = f"""[out:json][timeout:900];
                        {location_area};
                        ({params});
                        (._;>;
                        );
                        out {limit} {out_type};"""

    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    return response.json()
    # print(overpass_query)


if __name__ == "__main__":

    location = 'stockholm'
    country_code = 'SE'
    osm_id = get_id_deambiguate(location, country_code) + 3600000000

    print(query_params_osm(osm_id,
                           keys = {'amenity': ['atm', 'bank', 'bureau_de_change']},
                           features = 'nodes'))
