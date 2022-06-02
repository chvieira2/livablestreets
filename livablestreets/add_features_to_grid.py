import pandas as pd
import numpy as np
from livablestreets.utils import simple_time_tracker, get_file, save_file
from shapely.geometry import Point, Polygon


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

def features_into_list_points(file_name, lat='lat',lng='lon'):
    """ Receives a file name, download it from GCP (or local if exists).
        Iterates through column pairs and returns the corresponding points """
    # Get the feature df, create a list of points out for each feature
    df_feature = get_file(file_name)
    print(f'loaded {file_name}')
    return [[x, y] for x, y in df_feature[[lat,lng]].itertuples(index=False)]

def point_in_grid_counter(polygon, points):
    """Receives a shapely Polygon object and a list of points (a list of list of lat and lng pairs)
        and returns the number of points inside that polygon"""
    contains = np.vectorize(lambda p: polygon.contains(Point(p)), signature='(n)->()')
    return np.sum(contains(np.array(points)))

@simple_time_tracker
def integrate_all_features_counts(file_name):
    """ Receives the name of the file that is obtained from GCP (or local if available).
        Calls external function to create the grid polygon for each grid"""
    # Get grid and create polygons
    df_grid = get_file(file_name=file_name)
    print('loaded grid')
    df_grid=grid_to_polygon(df_grid)
    print('created polygons')

    # Get the list of points
    points_activities_economic = features_into_list_points('activities_economic.csv')
    points_activities_education = features_into_list_points('activities_education.csv')
    points_activities_health_care = features_into_list_points('activities_health_care.csv')
    points_activities_public_service = features_into_list_points('activities_public_service.csv')
    points_comfort_leisure_sports = features_into_list_points('comfort_leisure_sports.csv')
    points_comfort_sports = features_into_list_points('comfort_sports.csv')
    # points_comfort_trees = features_into_list_points('comfort_trees.csv')
    points_convenience = features_into_list_points('df_convenience.csv')
    points_mobility_public_transport = features_into_list_points('mobility_public_transport.csv')
    points_social_community = features_into_list_points('social_community.csv')
    points_social_culture = features_into_list_points('social_culture.csv')
    points_social_eating = features_into_list_points('social_eating.csv')
    points_social_night_life = features_into_list_points('social_night_life.csv')

    print('created points lists')

    # Iterates through the polygons and ask how many points are inside
    activities_economic_in_polygon = []
    activities_education_in_polygon = []
    activities_health_care_in_polygon = []
    activities_public_service_in_polygon = []
    comfort_leisure_sports_in_polygon = []
    comfort_sports_in_polygon = []
    # comfort_trees_in_polygon = []
    convenience_in_polygon = []
    mobility_public_transport_in_polygon = []
    social_community_in_polygon = []
    social_culture_in_polygon = []
    social_eating_in_polygon = []
    social_night_life_in_polygon = []

    for index, row in df_grid.iterrows():
        if row['grid_in_berlin']:
            polygon = row['polygon']
            activities_economic_in_polygon.append(point_in_grid_counter(polygon, points_activities_economic))
            activities_education_in_polygon.append(point_in_grid_counter(polygon, points_activities_education))
            activities_health_care_in_polygon.append(point_in_grid_counter(polygon, points_activities_health_care))
            activities_public_service_in_polygon.append(point_in_grid_counter(polygon, points_activities_public_service))
            comfort_leisure_sports_in_polygon.append(point_in_grid_counter(polygon, points_comfort_leisure_sports))
            comfort_sports_in_polygon.append(point_in_grid_counter(polygon, points_comfort_sports))
            # comfort_trees_in_polygon.append(point_in_grid_counter(polygon, points_comfort_trees))
            convenience_in_polygon.append(point_in_grid_counter(polygon, points_convenience))
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
            convenience_in_polygon.append(-1)
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
    df_grid['convenience'] = convenience_in_polygon
    df_grid['mobility_public_transport'] = mobility_public_transport_in_polygon
    df_grid['social_community'] = social_community_in_polygon
    df_grid['social_culture'] = social_culture_in_polygon
    df_grid['social_eating'] = social_eating_in_polygon
    df_grid['social_night_life'] = social_night_life_in_polygon

    ## Create the livability score
    # Remove polygons to save space
    # df_grid = df_grid.drop(columns=['polygon'])

    return df_grid




if __name__ == '__main__':
    # df_grid = integrate_all_features_counts(file_name='Berlin_grid_1000m.csv')
    # save_file(df_grid, file_name='Berlin_grid_1000m.csv')
    df_grid = integrate_all_features_counts(file_name='Berlin_grid_100m.csv')
    save_file(df_grid, file_name='FeatCounts_Berlin_grid_100m.csv')
