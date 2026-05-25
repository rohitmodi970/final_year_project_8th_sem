# Phase 3: SUMO Integration and Merge

## Goal

Phase 3 runs a SUMO simulation (or consumes its outputs) and merges realistic traffic and emission outputs back into the fused dataset.

## Inputs

- `fused_roads.geojson` (from Phase 1)
- `sumo_traffic_data.csv` (from SUMO integration)

## Outputs

- `fused_roads_with_sumo.geojson` (merged dataset)
- `fused_roads_with_sumo.csv`

## How it works

1. `phase3/cli.py` reads the fused geojson and the SUMO CSV.
2. It attempts to map SUMO `edge_id` values to `osmid` values by extracting integers from the `edge_id`.
3. It fills `avg_vehicle_count` and `avg_speed_kmh` from SUMO where available.
4. It recalculates `carbon_cost` using SUMO vehicle counts.
5. The merged dataset is saved for routing and further enrichment.

## Run

```bash
python phase3_pipeline.py --fused fused_roads.geojson --sumo-csv sumo_traffic_data.csv
```

If SUMO CSV is missing, the pipeline will copy the fused dataset to the output path unchanged (so downstream steps can continue).
