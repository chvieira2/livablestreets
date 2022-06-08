import requests
from geopy.geocoders import Nominatim

overpass_url = "http://overpass-api.de/api/interpreter"
# https://dev.overpass-api.de/overpass-doc/de/full_data/osm_types.html
#example query list:
keys_values_osm = {'amenity':['bbq','cafe']}



def get_id_deambiguate(location):

    # Geocoding request via Nominatim
    geolocator = Nominatim(user_agent="city_compare")
    geo_results = geolocator.geocode(location, exactly_one=False, limit=3)

    # Searching for relation in result set
    for r in geo_results:
        print(r.address, r.raw.get("osm_type"))
        if r.raw.get("osm_type") == "relation":
            city = r
            break


    # Calculating area id
    # area_relid = int(city.raw.get("osm_id")) + 3600000000 #for relations
    # area_wayid = int(city.raw.get("osm_id")) + 2400000000 #for ways
    area_osm_id = int(city.raw.get("osm_id")) #for city
    print(area_osm_id)
    return area_osm_id





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

    location_area = f'area[name={location}]->.city'
    # location_area = f'{{{{geocodeArea:{location}}}}}->.city'
    # location_area = f'area({get_id_deambiguate(location)})->.city'

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
