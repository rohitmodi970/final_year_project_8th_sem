from __future__ import annotations

import os
from typing import Any, Dict

from flask import Flask, jsonify, request

import eco_routing
from phase2.emissions import EmissionPredictor


def _load_predictor() -> EmissionPredictor:
    model_dir = os.environ.get("EMISSION_MODEL_DIR")
    return EmissionPredictor(model_dir=model_dir)


def _parse_int(value: Any, field: str) -> int:
    if value is None:
        raise ValueError(f"Missing required field: {field}")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid integer for {field}: {value}") from exc


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health() -> Any:
        try:
            edges = eco_routing.get_edges_dataset()
        except FileNotFoundError as exc:
            return jsonify(status="error", message=str(exc)), 500

        bounds = edges.total_bounds.tolist() if hasattr(edges, "total_bounds") else None
        return jsonify(status="ok", edge_count=int(len(edges)), bounds=bounds)

    @app.get("/")
    def index() -> Any:
        return jsonify(
            message="Phase 4 API is running.",
            endpoints=[
                "GET /health",
                "POST /route/compare",
                "POST /emissions/predict",
                "GET /map/roads",
            ],
        )

    @app.post("/route/compare")
    def route_compare() -> Any:
        payload: Dict[str, Any] = request.get_json(silent=True) or {}
        origin = _parse_int(payload.get("origin"), "origin")
        destination = _parse_int(payload.get("destination"), "destination")

        plot_path = payload.get("plot_path")
        show_plot = bool(payload.get("show_plot", False))

        result = eco_routing.compare_routes_data(origin, destination)
        if not result["results"]:
            return jsonify(error="No path found for the given nodes."), 404

        if plot_path:
            eco_routing._plot_route_comparison(
                result["routes_for_plot"],
                plot_path,
                show_plot,
            )

        response = {
            "origin": result["origin"],
            "destination": result["destination"],
            "results": result["results"],
            "best_eco": result["best_eco"],
            "plot_path": plot_path,
        }
        return jsonify(response)

    @app.post("/emissions/predict")
    def emissions_predict() -> Any:
        payload = request.get_json(silent=True) or {}
        try:
            predictor = _load_predictor()
        except FileNotFoundError as exc:
            return jsonify(error=str(exc)), 500

        prediction = predictor.predict_from_dict(payload)
        return jsonify(
            co2_g_per_km=prediction.co2_g_per_km,
            nox_g_per_km=prediction.nox_g_per_km,
            voc_g_per_km=prediction.voc_g_per_km,
            so2_g_per_km=prediction.so2_g_per_km,
            model_used=prediction.model_used,
            notes=prediction.notes,
        )

    @app.get("/map/roads")
    def map_roads() -> Any:
        try:
            edges = eco_routing.get_edges_dataset()
        except FileNotFoundError as exc:
            return jsonify(error=str(exc)), 500

        bounds = edges.total_bounds.tolist() if hasattr(edges, "total_bounds") else None
        return jsonify(
            edge_count=int(len(edges)),
            bounds=bounds,
            crs=str(edges.crs) if hasattr(edges, "crs") else None,
        )

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=False)
