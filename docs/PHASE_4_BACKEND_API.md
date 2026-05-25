# Phase 4: Backend APIs

This phase exposes routing and emissions as HTTP endpoints for the frontend.

## Server start

```bash
python phase4/run_api.py
```

Default port: `5001` (override with `PORT`).

## Endpoints

### `GET /health`
Returns a quick status and basic dataset info.

### `POST /route/compare`
Compares routes for the given origin and destination.

Example payload:
```json
{
  "origin": 290731701,
  "destination": 13851397444,
  "plot_path": "route_compare_api.png"
}
```

Response includes:
- route options with metrics
- best eco route
- optional plot path

### `POST /emissions/predict`
Predicts emissions for a vehicle profile.

Example payload:
```json
{
  "vehicle_type": "Car",
  "fuel_type": "Petrol",
  "road_type": "City",
  "engine_size": 1.5,
  "age_of_vehicle": 5,
  "mileage": 50000
}
```

### `GET /map/roads`
Returns counts and bounds for the current fused dataset.

## Notes

- The API loads the fused dataset once at startup.
- The emissions model is loaded once at startup.
- Plot generation is optional; pass `plot_path` when needed.
