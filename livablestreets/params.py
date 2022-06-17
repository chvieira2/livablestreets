### GCP configuration - - - - - - - - - - - - - - - - - - -

# /!\ you should fill these according to your account

### GCP Project - - - - - - - - - - - - - - - - - - - - - -

# not required here

### GCP Storage - - - - - - - - - - - - - - - - - - - - - -

BUCKET_NAME = 'wagon-data-871-vieira-livablestreets'

##### Data  - - - - - - - - - - - - - - - - - - - - - - - -

# train data file location
# /!\ here you need to decide if you are going to train using the provided and uploaded data/train_1k.csv sample file
# or if you want to use the full dataset (you need need to upload it first of course)
BUCKET_TRAIN_DATA_PATH = 'data/Berlin_grid_1000m.csv'

##### Training  - - - - - - - - - - - - - - - - - - - - - -

# not required here

##### Model - - - - - - - - - - - - - - - - - - - - - - - -

# model folder name (will contain the folders for all trained model versions)
MODEL_NAME = 'livablestreets'

# model version folder name (where the trained model.joblib file will be stored)
MODEL_VERSION = 'v1'

### GCP AI Platform - - - - - - - - - - - - - - - - - - - -

# not required here

### - - - - - - - - - - - - - - - - - - - - - - - - - - - -



#### Preloaded cities of choice ####
preloaded_cities = sorted([
            'Berlin',
            'Buenos Aires',
            'Santiago',
            'Dresden',
            'Montpellier',
            'München',

            'Paris',
            'Utrecht',
            'Budapest',
            'Strasbourg',
            'Lisboa',
            'São Paulo',

            'Rio de Janeiro',
            'Porto Alegre',
            'London',
            'Erfurt',
            'Kiel',
            'Milano',

            'Nova Iguaçu',
            'Fortaleza',
            'Recife',
            'Napoli',
            'Dublin',

            'San Jose',
            'Palo Alto',
            'Roma',
            'New York',
            'Vancouver',
            'Cordoba'
                    ])
