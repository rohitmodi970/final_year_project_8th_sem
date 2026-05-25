import osmnx as ox
import geopandas as gpd
import pandas as pd
import numpy as np
import requests
import logging

# ----------------------------
# Logging setup
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Starting data fusion pipeline")

# ----------------------------
# 1. Download road network
# ----------------------------
place = "Kolkata, India"

logging.info("Downloading road network")

G = ox.graph_from_place(place, network_type="drive")

nodes, edges = ox.graph_to_gdfs(G)

logging.info(f"Roads downloaded: {len(edges)}")

# convert CRS to meters
edges = edges.to_crs(epsg=3857)

# ----------------------------
# 2. Download building footprints
# ----------------------------
logging.info("Downloading building dataset")

buildings = ox.features_from_place(place, tags={"building": True})

buildings = buildings.to_crs(epsg=3857)

logging.info(f"Buildings loaded: {len(buildings)}")

# ----------------------------
# 3. Compute building density
# ----------------------------
logging.info("Calculating building density")

# Create spatial index for fast queries
buildings_sindex = buildings.sindex

building_counts = []

for idx, road in edges.iterrows():
    buffer = road.geometry.buffer(50)
    
    # Use spatial index to get candidates
    possible_matches_index = list(buildings_sindex.intersection(buffer.bounds))
    possible_matches = buildings.iloc[possible_matches_index]
    
    # Check actual intersection
    nearby_buildings = possible_matches[possible_matches.intersects(buffer)]
    building_counts.append(len(nearby_buildings))

edges["building_density"] = building_counts

logging.info("Building density computed")

# ----------------------------
# 4. Download vegetation dataset
# ----------------------------
logging.info("Downloading vegetation dataset")

tags = {"landuse": ["forest", "grass", "meadow"], 
        "natural": ["wood", "tree", "grassland"],
        "leisure": ["park", "garden"]}
vegetation = ox.features_from_place(place, tags=tags)

vegetation = vegetation.to_crs(epsg=3857)

logging.info(f"Vegetation polygons: {len(vegetation)}")

# ----------------------------
# 5. Compute vegetation score
# ----------------------------
logging.info("Calculating vegetation score")

# Create spatial index for fast queries
vegetation_sindex = vegetation.sindex

veg_counts = []

for idx, road in edges.iterrows():
    buffer = road.geometry.buffer(50)
    
    # Use spatial index to get candidates
    possible_matches_index = list(vegetation_sindex.intersection(buffer.bounds))
    possible_matches = vegetation.iloc[possible_matches_index]
    
    # Check actual intersection
    veg = possible_matches[possible_matches.intersects(buffer)]
    veg_counts.append(len(veg))

edges["vegetation_score"] = veg_counts

logging.info("Vegetation score computed")

# ----------------------------
# 6. Simulate traffic data
# ----------------------------
logging.info("Generating simulated traffic data")

edges["vehicle_count"] = np.random.randint(20, 200, len(edges))

edges["avg_speed"] = np.random.randint(20, 60, len(edges))

# ----------------------------
# 7. Get Weather Data
# ----------------------------
logging.info("Fetching wind data")

API_KEY = "c87754e82558c2df5352f5a899078d0d"

weather_url = f"https://api.openweathermap.org/data/2.5/weather?q=Kolkata&appid={API_KEY}"

try:
    response = requests.get(weather_url).json()

    wind_speed = response["wind"]["speed"]
    wind_direction = response["wind"]["deg"]

except:
    logging.warning("Weather API failed, using default values")

    wind_speed = 3
    wind_direction = 180

edges["wind_speed"] = wind_speed
edges["wind_direction"] = wind_direction

# ----------------------------
# 8. Get AQI Data
# ----------------------------
logging.info("Fetching AQI data")

try:
    # Kolkata coordinates
    lat, lon = 22.5726, 88.3639
    aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"

    aqi_data = requests.get(aqi_url).json()
    
    # Get PM2.5 value (good proxy for AQI)
    pm25 = aqi_data["list"][0]["components"]["pm2_5"]
    
    # Convert PM2.5 to AQI (simplified US EPA formula)
    if pm25 <= 12.0:
        AQI = (50 / 12.0) * pm25
    elif pm25 <= 35.4:
        AQI = 50 + ((100 - 50) / (35.4 - 12.1)) * (pm25 - 12.1)
    elif pm25 <= 55.4:
        AQI = 100 + ((150 - 100) / (55.4 - 35.5)) * (pm25 - 35.5)
    elif pm25 <= 150.4:
        AQI = 150 + ((200 - 150) / (150.4 - 55.5)) * (pm25 - 55.5)
    else:
        AQI = 200 + ((300 - 200) / (250.4 - 150.5)) * min(pm25 - 150.5, 99.9)
    
    AQI = int(AQI)

except Exception as e:
    logging.warning(f"AQI API failed: {e}, using default value")

    AQI = 100

edges["AQI"] = AQI

# ----------------------------
# 9. Compute emission factor
# ----------------------------
logging.info("Computing carbon emission score")

emission_factor = 0.12

edges["carbon_cost"] = (
    edges["length"] * emission_factor * edges["vehicle_count"]
    + edges["building_density"] * 5
    - edges["vegetation_score"] * 3
    + edges["AQI"] * 0.2
)

# ----------------------------
# 10. Save fused dataset
# ----------------------------
logging.info("Saving fused dataset")

edges.to_file("fused_roads.geojson", driver="GeoJSON")

edges.to_csv("fused_roads.csv")

logging.info("Pipeline finished successfully")