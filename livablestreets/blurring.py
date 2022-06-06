from sklearn.preprocessing import MinMaxScaler
from skimage.filters import gaussian
import numpy as np
from livablestreets.utils import simple_time_tracker, get_file, save_file, min_max_scaler
import pandas as pd

def grid_tomatrix(df):
    #set the limits of the df for getting the shape
    lat_start_limits = df['lat_start'].unique()
    lng_start_limits = df['lng_end'].unique()

    #discard lat long columns, only sparse matrix remains
    df_num = df.iloc[:,10:]
    matrix_1Dgrid = df_num.to_numpy()
    n_columns = len(df_num.columns)

    matrix_2Dgrid = matrix_1Dgrid.reshape(len(lat_start_limits),len(lng_start_limits),n_columns)

    return matrix_2Dgrid


def blur_matrix(array,sigmapx):

    truncate = sigmapx*3
    blurred_img = gaussian(
        array, sigma=(sigmapx, sigmapx), truncate= truncate, mode='wrap')

    print(blurred_img.shape)

    return blurred_img.reshape(array.shape[0],array.shape[1],1)


def minmax_array(array):

    x, y, z = array.shape

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled =scaler.fit_transform(array.reshape(x*y,z)).reshape(x,y,z)

    return scaled


def loop_channels(array, slice = None, sigma_list = [0,0,0,0,8,0,0,9,0,0,0,0,0,0]):
    if slice is None:
        slice = range(0,array.shape[2])

    assert len(sigma_list) == array.shape[2], f'sigma list ({len(sigma_list)}) and array ({array.shape[2]}) has different length'

    blurred_img = np.zeros((array.shape[0],array.shape[1],array.shape[2]))

    for i in slice:
        blur_channel = minmax_array(blur_matrix(array[:,:,i],sigma_list[i]))
        # print(blur_channel.shape)
        blurred_img[:,:,i+1] = blur_channel
    return blurred_img



if __name__ == '__main__':
    df = get_file(file_name='FeatCount_Berlin_grid_1000m.csv', local_file_path=f'data/Berlin/WorkingTables', gcp_file_path = f'data/Berlin/WorkingTables')
    array = grid_tomatrix(df)
    print(array[::1].shape)
    # print(loop_channels(array,sigma_list = [0,0,0,0,0,0,8,0,0,9,0,0,0,0]).shape)
