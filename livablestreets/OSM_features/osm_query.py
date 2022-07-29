import requests
from livablestreets.livability_map.create_grid import get_id_deambiguate

overpass_url = "http://overpass-api.de/api/interpreter"
# https://dev.overpass-api.de/overpass-doc/de/full_data/osm_types.html
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
            osm_keys += f"""rel['{k}'='{v}'](area.city);"""
    return osm_keys

def query_params_osm(location, keys, features, limit=''):
    '''Adding keys and values as a dictionary, example: keys_values_osm = {'amenity':['bbq','cafe']}
    several values can be added to a same key as a list, returns a dict
    feat = nodes, ways or areas (geometry type)
    limit = number (optional query limit)'''
    location_area = f'area[name="{location}"]->.city'
    ## To Do search for city ID instead of city name
    # location_area = f'{{{{geocodeArea:{location}}}}}->.city'
    # location_area = f'area({get_id_deambiguate(location)})->.city'
    if features == 'ways':
        params = param_ways(dict(keys))
        out_type = 'geom'
    if features == 'areas':
        params = param_areas(dict(keys))
        out_type = 'geom'
    if features == 'nodes':
        params = param_nodes(dict(keys))
        out_type = 'center'

    overpass_query = f"""
                    [out:json][timeout:900];
                    {location_area};
                    ({params}
                    );
                    (._;>;);
                    out {limit} {out_type};
                    """
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    return response.json()


if __name__ == "__main__":
    # print(param_nodes(keys = {'amenity': ['atm', 'bank', 'bureau_de_change']}))
    print(query_params_osm(location = "Copenhagen",
                    keys = {'amenity': ['atm', 'bank', 'bureau_de_change']},
                    features = 'nodes'))
