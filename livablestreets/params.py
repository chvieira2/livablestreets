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
dict_city_number_wggesucht = {
            'Berlin': '8',
            'München': '90',
            'Stuttgart': '124',
            'Köln': '73',
            'Hamburg': '55',
            'Düsseldorf': '30',
            'Bremen':'17',
            'Leipzig':'77',
            'Kiel':'71',
            'Heidelberg':'59',
            'Karlsruhe':'68',
            'Hannover':'57',
            'Dresden':'27',
            'Aachen':'1',
            'Bonn':'13',
            'Darmstadt': '23',
            'Frankfurt am Main':'41',
            'Göttingen':'49',
            'Münster':'91',
            'Mainz':'84',
            'Mannheim':'85',
            'Nürnberg':'96',
            'Regensburg':'111',
            'Tübingen':'127',
            'Würzburg':'141'
        }


preloaded_cities = sorted(set([
            'Berlin',
            'Buenos Aires',
            # 'Santiago', # Santiago de Chile?
            'Dresden',
            'Montpellier',
            'München',

            'Paris',
            'Budapest',
            'Lisboa',
            'São Paulo',

            'Rio de Janeiro',
            'Porto Alegre',
            'London',
            'Kiel',
            'Milano',

            'Dublin',

            'San Jose',
            'Palo Alto',
            'Roma',
            'Vancouver'
                    ] + list(dict_city_number_wggesucht.keys())))
