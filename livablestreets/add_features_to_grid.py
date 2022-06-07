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

    df_feature = get_file(file_name, local_file_path=f'data/{location}/Features', gcp_file_path = f'data/{location}/Features')
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

    for categories in ('activities', 'comfort', 'mobility', 'social'):
        columns_interest = [column for column in df.columns if f"{categories}_" in column]
        df[f"{categories}_mean"] = df[columns_interest].mean(axis=1)

    return df

@simple_time_tracker
def integrate_all_features_counts(stepsize, location,
                                    df_grid=None, file_name = None,
                                    save_local=True, save_gcp=True):
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
    points_activities_economic = features_into_list_points('activities_economic.csv', location=location)
    points_activities_education = features_into_list_points('activities_education.csv', location=location)
    points_activities_health_care = features_into_list_points('activities_health_care.csv', location=location)
    points_activities_public_service = features_into_list_points('activities_public_service.csv', location=location)
    points_comfort_leisure_spots = features_into_list_points('comfort_leisure_spots.csv', location=location)
    points_comfort_spots = features_into_list_points('comfort_spots.csv', location=location)
    # points_comfort_trees = features_into_list_points('comfort_trees.csv', location=location)
    points_mobility_public_transport = features_into_list_points('mobility_public_transport.csv', location=location)
    points_social_community = features_into_list_points('social_community.csv', location=location)
    points_social_culture = features_into_list_points('social_culture.csv', location=location)
    points_social_eating = features_into_list_points('social_eating.csv', location=location)
    points_social_night_life = features_into_list_points('social_night_life.csv', location=location)

    print('created points lists')

    # Iterates through the polygons and ask how many points are inside
    activities_economic_in_polygon = []
    activities_education_in_polygon = []
    activities_health_care_in_polygon = []
    activities_public_service_in_polygon = []
    comfort_leisure_spots_in_polygon = []
    comfort_spots_in_polygon = []
    # comfort_trees_in_polygon = []
    mobility_public_transport_in_polygon = []
    social_community_in_polygon = []
    social_culture_in_polygon = []
    social_eating_in_polygon = []
    social_night_life_in_polygon = []

    total_grids=len(df_grid)
    for index, row in df_grid.iterrows():
        print(f'{index+1}/{total_grids}', end='\r')
        if row['grid_in_location']:
            polygon = gpd.GeoDataFrame(pd.DataFrame({'index_value':1,
                                                     'geometry':df_grid.loc[index, 'polygon']}, index=[1]), crs='wgs84')

            activities_economic_in_polygon.append(point_in_grid_counter(polygon, points_activities_economic))
            activities_education_in_polygon.append(point_in_grid_counter(polygon, points_activities_education))
            activities_health_care_in_polygon.append(point_in_grid_counter(polygon, points_activities_health_care))
            activities_public_service_in_polygon.append(point_in_grid_counter(polygon, points_activities_public_service))
            comfort_leisure_spots_in_polygon.append(point_in_grid_counter(polygon, points_comfort_leisure_spots))
            comfort_spots_in_polygon.append(point_in_grid_counter(polygon, points_comfort_spots))
            # comfort_trees_in_polygon.append(point_in_grid_counter(polygon, points_comfort_trees))
            mobility_public_transport_in_polygon.append(point_in_grid_counter(polygon, points_mobility_public_transport))
            social_community_in_polygon.append(point_in_grid_counter(polygon, points_social_community))
            social_culture_in_polygon.append(point_in_grid_counter(polygon, points_social_culture))
            social_eating_in_polygon.append(point_in_grid_counter(polygon, points_social_eating))
            social_night_life_in_polygon.append(point_in_grid_counter(polygon, points_social_night_life))
        else:
            activities_economic_in_polygon.append(0)
            activities_education_in_polygon.append(0)
            activities_health_care_in_polygon.append(0)
            activities_public_service_in_polygon.append(0)
            comfort_leisure_spots_in_polygon.append(0)
            comfort_spots_in_polygon.append(0)
            # comfort_trees_in_polygon.append(0)
            mobility_public_transport_in_polygon.append(0)
            social_community_in_polygon.append(0)
            social_culture_in_polygon.append(0)
            social_eating_in_polygon.append(0)
            social_night_life_in_polygon.append(0)

    df_grid['activities_economic'] = activities_economic_in_polygon
    df_grid['activities_education'] = activities_education_in_polygon
    df_grid['activities_health_care'] = activities_health_care_in_polygon
    df_grid['activities_public_service'] = activities_public_service_in_polygon
    df_grid['comfort_leisure_spots'] = comfort_leisure_spots_in_polygon
    df_grid['comfort_spots'] = comfort_spots_in_polygon
    # df_grid['comfort_trees'] = comfort_trees_in_polygon
    df_grid['mobility_public_transport'] = mobility_public_transport_in_polygon
    df_grid['social_community'] = social_community_in_polygon
    df_grid['social_culture'] = social_culture_in_polygon
    df_grid['social_eating'] = social_eating_in_polygon
    df_grid['social_night_life'] = social_night_life_in_polygon

    ## Blurry count information
    # Remove polygons to save space
    df_grid = df_grid.drop(columns=['polygon'])

    # Apply blurrying function
    df_grid = FeatCount_blurrying(df=df_grid)

    ## Create the livability score
    # Calculate the mean per category
    df_grid= feature_cat_mean_score(df_grid)
    print('Categories mean were calculated')

    save_file(df_grid, file_name=f'FeatCount_{location}_grid_{stepsize}m.csv', local_file_path=f'data/{location}/WorkingTables', gcp_file_path = f'data/{location}/WorkingTables', save_local=save_local, save_gcp=save_gcp)

    return df_grid








if __name__ == '__main__':
    df_grid = integrate_all_features_counts(location = 'berlin', stepsize = 1000, file_name='berlin_grid_1000m.csv')
    # df_grid = integrate_all_features_counts(stepsize = 1000, file_name='Berlin_grid_1000m.csv')
    # df_grid = integrate_all_features_counts(stepsize = 100, file_name='Berlin_grid_100m.csv')
