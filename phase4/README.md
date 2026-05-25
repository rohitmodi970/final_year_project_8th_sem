# Phase 4: Backend API

This phase exposes routing and emissions through HTTP endpoints.

## Run the API

```bash
python phase4/run_api.py
```

The server listens on port 5001 by default. Override with `PORT=...`.

## Endpoints

### Health
```bash
curl http://127.0.0.1:5001/health
```

### Route compare
```bash
curl -X POST http://127.0.0.1:5001/route/compare \
  -H "Content-Type: application/json" \
  -d '{"origin": 290731701, "destination": 13851397444, "plot_path": "route_compare_api.png"}'
```

### Emissions predict
```bash
curl -X POST http://127.0.0.1:5001/emissions/predict \
  -H "Content-Type: application/json" \
  -d '{"vehicle_type": "Car", "fuel_type": "Petrol", "road_type": "City"}'
```

### Map bounds
```bash
curl http://127.0.0.1:5001/map/roads
```

## Smoke test (requires server running)

```bash
python phase4/smoke_test.py
```
