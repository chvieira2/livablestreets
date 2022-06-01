import pandas as pd

from livablestreets.utils import simple_time_tracker
from google.cloud import storage
from livablestreets.params import BUCKET_NAME


@simple_time_tracker
def get_grid_from_gcp(grid_size=1000, optimize=False, **kwargs):
    """method to get the training data (or a portion of it) from google cloud bucket"""
    # Add Client() here
    client = storage.Client()
    path = f"gs://{BUCKET_NAME}/data/Berlin_grid_{grid_size}m.csv"
    df = pd.read_csv(path)
    return df

def clean_data(df, test=False):
    unused_column = "Unnamed: 0"
    if unused_column in df.keys():
        df = df.drop(axis=1, columns=["Unnamed: 0"])
    df = df.dropna(how='any', axis='rows')
    df = df[(df.dropoff_latitude != 0) | (df.dropoff_longitude != 0)]
    df = df[(df.pickup_latitude != 0) | (df.pickup_longitude != 0)]
    if "fare_amount" in list(df):
        df = df[df.fare_amount.between(0, 4000)]
    df = df[df.passenger_count < 8]
    df = df[df.passenger_count >= 0]
    df = df[df["pickup_latitude"].between(left=40, right=42)]
    df = df[df["pickup_longitude"].between(left=-74.3, right=-72.9)]
    df = df[df["dropoff_latitude"].between(left=40, right=42)]
    df = df[df["dropoff_longitude"].between(left=-74, right=-72.9)]
    return df


if __name__ == '__main__':
    # print(f"gs://{BUCKET_NAME}/data/Berlin_grid_{1000}m.csv")
    df = get_grid_from_gcp()
    print(df)
