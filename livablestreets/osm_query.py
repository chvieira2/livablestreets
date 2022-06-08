import requests
# import json


overpass_url = "http://overpass-api.de/api/interpreter"

#example query list:
keys_values_osm = {'amenity':['bbq','cafe']}


def param_nodes(keys):
    '''converts the dict into a string, returns a str'''
    osm_keys = ''
    for k,val in keys.items():
        for v in val:
            osm_keys += f"""node['{k}'='{v}'](area.city);"""
    return osm_keys

def param_ways(keys):
    '''converts the dict into a string, returns a str'''
    osm_keys = ''
    for k,val in keys.items():
        for v in val:
            osm_keys += f"""way['{k}'='{v}'](area.city);"""
    return osm_keys

def param_areas(keys):
    '''converts the dict into a string, returns a str'''
    osm_keys = ''
    for k,val in keys.items():
        for v in val:
            osm_keys += f"""area['{k}'='{v}'](area.city);"""
    return osm_keys


def query_params_osm(location, keys, features, limit=''):
#     location_area = f'area[{location}]->.{location}'
    location_area = f'area[name={location}]->.city'

    '''Adding keys and values as a dictionary, example: keys_values_osm = {'amenity':['bbq','cafe']}
    several values can be added to a same key as a list, returns a dict
    feat = nodes, ways or areas (geometry type)
    limit = number (optional query limit)'''

    if features == 'ways':
        params = param_ways(keys)
        out_type = 'geom'
    if features == 'areas':
        params = param_areas(keys)
        out_type = 'geom'
    if features == 'nodes':
        params = param_nodes(keys)
        out_type = 'center'

    overpass_query = f"""
                    [out:json][timeout:500];
                    {location_area};
                    ({params}
                    );
                    out {limit} {out_type};
                    """
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    return response.json()
