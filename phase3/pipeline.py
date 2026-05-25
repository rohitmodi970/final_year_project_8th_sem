import logging
from pathlib import Path
from typing import Optional

import geopandas as gpd
import pandas as pd


def merge_sumo_with_fused(
    fused_path: Path,
    sumo_csv: Path,
    out_geojson: Path,
    out_csv: Optional[Path] = None,
):
    logging.info("Merging SUMO results into fused dataset")

    if not fused_path.exists():
        raise FileNotFoundError(f"Fused dataset not found: {fused_path}")

    fused = gpd.read_file(fused_path)
    logging.info("Loaded fused dataset: %d roads", len(fused))

    if not sumo_csv.exists():
        logging.warning("SUMO CSV not found: %s. Skipping merge.", sumo_csv)
        # Save copy of fused as the output to keep pipeline consistent
        fused.to_file(out_geojson, driver="GeoJSON")
        if out_csv:
            fused.drop(columns=["geometry"], errors="ignore").to_csv(out_csv, index=False)
        logging.info("Saved (unchanged) %s", out_geojson)
        return fused

    sumo = pd.read_csv(sumo_csv)
    logging.info("Loaded SUMO data: %d edges", len(sumo))

    # Attempt to extract osmid mapping from SUMO edge_id
    sumo = sumo.copy()
    if "edge_id" in sumo.columns:
        sumo["osmid_str"] = sumo["edge_id"].astype(str).str.extract(r'(-?\d+)')[0]

    fused["osmid_str"] = fused.get("osmid").astype(str)

    merged = fused.merge(
        sumo[[c for c in ["osmid_str", "avg_vehicle_count", "avg_speed_kmh", "total_co2_mg"] if c in sumo.columns]],
        on="osmid_str",
        how="left",
    )

    # Fill missing with existing columns where available
    merged["avg_vehicle_count"] = merged.get("avg_vehicle_count").fillna(merged.get("vehicle_count"))
    merged["avg_speed_kmh"] = merged.get("avg_speed_kmh").fillna(merged.get("avg_speed_kmph"))
    merged["total_co2_mg"] = merged.get("total_co2_mg").fillna(0)

    # Recompute carbon cost with SUMO vehicle counts where available
    merged["carbon_cost"] = (
        merged["length"] * 0.12 * merged["avg_vehicle_count"].fillna(merged["vehicle_count"]) 
        + merged["building_density"] * 5
        - merged["vegetation_score"] * 3
        + merged["AQI"] * 0.2
    )

    merged.to_file(out_geojson, driver="GeoJSON")
    if out_csv:
        merged.drop(columns=["geometry"], errors="ignore").to_csv(out_csv, index=False)

    logging.info("Saved merged dataset: %s", out_geojson)
    return merged
