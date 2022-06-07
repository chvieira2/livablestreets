import pandas as pd
import numpy as np
# from sqlalchemy import column
from livablestreets.utils import simple_time_tracker, get_file, save_file, min_max_scaler
from shapely.geometry import Point, Polygon
import matplotlib.path as mplPath
import geopandas as gpd
import shapely.speedups

from livablestreets.query_names_detailed import master_query_complex


## 79.36s to complete 1000m grids
### With sjoin
def features_into_list_points(file_name, location='berlin'):
    """ Receives a file name, download it from GCP (or local if exists).
        Iterates through column pairs and returns the corresponding points """
    # Get the feature df, create a list of points out for each feature

    geojson_feature = get_file(file_name, local_file_path=f'data/{location}/Features',
                            gcp_file_path = f'data/{location}/Features')
    return gpd.GeoDataFrame(geojson_feature)

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
    """ Receives a dataframe and looks for columns containing the field indicator (activities, comfort, mobility, social)
        Calculate the row-wise mean of columns in that field and add it to a new column called field_mean"""

    for field in ('activities', 'comfort', 'mobility', 'social'):
        columns_interest = [column for column in df.columns if f"{field}_" in column]
        df[f"{field}_mean"] = df[columns_interest].mean(axis=1)

    return df

@simple_time_tracker
def integrate_all_features_counts(df_grid=None, file_name = None,
                                    stepsize = 3000, location = 'berlin',
                                    save_local=True, save_gcp=False):
    """ Receives the name of the file that is obtained from GCP (or local if available).
        Calls external function to create the grid polygon for each grid"""

    # shapely.speedups makes some of the spatial queries running faster
    # shapely.speedups.enable()

    # Get grid and create polygons
    if df_grid is None:
        df_grid = get_file(file_name=file_name, local_file_path=f'data/{location}/WorkingTables', gcp_file_path = f'data/{location}/WorkingTables')
    print('loaded grid')
    df_grid=grid_to_polygon(df_grid)
    print('created polygons')

    # Get the list of points
    df_master = master_query_complex()



    total_grids=len(df_grid)

    for index_grid, row_grid in df_grid.iterrows():
        point_in_polygon = []
        print(f'{index_grid+1}/{total_grids}', end='\r')

        if row_grid['grid_in_location']:
            polygon = gpd.GeoDataFrame(pd.DataFrame({'index_value':1,
                                                    'geometry':df_grid.loc[index_grid, 'polygon']}, index=[1]), crs='wgs84')

            for index_points, row_points in df_master.iterrows():
                filter_name = index_points
                category = row_points['category']

                points = features_into_list_points(f'shapes-{category}-{filter_name}.geojson' , location=location)
                print(f'created points lists: filter_name')

                print(points['coordinates'])


            print(type(point_in_polygon), point_in_polygon)

            df_grid[filter_name] = point_in_polygon




            point_in_polygon.append(point_in_grid_counter(polygon, points))



        else:
            point_in_polygon.append(np.NaN)



    ## Create the livability score
    # Remove polygons to save space
    df_grid = df_grid.drop(columns=['polygon'])

    # MinMax normalize all features
    df_grid = min_max_scaler(df_grid)
    print('Features were MinMax scaled')

    # Calculate the mean per category
    df_grid= feature_cat_mean_score(df_grid)
    print('Category mean was calculated')

    save_file(df_grid, file_name=f'FeatCount_{location}_grid_{stepsize}m.csv', local_file_path=f'data/{location}/WorkingTables', gcp_file_path = f'data/{location}/WorkingTables', save_local=save_local, save_gcp=save_gcp)

    return df_grid








if __name__ == '__main__':
    df_grid = integrate_all_features_counts(stepsize = 3000, file_name='berlin_grid_3000m.csv')
    # df_grid = integrate_all_features_counts(stepsize = 1000, file_name='berlin_grid_1000m.csv')
    # df_grid = integrate_all_features_counts(stepsize = 100, file_name='berlin_grid_100m.csv')
