# from difflib import SequenceMatcher
from livablestreets.livability_map.create_grid import create_geofence, get_shape_of_location
from livablestreets.livability_map.add_features_to_grid import integrate_all_features_counts
from livablestreets.livability_map.livability_score import livability_score
from livablestreets.utils import simple_time_tracker, get_file, create_dir
from livablestreets.params import preloaded_cities
from livablestreets.string_utils import standardize_characters, capitalize_city_name
from config.config import ROOT_DIR


from livablestreets.OSM_features.query_names_detailed import master_query
from livablestreets.OSM_features.get_csv_detailed import get_csv

import pandas as pd


class LivabilityMap(object):
    def __init__(self, location, stepsize = 200, weights = [1,1,1,1,1]):
        """ This class puts together all processes to generate and plot the map with livability heatmap
            """
        self.df_grid = None
        self.df_grid_FeatCount = None
        self.df_grid_Livability = None
        self.location = capitalize_city_name(location)
        self.query_df = None
        self.stepsize = stepsize
        self.weights = weights
        self.sigmas = None

        ## Prepare location name used in query search. It has to be in local language and correctly capitalized. So it should be Rio de Janeiro, instead of Rio de janeiro, for example.
        self.location_name = standardize_characters(location)

        # # Manually correct cities with minor spelling mistakes, like missing accentuation
        # if SequenceMatcher(None, location, "Rio de Janeiro").ratio() >= 0.6:
        #     self.location = "Rio de Janeiro"
        # elif SequenceMatcher(None, location, "São Paulo").ratio() >= 0.6:
        #     self.location = "São Paulo"
        # elif SequenceMatcher(None, location, "Maricá").ratio() >= 0.6:
        #     self.location = "Maricá"
        # elif SequenceMatcher(None, location, "Nova Iguaçu").ratio() >= 0.6:
        #     self.location = "Nova Iguaçu"
        # # I don't know why, but Rīga won't work even with correct name spelling
        # elif SequenceMatcher(None, location, "Rīga").ratio() >= 0.6:
        #     self.location = "Rīga"



        # Create folder for location if it doesn't exist
        create_dir(path = f'{ROOT_DIR}/livablestreets/data/{self.location_name}')
        create_dir(path = f'{ROOT_DIR}/livablestreets/data/{self.location_name}/Features')
        create_dir(path = f'{ROOT_DIR}/livablestreets/data/{self.location_name}/WorkingTables')

    @simple_time_tracker
    def generate_grid(self):
        """ Function that puts together everything"""

        ## Creates the Geofance for the inputed location
        if self.df_grid is None:
            try :
                self.df_grid = get_file(f'{self.location_name}_grid_{self.stepsize}m.csv', local_file_path=f'livablestreets/data/{self.location_name}/WorkingTables', gcp_file_path = f'data/{self.location_name}/WorkingTables', save_local=True)
            except FileNotFoundError:
                self.df_grid = create_geofence(stepsize = self.stepsize, location = self.location, location_name=self.location_name, save_local=True, save_gcp=False)
        else:
            print('generate_grid has already been called before')

        ## Create the location center as class variable and the path to the corresponding GeoJson file
        # get location shape
        gdf_shape_location = get_shape_of_location(location = self.location, location_name = self.location_name)

        # Obtain shape's centroid
        centroid = gdf_shape_location.centroid
        centroid = list(centroid[0].coords)[0]
        self.location_centroid = centroid

        self.path_location_geojson = f'{ROOT_DIR}/livablestreets/data/{self.location_name}/{self.location_name}_boundaries.geojson'

        return self.df_grid

    @simple_time_tracker
    def get_features(self):
        # get_all(location=self.location)

        # get csv of cities of the world
        # df_cities = pd.read_csv('livablestreets/data/world-cities.csv')
        # city = self.location
        # # assigns country name to variable
        # country = df_cities.loc[df_cities['name'] == city.capitalize()].country.values.flatten()[0]


                ## Integrates features count to grid
        if self.query_df is None:
            # launchs queries of gejson and csv files from local PBF
            self.query_df = master_query(location_name=self.location_name)

        distances = list(self.query_df['distance'])
        self.sigmas = [(0.5*distance)/self.stepsize for distance in distances]
        get_csv(location=self.location, location_name = self.location_name, query_df = self.query_df)

    @simple_time_tracker
    def add_FeatCount_grid(self):
        """ Add features to grid """
        ## Makes sure that df_grid exists
        if self.df_grid is None:
            self.generate_grid()

        ## Get features for a given location
        if self.sigmas is None:
            self.get_features()

        ## Integrates features count to grid
        if self.df_grid_FeatCount is None:
            try :
                self.df_grid_FeatCount = get_file(f'FeatCount_{self.location_name}_grid_{self.stepsize}m.csv', local_file_path=f'livablestreets/data/{self.location_name}/WorkingTables', gcp_file_path = f'data/{self.location_name}/WorkingTables', save_local=True)
            except FileNotFoundError:
                self.df_grid_FeatCount = integrate_all_features_counts(df_grid = self.df_grid, stepsize=self.stepsize, location_name=self.location_name, sigmas = self.sigmas)
        else:
            print('add_FeatCount_grid has already been called before')

        ## Integrate other forms of features
        # For the future....

        return self.df_grid_FeatCount

    @simple_time_tracker
    def calc_livability(self):
        """ Calculate the livability score given the weights"""

        ## Calculate livability
        if self.df_grid_Livability is None:
            try :
                self.df_grid_Livability = get_file(f'Livability_{self.location_name}_grid_{self.stepsize}m.csv', local_file_path=f'livablestreets/data/{self.location_name}/WorkingTables', gcp_file_path = f'data/{self.location_name}/WorkingTables', save_local=True)

            except FileNotFoundError:
                self.df_grid_Livability = livability_score(self.add_FeatCount_grid(), weights = self.weights, stepsize = self.stepsize, location_name = self.location_name)
        else:
            print('livability_score has already been called before')

        return self.df_grid_Livability

    def update_livability(self, imputed_weights):
        """ Update the livability score given the weights"""

        # Get weights
        self.weights = imputed_weights

        ## Calculate livability
        self.df_grid_Livability = livability_score(self.add_FeatCount_grid(), weights = self.weights, stepsize = self.stepsize, location_name = self.location_name)

        print(f'Livability has been updated with weights {self.weights}')

        return self.df_grid_Livability





if __name__ == '__main__':
    city = LivabilityMap(location = 'Berlin')
    city.calc_livability()
    print(city.df_grid_Livability.info())

    # for city in preloaded_cities:#[::-1]:
    #     map_city = LivabilityMap(location = city, stepsize = 200)
    #     map_city.calc_livability()
    #     print(map_city.df_grid_Livability.info())
