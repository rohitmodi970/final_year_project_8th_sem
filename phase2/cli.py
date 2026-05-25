import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from .pipeline import run_phase2_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 2 emission integration")
    parser.add_argument(
        "--input-geojson",
        default="fused_roads.geojson",
        help="Input fused dataset (GeoJSON)",
    )
    parser.add_argument(
        "--output-geojson",
        default="fused_roads_with_emissions.geojson",
        help="Output GeoJSON with emission columns",
    )
    parser.add_argument(
        "--output-csv",
        default="fused_roads_with_emissions.csv",
        help="Output CSV with emission columns",
    )
    parser.add_argument(
        "--vehicle-json",
        default=None,
        help="Path to JSON file with vehicle fields for emission prediction",
    )
    parser.add_argument(
        "--model-dir",
        default=None,
        help="Optional model directory for emission predictor",
    )
    return parser.parse_args()


def load_vehicle_payload(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        logging.warning("No vehicle JSON provided. Using model defaults.")
        return {}

    payload_path = Path(path)
    if not payload_path.exists():
        logging.warning("Vehicle JSON not found at %s. Using model defaults.", payload_path)
        return {}

    data = json.loads(payload_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Vehicle JSON must be an object")
    return data


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    args = parse_args()
    vehicle_payload = load_vehicle_payload(args.vehicle_json)

    run_phase2_pipeline(
        input_path=Path(args.input_geojson),
        output_geojson=Path(args.output_geojson),
        output_csv=Path(args.output_csv) if args.output_csv else None,
        vehicle_payload=vehicle_payload,
        model_dir=Path(args.model_dir) if args.model_dir else None,
    )


if __name__ == "__main__":
    main()
