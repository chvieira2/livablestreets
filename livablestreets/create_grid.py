import numpy as np
import pandas as pd
from livablestreets.utils import m_to_coord


def create_geofence(north_lat, south_lat, east_lon, west_lon, stepsize = 10000):
    if stepsize > 1: # This means that the step size is in meters and should be converted to degrees
        stepsize_x = m_to_coord(stepsize, latitude=north_lat, direction='x')
        stepsize_y = m_to_coord(stepsize, direction='y')
    else:
        stepsize_x = stepsize
        stepsize_y = stepsize
    lat_start = []
    lat_end = []
    lon_start = []
    lon_end = []

    for x in np.arange(east_lon, west_lon-stepsize_x, stepsize_x):
        for y in np.arange(north_lat, south_lat-stepsize_y, stepsize_y):
            lat_start.append(y)
            lat_end.append(y+stepsize_y)
            lon_start.append(x)
            lon_end.append(x+stepsize_x)

    return pd.DataFrame({'lat_start':lat_start,
                         'lat_end':lat_end,
                         'lon_start':lon_start,
                         'lon_end':lon_end,
                         })


if __name__ == '__main__':
    print(m_to_coord(100)) # check if import is working
    print(create_geofence(52.343717, 52.650508, 13.114412, 13.739281))
