'''
uses matplotlib to plot gps data from csv file
'''
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

csv_path = 'output/gps_data_20260525_110843.csv'

df = pd.read_csv(csv_path)

lat0 = df['filtered_latitude'].iloc[0]
lon0 = df['filtered_longitude'].iloc[0]

# approx local metre conversion
m_per_deg_lat = 111_320
m_per_deg_lon = 111_320 * np.cos(np.radians(lat0))

df["raw_x"] = (df["raw_longitude"] - lon0) * m_per_deg_lon
df["raw_y"] = (df["raw_latitude"] - lat0) * m_per_deg_lat

df["filtered_x"] = (df["filtered_longitude"] - lon0) * m_per_deg_lon
df["filtered_y"] = (df["filtered_latitude"] - lat0) * m_per_deg_lat

plt.figure()
plt.plot(df["raw_x"], df["raw_y"], label="Raw GPS")
plt.plot(df["filtered_x"], df["filtered_y"], label="Kalman filtered")
plt.axis("equal")
plt.xlabel("x position, metres")
plt.ylabel("y position, metres")
plt.legend()
plt.grid(True)
plt.show()