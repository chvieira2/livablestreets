import numpy as np
import pandas as pd
from livablestreets.utils import m_to_coord, haversine_vectorized, save_file, simple_time_tracker
from livablestreets.string_utils import german_characters
import geopandas as gdp
from geopy.geocoders import Nominatim
from shapely.ops import linemerge, unary_union, polygonize
import overpy
from geojson import dump

import shapely.geometry as geometry
from shapely.geometry import Point, mapping
from config.config import ROOT_DIR



@simple_time_tracker
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
    try:
        area_osm_id = int(city.raw.get("osm_id")) #for city
    except UnboundLocalError:
        print(f"OpenStreetMaps could not find a relation osm_type for {location}")
        return get_id_deambiguate(german_characters(location))
    return area_osm_id

@simple_time_tracker
def get_city_geojson(area_osm_id,location_name):

    #overpass query with overpy
    query = f"""[out:json][timeout:25];
                rel({area_osm_id});
                out body;
                >;
                out skel qt; """
    # initiates overpy
    api = overpy.Overpass()
    result = api.query(query)

    lss = []  #convert ways to linstrings

    for ii_w, way in enumerate(result.ways):
        ls_coords = []

        for node in way.nodes:


            if location_name == 'hamburg': # Filter by tiles inside box around Hamburg
                if node.lon <= 10.35 and node.lon >= 9.62 and node.lat <= 53.76 and node.lat >= 53.36:
                    ls_coords.append((node.lon, node.lat))  # create a list of node coordinates

            elif location_name == 'bremen': # Filter by tiles inside box around Bremen
                if node.lon <= 9.04 and node.lon >= 8.43 and node.lat <= 53.23 and node.lat >= 53.0:
                    ls_coords.append((node.lon, node.lat))  # create a list of node coordinates

            else:
                ls_coords.append((node.lon, node.lat))  # create a list of node coordinates

        lss.append(
            geometry.LineString(ls_coords))  # create a LineString from coords

    merged = linemerge([*lss])  # merge LineStrings
    borders = unary_union(merged)  # linestrings to a MultiLineString
    polygons = list(polygonize(borders))
    city_shape = geometry.MultiPolygon(polygons)
    return city_shape

def save_geojson(location, location_name):
    # converts to geojson
    area_osm_id = get_id_deambiguate(location)
    city_shape = get_city_geojson(area_osm_id,location_name)

    # saves to file
    with open(f'{ROOT_DIR}/livablestreets/data/{location_name}/{location_name}_boundaries.geojson', 'w') as f:
        dump(mapping(city_shape), f)

@simple_time_tracker
def get_shape_of_location(location, location_name):
    """ Receives a location and returns the shape, if that location is in the data base (raw_data)"""
    try:
        gdf = gdp.read_file(f'{ROOT_DIR}/livablestreets/data/{location_name}/{location_name}_boundaries.geojson')
    except:
        save_geojson(location=location, location_name=location_name)
        gdf = gdp.read_file(f'{ROOT_DIR}/livablestreets/data/{location_name}/{location_name}_boundaries.geojson')


    gdf['Location'] = location_name
    gdf = gdf.set_index("Location")

    print(f'Obtained shape file for {location_name}')
    return gdf

@simple_time_tracker
def calculate_features_from_centroid(df, location, location_name, location_polygon = None):
    """ Iterates through all rows of grid squares and measures the distance (in km) to the location centroid (geographic center), angle (in degrees) and if point belongs to polygon shape """

    # get location shape location_polygon
    if location_polygon is None:
        gdf_shape_location = get_shape_of_location(location=location,
                                                   location_name=location_name)
        polygon = gdf_shape_location['geometry']

    # Obtain shape's centroid
    centroid = gdf_shape_location.centroid
    centroid = list(centroid[0].coords)[0]
    print(centroid)
    centroid_lat = centroid[1]
    centroid_lng = centroid[0]

    # Calculate distance for each grid
    df['km_to_centroid'] = haversine_vectorized(df,
                         start_lat="lat_center",
                         start_lon="lng_center",
                         end_lat=centroid_lat,
                         end_lon=centroid_lng)
    print(f'Calculated grid distance to {location} centroid')

    foo_boolean = []
    foo_angles = []
    for index in range(len(df)):
        lat = df['lat_center'][index]
        lng = df['lng_center'][index]
        # Test if point is inside the locations shape
        point = Point(lng,lat)
        foo_boolean.append(polygon.contains(point)[0])


        ## Next I calculate the angle of points and the centroid in the same for loop. A third point on the X-axis of the centroid is included for the calculation
        # The following formula to calculate the angle between three points and was taken from: https://manivannan-ai.medium.com/find-the-angle-between-three-points-from-2d-using-python-348c513e2cd
        a = np.array([centroid_lat, centroid_lng*1.1]) # centroid_point_extra. Multiply by 1.1 to extend on the x-axis
        b = np.array([centroid_lat, centroid_lng]) # centroid_point
        c = np.array([lat, lng])  #my_point

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)

        if lat <= centroid_lat: # Code needed to ensure that points south from the centroid have angles above 180
            foo_angles.append((360-np.degrees(angle)))
        else:
            foo_angles.append(np.degrees(angle))

    df['grid_in_location'] = foo_boolean
    df['degrees_to_centroid'] = foo_angles

    print(f'Identified grids inside and outside of {location}')
    print(f'Calculated the angular direction (degrees) of grids to centroid')

    return df

@simple_time_tracker
def create_geofence(location, location_name, stepsize,
                    north_lat=None, south_lat=None, east_lng=None, west_lng=None,
                    save_local=True, save_gcp=False):
    # Obtain location max bounds
    if north_lat is None:
        east_lng, south_lat, west_lng, north_lat = get_shape_of_location(location, location_name=location_name)['geometry'].total_bounds

    print(f'Bounds coordinates are north_lat:{north_lat}, south_lat:{south_lat}, east_lng:{east_lng}, west_lng:{west_lng}')

    # Adjust setpsize
    if stepsize > 10: # This probably means that the step size is in meters and should be converted to degrees
        stepsize_x = m_to_coord(stepsize, latitude=np.mean([north_lat,south_lat]), direction='x')
        stepsize_y = m_to_coord(stepsize, direction='y')
        print(f'Stepsize of {stepsize}m converted to step sizes of lat={stepsize_y} and lng={stepsize_x} degrees')
    else:
        stepsize_x = stepsize
        stepsize_y = stepsize

    ## Build the grid table
    # Obtain start and end of each grid individually
    lat_start = []
    lat_end = []
    lng_start = []
    lng_end = []
    lat_center = []
    lng_center = []

    for y in np.arange(south_lat, north_lat-stepsize_y, stepsize_y)[::-1]:
        for x in np.arange(east_lng, west_lng-stepsize_x, stepsize_x):
            lat_start.append(y)
            lat_end.append(y+stepsize_y)
            lng_start.append(x)
            lng_end.append(x+stepsize_x)

            lat_center.append(np.mean([y,y+stepsize_y]))
            lng_center.append(np.mean([x,x+stepsize_x]))

    # Aggregate all grids into a single dataframe
    df = pd.DataFrame({'lat_start':lat_start,
                         'lat_end':lat_end,
                         'lng_start':lng_start,
                         'lng_end':lng_end,
                         'lat_center': lat_center,
                         'lng_center': lng_center
                         })

    print(f'Created grid table with dimensions: {df.shape}')

    # Calculate distance and angle from centroid. Also check which grids belong to the Location map
    df = calculate_features_from_centroid(df, location = location, location_name=location_name)

    print(f'Successfully created geofence of {location}')

    save_file(df, file_name=f'{location_name}_grid_{stepsize}m.csv', local_file_path=f'livablestreets/data/{location_name}/WorkingTables', gcp_file_path = f'data/{location_name}/WorkingTables', save_local=save_local, save_gcp=save_gcp)

    return df



if __name__ == '__main__':
    # geolocator = Nominatim(user_agent="city_compare")
    # print(geolocator.geocode('Köln', exactly_one=False, limit=3))

    create_geofence(stepsize = 2000, location = 'Hamburg', location_name='hamburg')
