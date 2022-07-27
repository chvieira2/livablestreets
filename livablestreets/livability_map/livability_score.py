from cmath import inf
from livablestreets.utils import save_file, min_max_scaler, get_file
import pandas as pd
import numpy as np


def feature_cat_mean_score(df):
    """ Receives a dataframe and looks for columns containing the categories indicator (activities, comfort, mobility, social)
        Calculate the row-wise mean of columns in that categories and add it to a new column called categories_mean"""

    for categories in ('activities', 'comfort', 'mobility', 'social', 'negative'):
        columns_interest = [column for column in df.columns if f"{categories}_" in column]
        df[f"{categories}_mean"] = df[columns_interest].mean(axis=1)

    return df

#def livability_score(df, weights = [1,1,1,1,1],
def livability_score_old(df, weights = [1,1,1,1,1],
                     categories_interest = ['activities_mean', 'comfort_mean', 'mobility_mean', 'social_mean', 'negative_mean'],
                     stepsize = 200, location_name = 'berlin',
                     save_local=True, save_gcp=False):
    """ Calculates the livability score in each grid by taking the weighted sum of all category_mean values.
        """
    columns_of_interest = [col for col in df.columns if any(x in col for x in ['activities_', 'comfort_', 'mobility_', 'social_', 'negative_']) and col not in categories_interest]

    # Convert values of each feature
    # for c in columns_of_interest:
    #     df[c] = convert_feature_impact(df, c, stepsize = stepsize)


    # Calculate the mean per category
    df = min_max_scaler(df, columns = columns_of_interest)
    df_foo= feature_cat_mean_score(df)

    # weights[4] = (-1)*weights[4]
    new_cols = [col + '_weighted' for col in categories_interest]
    df_foo[new_cols] = df_foo[categories_interest].mul(weights)
    df['livability'] = df_foo[new_cols].sum(axis=1)
    df = min_max_scaler(df, columns = ['livability'])
    df = df[['lat_center','lng_center', 'grid_in_location'] + categories_interest + ['livability']]
    df = df[df['grid_in_location']]

    save_file(df, file_name=f'Livability_{location_name}_grid_{stepsize}m.csv', local_file_path=f'livablestreets/data/{location_name}/WorkingTables', gcp_file_path = f'data/{location_name}/WorkingTables', save_local=save_local, save_gcp=save_gcp)

    return df

def convert_feature_impact(df, column, stepsize = 200):

    ################### Activities ######################
    if column == 'activities_economic':
        x = [0, 1, 2, 3, 4, 5, 6]
        y = [0, 3, 4, 1, 0, -1, -1]
        degree = 4
    if column == 'activities_education':
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 4, 1, 0, -1, -1]
        degree = 4
    if column == 'activities_educational':
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 4, 1, 0, -1, -1]
        degree = 4
    if column == 'activities_goverment':
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 4, 2, 0, -1, -1]
        degree = 4
    if column == 'activities_health_local':
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 2, 4, 2, 0, -1]
        degree = 3
    if column == 'activities_health_regional':
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 4, 0, 0, -1, -1]
        degree = 4
    if column == 'activities_post':
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 4, 2, 0, -1, -1]
        degree = 4
    if column == 'activities_public_service':
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 4, 0, 0, -1, -1]
        degree = 4

    ################### Comfort ######################
    if column == 'comfort_comfort_spots':
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 4, 2, 1, 0, -1]
        degree = 3
    if column == 'comfort_green_forests':
        x = [val*3 for val in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
        y = [0, 2, 3, 4, 3, 2, 1, 1, 0, 0, -1]
        degree = 4
    if column == 'comfort_green_natural':
        x = [val*3 for val in [0, 1, 2, 3, 4, 5, 6, 7]]
        y = [-0.5, 4, 3, 2, 1, 0, -1, -1]
        degree = 4
    if column == 'comfort_green_parks':
        x = [val*3 for val in [0, 1, 2, 3, 4, 5, 6, 7]]
        y = [-0.5, 4, 3, 2, 1, 0, -1, -1]
        degree = 4
    if column == 'comfort_green_space':
        x = [val*3 for val in [0, 1, 2, 3, 4, 5, 6, 7, 8]]
        y = [0, 2, 4, 3, 2, 1, 0, -1, -1]
        degree = 3
    if column == 'comfort_lakes':
        x = [val*3 for val in [0, 1, 2, 3, 4, 5, 6, 7, 8]]
        y = [0, 4, 4, 3, 2, 1, 0, -1, -1]
        degree = 4
    if column == 'comfort_leisure_mass':
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 4, 1, 0, -1, -1]
        degree = 4
    if column == 'comfort_leisure_spots':
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 4, 1, 0, -1, -1]
        degree = 4
    if column == 'comfort_rivers':
        x = [0, 1, 2, 3, 4, 5, 6, 7]
        y = [0, 4, 3, 2, 1, 0, -1, -1]
        degree = 4

    ################### Mobility ######################
    if column == 'mobility_bike_infraestructure':
        x = [0, 1, 2, 3, 4, 5]
        y = [-0.5, 4, 2, 1, 0, -1]
        degree = 4
    if column == 'mobility_public_transport_bus':
        x = [0, 1, 2, 3, 4, 5]
        y = [-1, 2, 4, 1, 0, -1]
        degree = 4
    if column == 'mobility_public_transport_rail':
        x = [0, 1, 2, 3, 4, 5]
        y = [-0.5, 4, 2, 1, 0, -1]
        degree = 4

    ################### Negative ######################
    if column == 'negative_industrial':
        x = [0, 1, 2, 3, 4]
        y = [0, -2, -2, -4, -4]
        degree = 2
    if column == 'negative_railway':
        x = [0, 1, 2, 3, 4]
        y = [0, -2, -2, -4, -4]
        degree = 2
    if column == 'negative_retail':
        x = [0, 1, 2, 3, 4]
        y = [0, 0.5, -1, -2, -2]
        degree = 3
    if column == 'negative_street_motorway':
        x = [0, 1, 2, 3, 4]
        y = [0, -2, -2, -4, -4]
        degree = 2
    if column == 'negative_street_primary':
        x = [0, 1, 2, 3, 4]
        y = [0, -2, -2, -4, -4]
        degree = 2
    if column == 'negative_street_secondary':
        x = [0, 1, 2, 3, 4]
        y = [0, -2, -2, -4, -4]
        degree = 2
    if column == 'negative_supermarket':
        x = [0, 1, 2, 3, 4]
        y = [0, 0.5, -1, -2, -2]
        degree = 3
    if column == 'negative_warehouse':
        x = [0, 1, 2, 3, 4]
        y = [0, -2, -2, -4, -4]
        degree = 2

    ################### Social life ######################
    if column == 'social_life_community':
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 4, 1, 0, -1, -2]
        degree = 4
    if column == 'social_life_culture':
        x = [0, 1, 2, 3, 4, 5]
        y = [-0.5, 4, 1, 0, -1, -2]
        degree = 4
    if column == 'social_life_eating':
        x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [-1, 0, 1, 2, 4, 2, 1, 0, -1, -2, -4]
        degree = 3
    if column == 'social_life_night_life':
        x = [0, 1, 2, 3, 4, 5, 6, 7]
        y = [0, 1, 4, 1, 0, -1, -2, -2]
        degree = 4

    # Create the polynomial curve based on the x, y and degree
    model = np.polyfit(x, y, degree)
    predict = np.poly1d(model)

    # Obtain values to be converted normalized to a grid of 100 meters. This makes the normalization intuitive: number of features is a 100mx100m square, which is roughly a city block.
    values = [val/int(stepsize/100) for val in list(df[column])] # Divide by stepsize/100 to unify measurement over a 100 meters area

    # Convert values with the following rule:
    # - if the value is smaller than the scale, take as if it was zero (to avoid bugs with possible negative values)
    # - if the value is larger than the scale, take as if it was the max value in the scale (to avoid extrapolating the model beyond the scale)
    # Convert values in between the scale using the polynomial curve
    converted_values = [value*y[0] if value <= x[0] else value*y[-1] if value >= x[-1] else value*predict(value) for value in values]

    return converted_values

# def livability_score_ind_weights(df, weights = [1,1,1,1,1],
def livability_score(df, weights = [1,1,1,1,1],
                     categories_interest = ['activities_mean', 'comfort_mean', 'mobility_mean', 'social_mean', 'negative_mean'],
                     indiv_factors_mapping = {'activities_economic':1,
                                        'activities_education':1,
                                        'activities_educational':1,
                                        'activities_goverment':0.25,
                                        'activities_health_local':2, 'activities_health_regional':1,
                                        'activities_post':0.5,
                                        'activities_public_service':0.5,
                                        'comfort_comfort_spots':0.25,
                                        'comfort_green_forests':0.5,
                                        'comfort_green_natural':0.5,
                                        'comfort_green_parks':4,
                                        'comfort_green_space':2,
                                        'comfort_lakes':1,
                                        'comfort_leisure_mass':0.5,
                                        'comfort_leisure_spots':0.25,
                                        'comfort_rivers':1,
                                        'mobility_bike_infraestructure':2,
                                        'mobility_public_transport_bus':4,
                                        'mobility_public_transport_rail':1, 'negative_industrial':2,
                                        'negative_railway':4,
                                        'negative_retail':0.5,
                                        'negative_street_motorway':2, 'negative_street_primary':1, 'negative_street_secondary':1,
                                        'negative_supermarket':0.5,
                                        'negative_warehouse':1,
                                        'social_life_community':1,
                                        'social_life_culture':1,
                                        'social_life_eating':4,
                                        'social_life_night_life':0.5},
                     stepsize = 200, location_name = 'berlin',
                     save_local=True):
    """ Calculates the livability score in each grid by taking the weighted sum of all feature values after normalization by a specific factor. The logic here is that not all features matter the same for livability, therefore they are corrected by an individual factor. At the same time, the user can input weights for each category to define which ones matter the most for them (weighted sum of categories = livability).
        """

    ## Convert values into non-linear scale (more of a feature doesn't mean better)
    df_converted = df.copy()
    columns_of_interest = list(indiv_factors_mapping.keys())
    for col in columns_of_interest:
        df_converted[col] = convert_feature_impact(df_converted, col, stepsize = stepsize)



    ## Correct features by individual factors
    df_factored = df_converted.copy()
    # Use a common denominator approach to multiply by the feature weights without changing the scale
    # In practice, I multiply all columns by the multiplication of all factors (common factor), then I divided each column by the common factor divided by the individual factor
    # This is all done in a for loop to garantee that the mapping is correct, as dictionaries are not ordered
    common_factor = np.prod(list(indiv_factors_mapping.values()))
    for col in columns_of_interest:
        mod_factor = common_factor*(common_factor/indiv_factors_mapping.get(col))
        df_factored[col] = df_factored[col].mul(mod_factor)



    ## Calculate livability as the weighted sum
    # Calculate the mean per category. This is important cause some categories have more features than others, so sum wouldn't work
    df_foo= feature_cat_mean_score(df_factored)

    # Create weighted values for the mean of each category by multiplying to inputed weights
    new_cols = [col + '_weighted' for col in categories_interest]
    df_foo[new_cols] = df_foo[categories_interest].mul(weights)

    # Calculate livability as the sum of all 4 categories
    df['livability'] = df_foo[new_cols].sum(axis=1)

    # MinMax scale it for displaying across cities. Might not be necessary once the values had been converted to a unified scale
    df = min_max_scaler(df, columns = ['livability'])

    # Trim unnecessary columns for saving smaller file
    df = df[df['grid_in_location']]
    df = df[['lat_center','lng_center'] + categories_interest + ['livability']]


    save_file(df, file_name=f'Livability_{location_name}_grid_{stepsize}m.csv', local_file_path=f'livablestreets/data/{location_name}/WorkingTables', save_local=save_local)

    return df


if __name__ == '__main__':
    df_grid = get_file(file_name='FeatCount_berlin_grid_200m.csv', local_file_path=f'/livablestreets/data/berlin/WorkingTables')
    df = livability_score(df = df_grid, stepsize = 200, location_name = 'berlin')
