from sklearn.preprocessing import MinMaxScaler
from skimage.filters import gaussian
import numpy as np
from livablestreets.utils import simple_time_tracker, get_file, save_file, min_max_scaler
import pandas as pd

def blur_matrix(array,sigmapx):

    truncate = sigmapx*3
    blurred_img = gaussian(
        array, sigma=(sigmapx, sigmapx), truncate= truncate, mode='wrap')

    return blurred_img.reshape(array.shape[0],array.shape[1])

@simple_time_tracker
def FeatCount_blurrying(df, slice = None, sigma_list = [10,10,10,10,10,10,10,10,10,10]):
    """ Receives a dataframe and the features columns for blurrying and returns the modified data frame
    """
    # Define possible features
    feature_names = ['activities_education', 'activities_health_care',
       'activities_public_service', 'comfort_leisure_sports', 'comfort_sports',
       'mobility_public_transport', 'social_community', 'social_culture',
       'social_eating', 'social_night_life']

    # Check if slice exists, otherwise creates it
    if slice is None:
        slice = range(0,len(feature_names))

    # Filter features of interest according to slice
    feature_names = [feature_names[index] for index in slice]

    #set the limits of the df for getting the shape of the 2d matrix to be created
    lat_start_limits = df['lat_start'].unique()
    lng_start_limits = df['lng_end'].unique()

    # Loop over features bluryying one by one and adding back to the df
    for index in range(len(feature_names)):
        # Creates a 1D matrix from the list of values in that column
        matrix_to_blurry = np.array(df[feature_names[index]])
        # Changes the matrix to 2D using the dimensions given by lat and lng start limits
        matrix_to_blurry = matrix_to_blurry.reshape(len(lat_start_limits),len(lng_start_limits),1)
        # Apply blurrying function to 2D matrix
        matrix_to_blurry = blur_matrix(matrix_to_blurry,sigma_list[index])
        # MinMax scale blurred feature
        scaler = MinMaxScaler(feature_range=(0, 1))
        matrix_to_blurry =scaler.fit_transform(matrix_to_blurry)
        # Reshapes it back to 1D
        matrix_to_blurry = matrix_to_blurry.reshape(len(df))

        # Adds new values back to the original dataframe
        df[feature_names[index]] = list(matrix_to_blurry)

    return df


if __name__ == '__main__':
    df = get_file(file_name='FeatCount_berlin_grid_1000m.csv', local_file_path=f'data/berlin/WorkingTables', gcp_file_path = f'data/berlin/WorkingTables')

    df = FeatCount_blurrying(df, slice = None, sigma_list = [0,0,0,0,8,0,0,9,0,0])

    print(df.shape)
