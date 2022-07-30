from cmath import inf
from livablestreets.utils import save_file, min_max_scaler, get_file
from livablestreets.params import conversion_formulas_OSM_features, indiv_factors_mapping
import pandas as pd
import numpy as np


def feature_cat_mean_score(df):
    """ Receives a dataframe and looks for columns containing the categories indicator (activities, comfort, mobility, social)
        Calculate the row-wise mean of columns in that categories and add it to a new column called categories_mean"""

    for categories in ('activities', 'comfort', 'mobility', 'social', 'negative'):
        columns_interest = [column for column in df.columns if f"{categories}_" in column]
        df[f"{categories}_mean"] = df[columns_interest].mean(axis=1)

    return df

def convert_feature_impact(df, column, stepsize = 200):

    conversion_factor = conversion_formulas_OSM_features[conversion_formulas_OSM_features['feature'] == column]

    # Create the polynomial curve based on the x, y and degree
    x = list(conversion_factor['x'])[0]
    y = list(conversion_factor['y'])[0]
    poly_degree = int(conversion_factor['poly_degree'])

    model = np.polyfit(x, y, poly_degree)
    predict = np.poly1d(model)

    # Obtain values to be converted normalized to a grid of 100 meters. This makes the normalization intuitive: number of features in a 100mx100m square, which is roughly a city block.
    values = [val/int(stepsize/100) for val in list(df[column])] # Divide by stepsize/100 to unify measurement over a 100x100 meters area

    # Convert values with the following rule:
    # - if the value is smaller than the scale, take as if it was zero (to avoid bugs with possible negative values)
    # - if the value is larger than the scale, take as if it was the max value in the scale (to avoid extrapolating the model beyond the scale)
    # Convert values in between the scale using the polynomial curve
    converted_values = [y[0] if value <= x[0] else y[-1] if value >= x[-1] else predict(value) for value in values]

    return converted_values

def update_livability(df_livability, weights = [1,1,1,1],
                      categories_interest = ['activities_mean', 'comfort_mean', 'mobility_mean', 'social_mean']):

    ## Calculate livability as the weighted sum

    # Create weighted values for the mean of each category by multiplying to inputed weights
    new_cols = [col + '_weighted' for col in categories_interest]
    df_livability[new_cols] = df_livability[categories_interest].mul(weights)

    # Calculate livability as the sum of all 4 categories
    df_livability['livability'] = df_livability[new_cols].sum(axis=1)

    ## Scale values to absolut scale between min and max livability score
    # Get mins and max per category according to weights
    mins, maxs = [], []
    for cat in ['activities_', 'comfort_', 'mobility_', 'social_']:
        # Filter df for features in the category
        foo = conversion_formulas_OSM_features[[str(feat_name).startswith(cat) for feat_name in list(conversion_formulas_OSM_features['feature'])]]
        mins.append(foo['min_val'].mean())
        maxs.append(foo['max_val'].mean())

    abs_min = 0#abs(sum(mins))
    abs_max = abs(sum(maxs))

    df_livability['livability'] = df_livability['livability']\
        .apply(lambda x: round((x+abs_min) / (abs_max+abs_min), 3))


    # Transform livability for visualization
    df_livability['absolute_livability'] = df_livability['livability']
    df_livability = min_max_scaler(df_livability, columns = ['livability'])#, min_val=-0.3) # Added min_val here to better display discrepancy of low and high livability areas




    # MinMax scale it for displaying across cities. Might not be necessary once the values had been converted to a unified scale
    # df_livability = min_max_scaler(df_livability, columns = ['livability'])

    # Trim unnecessary columns for saving smaller file
    df_livability = df_livability[df_livability['grid_in_location']]
    df_livability = df_livability[['lat_center','lng_center', 'grid_in_location'] + categories_interest + ['livability']]#, 'absolute_livability']]

    return df_livability

def livability_score(df, weights = [1,1,1,1],
                     stepsize = 200, location_name = 'berlin',
                     save_local=True):
    """ Calculates the livability score in each grid by taking the weighted sum of all feature values after normalization by a specific factor. The logic here is that not all features matter the same for livability, therefore they are corrected by an individual factor. At the same time, the user can input weights for each category to define which ones matter the most for them (weighted sum of categories = livability). Finally, livability score is normalized to the maximum and minimum possible scores. In the end, livability is an absolute measurement related to the maximum and minimum possible values.
        """

    ## Convert values into non-linear scale (more of a feature doesn't mean better)
    df_converted = df.copy()
    columns_of_interest = list(indiv_factors_mapping.keys())
    for col in columns_of_interest:
        df_converted[col] = convert_feature_impact(df_converted, col, stepsize = stepsize)


    ## Correct features by individual factors
    df_factored = df_converted.copy()

    for col in columns_of_interest:
        mod_factor = indiv_factors_mapping.get(col)
        df_factored[col] = df_factored[col].mul(mod_factor)


    ## Calculate livability as the weighted sum
    # Calculate the mean per category. This is important cause some categories have more features than others, so sum wouldn't work
    df_foo= feature_cat_mean_score(df_factored)

    df = update_livability(df_foo, weights=weights)

    save_file(df, file_name=f'Livability_{location_name}_grid_{stepsize}m.csv', local_file_path=f'livablestreets/data/{location_name}/WorkingTables', save_local=save_local)

    return df


if __name__ == '__main__':
    df_grid = get_file(file_name='FeatCount_berlin_grid_200m.csv', local_file_path=f'/livablestreets/data/berlin/WorkingTables')
    df = livability_score(df = df_grid, stepsize = 200, location_name = 'berlin')
