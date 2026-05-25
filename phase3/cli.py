import argparse
import logging
from pathlib import Path

from .pipeline import merge_sumo_with_fused


def parse_args():
    parser = argparse.ArgumentParser(description="Phase 3 SUMO merge pipeline")
    parser.add_argument("--fused", default="fused_roads.geojson", help="Input fused geojson")
    parser.add_argument("--sumo-csv", default="sumo_traffic_data.csv", help="SUMO processed CSV")
    parser.add_argument("--out-geojson", default="fused_roads_with_sumo.geojson", help="Output geojson")
    parser.add_argument("--out-csv", default="fused_roads_with_sumo.csv", help="Output csv")
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args()

    merge_sumo_with_fused(
        fused_path=Path(args.fused),
        sumo_csv=Path(args.sumo_csv),
        out_geojson=Path(args.out_geojson),
        out_csv=Path(args.out_csv),
    )


if __name__ == "__main__":
    main()
