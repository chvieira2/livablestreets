import pandas as pd
from livablestreets.utils import save_file

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


# Distance and sigma


mobility = {
            'public_transport_bus' : [public_transport_bus, 'bus', 200 , 'Node', 'Point', 'Point' , 'mobility' ] ,
            'public_transport_rail' : [public_transport_rail, 'rail', 500 , 'Node', 'Point', 'Point' , 'mobility' ] ,
            'bike_infraestructure' : [bike_infraestructure, 'bike' , 50 , 'Node', 'Point', 'Point' , 'mobility' ]
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


# Distance and sigma

comfort = {
            'comfort_spots' : [ comfort_spots, 'comfort_spots', 100 , 'Node' , 'Point', 'Point', 'comfort' ] ,
            'leisure_spots' : [ leisure_spots, 'leisure_spots', 200 , 'Node' , 'Point', 'Point', 'comfort' ] ,
            'leisure_mass' : [ leisure_mass, 'leisure_mass', 500 , 'Node' , 'Point', 'Point', 'comfort' ] }



'''--------------------------complex query--------------------------'''
# Ways

green = {'landuse':['grass','forest','orchard']}
green1 = {'landuse':['allotments','cementery','flowerbed', 'meadow','greenfield', 'recreation_ground','village_green']}
green2 = {'leisure':['park','playground','garden','swimming_area','playground', 'nature_reserve', 'marina']}
green3 = {'natural':['heath','shrubbery','wood','grassland']}

water = {'natural':['water','beach']}

# Ways
pedestrian = {'highway':['pedestrian']}
pedestrian1 = {'highway': ['footway']}
pedestrian2 = {'highway':['living_street','corridor']}
pedestrian3 = {'foot':['designated']}

cycle_paths = {'bicycle':['designated']}
cycle_paths1 = {'highway':['cycleway'],
              'cycleway':['lane','opposite','opposite_lane']}
cycle_paths2 = {'cycleway':['track','opposite_track','share_busway']}




complex = {
            # 'pedestrian' : [pedestrian,'pedestrian' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            # 'pedestrian1' : [pedestrian1,'pedestrian1' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            # 'pedestrian2' : [pedestrian2,'pedestrian2' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            # 'pedestrian3' : [pedestrian3,'pedestrian3' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            # 'cycle_paths' : [cycle_paths,'cyclpath' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            # 'cycle_paths1' : [cycle_paths1,'cyclpath1' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            # 'cycle_paths2' : [cycle_paths2,'cyclpath2' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            'green' : [ green,'green', 500 , 'Node' ,'Line','multiPolygon', 'comfort' ] ,
            'green1' : [ green1,'green1', 500 , 'Node' ,'Line','multiPolygon', 'comfort' ] ,
            'green2' : [ green2,'green2', 500 , 'Node' ,'Line','multiPolygon', 'comfort' ] ,
            'green3' : [ green3,'green3', 500 , 'Node' ,'Line','multiPolygon', 'comfort' ] ,
            'water' : [ water,'water', 500 , 'Node' ,'Line','multiPolygon', 'comfort' ]
            }

'''--------------------------negative query--------------------------'''


street_motorway = {'highway':['motorway']}
# street_motorway_wf = [(('',''),('','')),]
# street_motorway_bf = [('',''),]


street_primary = {'highway':['primary']}
# street_primary_wf = [(('',''),('','')),]
# street_primary_bf = [('',''),]


street_secondary = {'highway':['secondary']}
# street_secondary_wf = [(('',''),('','')),]
# street_secondary_bf = [('',''),]


# street_terteary = {'highway':['terteary']}
# street_terteary_wf = [(('',''),('','')),]
# street_terteary_bf = [('',''),]

railway = {'railway':['light_rail'],
            'bridge':['viaduct']}
# street_terteary_wf = [(('',''),('','')),]
# street_terteary_bf = [('',''),]



negative = {
            'street_motorway' : [street_motorway,'street_motorway' ,
             500 , 'Way', 'Line', 'lineString' , 'negative'], #, street_motorway_wf, street_motorway_bf ] ,
             'street_primary' : [street_primary,'street_primary' ,
             250 , 'Way', 'Line', 'lineString' , 'negative'],#, street_primary_wf, street_primary_bf ] ,
             'street_secondary' : [street_secondary,'street_secondary' ,
             100 , 'Way', 'Line', 'lineString' , 'negative'],#, street_secondary_wf, street_secondary_bf ] ,
            #  'street_terteary' : [street_terteary,'street_terteary' ,
            #  50 , 'Way', 'Line', 'lineString' , 'negative'], #, street_terteary_wf, street_terteary_bf ] ,
             'railway' : [railway,'railway' ,
             50 , 'Way', 'Line', 'lineString' , 'negative'], #, railway_wf, railway_bf ] ,
}




'''--------------------------  definitions  --------------------------'''

columns = ['query_string','name','distance','geomtype','jsontype','shapelytype','category']
columns_wb = ['query_string', 'name','distance','geomtype','jsontype','shapelytype','category','whitefilter','blackfilter']


def master_query(save_local=True, save_gcp=False):

        master_q = {}
        master_q.update(mobility)
        master_q.update(social_life)
        master_q.update(activities)
        master_q.update(comfort)

        query_df = pd.DataFrame.from_dict(master_q, orient='index', columns = columns)
        # query_df['whitefilter'] = [(('',''),('','')),]
        # query_df['blackfilter'] = [('',''),]

        # save_file(query_df, file_name=f'master_query_{location}.csv', local_file_path=f'livablestreets/data/{location}/WorkingTables', gcp_file_path = f'data/{location}/WorkingTables', save_local=save_local, save_gcp=save_gcp)

        return query_df

def master_query_complex(save_local=True, save_gcp=False):

        master_q = {}
        master_q.update(complex)

        query_df = pd.DataFrame.from_dict(master_q, orient='index', columns = columns)
        # query_df['whitefilter'] = [(('',''),('','')),]
        # query_df['blackfilter'] = [('',''),]

        # save_file(query_df, file_name=f'master_query_complex_{location}.csv', local_file_path=f'livablestreets/data/{location}/WorkingTables', gcp_file_path = f'data/{location}/WorkingTables', save_local=save_local, save_gcp=save_gcp)

        return query_df

def master_query_negative(save_local=True, save_gcp=False):

        master_neg = {}
        master_neg.update(negative)

        query_df = pd.DataFrame.from_dict(master_neg, orient='index', columns = columns)

        # save_file(query_df, file_name=f'master_query_negative_{location}.csv', local_file_path=f'livablestreets/data/{location}/WorkingTables', gcp_file_path = f'data/{location}/WorkingTables', save_local=save_local, save_gcp=save_gcp)

        return query_df


if __name__ == "__main__":
    print(master_query())
