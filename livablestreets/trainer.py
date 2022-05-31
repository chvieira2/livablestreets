import joblib
from matplotlib.pyplot import step
from termcolor import colored
import mlflow
from livablestreets.create_grid import create_geofence
from livablestreets.encoders import TimeFeaturesEncoder, DistanceTransformer
from livablestreets.gcp import storage_upload
from livablestreets.utils import compute_rmse
from livablestreets.params import MLFLOW_URI, EXPERIMENT_NAME, BUCKET_NAME, MODEL_VERSION, MODEL_VERSION
from memoized_property import memoized_property
from mlflow.tracking import MlflowClient
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler



class Trainer(object):
    def __init__(self, X, y):
        """
            X: pandas DataFrame
            y: pandas Series
        """
        self.pipeline = None
        self.X = X
        self.y = y
        # for MLFlow
        self.experiment_name = EXPERIMENT_NAME

    def set_experiment_name(self, experiment_name):
        '''defines the experiment name for MLFlow'''
        self.experiment_name = experiment_name

    def set_pipeline(self, method='linear'):
        """defines the pipeline as a class attribute"""
        dist_pipe = Pipeline([
            ('dist_trans', DistanceTransformer()),
            ('stdscaler', StandardScaler())
        ])
        time_pipe = Pipeline([
            ('time_enc', TimeFeaturesEncoder('pickup_datetime')),
            ('ohe', OneHotEncoder(handle_unknown='ignore'))
        ])
        preproc_pipe = ColumnTransformer([
            ('distance', dist_pipe, [
                "pickup_latitude",
                "pickup_longitude",
                'dropoff_latitude',
                'dropoff_longitude'
            ]),
            ('time', time_pipe, ['pickup_datetime'])
        ], remainder="drop")

        ## Code defining which regression method to use
        if method in ['linear', 'Linear', 'l']:
            from sklearn.linear_model import LinearRegression
            self.pipeline = Pipeline([
                ('preproc', preproc_pipe),
                (f'{method}_model', LinearRegression())
            ])
        elif method in ['DeepLearn', 'deeplearn', 'dp']: # TO DO add DP model
            from sklearn.linear_model import LinearRegression
            self.pipeline = Pipeline([
                ('preproc', preproc_pipe),
                (f'{method}_model', LinearRegression())
            ])

    def run(self, model_name='model', method='linear'):
        self.set_pipeline(method=method)
        self.mlflow_log_param(model_name, method)
        self.pipeline.fit(self.X, self.y)

    def evaluate(self, X_test, y_test):
        """evaluates the pipeline on df_test and return the RMSE"""
        y_pred = self.pipeline.predict(X_test)
        rmse = compute_rmse(y_pred, y_test)
        self.mlflow_log_metric("rmse", rmse)
        return round(rmse, 2)

    def save_model_locally(self, model_name='model'):
        """Save the model into a .joblib format"""
        joblib.dump(self.pipeline, f"{model_name}.joblib")
        print(f"{model_name}.joblib saved locally")

    # MLFlow methods
    @memoized_property
    def mlflow_client(self):
        mlflow.set_tracking_uri(MLFLOW_URI)
        return MlflowClient()

    @memoized_property
    def mlflow_experiment_id(self):
        try:
            return self.mlflow_client.create_experiment(self.experiment_name)
        except BaseException:
            return self.mlflow_client.get_experiment_by_name(
                self.experiment_name).experiment_id

    @memoized_property
    def mlflow_run(self):
        return self.mlflow_client.create_run(self.mlflow_experiment_id)

    def mlflow_log_param(self, key, value):
        self.mlflow_client.log_param(self.mlflow_run.info.run_id, key, value)

    def mlflow_log_metric(self, key, value):
        self.mlflow_client.log_metric(self.mlflow_run.info.run_id, key, value)


if __name__ == "__main__":
    # Get geafence and features
    grid_spacing = 20 # in meters (but also accepts degrees if wanted)
    coordenates = [52.343717, 52.650508, 13.114412, 13.739281] # Geofence over Berlin (coordenates chosen by eye). Should input users locations in the future.
    df = create_geofence(coordenates[0], coordenates[1], coordenates[2], coordenates[3], stepsize=grid_spacing)
    # df = function_that_adds_features(df)

    # Define X, y and test and training sets. Validation set needed?
    y = df["livability_score"]
    X = df.drop(columns=["livability_score", 'lat_start', 'lat_end', 'lon_start', 'lon_end'], axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

    # Train and save model, locally and log model online on mlflow
    trainer = Trainer(X=X_train, y=y_train)
    trainer.set_experiment_name('First try')
    trainer.run(model_name='Linear_first_try',  method='Linear')
    rmse = trainer.evaluate(X_test, y_test)
    print(f"rmse: {rmse}")
    trainer.save_model_locally(model_name='Linear_first_try')
    storage_upload()
