from livablestreets.create_grid import create_geofence
from livablestreets.add_features_to_grid import integrate_all_features_counts3
from livablestreets.livability_score import livability_score
from livablestreets.utils import simple_time_tracker

class LivabilityMap(object):
    def __init__(self,stepsize = 3000):
        """ This class puts together all processes to generate and plot the map with livability heatmap
            """
        self.df_grid = None
        self.location = None
        self.stepsize = stepsize
        self.weights = None

    def location_input(self):
        """ Function that asks the user for their input.
        for now it automatically returns Berlin"""
        self.location = 'Berlin'

    def stepsize_input(self):
        """ Function that asks the user for their input.
        for now it automatically returns 3000"""
        self.stepsize = 3000

    def weights_input(self):
        """ Function that asks the user for their input.
        for now it automatically returns (1,1,1,1)"""
        self.weights = (1,1,1,1)

    @simple_time_tracker
    def generate_grid(self):
        """ Function that puts together everything"""

        ## Gets input from user
        if self.location is None:
            self.location_input()

        if self.stepsize is None:
            self.stepsize_input()


        ## Creates the Geofance of the inputed location
        self.df_grid = create_geofence(stepsize=self.stepsize, location=self.location)

        ## Get features for that location
        # Needs fixing as it isn't working stand alone as it is

        ## Integrates features to grid by count
        self.df_grid = integrate_all_features_counts3(stepsize=self.stepsize, location=self.location, file_name=f'{self.location}_grid_{self.stepsize}m.csv')

        ## Integrate other forms of features
        # For the future....

        return self.df_grid

    @simple_time_tracker
    def calc_livability(self):
        """ Calculate the livability score given the weights"""

        # Get weights
        if self.weights is None:
            self.weights_input()

        ## Calculate livability
        if self.df_grid is None:
            self.generate_grid()

        self.df_grid = livability_score(self.df_grid, weights = self.weights,
                        columns_interest = ['activities_mean', 'comfort_mean', 'mobility_mean', 'social_mean'],
                        stepsize = self.stepsize, location = self.location,
                        save_local=True, save_gcp=True)

        return self.df_grid

    def visualize(self):
        """ This method should plot the interactive map of location with the features and the livability shown in heatmap"""
        pass




if __name__ == '__main__':
    Berlin = LivabilityMap(stepsize = 10000).calc_livability()
    Berlin = LivabilityMap(stepsize = 3000).calc_livability()
    Berlin = LivabilityMap(stepsize = 1000).calc_livability()
    Berlin = LivabilityMap(stepsize = 100).calc_livability()
    print(Berlin.describe())
