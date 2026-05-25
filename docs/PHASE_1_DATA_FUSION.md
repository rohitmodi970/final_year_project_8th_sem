# Phase 1: Data Fusion

## Goal

Phase 1 builds the foundation of the project by combining road, building, vegetation, traffic, weather, and air-quality data into one fused road-level dataset.

The output is a road graph where each edge has environmental and traffic attributes that can later be used by the routing engine.

## Inputs

- OpenStreetMap road network
- OpenStreetMap building footprints
- OpenStreetMap vegetation polygons
- Weather data from OpenWeatherMap
- AQI data from OpenWeatherMap air pollution API
- Simulated traffic values for the first version

## Output

- `fused_roads.geojson`
- `fused_roads.csv`

Each road segment gets attributes such as:

- length
- building density
- vegetation score
- vehicle count
- average speed
- wind speed
- wind direction
- AQI
- carbon cost

## What Phase 1 is doing technically

Phase 1 is not just file merging. It is a spatial data fusion pipeline.

It performs these steps:

1. download a road graph,
2. convert road data into metric coordinates,
3. find nearby buildings using a 50-meter buffer,
4. find nearby vegetation using a 50-meter buffer,
5. attach traffic values,
6. attach weather and AQI values,
7. compute a carbon cost for every road,
8. export the fused dataset for later routing.

## Why Phase 1 exists

Phase 1 gives the project a usable base dataset.

Without this fused layer:

- eco-routing would have no environmental features,
- the router would only know road geometry,
- and later live data would have nowhere to attach.

## Main idea

The project uses the road segment as the unit of analysis.

Each road becomes a small record with both geometry and environmental context, which makes it possible to score routes by carbon impact instead of only distance.

## Current status

Phase 1 is already implemented in the codebase and generates fused datasets. The next step is to keep the pipeline clean, documented, and ready for global expansion and live data integration.