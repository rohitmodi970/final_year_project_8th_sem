# Phase 1: Implementation Guide

## Purpose

Phase 1 is the data-fusion layer of the project. Its job is to turn raw city data into one fused road dataset that the routing engine can use.

The current implementation is in [phase1_pipeline.py](../phase1_pipeline.py).

## What Phase 1 produces

Phase 1 produces a road-level dataset with:

- geometry
- road length
- building density
- vegetation score
- simulated traffic values
- weather data
- AQI data
- carbon cost

It also writes legacy root files so the existing routing code can keep working.

## Implementation flow

### 1. City selection

The script starts with a place name and an output directory.

Why:

- so the pipeline can run for any city

What:

- resolves the city to coordinates
- creates a safe output folder name

Example:

- `"Kolkata, India"`
- `"Delhi, India"`
- `"London, UK"`

### 2. Road network download

The script downloads the drivable road network using OSMnx.

Why:

- the route engine needs roads as a graph

What:

- creates a road graph around the selected city
- converts it to a GeoDataFrame
- projects it to metric coordinates

Example:

- a road segment with length in meters and geometry in EPSG:3857

### 3. Building footprint download

The script downloads all building footprints near the city center.

Why:

- buildings are used as a pollution-density proxy

What:

- fetches building polygons from OpenStreetMap
- converts them to metric coordinates
- computes area where available

Example:

- a road with 14 buildings inside a 50 m buffer gets building_density = 14

### 4. Vegetation download

The script downloads green-space polygons near the city center.

Why:

- vegetation lowers the local environmental score

What:

- fetches forest, grass, meadow, park, and garden areas
- converts them to metric coordinates
- counts how much green space is near each road

Example:

- a road with 6 nearby green polygons gets vegetation_score = 6

### 5. Spatial counting with buffers

The script creates a 50-meter buffer around every road and counts nearby features.

Why:

- to measure the local environment around each route edge

What:

- creates a road buffer
- uses a spatial index to narrow candidates
- checks exact intersections
- counts buildings and vegetation

Example:

- road A intersects 20 buildings and 3 vegetation polygons

### 6. Traffic generation

The script creates simulated traffic values for the first version.

Why:

- the route score needs traffic before live simulation is fully connected

What:

- assigns a vehicle count
- assigns an average speed

Example:

- 120 vehicles on one edge, 35 km/h average speed

### 7. Weather and AQI fetch

The script fetches live weather and air-quality data from OpenWeatherMap.

Why:


What:


Example:

If `OPENWEATHER_API_KEY` or `OPEN_WEATHER_API_KEY` is not set the pipeline uses fallback values for weather/AQI.

You can place the key in `.env.local` using either name:

```dotenv
OPENWEATHER_API_KEY=your_key_here
# or
OPEN_WEATHER_API_KEY=your_key_here
```
### 8. Carbon cost calculation

The script combines road length, traffic, buildings, vegetation, and AQI into a carbon cost.

Why:

- routing needs one comparable score per edge

What:

- computes a single road score using the project formula

Example:

- a longer and more crowded road gets a higher carbon cost

### 9. File export

The script saves both modern and legacy outputs.

Why:

- modern outputs support the new folder structure
- legacy outputs keep existing code working

What:

- writes city-specific files into a city folder
- copies fused files back to the project root

Example:

- `delhi/fused_roads.geojson`
- `fused_roads.geojson`

## Which parts are existing algorithms and which are ours?

- Existing tools: OSMnx, GeoPandas, Shapely spatial buffers, R-tree spatial indexing, OpenWeatherMap APIs
- Our logic: city selection flow, output organization, feature aggregation, traffic fallback strategy, carbon-cost formula, compatibility copying

## Why this matters for the project

Phase 1 gives the routing engine a stable base dataset. That base can be reused for any city, then enriched later with SUMO, live traffic, and emission-prediction APIs.