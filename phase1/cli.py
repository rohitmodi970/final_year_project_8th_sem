import argparse
import logging
import os
from pathlib import Path

from .geo_utils import ensure_output_dir, slugify
from .pipeline import build_fused_dataset, save_outputs


def _load_api_key_from_env_file() -> str:
    env_file = Path(".env.local")
    if not env_file.exists():
        return ""

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in {"OPENWEATHER_API_KEY", "OPEN_WEATHER_API_KEY"} and value:
            return value

    return ""


def _resolve_api_key() -> str:
    return (
        os.getenv("OPENWEATHER_API_KEY")
        or os.getenv("OPEN_WEATHER_API_KEY")
        or _load_api_key_from_env_file()
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 1 data fusion pipeline")
    parser.add_argument("--place", default="Kolkata, India", help="Location to process")
    parser.add_argument("--city-name", default=None, help="Display name for the city")
    parser.add_argument("--output-dir", default=None, help="Output directory for generated files")
    parser.add_argument("--radius-m", type=int, default=5000, help="Query radius in meters")
    parser.add_argument("--api-key", default=_resolve_api_key(), help="OpenWeatherMap API key")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    args = parse_args()
    city_name = args.city_name or args.place.split(",")[0].strip()
    output_dir = ensure_output_dir(args.output_dir or slugify(city_name))

    if not args.api_key:
        logging.warning(
            "OpenWeatherMap API key not found. Set OPENWEATHER_API_KEY or OPEN_WEATHER_API_KEY, or add it to .env.local."
        )

    roads = build_fused_dataset(
        place=args.place,
        city_name=city_name,
        query_radius_m=args.radius_m,
        api_key=args.api_key,
    )
    save_outputs(roads, output_dir)

    logging.info("Phase 1 completed successfully for %s", city_name)
    logging.info("Output directory: %s", output_dir)
