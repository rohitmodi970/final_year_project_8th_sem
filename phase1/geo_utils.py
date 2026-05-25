from pathlib import Path

import geopandas as gpd
import pandas as pd


def slugify(value: str) -> str:
    cleaned = []
    for char in value.strip().lower():
        if char.isalnum():
            cleaned.append(char)
        elif cleaned and cleaned[-1] != "_":
            cleaned.append("_")
    result = "".join(cleaned).strip("_")
    return result or "city"


def ensure_output_dir(path: str) -> Path:
    output_path = Path(path)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def to_metric(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    return gdf.to_crs(epsg=3857)


def count_nearby_features(
    roads: gpd.GeoDataFrame,
    features: gpd.GeoDataFrame,
    buffer_m: float,
) -> list[int]:
    if roads.empty or features.empty:
        return [0] * len(roads)

    road_buffers = roads[["geometry"]].copy()
    road_buffers = road_buffers.reset_index(drop=True)
    road_buffers["road_index"] = road_buffers.index
    road_buffers["geometry"] = road_buffers.geometry.buffer(buffer_m)

    buffered_roads = road_buffers[["road_index", "geometry"]]
    feature_geoms = features[["geometry"]].copy()

    joined = gpd.sjoin(feature_geoms, buffered_roads, how="inner", predicate="intersects")

    counts = (
        joined.groupby("road_index").size().reindex(buffered_roads["road_index"], fill_value=0)
    )

    return counts.astype(int).tolist()
