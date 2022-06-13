import pandas as pd
import numpy as np
from livablestreets.utils import simple_time_tracker, get_file, save_file
from livablestreets.FeatCount_blurrying import FeatCount_blurrying
from shapely.geometry import Point, Polygon
# import matplotlib.path as mplPath
import geopandas as gpd
# import shapely.speedups
import os
from config.config import ROOT_DIR


## 79.36s to complete 1000m grids
### With sjoin
def features_into_list_points(file_name, location, lat='lat',lng='lon'):
    """ Receives a file name, download it from GCP (or local if exists).
        Iterates through column pairs and returns the corresponding points """
    # Get the feature df, create a list of points out for each feature

    df_feature = get_file(file_name, local_file_path=f'livablestreets/data/{location}/Features') #, gcp_file_path = f'data/{location}/Features')
    print(f'loaded {file_name}')
    df_feature = df_feature[[lat,lng]].copy()
    df_feature['coords'] = list(zip(df_feature[lat],df_feature[lng]))
    df_feature['coords'] = df_feature['coords'].apply(Point)
    return gpd.GeoDataFrame(df_feature, geometry='coords', crs='wgs84')

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

def point_in_grid_counter(polygon, points):
    """Receives a shapely Polygon object and a list of points (a list of list of lat and lng pairs)
        and returns the number of points inside that polygon"""
    pointInPolys = gpd.tools.sjoin(points, polygon, predicate="within", how='inner')
    return len(pointInPolys)

def feature_cat_mean_score(df):
    """ Receives a dataframe and looks for columns containing the categories indicator (activities, comfort, mobility, social)
        Calculate the row-wise mean of columns in that categories and add it to a new column called categories_mean"""

    for categories in ('activities', 'comfort', 'mobility', 'social', 'negative'):
        columns_interest = [column for column in df.columns if f"{categories}_" in column]
        df[f"{categories}_mean"] = df[columns_interest].mean(axis=1)

    return df

@simple_time_tracker
def integrate_all_features_counts(stepsize, location_name, sigmas,
                                    df_grid=None,
                                    save_local=True, save_gcp=False):
    """ Receives the name of the file that is obtained from GCP (or local if available).
        Calls external function to create the grid polygon for each grid"""
    # shapely.speedups makes some of the spatial queries running faster
    # shapely.speedups.enable()

    # Get grid and create polygons
    if df_grid is None:
        df_grid = get_file(file_name=f'{location_name}_grid_{stepsize}m.csv', local_file_path=f'livablestreets/data/{location_name}/WorkingTables', gcp_file_path = f'data/{location_name}/WorkingTables')
    print('loaded grid')
    df_grid=grid_to_polygon(df_grid)
    print('created polygons')


    # Get list of features file
    directory = f'{ROOT_DIR}/livablestreets/data/{location_name}/Features'

    feature_names = [feature_name.replace(".csv", "") \
                    for feature_name in os.listdir(directory) if (feature_name.startswith("activities_") \
                    or feature_name.startswith("comfort_") or feature_name.startswith("mobility_") \
                    or feature_name.startswith("social_life_" ) or feature_name.startswith("negative_") ) \
                    and feature_name.endswith(".csv")]

    # Get the dict of points and in_polygons values
    dict_of_points = {}
    dict_in_polygon = {}
    for feature in feature_names:
        dict_of_points[f"points_{feature}"] = features_into_list_points(f'{feature}.csv', location=location_name)
        dict_in_polygon[f"{feature}_in_polygon"] = []

    # Iterate through grids and collects counts of features per grid
    total_grids=len(df_grid)
    for index, row in df_grid.iterrows():
        print(f'{index+1}/{total_grids}', end='\r')
        if row['grid_in_location']:
            polygon = gpd.GeoDataFrame(pd.DataFrame({'index_value':1,
                                                     'geometry':df_grid.loc[index, 'polygon']}, index=[1]), crs='wgs84')

            for feature in feature_names:
                dict_in_polygon[f'{feature}_in_polygon'].append(point_in_grid_counter(polygon, dict_of_points[f'points_{feature}']))
        else:
            for feature in feature_names:
                dict_in_polygon[f'{feature}_in_polygon'].append(0)

    for feature in feature_names:
        df_grid[feature] = dict_in_polygon[f'{feature}_in_polygon']



    ## Blurry count information
    # Remove polygons to save space
    df_grid = df_grid.drop(columns=['polygon'])

    # Apply blurrying function
    df_grid = FeatCount_blurrying(df=df_grid, sigmas_list=sigmas)

    ## Create the livability score
    # Calculate the mean per category
    df_grid= feature_cat_mean_score(df_grid)
    print('Categories mean were calculated')

    save_file(df_grid, file_name=f'FeatCount_{location_name}_grid_{stepsize}m.csv', local_file_path=f'livablestreets/data/{location_name}/WorkingTables', gcp_file_path = f'data/{location_name}/WorkingTables', save_local=save_local, save_gcp=save_gcp)

    return df_grid








if __name__ == '__main__':
    df_grid = integrate_all_features_counts(location_name = 'berlin', stepsize = 1000,
                                            sigmas=[0.1, 0.25, 0.025, 0.1, 0.15, 0.25, 0.2, 0.5, 0.15, 0.25, 0.2, 0.05, 0.25, 0.1, 0.05, 0.05, 0.1, 0.25, 0.4, 0.15, 0.25, 0.1, 0.1, 0.15, 0.25, 0.125, 0.05, 0.025, 0.15, 0.1, 0.1, 0.1])
    print(df_grid.info())
    # df_grid = integrate_all_features_counts(stepsize = 1000)
    # df_grid = integrate_all_features_counts(stepsize = 100)
