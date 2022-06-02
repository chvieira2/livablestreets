import os

from google.cloud import storage
from TaxiFareModel.params import BUCKET_NAME, MODEL_NAME, MODEL_VERSION


def storage_upload(rm=False):
    client = storage.Client().bucket(BUCKET_NAME)

    local_model_name = 'model.joblib'
    storage_location = f"models/{MODEL_NAME}/{MODEL_VERSION}/{local_model_name}"
    blob = client.blob(storage_location)
    blob.upload_from_filename('model.joblib')
    print(f"=> model.joblib uploaded to bucket {BUCKET_NAME} inside {storage_location}")
    if rm:
        os.remove('model.joblib')
