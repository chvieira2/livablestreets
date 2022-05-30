import time

import numpy as np


def haversine_vectorized(df,
                         start_lat="pickup_latitude",
                         start_lon="pickup_longitude",
                         end_lat="dropoff_latitude",
                         end_lon="dropoff_longitude"):
    """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees).
        Vectorized version of the haversine distance for pandas df
        Computes distance in kms
    """

    lat_1_rad, lon_1_rad = np.radians(df[start_lat].astype(float)), np.radians(df[start_lon].astype(float))
    lat_2_rad, lon_2_rad = np.radians(df[end_lat].astype(float)), np.radians(df[end_lon].astype(float))
    dlon = lon_2_rad - lon_1_rad
    dlat = lat_2_rad - lat_1_rad

    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat_1_rad) * np.cos(lat_2_rad) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return 6371 * c


def minkowski_distance(df, p,
                       start_lat="pickup_latitude",
                       start_lon="pickup_longitude",
                       end_lat="dropoff_latitude",
                       end_lon="dropoff_longitude"):
    x1 = df[start_lon]
    x2 = df[end_lon]
    y1 = df[start_lat]
    y2 = df[end_lat]
    return ((abs(x2 - x1) ** p) + (abs(y2 - y1)) ** p) ** (1 / p)
