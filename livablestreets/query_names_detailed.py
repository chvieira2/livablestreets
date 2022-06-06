import pandas as pd

# 4 categories with key, values list for openstreetmap feature extraction
# dictionaries determinating geometry type (node or ways)
# dictionaries for determinig influece distance, for computing sigma (blurring)
# final master dictionary with all the information 'master_query'


'''-------------------------mobility------------------------------'''

#Queries for mobility

# Nodes
public_transport_bus = {'amenity':['bus_station'],
                    'bus_bay':'',
                   'highway':['bus_stop']}

public_transport_rail = { 'public_transport':['stop_position','station','stop_area'],
                   'railway':['station','tram_stop', 'subway_entrance']}

bike_infraestructure =  {'amenity':['bicycle_parking', 'bicycle_repair_station', 'bicycle_rental']}

# Ways
cycle_paths = {'bicycle':['designated'],
              'highway':['cycleway'],
              'cycleway':['lane','opposite','opposite_lane','track','opposite_track','share_busway']}

pedestrian = {'highway':['pedestrian','footway','living_street','corridor'],
                'foot':['designated']}

# Distance and sigma


mobility = {
            'public_transport_bus' : [public_transport_bus, 'bus', 200 , 'Node', 'Point', 'Point' , 'mobility' ] ,
            'public_transport_rail' : [public_transport_rail, 'rail', 500 , 'Node', 'Point', 'Point' , 'mobility' ] ,
            'bike_infraestructure' : [bike_infraestructure, 'bike' , 50 , 'Node', 'Point', 'Point' , 'mobility' ] ,
            'pedestrian' : [pedestrian,'pedestrian' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            'cycle_paths' : [cycle_paths,'cyclpath' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ]
            }

'''-------------------------social life---------------------------'''

#Queries for social life

# Nodes
eating = {'amenity':['cafe','restaurant', 'food_court', 'ice_cream']}

night_life = { 'amenity':['bar','pub','biergarten', 'nightclub', 'swingerclub', 'casino']}

culture = {'amenity':['social_centre','theatre','public_bookcase',
                      'events_venue', 'community_centre', 'cinema',
                      'arts_centre', 'conference_centre']}

community = {'office': ['association','charity', 'coworking',
                        'educational_institution', 'employment_agency', 'foundation',
                        'ngo', 'political_party', 'research']}

# Distance and sigma

social_life = {
                'eating' : [eating, 'eating', 200 , 'Node', 'Point', 'Point' , 'social_life' ] ,
                'night_life' : [night_life,'nightlife' , 300 , 'Node', 'Point', 'Point' , 'social_life' ] ,
                'culture' : [culture,'culture' ,  500 , 'Node', 'Point', 'Point' , 'social_life' ] ,
                'community' : [community,'community', 400 , 'Node', 'Point', 'Point' , 'social_life' ]
                }

'''------------------------activities-------------------------------'''


#Queries for acitvities

#Nodes
health_regional = {'amenity':['hospital', 'clinic','nursing_home', 'social_facility']}

health_local = {'amenity':['baby_hatch','dentist', 'doctors', 'pharmacy', 'veterinary']}

goverment = { 'amenity': ['townhall', 'courthouse']}

public_service = {'amenity':[ 'fire_station','police' ]}

post = {'amenity':[ 'post_box', 'post_office' ]}

education = {'amenity':['college', 'music_school', 'school', 'university']}

educational = { 'amenity' : ['kindergarten','language_school', 'library',]}

economic = {'amenity':['atm', 'bank', 'bureau_de_change']}

# Distance and sigma

activities = {
            'health_regional' : [health_regional, 'health_regional', 1000 , 'Node','Point','Point', 'activities'] ,
            'health_local' : [health_local, 'health_local', 300 , 'Node','Point','Point', 'activities'] ,
            'goverment' : [goverment,'goverment', 500  , 'Node','Point','Point', 'activities'] ,
            'public_service' : [public_service, 'public_service', 400 , 'Node','Point','Point', 'activities'] ,
            'post' : [post, 'post', 100, 'Node','Point','Point', 'activities'] ,
            'education' : [education, 'education', 500, 'Node','Point','Point', 'activities'] ,
            'educational' : [educational, 'educational', 200, 'Node','Point','Point', 'activities'] ,
            'economic' : [economic, 'economic', 100 , 'Node','Point','Point', 'activities']
            }

'''-----------------------------comfort--------------------------'''


#Queries for comfort

# Nodes
comfort_spots = {'amenity':['bbq','bench','dog_toilet',
                      '	drinking_water', 'give_box', 'shelter', 'shower',
                      'toilets', 'water_point', 'watering_place', 'fountain']}

leisure_spots = {'leisure':['bird_hide','dog_park', 'firepit', 'pitch', 'picnic_table'],
                 'historic': [True]}

leisure_mass = {'leisure':['bandstand', 'swimming_pool', 'stadium', 'sports_centre', 'fitness_centre']}

# Ways

green = {'landuse':['grass','forest','orchard','allotments','cementery','flowerbed', 'meadow','greenfield', 'recreation_ground','village_green'],
         'leisure':['park','playground','garden','swimming_area','playground', 'nature_reserve', 'marina'],
         'natural':['heath','shrubbery','wood','grassland']}

water = {'natural':['water','beach'],
         'amenity':['fountain']}

# Distance and sigma

comfort = {
            'comfort_spots' : [ comfort_spots, 'comfort_spots', 100 , 'Node' , 'Point', 'Point', 'comfort' ] ,
            'leisure_spots' : [ leisure_spots, 'leisure_spots', 200 , 'Node' , 'Point', 'Point', 'comfort' ] ,
            'leisure_mass' : [ leisure_mass, 'leisure_mass', 500 , 'Node' , 'Point', 'Point', 'comfort' ] ,
            'green' : [ green,'green', 500 , 'Way' ,'Line','multiPolygon', 'comfort' ] ,
            'water' : [ water,'water', 500 , 'Way' ,'Line','multiPolygon', 'comfort' ]
            }


'''--------------------------master query--------------------------'''




def master_query():

        master_q = {}
        master_q.update(mobility)
        master_q.update(social_life)
        master_q.update(activities)
        master_q.update(comfort)

        columns = ['query_string','name','distance','geomtype','jsontype','shapelytype','category']
        query_df = pd.DataFrame.from_dict(master_q, orient='index', columns = columns)
        return query_df

if __name__ == "__main__":
    print(master_query())
