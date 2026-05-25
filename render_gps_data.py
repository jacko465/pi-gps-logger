'''
This script is used for creating the plots
of the gps data output
'''

import pandas as pd
import folium
import os

input_path = 'output\\gps_data_20260525_110843.csv'
filename = os.path.basename(input_path)
output_path = f'output/plot_{filename.replace(".csv", ".html")}'

df = pd.read_csv(input_path)

# Create a map centered around the average location
# folium_map_provider = 'OpenStreetMap'
folium_map_provider = 'CartoDB positron'
# folium_map_provider = 'OpenTopoMap'
# folium_map_provider = 'Esri World Imagery'
# folium_map_provider = 'Esri World Street Map'
# folium_map_provider = None
centre = [df['filtered_latitude'].mean(), df['filtered_longitude'].mean()]
m = folium.Map(location=centre, zoom_start=15, tiles=folium_map_provider, max_zoom=30)

# Add the GPS points to the map
raw_points = list(zip(df['raw_latitude'], df['raw_longitude']))
filtered_points = list(zip(df['filtered_latitude'], df['filtered_longitude']))

# Raw GPS track in red
folium.PolyLine(
    raw_points,
    color='red',
    weight=2.5,
    opacity=0.8,
    tooltip='Raw GPS'
).add_to(m)

# Filtered GPS track in blue
folium.PolyLine(
    filtered_points,
    color='blue',
    weight=2.5,
    opacity=0.8,
    tooltip='Filtered GPS'
).add_to(m)

# layer toggle
folium.LayerControl().add_to(m)

m.save(output_path)
print(f"Saved GPS plot to {output_path}")