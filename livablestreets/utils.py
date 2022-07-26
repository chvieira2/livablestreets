import math
import numpy as np
import time
import pandas as pd
from livablestreets.params import BUCKET_NAME
# from google.cloud import storage
from sklearn.preprocessing import MinMaxScaler
import os
import os
from config.config import ROOT_DIR


def create_dir(path):
    # Check whether the specified path exists or not
    if os.path.exists(path):
        pass
    else:
        # Create a new directory because it does not exist
        os.makedirs(path)
        print(f"The new directory has been created!")

def min_max_scaler(df, columns = ['activities_economic', 'activities_education',
                                         'activities_health_care', 'activities_public_service',
                                         'comfort_leisure_sports', 'comfort_sports',
                                         'mobility_public_transport', 'social_community', 'social_culture',
                                         'social_eating', 'social_night_life']):

    """ Takes a dataframe and a list of columns and MinMax scale each column"""
    scaler = MinMaxScaler()
    df[columns] = scaler.fit_transform(df[columns])
    return df

def get_file(file_name, local_file_path='data/berlin/WorkingTables', gcp_file_path = 'data/berlin/WorkingTables', save_local=True):
    """method to get the training data (or a portion of it) from google cloud bucket"""
    # try:
    local_path = f'{ROOT_DIR}/{local_file_path}/{file_name}'
    df = pd.read_csv(local_path)
    print(f'===> Loaded {file_name} locally')
    # except FileNotFoundError:
    #     # client = storage.Client()
    #     gcp_path = f"gs://{BUCKET_NAME}/{gcp_file_path}/{file_name}"
    #     df = pd.read_csv(gcp_path)
    #     print(f'===> Loaded {file_name} from GCP at: {gcp_path}')
    #     if save_local:
    #         df.to_csv(local_path, index=False)
    #         print(f'===> Saved {file_name} locally at: {local_path}')

    return df

def save_file(df, file_name, local_file_path='data/berlin/WorkingTables', gcp_file_path = 'data/berlin/WorkingTables', save_local=True, save_gcp=False):
    # Create directory for saving
    create_dir(path = f'{ROOT_DIR}/{local_file_path}')

    # Save locally
    if save_local:
        local_path = f'{ROOT_DIR}/{local_file_path}/{file_name}'
        df.to_csv(local_path, index=False)
        print(f"===> {file_name} saved locally")

    # Save on GCP
    # if save_gcp:
    #     client = storage.Client().bucket(BUCKET_NAME)
    #     storage_location = f'{gcp_file_path}/{file_name}'
    #     blob = client.blob(storage_location)
    #     local_path = f'livablestreets/{local_file_path}/{file_name}'
    #     blob.upload_from_filename(local_path)
    #     print(f"===> {file_name} uploaded to bucket {BUCKET_NAME} inside {storage_location}")


def get_liv_from_coord(lat, lon,liv_df):

    # Calculate the 100 m square coordinates around given coordinates
    lat_north = lat+m_to_coord(100, latitude=lat, direction='north')
    lat_south = lat-m_to_coord(-100, latitude=lat, direction='south')
    lon_east = lon+m_to_coord(100, latitude=lat, direction='east')
    lon_west = lon-m_to_coord(-100, latitude=lat, direction='west')

    # Filter possible grid locations
    liv_df = liv_df[liv_df['lat_center'] <= lat_north]
    liv_df = liv_df[liv_df['lat_center'] >= lat_south]
    liv_df = liv_df[liv_df['lng_center'] <= lon_east]
    liv_df = liv_df[liv_df['lng_center'] >= lon_west]

    # return nan if there are no grid, mean of livability if there are multiple which equals the single value if there's only one grid
    if len(liv_df) == 0:
        return np.nan
    else:
        return round(float(liv_df['livability'].mean()),2)


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
        latitude = math.pi*latitude/180 # Convert latitude to raians
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
    print(get_liv_from_coord(52.438432250000005, 13.309635608453753,None))
