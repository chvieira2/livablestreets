from sklearn.preprocessing import MinMaxScaler
from skimage.filters import gaussian
import numpy as np

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

    return blurred_img.reshape(array.shape[0],array.shape[1],1)



def minmax_array(array):

    x, y, z = array.shape

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled =scaler.fit_transform(array.reshape(x*y,z)).reshape(x,y,z)

    return scaled


sigma_list = [1,2,1,1,3,4,2,1,2,4,2,1]
sigma_list = [0,0,0,0,0,0,8,0,0,9,0,0]


def loop_channels(array,slice_start,slice_stop,sigma_list):
    assert len(sigma_list) == array.shape[2], 'sigma list and array has different length'

    blurred_img = np.zeros((array.shape[0],array.shape[1],1))

    for i in list( range( slice_start, slice_stop )):
        blur_channel = minmax_array(blur_matrix(array[:,:,i],sigma_list[i]))
        blurred_img += blur_channel
    return blurred_img
