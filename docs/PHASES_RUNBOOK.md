# How to Run Phases 1 → 3

This runbook shows the minimal steps to run Phase 1 (Data Fusion), Phase 2 (Emission enrichment), and Phase 3 (SUMO merge). It assumes you're in the project root: `E:\cllg project\sem8\proj`.

**Prerequisites**
- Python 3.10+ (project used Python 3.13 in development)
- Git Bash or PowerShell on Windows
- (optional) SUMO installed if you want to run the simulation end-to-end
- A virtualenv or venv active

Install Python dependencies (from your active venv):

```powershell
python -m pip install -r requirements.txt
# If there is no requirements.txt, install these:
pip install geopandas osmnx pandas numpy requests networkx joblib flask
```

Set your OpenWeatherMap API key (used by Phase 1):

```powershell
setx OPENWEATHER_API_KEY "YOUR_API_KEY"
# or in current PowerShell session
$env:OPENWEATHER_API_KEY = 'YOUR_API_KEY'
```

**Quick file notes**
- Phase 1 pipeline: `phase1_pipeline.py` (calls `phase1.pipeline.build_fused_dataset`)
- Phase 2 pipeline: `phase2_pipeline.py` (adds emissions from model)
- Phase 3 pipeline: `phase3_pipeline.py` (merges SUMO outputs into fused dataset)
- Sample vehicle payload: `data/vehicle_request.json`

---

## Phase 1 — Data Fusion
Produces: `fused_roads.geojson` and `fused_roads.csv`.

Run:

```powershell
python phase1_pipeline.py --place "Kolkata, India" --radius-m 5000
```

Notes:
- If `OPENWEATHER_API_KEY` is not set the pipeline uses fallback values for weather/AQI.
- Outputs are written to a city folder (slugified) and copied to repository root as `fused_roads.geojson` and `fused_roads.csv`.

Troubleshooting:
- If OSMnx fails due to network, ensure internet access and try again.
- Long runs: building/vegetation counting uses spatial indices; for very large radii it can be slow.

---

## Phase 2 — Emission Enrichment
Produces: `fused_roads_with_emissions.geojson` and `fused_roads_with_emissions.csv`.

Usage (defaults use `fused_roads.geojson`):

```powershell
# Use a sample vehicle payload
python phase2_pipeline.py --vehicle-json data/vehicle_request.json

# Provide a different fused input
python phase2_pipeline.py --input-geojson delhi/fused_roads.geojson --vehicle-json data/vehicle_request.json
```

What it does:
- Loads the trained emission models from `model_for_emissions/model_for_emissions/`.
- Predicts `co2_g_per_km` (and derived pollutants) for the given vehicle payload.
- Adds per-road emission columns and computes `emission_cost_g`.
- Creates `carbon_cost_with_emissions` (if `carbon_cost` existed).

Troubleshooting:
- If the model files `model.pkl` or `car_model.pkl` are missing, place them under `model_for_emissions/model_for_emissions/`.
- If `vehicle_json` is missing, the CLI falls back to model defaults (check `data/vehicle_request.json`).

---

## Phase 3 — SUMO Merge
Produces: `fused_roads_with_sumo.geojson` and `fused_roads_with_sumo.csv`.

Prerequisite: Either run SUMO and produce `sumo_traffic_data.csv` (via `sumo_integration.py`), or provide an existing SUMO CSV.

Run:

```powershell
python phase3_pipeline.py --fused fused_roads.geojson --sumo-csv sumo_traffic_data.csv
```

What it does:
- Loads `fused_roads.geojson` and `sumo_traffic_data.csv`.
- Attempts to map `sumo.edge_id` → `osmid` and merge simulated `avg_vehicle_count`, `avg_speed_kmh`, and `total_co2_mg`.
- Recomputes `carbon_cost` using SUMO counts and saves merged output.

If `sumo_traffic_data.csv` is missing the script copies `fused_roads.geojson` to the output path so downstream steps will still run.

---

## End-to-end sequence (recommended order)
1. Phase 1: create baseline fused dataset

```powershell
python phase1_pipeline.py --place "Kolkata, India" --radius-m 5000
```

2. (Optional) Run SUMO integration to create `sumo_traffic_data.csv` (requires SUMO installed). The current script builds valid routes directly from the SUMO network first, then falls back to `randomTrips.py` if needed. If you don't run SUMO, skip to Phase 3 — the merge will no-op.

3. Phase 3: merge SUMO data into the fused dataset

```powershell
python phase3_pipeline.py --fused fused_roads.geojson --sumo-csv sumo_traffic_data.csv
```

4. Phase 2: enrich the (possibly SUMO-merged) fused dataset with emissions

```powershell
# If you want emissions applied to SUMO-merged dataset, point --input-geojson
python phase2_pipeline.py --input-geojson fused_roads_with_sumo.geojson --vehicle-json data/vehicle_request.json
```

Output from step 4 (recommended filename):
- `fused_roads_with_sumo_with_emissions.geojson` (if you keep the CLI defaults, check the files written by the script)

5. Run routing (eco-routing will automatically pick the best available fused file):

```powershell
python eco_routing.py
```

---

## One-command helper (optional small script)

Create `run_all.bat` (Windows) or `run_all.sh` (bash) that runs the sequence above. Example `run_all.bat`:

```powershell
@echo off
python phase1_pipeline.py --place "Kolkata, India" --radius-m 5000
python phase3_pipeline.py --fused fused_roads.geojson --sumo-csv sumo_traffic_data.csv
python phase2_pipeline.py --input-geojson fused_roads_with_sumo.geojson --vehicle-json data/vehicle_request.json
pause
```

---

## Common issues & fixes
- Missing model files: copy `model.pkl` and `car_model.pkl` to `model_for_emissions/model_for_emissions/`.
- OSMnx rate limits: reduce `--radius-m` or cache OSM requests.
- SUMO tooling errors: ensure `netconvert`, `duarouter`, and `sumo-gui` are on PATH or call with full path.
- File not found errors: check current working directory is project root.

---

If you'd like, I can:
- Add a single `run_end_to_end.py` runner that orchestrates all three phases and writes a final `fused_roads_with_sumo_with_emissions.geojson` file.
- Add `requirements.txt` generated from used packages.

*** End of runbook ***
