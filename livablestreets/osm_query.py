import requests
import json


overpass_url = "http://overpass-api.de/api/interpreter"

study_area = 'area["ISO3166-2"="DE-BE"]->.berlin'

#example query list:
keys_values_osm = {'amenity':['bbq','cafe']}


def param_nodes(keys):
    '''converts the dict into a string, returns a str'''
    osm_keys = ''
    for k,val in keys.items():
        for v in val:
            osm_keys += f"""node['{k}'='{v}'](area.berlin);"""
    return osm_keys

def param_ways(keys):
    '''converts the dict into a string, returns a str'''
    osm_keys = ''
    for k,val in keys.items():
        for v in val:
            osm_keys += f"""way['{k}'='{v}'](area.berlin);"""
    return osm_keys

def param_areas(keys):
    '''converts the dict into a string, returns a str'''
    osm_keys = ''
    for k,val in keys.items():
        for v in val:
            osm_keys += f"""area['{k}'='{v}'](area.berlin);"""
    return osm_keys


def query_params_osm(keys, feat, limit=''):
    '''Adding keys and values as a dictionary, example: keys_values_osm = {'amenity':['bbq','cafe']}
    several values can be added to a same key as a list, returns a dict
    feat = nodes, ways or areas (geometry type)
    limit = number (optional query limit)'''

    if feat == 'ways':
        params = param_ways(keys)
        out_type = 'geom'
    if feat == 'areas':
        params = param_areas(keys)
        out_type = 'geom'
    if feat == 'nodes':
        params = param_nodes(keys)
        out_type = 'center'

    overpass_query = f"""
                    [out:json];
                    {study_area};
                    ({params}
                    );
                    out {limit} {out_type};
                    """
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    return response.json()
