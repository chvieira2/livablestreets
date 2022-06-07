import pandas as pd
import numpy as np
from livablestreets.utils import simple_time_tracker, get_file, save_file, min_max_scaler
from livablestreets.FeatCount_blurrying import FeatCount_blurrying
from shapely.geometry import Point, Polygon
import matplotlib.path as mplPath
import geopandas as gpd
import shapely.speedups


## 79.36s to complete 1000m grids
### With sjoin
def features_into_list_points(file_name, location, lat='lat',lng='lon'):
    """ Receives a file name, download it from GCP (or local if exists).
        Iterates through column pairs and returns the corresponding points """
    # Get the feature df, create a list of points out for each feature

    gdf = gpd.read_file(filename=f'livablestreets/data/{location}/Features/{file_name}')
    print(f'loaded {file_name}')

    gdf = gdf.explode(index_parts=True)
    return gdf

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
def integrate_all_features_counts(stepsize, location,
                                    df_grid=None, file_name = None,
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
    points_activities_economic = features_into_list_points('shapes-mobility-public_transport_rail.geojson', location=location)

    print('created points lists')

    # Iterates through the polygons and ask how many points are inside
    activities_economic_in_polygon = []

    total_grids=len(df_grid)
    for index, row in df_grid.iterrows():
        print(f'{index+1}/{total_grids}', end='\r')
        if row['grid_in_location']:
            polygon = gpd.GeoDataFrame(pd.DataFrame({'index_value':1,
                                                     'geometry':df_grid.loc[index, 'polygon']}, index=[1]), crs='wgs84')

            activities_economic_in_polygon.append(point_in_grid_counter(polygon, points_activities_economic))

        else:
            activities_economic_in_polygon.append(np.NaN)


    df_grid['activities_economic'] = activities_economic_in_polygon

    ## Blurry count information
    # Remove polygons to save space
    df_grid = df_grid.drop(columns=['polygon'])

    # Apply blurrying function
    # df_grid = FeatCount_blurrying(df=df_grid)

    ## Create the livability score
    # Calculate the mean per category
    df_grid= feature_cat_mean_score(df_grid)
    print('Categories mean were calculated')

    save_file(df_grid, file_name=f'FeatCount_{location}_grid_{stepsize}m.csv', local_file_path=f'data/{location}/WorkingTables', gcp_file_path = f'data/{location}/WorkingTables', save_local=save_local, save_gcp=save_gcp)

    return df_grid








if __name__ == '__main__':
    df_grid = integrate_all_features_counts(location = 'berlin', stepsize = 1000, file_name='berlin_grid_1000m.csv')
