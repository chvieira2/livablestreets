import numpy as np
import pandas as pd
from livablestreets.utils import m_to_coord
from shapely.geometry import Point, Polygon
import geopandas
from livablestreets.utils import haversine_vectorized


def get_shape_berlin():
    # Use geopandas package to work with the shape file of Berlin
    # geojson for all berlin neighbourhoods was downloaded from here: https://daten.odis-berlin.de/de/dataset/bezirksgrenzen/
    gdf = geopandas.read_file('raw_data/bezirksgrenzen.geojson')

    # gdf.dissolve will colapse all neighborhoods into a single shape of the whole berlin
    gdf = gdf.dissolve()

    # Clean table to keep only relevant info
    gdf = gdf.drop(columns=['Gemeinde_name', "Gemeinde_schluessel","gml_id", "Land_name","Land_schluessel","Schluessel_gesamt"])
    gdf['Location'] = 'Berlin'
    gdf = gdf.set_index("Location")

    # Collect boundary
    gdf_boundary = gdf.boundary

    return gdf

def calculate_features_from_centroid(df, polygon = None):
    """ Iterates through all rows of grid squares and measures the distance (in km) to the location centroid (geographic center), angle (in degrees) and if point belongs to polygon shape """

    # get berlin shape polygon
    if polygon is None:
        gdf_shape_location = get_shape_berlin()
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

    foo_boolean = []
    foo_angles = []
    for index in range(len(df)):
        lat = df['lat_center'][index]
        lng = df['lng_center'][index]

        # Test if point is inside the locations shape
        point = Point(lng,lat)
        test = polygon.contains(point)
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

    return df

def create_geofence(north_lat, south_lat, east_lng, west_lng, stepsize = 1000):
    if stepsize > 1: # This means that the step size is in meters and should be converted to degrees
        stepsize_x = m_to_coord(stepsize, latitude=north_lat, direction='x')
        stepsize_y = m_to_coord(stepsize, direction='y')
    else:
        stepsize_x = stepsize
        stepsize_y = stepsize

    lat_start = []
    lat_end = []
    lng_start = []
    lng_end = []
    lat_center = []
    lng_center = []
    # polygons = []
    for y in np.arange(north_lat, south_lat-stepsize_y, stepsize_y)[::-1]:
        for x in np.arange(east_lng, west_lng-stepsize_x, stepsize_x):
            lat_start.append(y)
            lat_end.append(y+stepsize_y)
            lng_start.append(x)
            lng_end.append(x+stepsize_x)

            lat_center.append(np.mean([y,y+stepsize_y]))
            lng_center.append(np.mean([x,x+stepsize_x]))

            # polygons.append(Polygon([Point(y,x),
            #       Point(y,x+stepsize_x),
            #       Point(y+stepsize_y,x),
            #       Point(y+stepsize_y,x+stepsize_x)]))

    df = pd.DataFrame({'lat_start':lat_start,
                         'lat_end':lat_end,
                         'lng_start':lng_start,
                         'lng_end':lng_end,
                         'lat_center': lat_center,
                         'lng_center': lng_center
                        #  'geometry':polygons
                         })

    df = calculate_features_from_centroid(df)
    return df



if __name__ == '__main__':
    # print(m_to_coord(100)) # check if import is working
    df = create_geofence(52.338246, 52.675508, 13.088348, 13.761159) # using official Berlin boundaries
    print(df)
    print(len(df[df['grid_in_berlin']]), len(df))
    df.to_csv('raw_data/Berlin_grid_1000m.csv',index=False)
    # print(get_shape_berlin()[1])
    # print(is_point_in_polygon(52.50149,13.40232)) # Berlin centroid, so it should return True
    # calculate_features_from_centroid(create_geofence(52.338246, 52.675508, 13.088348, 13.761159))
