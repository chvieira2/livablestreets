import numpy as np
import pandas as pd
from livablestreets.utils import m_to_coord
import geopandas as gdp
from livablestreets.utils import haversine_vectorized, save_file
from livablestreets.utils import simple_time_tracker, create_dir

from geopy.geocoders import Nominatim
from shapely.ops import linemerge, unary_union, polygonize
import overpy
from geojson import dump

import shapely.geometry as geometry
from shapely.geometry import Point, mapping



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
    area_osm_id = int(city.raw.get("osm_id")) #for city
    return area_osm_id

def get_city_geojson(area_osm_id):

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
            ls_coords.append(
                (node.lon, node.lat))  # create a list of node coordinates

        lss.append(
            geometry.LineString(ls_coords))  # create a LineString from coords

    merged = linemerge([*lss])  # merge LineStrings
    borders = unary_union(merged)  # linestrings to a MultiLineString
    polygons = list(polygonize(borders))
    city_shape = geometry.MultiPolygon(polygons)
    return city_shape

def save_geojson(location):
    # converts to geojson
    area_osm_id = get_id_deambiguate(location)
    city_shape = get_city_geojson(area_osm_id)

    # saves to file
    with open(f'livablestreets/data/{location}/{location}_boundaries.geojson', 'w') as f:
        dump(mapping(city_shape), f)

'''----------------------------------------------------'''

def get_shape_of_location(location):
    """ Receives a location and returns the shape, if that location is in the data base (raw_data)"""
    try:
        gdf = gdp.read_file(f'livablestreets/data/{location}/{location}_boundaries.geojson')
    except:
        save_geojson(location)
        gdf = gdp.read_file(f'livablestreets/data/{location}/{location}_boundaries.geojson')


    gdf['Location'] = location
    gdf = gdf.set_index("Location")

    print(f'Obtained shape file for {location}')
    return gdf

def get_shape_of_location_Berlin(location):
    """ Receives a location and returns the shape, if that location is in the data base (raw_data)"""

    if location in ['Berlin', 'berlin', 'BER', 'ber']:
        # Use geopandas package to work with the shape file of Berlin
        # geojson for all berlin neighbourhoods was downloaded from here: https://daten.odis-berlin.de/de/dataset/bezirksgrenzen/
        gdf = gdp.read_file(f'livablestreets/data/{location}/bezirksgrenzen.geojson')

        # gdf.dissolve will colapse all neighborhoods into a single shape of the whole berlin
        gdf = gdf.dissolve()

        # Clean table to keep only relevant info
        gdf = gdf.drop(columns=['Gemeinde_name', "Gemeinde_schluessel","gml_id", "Land_name","Land_schluessel","Schluessel_gesamt"])
        gdf['Location'] = 'Berlin'
        gdf = gdf.set_index("Location")

        print(f'Obtained shape file for {location}')
        return gdf

def calculate_features_from_centroid(df, location, location_polygon = None):
    """ Iterates through all rows of grid squares and measures the distance (in km) to the location centroid (geographic center), angle (in degrees) and if point belongs to polygon shape """

    # get location shape location_polygon
    if location_polygon is None:
        gdf_shape_location = get_shape_of_location(location)
        polygon = gdf_shape_location['geometry']

    # Obtain shape's centroid
    centroid = gdf_shape_location.centroid
    centroid = list(centroid[0].coords)[0]
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

    df['grid_in_berlin'] = foo_boolean
    df['degrees_to_centroid'] = foo_angles

    print(f'Identified grids inside and outside of {location}')
    print(f'Calculated the angular direction (degrees) of grids to centroid')

    return df

@simple_time_tracker
def create_geofence(location, stepsize,
                    north_lat=None, south_lat=None, east_lng=None, west_lng=None,
                    save_local=True, save_gcp=False):
    # Obtain location max bounds
    if north_lat is None:
        east_lng, north_lat, west_lng, south_lat = get_shape_of_location(location)['geometry'].total_bounds

    print(f'Bounds coordinates are north_lat:{north_lat}, south_lat:{south_lat}, east_lng:{east_lng}, west_lng:{west_lng}')

    # Adjust setpsize
    if stepsize > 10: # This probably means that the step size is in meters and should be converted to degrees
        stepsize_x = m_to_coord(stepsize, latitude=north_lat, direction='x')
        stepsize_y = m_to_coord(stepsize, direction='y')
        print(f'Stepsize of {stepsize}m converted to step sizes of lat={stepsize_y} and lng={stepsize_x} degrees')
    else:
        stepsize_x = stepsize
        stepsize_y = stepsize

    # Obtain start and end of each grid individually
    lat_start = []
    lat_end = []
    lng_start = []
    lng_end = []
    lat_center = []
    lng_center = []

    for y in np.arange(north_lat, south_lat-stepsize_y, stepsize_y)[::-1]:
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
    df = calculate_features_from_centroid(df, location = location)

    print(f'Successfully created geofence of {location}')

    save_file(df, file_name=f'{location}_grid_{stepsize}m.csv', local_file_path=f'data/{location}/WorkingTables', gcp_file_path = f'data/{location}/WorkingTables', save_local=save_local, save_gcp=save_gcp)

    return df



if __name__ == '__main__':
    print(create_geofence(location = 'London', stepsize = 1000))
