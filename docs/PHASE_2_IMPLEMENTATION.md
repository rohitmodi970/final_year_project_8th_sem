# Phase 2: Implementation Guide

## Purpose

Phase 2 wires the emission model into the pipeline and routing layer. The goal is to produce vehicle-aware emission scores that can be used as routing weights.

## What Phase 2 produces

- Enriched fused datasets with emission columns
- A combined routing score (`carbon_cost_with_emissions`)
- Optional JSON emission API for integration

## Implementation flow

### 1. Emission prediction adapter

- Uses the local models in model_for_emissions
- Switches between the Canadian and synthetic models based on inputs
- Produces CO2 and derived pollutant values

Code: phase2/emissions.py

### 2. Enrich the fused dataset

- Load `fused_roads.geojson`
- Predict emissions for the provided vehicle
- Add emission columns and combined cost
- Save `fused_roads_with_emissions.geojson` and CSV

Code: phase2/pipeline.py

### 3. Routing integration

- If `carbon_cost_with_emissions` exists, routing uses it
- Route stats expose `emission_cost_g` when available

Code: eco_routing.py

### 4. Optional HTTP API

- Adds `/predict-json` to the Flask app
- Returns JSON for external services

Code: model_for_emissions/model_for_emissions/unified_app.py

## How to run

### A) Enrich the dataset

```
python phase2_pipeline.py --vehicle-json data/vehicle_request.json
```

### B) Use in routing

```
python eco_routing.py
```

## Vehicle payload example

Save as `data/vehicle_request.json`:

```
{
  "Vehicle Type": "Car",
  "Fuel Type": "Petrol",
  "Road Type": "City",
  "Traffic Conditions": "Moderate",
  "engine_size": 1.6,
  "Age of Vehicle": 4,
  "Mileage": 42000,
  "Speed": 50.0,
  "Acceleration": 2.2,
  "Temperature": 28.0,
  "Humidity": 55.0,
  "Wind Speed": 8.0,
  "Air Pressure": 1010.0
}
```

If you add these fields, the high-accuracy model is used:

- cylinders
- fuel_cons_comb
- fuel_cons_comb_mpg

## Notes

- Phase 2 keeps Phase 1 data unchanged and only adds emission columns.
- If no vehicle JSON is provided, the model uses defaults from the emission adapter.
