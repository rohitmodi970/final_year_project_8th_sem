import logging
from pathlib import Path
from typing import Any, Dict, Optional

import geopandas as gpd

from .emissions import EmissionPredictor, EmissionResult


def load_roads(path: Path) -> gpd.GeoDataFrame:
    roads = gpd.read_file(path)
    return roads


def enrich_with_emissions(
    roads: gpd.GeoDataFrame,
    emissions: EmissionResult,
    vehicle_count_column: str = "vehicle_count",
) -> gpd.GeoDataFrame:
    roads = roads.copy()

    if vehicle_count_column in roads.columns:
        vehicle_count = roads[vehicle_count_column].fillna(1)
    else:
        logging.warning("%s not found. Using 1 for vehicle_count.", vehicle_count_column)
        vehicle_count = 1

    length_km = roads["length"] / 1000
    roads["emission_g_per_km"] = emissions.co2_g_per_km
    roads["nox_g_per_km"] = emissions.nox_g_per_km
    roads["voc_g_per_km"] = emissions.voc_g_per_km
    roads["so2_g_per_km"] = emissions.so2_g_per_km

    roads["emission_cost_g"] = emissions.co2_g_per_km * length_km * vehicle_count
    roads["nox_cost_g"] = emissions.nox_g_per_km * length_km * vehicle_count
    roads["voc_cost_g"] = emissions.voc_g_per_km * length_km * vehicle_count
    roads["so2_cost_g"] = emissions.so2_g_per_km * length_km * vehicle_count

    if "carbon_cost" in roads.columns:
        roads["carbon_cost_with_emissions"] = roads["carbon_cost"] + roads["emission_cost_g"]

    roads["emission_model_used"] = emissions.model_used
    roads["emission_notes"] = emissions.notes

    return roads


def save_outputs(
    roads: gpd.GeoDataFrame,
    geojson_path: Path,
    csv_path: Optional[Path] = None,
) -> None:
    roads.to_file(geojson_path, driver="GeoJSON")

    if csv_path is not None:
        roads.drop(columns=["geometry"], errors="ignore").to_csv(csv_path, index=False)

    logging.info("Saved %s", geojson_path)
    if csv_path is not None:
        logging.info("Saved %s", csv_path)


def run_phase2_pipeline(
    input_path: Path,
    output_geojson: Path,
    output_csv: Optional[Path],
    vehicle_payload: Dict[str, Any],
    model_dir: Optional[Path] = None,
) -> None:
    logging.info("Starting Phase 2 emission integration")

    predictor = EmissionPredictor(model_dir=model_dir)
    emissions = predictor.predict_from_dict(vehicle_payload)

    roads = load_roads(input_path)
    enriched = enrich_with_emissions(roads, emissions)
    save_outputs(enriched, output_geojson, output_csv)

    logging.info("Phase 2 completed successfully")
