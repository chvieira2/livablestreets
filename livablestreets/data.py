import pandas as pd

from livablestreets.utils import simple_time_tracker
from google.cloud import storage
from livablestreets.params import BUCKET_NAME


@simple_time_tracker
def get_file_from_gcp(file_name, save_local=True, optimize=False, **kwargs):
    """method to get the training data (or a portion of it) from google cloud bucket"""
    # Add Client() here
    client = storage.Client()
    path = f"gs://{BUCKET_NAME}/data/{file_name}"
    df = pd.read_csv(path)

    if save_local:
        df.to_csv(f'livablestreets/data/{file_name}', index=False)

    return df

@simple_time_tracker
def integrate_feature_counts(df_grid,feature_file):
    df_feature = get_file_from_gcp(file_name=feature_file)

    # Break grid in rows. First as if feature is in row
    lat_start_limits = df_grid['lat_start'].unique()
    lat_end_limits = df_grid['lat_end'].unique()
    for lats_index in range(len(lat_start_limits)):
        df_feature_row = df_feature[df_feature['lat']<=lat_start_limits[lats_index]]



    # return mod_grid # added feature column


if __name__ == '__main__':
    # print(f"gs://{BUCKET_NAME}/data/Berlin_grid_{1000}m.csv")
    df_grid = get_file_from_gcp(file_name='Berlin_grid_1000m.csv')

    # df_test = integrate_feature_counts(df_grid,'df_convenience.csv')
    print(integrate_feature_counts(df_grid,'df_convenience.csv'))
