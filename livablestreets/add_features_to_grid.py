import pandas as pd
import numpy as np
# from sqlalchemy import column
from livablestreets.utils import simple_time_tracker, get_file, save_file, min_max_scaler
from shapely.geometry import Point, Polygon
import matplotlib.path as mplPath
import geopandas as gpd
import shapely.speedups



def features_into_list_points(file_name, lat='lat',lng='lon', location='Berlin'):
    """ Receives a file name, download it from GCP (or local if exists).
        Iterates through column pairs and returns the corresponding points """
    # Get the feature df, create a list of points out for each feature
    df_feature = get_file(file_name, local_file_path=f'data/{location}/Features', gcp_file_path = f'data/{location}/Features')
    print(f'loaded {file_name}')
    return [[x, y] for x, y in df_feature[[lat,lng]].itertuples(index=False)]



## 132.76s to complete 1000m grids
# List of points cointain in for loop of grids
def grid_to_polygon(df_grid):
    """Receives a dataframe with coordinates columns and adds a column of respective polygons"""
    polygons = []
    for index, row in df_grid.iterrows():
        polygons.append(mplPath.Path(np.array([[row['lat_start'],row['lng_start']],
                                                [row['lat_start'],row['lng_end']],
                                                [row['lat_end'],row['lng_start']],
                                                [row['lat_end'],row['lng_end']]])))
    df_grid['polygon'] = polygons

    return df_grid

def point_in_grid_counter(polygon, points):
    """Receives a shapely Polygon object and a list of points (a list of list of lat and lng pairs)
        and returns the number of points inside that polygon"""
    matches = 0
    for i in range(len(points)):
        np.sum(polygon.contains_point(points[i]))
    return matches

def feature_cat_mean_score(df):
    """ Receives a dataframe and looks for columns containing the field indicator (activities, comfort, mobility, social)
        Calculate the row-wise mean of columns in that field and add it to a new column called field_mean"""

    for field in ('activities', 'comfort', 'mobility', 'social'):
        columns_interest = [column for column in df.columns if f"{field}_" in column]
        df[f"{field}_mean"] = df[columns_interest].mean(axis=1)

    return df

@simple_time_tracker
def integrate_all_features_counts(df_grid=None, file_name = None,
                                    stepsize = 10000, location = 'Berlin',
                                    save_local=True, save_gcp=True):
    """ Receives the name of the file that is obtained from GCP (or local if available).
        Calls external function to create the grid polygon for each grid"""
    # shapely.speedups makes some of the spatial queries running faster
    # shapely.speedups.enable()

    # Get grid and create polygons
    if file_name is not None:
        df_grid = get_file(file_name=file_name, local_file_path=f'data/{location}/WorkingTables', gcp_file_path = f'data/{location}/WorkingTables')
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
    points_comfort_leisure_sports = features_into_list_points('comfort_leisure_sports.csv', location=location)
    points_comfort_sports = features_into_list_points('comfort_sports.csv', location=location)
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
    comfort_leisure_sports_in_polygon = []
    comfort_sports_in_polygon = []
    # comfort_trees_in_polygon = []
    mobility_public_transport_in_polygon = []
    social_community_in_polygon = []
    social_culture_in_polygon = []
    social_eating_in_polygon = []
    social_night_life_in_polygon = []

    total_grids=len(df_grid)
    for index, row in df_grid.iterrows():
        print(f'{index+1}/{total_grids}', end='\r')
        if row['grid_in_berlin']:
            polygon = row['polygon']
            activities_economic_in_polygon.append(point_in_grid_counter(polygon, points_activities_economic))
            activities_education_in_polygon.append(point_in_grid_counter(polygon, points_activities_education))
            activities_health_care_in_polygon.append(point_in_grid_counter(polygon, points_activities_health_care))
            activities_public_service_in_polygon.append(point_in_grid_counter(polygon, points_activities_public_service))
            comfort_leisure_sports_in_polygon.append(point_in_grid_counter(polygon, points_comfort_leisure_sports))
            comfort_sports_in_polygon.append(point_in_grid_counter(polygon, points_comfort_sports))
            # comfort_trees_in_polygon.append(point_in_grid_counter2(polygon, points_comfort_trees))
            mobility_public_transport_in_polygon.append(point_in_grid_counter(polygon, points_mobility_public_transport))
            social_community_in_polygon.append(point_in_grid_counter(polygon, points_social_community))
            social_culture_in_polygon.append(point_in_grid_counter(polygon, points_social_culture))
            social_eating_in_polygon.append(point_in_grid_counter(polygon, points_social_eating))
            social_night_life_in_polygon.append(point_in_grid_counter(polygon, points_social_night_life))
        else:
            activities_economic_in_polygon.append(-1)
            activities_education_in_polygon.append(-1)
            activities_health_care_in_polygon.append(-1)
            activities_public_service_in_polygon.append(-1)
            comfort_leisure_sports_in_polygon.append(-1)
            comfort_sports_in_polygon.append(-1)
            # comfort_trees_in_polygon.append(-1)
            mobility_public_transport_in_polygon.append(-1)
            social_community_in_polygon.append(-1)
            social_culture_in_polygon.append(-1)
            social_eating_in_polygon.append(-1)
            social_night_life_in_polygon.append(-1)

    df_grid['activities_economic'] = activities_economic_in_polygon
    df_grid['activities_education'] = activities_education_in_polygon
    df_grid['activities_health_care'] = activities_health_care_in_polygon
    df_grid['activities_public_service'] = activities_public_service_in_polygon
    df_grid['comfort_leisure_sports'] = comfort_leisure_sports_in_polygon
    df_grid['comfort_sports'] = comfort_sports_in_polygon
    # df_grid['comfort_trees'] = comfort_trees_in_polygon
    df_grid['mobility_public_transport'] = mobility_public_transport_in_polygon
    df_grid['social_community'] = social_community_in_polygon
    df_grid['social_culture'] = social_culture_in_polygon
    df_grid['social_eating'] = social_eating_in_polygon
    df_grid['social_night_life'] = social_night_life_in_polygon

    ## Create the livability score
    # Remove polygons to save space
    df_grid = df_grid.drop(columns=['polygon'])

    # MinMax normalize all features
    df_grid = min_max_scaler(df_grid)
    print('Features were MinMax scaled')

    # Calculate the mean per category
    df_grid= feature_cat_mean_score(df_grid)
    print('Category mean was calculated')

    return df_grid







## 338.25s to complete 1000m grids
# for loop of points in for loop of grids
def grid_to_polygon2(df_grid):
    """Receives a dataframe with coordinates columns and adds a column of respective polygons"""
    polygons = []
    for index, row in df_grid.iterrows():
        polygons.append(Polygon([Point(row['lat_start'],row['lng_start']),
                                  Point(row['lat_start'],row['lng_end']),
                                  Point(row['lat_end'],row['lng_start']),
                                  Point(row['lat_end'],row['lng_end'])]))
    df_grid['polygon'] = polygons
    return df_grid

def point_in_grid_counter2(polygon, points):
    """Receives a shapely Polygon object and a list of points (a list of list of lat and lng pairs)
        and returns the number of points inside that polygon"""
    contains = np.vectorize(lambda p: polygon.contains(Point(p)), signature='(n)->()')
    return np.sum(contains(np.array(points)))

@simple_time_tracker
def integrate_all_features_counts2(df_grid=None, file_name = None,
                                    stepsize = 10000, location = 'Berlin',
                                    save_local=True, save_gcp=True):
    """ Receives the name of the file that is obtained from GCP (or local if available).
        Calls external function to create the grid polygon for each grid"""
    # Get grid and create polygons
    df_grid = get_file(file_name=file_name, local_file_path=f'data/{location}/WorkingTables', gcp_file_path = f'data/{location}/WorkingTables')
    print('loaded grid')
    df_grid=grid_to_polygon2(df_grid)
    print('created polygons')

    # Get the list of points
    points_activities_economic = features_into_list_points('activities_economic.csv', location=location)
    points_activities_education = features_into_list_points('activities_education.csv', location=location)
    points_activities_health_care = features_into_list_points('activities_health_care.csv', location=location)
    points_activities_public_service = features_into_list_points('activities_public_service.csv', location=location)
    points_comfort_leisure_sports = features_into_list_points('comfort_leisure_sports.csv', location=location)
    points_comfort_sports = features_into_list_points('comfort_sports.csv', location=location)
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
    comfort_leisure_sports_in_polygon = []
    comfort_sports_in_polygon = []
    # comfort_trees_in_polygon = []
    mobility_public_transport_in_polygon = []
    social_community_in_polygon = []
    social_culture_in_polygon = []
    social_eating_in_polygon = []
    social_night_life_in_polygon = []

    total_grids=len(df_grid)
    for index, row in df_grid.iterrows():
        print(f'{index+1}/{total_grids}', end='\r')
        if row['grid_in_berlin']:
            polygon = row['polygon']
            activities_economic_in_polygon.append(point_in_grid_counter2(polygon, points_activities_economic))
            activities_education_in_polygon.append(point_in_grid_counter2(polygon, points_activities_education))
            activities_health_care_in_polygon.append(point_in_grid_counter2(polygon, points_activities_health_care))
            activities_public_service_in_polygon.append(point_in_grid_counter2(polygon, points_activities_public_service))
            comfort_leisure_sports_in_polygon.append(point_in_grid_counter2(polygon, points_comfort_leisure_sports))
            comfort_sports_in_polygon.append(point_in_grid_counter2(polygon, points_comfort_sports))
            # comfort_trees_in_polygon.append(point_in_grid_counter2(polygon, points_comfort_trees))
            mobility_public_transport_in_polygon.append(point_in_grid_counter2(polygon, points_mobility_public_transport))
            social_community_in_polygon.append(point_in_grid_counter2(polygon, points_social_community))
            social_culture_in_polygon.append(point_in_grid_counter2(polygon, points_social_culture))
            social_eating_in_polygon.append(point_in_grid_counter2(polygon, points_social_eating))
            social_night_life_in_polygon.append(point_in_grid_counter2(polygon, points_social_night_life))
        else:
            activities_economic_in_polygon.append(-1)
            activities_education_in_polygon.append(-1)
            activities_health_care_in_polygon.append(-1)
            activities_public_service_in_polygon.append(-1)
            comfort_leisure_sports_in_polygon.append(-1)
            comfort_sports_in_polygon.append(-1)
            # comfort_trees_in_polygon.append(-1)
            mobility_public_transport_in_polygon.append(-1)
            social_community_in_polygon.append(-1)
            social_culture_in_polygon.append(-1)
            social_eating_in_polygon.append(-1)
            social_night_life_in_polygon.append(-1)

    df_grid['activities_economic'] = activities_economic_in_polygon
    df_grid['activities_education'] = activities_education_in_polygon
    df_grid['activities_health_care'] = activities_health_care_in_polygon
    df_grid['activities_public_service'] = activities_public_service_in_polygon
    df_grid['comfort_leisure_sports'] = comfort_leisure_sports_in_polygon
    df_grid['comfort_sports'] = comfort_sports_in_polygon
    # df_grid['comfort_trees'] = comfort_trees_in_polygon
    df_grid['mobility_public_transport'] = mobility_public_transport_in_polygon
    df_grid['social_community'] = social_community_in_polygon
    df_grid['social_culture'] = social_culture_in_polygon
    df_grid['social_eating'] = social_eating_in_polygon
    df_grid['social_night_life'] = social_night_life_in_polygon

    ## Create the livability score
    # Remove polygons to save space
    # df_grid = df_grid.drop(columns=['polygon'])

    return df_grid




## 79.36s to complete 1000m grids
### With sjoin
def features_into_list_points3(file_name, lat='lat',lng='lon', location='Berlin'):
    """ Receives a file name, download it from GCP (or local if exists).
        Iterates through column pairs and returns the corresponding points """
    # Get the feature df, create a list of points out for each feature

    df_feature = get_file(file_name, local_file_path=f'data/{location}/Features', gcp_file_path = f'data/{location}/Features')
    print(f'loaded {file_name}')
    df_feature = df_feature[[lat,lng]].copy()
    df_feature['coords'] = list(zip(df_feature[lat],df_feature[lng]))
    df_feature['coords'] = df_feature['coords'].apply(Point)
    return gpd.GeoDataFrame(df_feature, geometry='coords', crs='wgs84')

def grid_to_polygon3(df_grid):
    """Receives a dataframe with coordinates columns and adds a column of respective polygons"""
    polygons = []
    for index, row in df_grid.iterrows():
        polygons.append(Polygon([Point(row['lat_start'],row['lng_start']),
                                  Point(row['lat_start'],row['lng_end']),
                                  Point(row['lat_end'],row['lng_start']),
                                  Point(row['lat_end'],row['lng_end'])]))
    df_grid['polygon'] = polygons
    return df_grid

def point_in_grid_counter3(polygon, points):
    """Receives a shapely Polygon object and a list of points (a list of list of lat and lng pairs)
        and returns the number of points inside that polygon"""
    pointInPolys = gpd.tools.sjoin(points, polygon, predicate="within", how='inner')
    return len(pointInPolys)

@simple_time_tracker
def integrate_all_features_counts3(df_grid=None, file_name = None,
                                    stepsize = 10000, location = 'Berlin',
                                    save_local=True, save_gcp=True):
    """ Receives the name of the file that is obtained from GCP (or local if available).
        Calls external function to create the grid polygon for each grid"""

    # shapely.speedups makes some of the spatial queries running faster
    # shapely.speedups.enable()

    # Get grid and create polygons
    if df_grid is None:
        df_grid = get_file(file_name=file_name, local_file_path=f'data/{location}/WorkingTables', gcp_file_path = f'data/{location}/WorkingTables')
    print('loaded grid')
    df_grid=grid_to_polygon3(df_grid)
    print('created polygons')

    # Get the list of points
    points_activities_economic = features_into_list_points3('activities_economic.csv', location=location)
    points_activities_education = features_into_list_points3('activities_education.csv', location=location)
    points_activities_health_care = features_into_list_points3('activities_health_care.csv', location=location)
    points_activities_public_service = features_into_list_points3('activities_public_service.csv', location=location)
    points_comfort_leisure_sports = features_into_list_points3('comfort_leisure_sports.csv', location=location)
    points_comfort_sports = features_into_list_points3('comfort_sports.csv', location=location)
    # points_comfort_trees = features_into_list_points3('comfort_trees.csv', location=location)
    points_mobility_public_transport = features_into_list_points3('mobility_public_transport.csv', location=location)
    points_social_community = features_into_list_points3('social_community.csv', location=location)
    points_social_culture = features_into_list_points3('social_culture.csv', location=location)
    points_social_eating = features_into_list_points3('social_eating.csv', location=location)
    points_social_night_life = features_into_list_points3('social_night_life.csv', location=location)

    print('created points lists')

    # Iterates through the polygons and ask how many points are inside
    activities_economic_in_polygon = []
    activities_education_in_polygon = []
    activities_health_care_in_polygon = []
    activities_public_service_in_polygon = []
    comfort_leisure_sports_in_polygon = []
    comfort_sports_in_polygon = []
    # comfort_trees_in_polygon = []
    mobility_public_transport_in_polygon = []
    social_community_in_polygon = []
    social_culture_in_polygon = []
    social_eating_in_polygon = []
    social_night_life_in_polygon = []

    total_grids=len(df_grid)
    for index, row in df_grid.iterrows():
        print(f'{index+1}/{total_grids}', end='\r')
        if row['grid_in_berlin']:
            polygon = gpd.GeoDataFrame(pd.DataFrame({'index_value':1,
                                                     'geometry':df_grid.loc[index, 'polygon']}, index=[1]), crs='wgs84')

            activities_economic_in_polygon.append(point_in_grid_counter3(polygon, points_activities_economic))
            activities_education_in_polygon.append(point_in_grid_counter3(polygon, points_activities_education))
            activities_health_care_in_polygon.append(point_in_grid_counter3(polygon, points_activities_health_care))
            activities_public_service_in_polygon.append(point_in_grid_counter3(polygon, points_activities_public_service))
            comfort_leisure_sports_in_polygon.append(point_in_grid_counter3(polygon, points_comfort_leisure_sports))
            comfort_sports_in_polygon.append(point_in_grid_counter3(polygon, points_comfort_sports))
            # comfort_trees_in_polygon.append(point_in_grid_counter3(polygon, points_comfort_trees))
            mobility_public_transport_in_polygon.append(point_in_grid_counter3(polygon, points_mobility_public_transport))
            social_community_in_polygon.append(point_in_grid_counter3(polygon, points_social_community))
            social_culture_in_polygon.append(point_in_grid_counter3(polygon, points_social_culture))
            social_eating_in_polygon.append(point_in_grid_counter3(polygon, points_social_eating))
            social_night_life_in_polygon.append(point_in_grid_counter3(polygon, points_social_night_life))
        else:
            activities_economic_in_polygon.append(np.NaN)
            activities_education_in_polygon.append(np.NaN)
            activities_health_care_in_polygon.append(np.NaN)
            activities_public_service_in_polygon.append(np.NaN)
            comfort_leisure_sports_in_polygon.append(np.NaN)
            comfort_sports_in_polygon.append(np.NaN)
            # comfort_trees_in_polygon.append(np.NaN)
            mobility_public_transport_in_polygon.append(np.NaN)
            social_community_in_polygon.append(np.NaN)
            social_culture_in_polygon.append(np.NaN)
            social_eating_in_polygon.append(np.NaN)
            social_night_life_in_polygon.append(np.NaN)

    df_grid['activities_economic'] = activities_economic_in_polygon
    df_grid['activities_education'] = activities_education_in_polygon
    df_grid['activities_health_care'] = activities_health_care_in_polygon
    df_grid['activities_public_service'] = activities_public_service_in_polygon
    df_grid['comfort_leisure_sports'] = comfort_leisure_sports_in_polygon
    df_grid['comfort_sports'] = comfort_sports_in_polygon
    # df_grid['comfort_trees'] = comfort_trees_in_polygon
    df_grid['mobility_public_transport'] = mobility_public_transport_in_polygon
    df_grid['social_community'] = social_community_in_polygon
    df_grid['social_culture'] = social_culture_in_polygon
    df_grid['social_eating'] = social_eating_in_polygon
    df_grid['social_night_life'] = social_night_life_in_polygon

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
    df_grid = integrate_all_features_counts3(stepsize = 3000, file_name='Berlin_grid_3000m.csv')
    # df_grid = integrate_all_features_counts3(stepsize = 1000, file_name='Berlin_grid_1000m.csv')
    # df_grid = integrate_all_features_counts3(stepsize = 100, file_name='Berlin_grid_100m.csv')

    print('This shouldnt run add_features_to_grid.py')
