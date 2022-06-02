import pandas as pd
import numpy as np
from livablestreets.utils import simple_time_tracker
from google.cloud import storage
from livablestreets.params import BUCKET_NAME
from shapely.geometry import Point, Polygon
import geopandas

@simple_time_tracker
def get_file_from_gcp(file_name, save_local=True, optimize=False, **kwargs):
    """method to get the training data (or a portion of it) from google cloud bucket"""

    try:
        df = pd.read_csv(f'livablestreets/data/{file_name}')
    except FileNotFoundError:
        # Add Client() here
        client = storage.Client()
        path = f"gs://{BUCKET_NAME}/data/{file_name}"
        df = pd.read_csv(path)
        if save_local:
            df.to_csv(f'livablestreets/data/{file_name}', index=False)

    return df

def grid_to_polygon(df_grid):
    """Receives a dataframe with coordinates columns and adds a column of respective polygons"""
    polygons = []
    for index, row in df_grid.iterrows():
        polygons.append(Polygon([Point(row['lat_start'],row['lng_start']),
                                  Point(row['lat_start'],row['lng_end']),
                                  Point(row['lat_end'],row['lng_start']),
                                  Point(row['lat_end'],row['lng_end'])]))
    df_grid['polygon'] = polygons
    return df_grid

def integrate_feature_counts(df_grid,feature_file, feature_name):
    df_feature = get_file_from_gcp(file_name=feature_file)

    # Collect all features as a list of points
    points = [[lat, lng] for lat, lng in df_feature[['lat','lon']].itertuples(index=False)]

    # Iterates through the polygons and ask how many points are inside
    count_in_polygon = []
    for index, row in df_grid.iterrows():
        if row['grid_in_berlin']:
            poly = row['polygon']
            contains = np.vectorize(lambda p: poly.contains(Point(p)), signature='(n)->()')
            count_in_polygon.append(np.sum(contains(np.array(points))))
        else:
            count_in_polygon.append(-1)
    df_grid[feature_name] = count_in_polygon
    return df_grid

@simple_time_tracker
def integrate_all_features_counts(file_name, save_local=False, save_gcp=False):

    df_grid = get_file_from_gcp(file_name=file_name)
    df_grid=grid_to_polygon(df_grid)

    df_grid=integrate_feature_counts(df_grid,'activities_economic.csv', feature_name='activities_economic')
    df_grid=integrate_feature_counts(df_grid,'activities_education.csv', feature_name='activities_education')
    df_grid=integrate_feature_counts(df_grid,'activities_health_care.csv', feature_name='activities_health_care')
    df_grid=integrate_feature_counts(df_grid,'activities_public_service.csv', feature_name='activities_public_service')
    df_grid=integrate_feature_counts(df_grid,'comfort_leisure_sports.csv', feature_name='comfort_leisure_sports')
    df_grid=integrate_feature_counts(df_grid,'comfort_sports.csv', feature_name='comfort_sports')
    # df_grid=integrate_feature_counts(df_grid,'comfort_trees.csv', feature_name='comfort_trees')
    df_grid=integrate_feature_counts(df_grid,'df_convenience.csv', feature_name='convenience')
    df_grid=integrate_feature_counts(df_grid,'mobility_public_transport.csv', feature_name='mobility_public_transport')
    df_grid=integrate_feature_counts(df_grid,'social_community.csv', feature_name='social_community')
    df_grid=integrate_feature_counts(df_grid,'social_culture.csv', feature_name='social_culture')
    df_grid=integrate_feature_counts(df_grid,'social_eating.csv', feature_name='social_eating')
    df_grid=integrate_feature_counts(df_grid,'social_night_life.csv', feature_name='social_night_life')

    # Remove polygons to save space
    df_grid = df_grid.drop(columns=['polygon'])

    # Save locally
    if save_local:
        df_grid.to_csv(f'livablestreets/data/FeatCounts_{file_name}', index=False)

    # Save on GCP
    if save_gcp:
        client = storage.Client().bucket(BUCKET_NAME)

        storage_location = f'data/WorkingTables/FeatCounts_{file_name}'
        blob = client.blob(storage_location)
        print('blob passed')
        blob.upload_from_filename(f'livablestreets/data/FeatCounts_{file_name}')
        print(f"=> FeatCounts_{file_name} uploaded to bucket {BUCKET_NAME} inside {storage_location}")

    return df_grid

if __name__ == '__main__':
    df_grid = integrate_all_features_counts(file_name='Berlin_grid_1000m.csv', save_local=True, save_gcp=True)
    df_grid = integrate_all_features_counts(file_name='Berlin_grid_100m.csv', save_local=True, save_gcp=True)
