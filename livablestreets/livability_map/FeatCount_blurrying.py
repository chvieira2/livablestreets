from sklearn.preprocessing import MinMaxScaler
from skimage.filters import gaussian
import numpy as np
from livablestreets.utils import simple_time_tracker, get_file
import pandas as pd

from livablestreets.OSM_features.query_names_detailed import master_query

def blur_matrix(array,sigmapx):

    truncate = sigmapx*3
    blurred_img = gaussian(
        array, sigma=(sigmapx, sigmapx), truncate= truncate, mode='wrap')

    return blurred_img.reshape(array.shape[0],array.shape[1])



@simple_time_tracker
def FeatCount_blurrying(df, slice = None, sigmas_list = None):
    """ Receives a dataframe and the features columns for blurrying and returns the modified data frame
    """
    df_master = master_query()
    feature_names = df_master['name'].tolist()

    # Check if slice exists, otherwise creates it
    if slice is None:
        slice = range(0,len(feature_names))

    # Filter features of interest according to slice
    feature_names = [feature_names[index] for index in slice]


    # set the limits of the df for getting the shape of the 2d matrix to be created
    lat_start_limits = df['lat_start'].unique()
    lng_start_limits = df['lng_end'].unique()

    # Loop over features bluryying one by one and adding back to the df
    for index in range(len(feature_names)):

        # Creates a 1D matrix from the list of values in that column
        matrix_to_blurry = np.array(df[feature_names[index]])
        # Changes the matrix to 2D using the dimensions given by lat and lng start limits
        matrix_to_blurry = matrix_to_blurry.reshape(len(lat_start_limits),len(lng_start_limits))
        # Apply blurrying function to 2D matrix
        matrix_to_blurry = blur_matrix(matrix_to_blurry,sigmas_list[index])
        # Reshapes it back to 1D and MinMax scale blurred feature
        scaler = MinMaxScaler(feature_range=(0, 1))
        matrix_to_blurry = scaler.fit_transform(matrix_to_blurry.reshape(len(df), 1))

        # Adds new values back to the original dataframe
        df[feature_names[index]] = [value[0] for value in list(matrix_to_blurry)]

    return df


if __name__ == '__main__':
    df = get_file(file_name='FeatCount_berlin_grid_1000m.csv', local_file_path=f'livablestreets/data/berlin/WorkingTables', gcp_file_path = f'data/berlin/WorkingTables')

    df = FeatCount_blurrying(df)

    print(df.info())
