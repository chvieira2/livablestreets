import math
import numpy as np
import time
import pandas as pd
from livablestreets.params import BUCKET_NAME
from google.cloud import storage
from sklearn.preprocessing import MinMaxScaler

def min_max_scaler(df, columns = ['activities_economic', 'activities_education',
                                         'activities_health_care', 'activities_public_service',
                                         'comfort_leisure_sports', 'comfort_sports',
                                         'mobility_public_transport', 'social_community', 'social_culture',
                                         'social_eating', 'social_night_life']):

    """ Takes a dataframe and a list of columns and MinMax scale each column"""
    scaler = MinMaxScaler()
    df[columns] = scaler.fit_transform(df[columns])
    return df

def get_file(file_name, local_file_path='data', gcp_file_path = 'data', save_local=True):
    """method to get the training data (or a portion of it) from google cloud bucket"""

    try:
        df = pd.read_csv(f'livablestreets/{local_file_path}/{file_name}')
    except FileNotFoundError:
        # Add Client() here
        client = storage.Client()
        path = f"gs://{BUCKET_NAME}/{gcp_file_path}/{file_name}"
        df = pd.read_csv(path)
        if save_local:
            df.to_csv(f'livablestreets/{local_file_path}/{file_name}', index=False)

    return df

def save_file(df_grid, file_name, local_file_path='data', gcp_file_path = 'data/WorkingTables', save_local=True, save_gcp=True):
    # Save locally
    if save_local:
        df_grid.to_csv(f'livablestreets/{local_file_path}/{file_name}', index=False)
        print(f"=> {file_name} saved locally in livablestreets/{local_file_path}/{file_name}")

    # Save on GCP
    if save_gcp:
        client = storage.Client().bucket(BUCKET_NAME)

        storage_location = f'{gcp_file_path}/{file_name}'
        blob = client.blob(storage_location)
        blob.upload_from_filename(f'livablestreets/{local_file_path}/{file_name}')
        print(f"=> {file_name} uploaded to bucket {BUCKET_NAME} inside {storage_location}")


def coord_to_m(start_lat,
               start_lon,
               end_lat,
               end_lon):
    """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees).
        Vectorized version of the haversine distance for pandas df
        Computes distance in kms
    """

    lat_1_rad, lon_1_rad = np.radians(start_lat), np.radians(start_lon)
    lat_2_rad, lon_2_rad = np.radians(end_lat), np.radians(end_lon)
    dlon = lon_2_rad - lon_1_rad
    dlat = lat_2_rad - lat_1_rad

    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat_1_rad) * np.cos(lat_2_rad) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return 6371 * c

def m_to_coord(m, latitude=52.52, direction='east'):
    """
        Takes an offset in meters in a given direction (north, south, east and west) at a given latitude and returns the corresponding value in lat (north or south) or lon (east or west) degrees
        Uses the French approximation.
        More info here: https://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """

    # Coordinate offsets in radians
    if direction in ['x', 'east', 'west', 'e', 'w']:
        return abs(m/(111_111*math.cos(latitude)))
    elif direction in ['y', 'north', 'south', 'n', 's']:
        return abs(m/111_111)
    return None

def compute_rmse(y_pred, y_true):
    return np.sqrt(((y_pred - y_true) ** 2).mean())

def haversine_vectorized(df,
                         start_lat="lat_center",
                         start_lon="lng_center",
                         end_lat=52.50149,  # Berlin centroid lat
                         end_lon=13.40232):  # Berlin centroid lng
    """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees).
        Vectorized version of the haversine distance for pandas df
        Computes distance in kms
    """

    lat_1_rad, lon_1_rad = np.radians(df[start_lat].astype(float)), np.radians(df[start_lon].astype(float))
    lat_2_rad, lon_2_rad = np.radians(end_lat), np.radians(end_lon)
    dlon = lon_2_rad - lon_1_rad
    dlat = lat_2_rad - lat_1_rad

    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat_1_rad) * np.cos(lat_2_rad) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return 6371 * c

def simple_time_tracker(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts))
        else:
            print(method.__name__, round(te - ts, 2))
        return result

    return timed

if __name__ == '__main__':
    print(m_to_coord(10))
    print(m_to_coord(10, direction='south'))
