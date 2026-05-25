import logging
import shutil
from pathlib import Path

import geopandas as gpd
import numpy as np
import osmnx as ox
import pandas as pd

from .api_utils import fetch_aqi, fetch_weather
from .geo_utils import count_nearby_features, to_metric


def get_city_coordinates(place: str) -> tuple[float, float]:
    return ox.geocode(place)


def build_fused_dataset(
    place: str,
    city_name: str,
    query_radius_m: int,
    api_key: str,
) -> gpd.GeoDataFrame:
    logging.info("Starting Phase 1 data fusion for %s", city_name)

    lat, lon = get_city_coordinates(place)

    logging.info("Downloading road network")
    road_graph = ox.graph_from_point((lat, lon), dist=query_radius_m, network_type="drive")
    _, roads = ox.graph_to_gdfs(road_graph)
    roads = to_metric(roads)

    logging.info("Downloading building footprints")
    buildings = ox.features_from_point((lat, lon), tags={"building": True}, dist=query_radius_m)
    buildings = to_metric(buildings)

    logging.info("Downloading vegetation data")
    vegetation_tags = {
        "landuse": ["forest", "grass", "meadow"],
        "natural": ["wood", "tree", "grassland"],
        "leisure": ["park", "garden"],
    }
    vegetation = ox.features_from_point((lat, lon), tags=vegetation_tags, dist=query_radius_m)
    vegetation = to_metric(vegetation)

    logging.info("Counting nearby buildings and vegetation")
    roads = roads.copy()
    roads["building_density"] = count_nearby_features(roads, buildings, 50)
    roads["vegetation_score"] = count_nearby_features(roads, vegetation, 50)

    logging.info("Generating simulated traffic values")
    roads["vehicle_count"] = np.random.randint(20, 200, len(roads))
    roads["avg_speed_kmph"] = np.random.randint(20, 60, len(roads))

    weather = fetch_weather(lat, lon, api_key, city_name)
    aqi = fetch_aqi(lat, lon, api_key, city_name)

    roads["wind_speed_mps"] = weather["wind_speed_mps"]
    roads["wind_dir_deg"] = weather["wind_dir_deg"]
    roads["temperature_k"] = weather["temperature_k"]
    roads["humidity_pct"] = weather["humidity_pct"]
    roads["weather_description"] = weather["description"]
    roads["weather_source"] = weather["source"]

    roads["pm2_5_ugm3"] = aqi["pm2_5_ugm3"]
    roads["pm10_ugm3"] = aqi["pm10_ugm3"]
    roads["no2_ugm3"] = aqi["no2_ugm3"]
    roads["o3_ugm3"] = aqi["o3_ugm3"]
    roads["so2_ugm3"] = aqi["so2_ugm3"]
    roads["co_ugm3"] = aqi["co_ugm3"]
    roads["openweather_aqi_1to5"] = aqi["openweather_aqi_1to5"]
    roads["AQI"] = aqi["us_epa_aqi"]
    roads["aqi_source"] = aqi["source"]

    logging.info("Computing carbon cost")
    emission_factor = 0.12
    roads["carbon_cost"] = (
        roads["length"] * emission_factor * roads["vehicle_count"]
        + roads["building_density"] * 5
        - roads["vegetation_score"] * 3
        + roads["AQI"] * 0.2
    )

    return roads


def save_outputs(roads: gpd.GeoDataFrame, output_dir: Path) -> None:
    fused_geojson = output_dir / "fused_roads.geojson"
    fused_csv = output_dir / "fused_roads.csv"
    units_csv = output_dir / "fused_roads__UNITS_LEGEND.csv"

    roads.to_file(fused_geojson, driver="GeoJSON")
    roads.drop(columns=["geometry"], errors="ignore").to_csv(fused_csv, index=False)

    legacy_geojson = Path("fused_roads.geojson")
    legacy_csv = Path("fused_roads.csv")
    legacy_units = Path("fused_roads__UNITS_LEGEND.csv")

    if output_dir.resolve() != Path(".").resolve():
        shutil.copyfile(fused_geojson, legacy_geojson)
        shutil.copyfile(fused_csv, legacy_csv)

    units = pd.DataFrame(
        [
            {"column": "length", "unit": "meters", "source": "OSMnx road network"},
            {"column": "building_density", "unit": "count (50 m buffer)", "source": "OSM buildings"},
            {"column": "vegetation_score", "unit": "count (50 m buffer)", "source": "OSM land-use/natural"},
            {"column": "vehicle_count", "unit": "vehicles", "source": "simulated"},
            {"column": "avg_speed_kmph", "unit": "km/h", "source": "simulated"},
            {"column": "wind_speed_mps", "unit": "m/s", "source": "OpenWeatherMap"},
            {"column": "wind_dir_deg", "unit": "degrees", "source": "OpenWeatherMap"},
            {"column": "AQI", "unit": "0-500 (dimensionless)", "source": "OpenWeatherMap Air Pollution"},
            {"column": "carbon_cost", "unit": "dimensionless index", "source": "derived formula"},
        ]
    )
    units.to_csv(units_csv, index=False)

    if output_dir.resolve() != Path(".").resolve():
        shutil.copyfile(units_csv, legacy_units)

    logging.info("Saved %s", fused_geojson.name)
    logging.info("Saved %s", fused_csv.name)
    logging.info("Saved %s", units_csv.name)
