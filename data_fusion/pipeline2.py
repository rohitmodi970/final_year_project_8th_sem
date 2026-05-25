import os
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

logging.info("Starting data fusion pipeline — saving each source separately before merge")

place = "Delhi, India"
city_name = "Delhi"
output_dir = "delhi"
query_radius_m = 5000
os.makedirs(output_dir, exist_ok=True)

lat, lon = ox.geocode(place)
ox.settings.use_cache = True


def out_file(filename):
    return os.path.join(output_dir, filename)

# ==============================================================
# SOURCE 1: Road Network
# File: roads_raw__length_m__lanes_count.geojson
# Units: geometry (EPSG:3857), length in meters, lanes as count
# ==============================================================
logging.info("[SOURCE 1] Downloading road network")

G = ox.graph_from_point((lat, lon), dist=query_radius_m, network_type="drive")
nodes, edges = ox.graph_to_gdfs(G)
edges = edges.to_crs(epsg=3857)

# Keep only useful raw columns for preview
road_raw_cols = ["geometry", "length", "name", "highway", "lanes", "maxspeed", "oneway"]
road_raw_cols = [c for c in road_raw_cols if c in edges.columns]
roads_raw = edges[road_raw_cols].copy()

# Annotate units clearly in a separate metadata dict (also saved as CSV header comment)
roads_raw["length_unit"] = "meters"
roads_raw["crs"] = "EPSG:3857"

roads_raw.to_file(out_file("roads_raw__length_m__lanes_count.geojson"), driver="GeoJSON")
roads_raw.drop(columns="geometry").to_csv(out_file("roads_raw__length_m__lanes_count.csv"), index=False)

logging.info(f"  Saved: roads_raw__length_m__lanes_count.geojson  ({len(roads_raw)} roads)")
logging.info(f"  Columns: {list(roads_raw.columns)}")


# ==============================================================
# SOURCE 2: Building Footprints
# File: buildings_raw__footprint_m2.geojson
# Units: geometry in meters (EPSG:3857), area computed in m²
# ==============================================================
logging.info("[SOURCE 2] Downloading building footprints")

buildings = ox.features_from_point((lat, lon), tags={"building": True}, dist=query_radius_m)
buildings = buildings.to_crs(epsg=3857)

# Compute area in m²
buildings["area_m2"] = buildings.geometry.area

# Keep useful raw columns
bld_raw_cols = ["geometry", "area_m2", "building", "name", "addr:street", "levels"]
bld_raw_cols = [c for c in bld_raw_cols if c in buildings.columns]
buildings_raw = buildings[bld_raw_cols].copy()
buildings_raw["area_unit"] = "square_meters"

buildings_raw.to_file(out_file("buildings_raw__footprint_m2.geojson"), driver="GeoJSON")
buildings_raw.drop(columns="geometry").to_csv(out_file("buildings_raw__footprint_m2.csv"), index=False)

logging.info(f"  Saved: buildings_raw__footprint_m2.geojson  ({len(buildings_raw)} buildings)")
logging.info(f"  Columns: {list(buildings_raw.columns)}")


# ==============================================================
# SOURCE 3: Vegetation / Green Spaces
# File: vegetation_raw__area_m2__type_category.geojson
# Units: geometry in meters (EPSG:3857), area in m²
# ==============================================================
logging.info("[SOURCE 3] Downloading vegetation dataset")

veg_tags = {
    "landuse": ["forest", "grass", "meadow"],
    "natural": ["wood", "tree", "grassland"],
    "leisure": ["park", "garden"]
}
vegetation = ox.features_from_point((lat, lon), tags=veg_tags, dist=query_radius_m)
vegetation = vegetation.to_crs(epsg=3857)

vegetation["area_m2"] = vegetation.geometry.area

# Determine veg type from available tag columns
def get_veg_type(row):
    for col in ["landuse", "natural", "leisure"]:
        if col in row.index and pd.notna(row.get(col)):
            return f"{col}:{row[col]}"
    return "unknown"

vegetation["veg_type"] = vegetation.apply(get_veg_type, axis=1)

veg_raw_cols = ["geometry", "area_m2", "veg_type", "name"]
veg_raw_cols = [c for c in veg_raw_cols if c in vegetation.columns]
vegetation_raw = vegetation[veg_raw_cols].copy()
vegetation_raw["area_unit"] = "square_meters"

vegetation_raw.to_file(out_file("vegetation_raw__area_m2__type_category.geojson"), driver="GeoJSON")
vegetation_raw.drop(columns="geometry").to_csv(out_file("vegetation_raw__area_m2__type_category.csv"), index=False)

logging.info(f"  Saved: vegetation_raw__area_m2__type_category.geojson  ({len(vegetation_raw)} polygons)")
logging.info(f"  Columns: {list(vegetation_raw.columns)}")


# ==============================================================
# SOURCE 4: Simulated Traffic Data
# File: traffic_simulated__vehicle_count__speed_kmph.csv
# Units: vehicle_count = vehicles/hr (simulated), avg_speed = km/h
# ==============================================================
logging.info("[SOURCE 4] Generating simulated traffic data")

traffic_raw = pd.DataFrame({
    "edge_osmid": [str(i) for i in edges.index],
    "vehicle_count_per_hr": np.random.randint(20, 200, len(edges)),
    "avg_speed_kmph":       np.random.randint(20, 60,  len(edges)),
})

# Metadata row at top (saved as comment in a separate readme-style header)
traffic_raw.to_csv(out_file("traffic_simulated__vehicle_count__speed_kmph.csv"), index=False)

# Also save a units legend
units_legend = pd.DataFrame([
    {"column": "vehicle_count_per_hr", "unit": "vehicles/hour", "source": "simulated (uniform random 20-200)"},
    {"column": "avg_speed_kmph",       "unit": "km/h",          "source": "simulated (uniform random 20-60)"},
])
units_legend.to_csv(out_file("traffic_simulated__UNITS_LEGEND.csv"), index=False)

logging.info(f"  Saved: traffic_simulated__vehicle_count__speed_kmph.csv  ({len(traffic_raw)} rows)")
logging.info(f"  Saved: traffic_simulated__UNITS_LEGEND.csv")


# ==============================================================
# SOURCE 5: Weather Data (OpenWeatherMap)
# File: weather_raw__wind_speed_mps__wind_dir_deg.csv
# Units: wind_speed = m/s, wind_direction = degrees (meteorological)
# ==============================================================
logging.info("[SOURCE 5] Fetching wind/weather data")

API_KEY = "c87754e82558c2df5352f5a899078d0d"
weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"

try:
    response = requests.get(weather_url, timeout=20)
    response.raise_for_status()
    response = response.json()
    wind_speed     = response["wind"]["speed"]       # m/s
    wind_direction = response["wind"]["deg"]         # degrees
    temperature_k  = response["main"]["temp"]        # Kelvin
    humidity_pct   = response["main"]["humidity"]    # %
    description    = response["weather"][0]["description"]
    source_note    = "live_OpenWeatherMap"
except Exception as e:
    logging.warning(f"  Weather API failed ({e}), using fallback values")
    wind_speed     = 3.0
    wind_direction = 180
    temperature_k  = 305.15
    humidity_pct   = 70
    description    = "fallback"
    source_note    = "fallback_defaults"

weather_raw = pd.DataFrame([{
    "location":          city_name,
    "wind_speed_mps":    wind_speed,
    "wind_dir_deg":      wind_direction,
    "temperature_K":     temperature_k,
    "temperature_C":     round(temperature_k - 273.15, 2),
    "humidity_pct":      humidity_pct,
    "description":       description,
    "source":            source_note,
}])

weather_raw.to_csv(out_file("weather_raw__wind_speed_mps__wind_dir_deg.csv"), index=False)

weather_units = pd.DataFrame([
    {"column": "wind_speed_mps",  "unit": "meters/second",  "notes": "from OpenWeatherMap wind.speed"},
    {"column": "wind_dir_deg",    "unit": "degrees (0=N)",  "notes": "meteorological convention"},
    {"column": "temperature_K",   "unit": "Kelvin",         "notes": "raw API value"},
    {"column": "temperature_C",   "unit": "Celsius",        "notes": "derived = K - 273.15"},
    {"column": "humidity_pct",    "unit": "percent (%)",    "notes": "relative humidity"},
])
weather_units.to_csv(out_file("weather_raw__UNITS_LEGEND.csv"), index=False)

logging.info(f"  Saved: weather_raw__wind_speed_mps__wind_dir_deg.csv")
logging.info(f"  wind_speed={wind_speed} m/s, wind_dir={wind_direction}°")


# ==============================================================
# SOURCE 6: Air Quality / AQI Data (OpenWeatherMap Air Pollution)
# File: aqi_raw__pm25_ugm3__aqi_index.csv
# Units: PM2.5 in µg/m³, AQI dimensionless (US EPA scale 0-500)
# ==============================================================
logging.info("[SOURCE 6] Fetching AQI / air pollution data")

aqi_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"

try:
    aqi_data = requests.get(aqi_url, timeout=20)
    aqi_data.raise_for_status()
    aqi_data = aqi_data.json()
    comp = aqi_data["list"][0]["components"]

    pm25  = comp["pm2_5"]   # µg/m³
    pm10  = comp["pm10"]    # µg/m³
    no2   = comp["no2"]     # µg/m³
    o3    = comp["o3"]      # µg/m³
    so2   = comp["so2"]     # µg/m³
    co    = comp["co"]      # µg/m³
    owi_aqi = aqi_data["list"][0]["main"]["aqi"]  # OpenWeather's own 1-5 index

    # US EPA PM2.5 → AQI conversion
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
    source_note = "live_OpenWeatherMap_AirPollution"

except Exception as e:
    logging.warning(f"  AQI API failed ({e}), using fallback values")
    pm25 = pm10 = no2 = o3 = so2 = co = float("nan")
    owi_aqi = -1
    AQI = 100
    source_note = "fallback_defaults"

aqi_raw = pd.DataFrame([{
    "location":          city_name,
    "lat":               lat,
    "lon":               lon,
    "pm2_5_ugm3":        pm25,
    "pm10_ugm3":         pm10,
    "no2_ugm3":          no2,
    "o3_ugm3":           o3,
    "so2_ugm3":          so2,
    "co_ugm3":           co,
    "openweather_aqi_1to5": owi_aqi,
    "us_epa_aqi":        AQI,
    "source":            source_note,
}])

aqi_raw.to_csv(out_file("aqi_raw__pm25_ugm3__aqi_index.csv"), index=False)

aqi_units = pd.DataFrame([
    {"column": "pm2_5_ugm3",          "unit": "µg/m³",         "notes": "PM2.5 particulate matter"},
    {"column": "pm10_ugm3",           "unit": "µg/m³",         "notes": "PM10 particulate matter"},
    {"column": "no2_ugm3",            "unit": "µg/m³",         "notes": "Nitrogen dioxide"},
    {"column": "o3_ugm3",             "unit": "µg/m³",         "notes": "Ozone"},
    {"column": "so2_ugm3",            "unit": "µg/m³",         "notes": "Sulfur dioxide"},
    {"column": "co_ugm3",             "unit": "µg/m³",         "notes": "Carbon monoxide"},
    {"column": "openweather_aqi_1to5","unit": "1-5 index",     "notes": "OpenWeather's own AQI scale (1=Good, 5=Very Poor)"},
    {"column": "us_epa_aqi",          "unit": "0-500 (EPA)",   "notes": "Derived from PM2.5 using US EPA breakpoints"},
])
aqi_units.to_csv(out_file("aqi_raw__UNITS_LEGEND.csv"), index=False)

logging.info(f"  Saved: aqi_raw__pm25_ugm3__aqi_index.csv")
logging.info(f"  PM2.5={pm25} µg/m³ → US EPA AQI={AQI}")

logging.info("Raw data download complete. Skipping derived and fused dataset generation.")
logging.info(f"Output directory: {output_dir}")
raise SystemExit(0)


# ==============================================================
# DERIVED: Building Density per Road Segment
# File: building_density_per_road__count_per_50m_buffer.csv
# Units: count of building footprints within 50 m buffer of road
# ==============================================================
logging.info("[DERIVED] Computing building density per road segment")

buildings_sindex = buildings.sindex
building_counts = []

for idx, road in edges.iterrows():
    buffer = road.geometry.buffer(50)
    possible = list(buildings_sindex.intersection(buffer.bounds))
    nearby   = buildings.iloc[possible][buildings.iloc[possible].intersects(buffer)]
    building_counts.append(len(nearby))

bld_density = pd.DataFrame({
    "edge_osmid":              [str(i) for i in edges.index],
    "building_count_50m":     building_counts,
    "buffer_radius_m":        50,
})
bld_density.to_csv(out_file("building_density_per_road__count_per_50m_buffer.csv"), index=False)
logging.info(f"  Saved: building_density_per_road__count_per_50m_buffer.csv")


# ==============================================================
# DERIVED: Vegetation Score per Road Segment
# File: vegetation_score_per_road__count_per_50m_buffer.csv
# Units: count of vegetation polygons within 50 m buffer of road
# ==============================================================
logging.info("[DERIVED] Computing vegetation score per road segment")

vegetation_sindex = vegetation.sindex
veg_counts = []

for idx, road in edges.iterrows():
    buffer = road.geometry.buffer(50)
    possible = list(vegetation_sindex.intersection(buffer.bounds))
    nearby   = vegetation.iloc[possible][vegetation.iloc[possible].intersects(buffer)]
    veg_counts.append(len(nearby))

veg_score = pd.DataFrame({
    "edge_osmid":          [str(i) for i in edges.index],
    "veg_count_50m":       veg_counts,
    "buffer_radius_m":     50,
})
veg_score.to_csv(out_file("vegetation_score_per_road__count_per_50m_buffer.csv"), index=False)
logging.info(f"  Saved: vegetation_score_per_road__count_per_50m_buffer.csv")


# ==============================================================
# FINAL MERGE: All sources joined on road edges
# File: fused_roads__carbon_cost_index.geojson / .csv
# ==============================================================
logging.info("[MERGE] Fusing all sources into final dataset")

edges["building_density"] = building_counts
edges["vegetation_score"] = veg_counts
edges["vehicle_count"]    = traffic_raw["vehicle_count_per_hr"].values
edges["avg_speed_kmph"]   = traffic_raw["avg_speed_kmph"].values
edges["wind_speed_mps"]   = wind_speed
edges["wind_direction_deg"] = wind_direction
edges["AQI_us_epa"]       = AQI
edges["pm2_5_ugm3"]       = pm25

# Carbon cost formula (same as original)
emission_factor = 0.12  # kg CO₂ per vehicle-meter (placeholder)
edges["carbon_cost"] = (
    edges["length"] * emission_factor * edges["vehicle_count"]
    + edges["building_density"] * 5
    - edges["vegetation_score"] * 3
    + edges["AQI_us_epa"] * 0.2
)

edges.to_file(out_file("fused_roads__carbon_cost_index.geojson"), driver="GeoJSON")
edges.drop(columns=["geometry"]).to_csv(out_file("fused_roads__carbon_cost_index.csv"), index=False)

# Save a full column-level units reference for the fused file
fused_units = pd.DataFrame([
    {"column": "length",             "unit": "meters",                "source": "OSMnx road network"},
    {"column": "building_density",   "unit": "count (50 m buffer)",   "source": "OSM buildings"},
    {"column": "vegetation_score",   "unit": "count (50 m buffer)",   "source": "OSM land-use/natural"},
    {"column": "vehicle_count",      "unit": "vehicles/hour",         "source": "simulated"},
    {"column": "avg_speed_kmph",     "unit": "km/h",                  "source": "simulated"},
    {"column": "wind_speed_mps",     "unit": "m/s",                   "source": "OpenWeatherMap"},
    {"column": "wind_direction_deg", "unit": "degrees (meteorological)","source": "OpenWeatherMap"},
    {"column": "AQI_us_epa",         "unit": "0-500 (dimensionless)", "source": "OpenWeatherMap Air Pollution → US EPA formula"},
    {"column": "pm2_5_ugm3",         "unit": "µg/m³",                 "source": "OpenWeatherMap Air Pollution"},
    {"column": "carbon_cost",        "unit": "dimensionless index",   "source": "derived formula"},
])
fused_units.to_csv(out_file("fused_roads__UNITS_LEGEND.csv"), index=False)

logging.info("Pipeline complete. Files saved:")
logging.info(f"Output directory: {output_dir}")
logging.info("  [RAW]     roads_raw__length_m__lanes_count.geojson / .csv")
logging.info("  [RAW]     buildings_raw__footprint_m2.geojson / .csv")
logging.info("  [RAW]     vegetation_raw__area_m2__type_category.geojson / .csv")
logging.info("  [RAW]     traffic_simulated__vehicle_count__speed_kmph.csv + UNITS_LEGEND")
logging.info("  [RAW]     weather_raw__wind_speed_mps__wind_dir_deg.csv + UNITS_LEGEND")
logging.info("  [RAW]     aqi_raw__pm25_ugm3__aqi_index.csv + UNITS_LEGEND")
logging.info("  [DERIVED] building_density_per_road__count_per_50m_buffer.csv")
logging.info("  [DERIVED] vegetation_score_per_road__count_per_50m_buffer.csv")
logging.info("  [FUSED]   fused_roads__carbon_cost_index.geojson / .csv + UNITS_LEGEND")