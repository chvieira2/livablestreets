# import folium
# from folium import GeoJson
# from folium.plugins import HeatMap
# import pandas as pd
# import numpy as np
# from livablestreets.utils import create_coords

# # zoom = [11-13] ood values
# mapObj = folium.Map(location=[52.5200, 13.4050], zoom_start=11)

# #Read in GeoJson file with Ortsteile-Berlin
# geo1=r"livablestreets/data/lor_ortsteile.geojson"
# file1 = open(geo1, encoding="utf8")
# text1 = file1.read()
# geo_livingArea = GeoJson(text1, name="Living Areas",show=False, zoom_on_click=True)
# geo2=r"livablestreets/data/OSMB-Berlin.geojson"
# file2 = open(geo2, encoding="utf8")
# text2 = file2.read()
# geo_Berlin = GeoJson(text2, name="Berlin",show=True, zoom_on_click=True)

# #Add a layer over the map
# geo_livingArea.add_to(mapObj)
# geo_Berlin.add_to(mapObj)

# # Create a Heatmap
# # convert to (n, 2) nd-array format for heatmap if not in right format
# PATH_TO_FILE='livablestreets/data/bars_BE.json'
# coords = create_coords(PATH_TO_FILE)

# #print(type(coords))
# coords = np.array(coords)
# #print(type(coords))

# # plot heatmap
# heatmap = HeatMap(coords, min_opacity=0.2, radius=15, name='bars in Berlin', show=True)
# mapObj.add_child(heatmap)

# # Add clickable overlayers
# folium.LayerControl().add_to(mapObj)

# # save the map object as a html file
# mapObj.save('index.html')
