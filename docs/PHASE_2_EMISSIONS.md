# Phase 2: Emission Integration

## Goal

Phase 2 integrates the vehicle emission model into the eco-routing pipeline. It adds a prediction adapter, defines clear request/response schemas, and maps predicted emissions into route scoring and datasets.

## Inputs

- Vehicle characteristics (type, fuel, engine size, mileage)
- Optional fuel-consumption fields for the high-accuracy model
- Context features (traffic condition, speed, weather)

## Output

Normalized emission response:

- CO2 grams per kilometer
- NOx grams per kilometer
- VOC grams per kilometer
- SO2 grams per kilometer
- The model used and fallback notes

Enriched road datasets:

- fused_roads_with_emissions.geojson
- fused_roads_with_emissions.csv

## Request schema

The adapter accepts a dictionary or an EmissionRequest object. Fields are optional; missing fields use defaults.

Primary fields:

- vehicle_type
- fuel_type
- road_type
- traffic_conditions
- engine_size
- age_of_vehicle
- mileage
- speed
- acceleration
- temperature
- humidity
- wind_speed
- air_pressure

High-accuracy fields (Canadian model):

- cylinders
- fuel_cons_comb
- fuel_cons_comb_mpg

If all three high-accuracy fields exist, the Canadian model is used. Otherwise, the synthetic model is used.

## Response schema

The adapter returns:

- co2_g_per_km
- nox_g_per_km
- voc_g_per_km
- so2_g_per_km
- model_used
- notes

## Dataset enrichment

Each road segment receives emission columns and a combined carbon score:

- emission_g_per_km
- nox_g_per_km
- voc_g_per_km
- so2_g_per_km
- emission_cost_g
- nox_cost_g
- voc_cost_g
- so2_cost_g
- carbon_cost_with_emissions
- emission_model_used
- emission_notes

## Emission cost formula

The per-road emission cost uses the predicted g/km scaled by length and traffic:

```
emission_cost_g = emission_g_per_km * (length_m / 1000) * vehicle_count
```

The combined routing score is:

```
carbon_cost_with_emissions = carbon_cost + emission_cost_g
```

## Normalization

The emission model predicts CO2. Other pollutants are derived with fixed ratios (documented in the adapter) so the routing layer can keep a multi-pollutant score. These are approximate and should be replaced by real multi-output models later.

## File locations

- Emission adapter: phase2/emissions.py
- Phase 2 pipeline: phase2/pipeline.py
- Phase 2 CLI: phase2/cli.py and phase2_pipeline.py
- Models: model_for_emissions/model_for_emissions/model.pkl and car_model.pkl
- Optional API endpoint: model_for_emissions/model_for_emissions/unified_app.py
