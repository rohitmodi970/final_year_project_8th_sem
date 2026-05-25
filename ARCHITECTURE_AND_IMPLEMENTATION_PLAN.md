# Carbon-Aware Eco Routing System

## 1. Project Summary

This project builds a carbon-aware eco-routing system for any city worldwide. The goal is to recommend routes that reduce environmental impact, not only travel distance or time. The system combines road geometry, traffic conditions, vegetation, weather, air quality, and vehicle-specific emission predictions to compute route scores.

The final output should allow a user to:

- enter a source and destination,
- optionally provide vehicle type and vehicle specifications,
- compare multiple route options,
- view a map-based visualization,
- see pollution-related metrics for each route,
- and observe live or near-live traffic simulation updates.

## 2. Core Idea

Traditional navigation systems optimize for shortest distance or fastest time. This project adds an environmental objective.

Each road segment receives a cost score based on:

- road length,
- traffic volume,
- vehicle type,
- vehicle-spec emission prediction,
- building density,
- vegetation coverage,
- wind speed and direction,
- and air quality.

The routing engine uses that score to rank routes and suggest the lowest-impact path.

## 3. Current Data Foundation

The project already has a fused dataset built in [pipeline.py](pipeline.py). That dataset is important because it gives the routing engine a complete baseline even before live services are connected.

### Existing fused sources

- road network from OpenStreetMap for the selected city,
- building density near each road,
- vegetation coverage near each road,
- simulated or SUMO-derived traffic values,
- weather data,
- and AQI data.

### Why fused data matters

The fused dataset is the offline backbone of the system. It makes sure the route engine can work even when live APIs are unavailable, slow, rate-limited, or incomplete.

## 4. Can Real-Time Data Replace Fused Data?

Short answer: partially yes, but not completely.

### What can be real-time

- traffic volume,
- vehicle speed,
- vehicle type distribution,
- air quality,
- wind speed and wind direction,
- weather conditions,
- and vehicle emission predictions from your model API.

### What should usually remain fused or periodically refreshed

- road geometry,
- building footprints,
- vegetation coverage,
- road classification,
- and spatial relationships between roads and nearby features.

These are not truly real-time in most cities. They change slowly, so a fused dataset is the correct base layer.

### Recommended approach

Use a hybrid design:

1. Keep fused data as the stable geographic and environmental base.
2. Pull real-time traffic, AQI, weather, and emission predictions on top of that base.
3. Recompute route scores using the latest live inputs.

This is the most realistic and practical approach for your project.

## 5. Proposed Architecture

### 5.1 Data Layer

This layer stores and provides all route-relevant inputs.

Inputs:

- fused road graph,
- fused geojson/csv outputs,
- SUMO traffic simulation outputs,
- weather API data,
- AQI API data,
- vehicle-spec emission API responses.

Output:

- a normalized road/edge dataset used by the routing engine.

### 5.2 Routing Layer

This layer computes route candidates and scores them.

Responsibilities:

- load the road network as a graph,
- calculate shortest-distance routes,
- calculate fastest-time routes,
- calculate lowest-emission routes,
- calculate balanced routes,
- and compare route metrics.

The main score can combine:

- distance,
- traffic,
- predicted CO2,
- predicted NOx,
- predicted VOC,
- predicted SO2,
- and environmental context.

### 5.3 Emission Prediction Layer

This is your vehicle emission API.

Responsibilities:

- accept vehicle type and vehicle specification data,
- switch between two models based on the amount of data provided,
- predict emissions for CO2, NOx, VOC, and SO2,
- and return structured outputs for the routing layer.

This layer improves the project because it moves beyond a generic carbon formula and makes emissions vehicle-specific.

### 5.4 Simulation Layer

This layer uses SUMO to create realistic traffic conditions.

Responsibilities:

- simulate vehicles on the road network,
- generate vehicle counts and speeds per edge,
- produce congestion patterns,
- and optionally export emission-related outputs.

The simulation layer can feed live updates into the routing engine and frontend.

### 5.5 Backend API Layer

This layer exposes the project as a usable service.

Possible endpoints:

- `POST /route/compare`
- `POST /emissions/predict`
- `GET /simulation/state`
- `GET /map/roads`
- `GET /routes/live`

Responsibilities:

- accept user input,
- coordinate routing and emission calculation,
- merge live data with fused data,
- and return JSON responses to the frontend.

### 5.6 Frontend Layer

This layer presents the system to the user.

UI components:

- source and destination form,
- optional vehicle details form,
- route comparison cards,
- map with route overlays,
- emission breakdown charts,
- traffic simulation panel,
- and live status indicators.

## 6. Data Flow

1. User enters source, destination, and optional vehicle details.
2. Frontend sends the request to the backend API.
3. Backend loads the fused road graph.
4. Backend fetches live weather, AQI, and simulation state if available.
5. Backend calls the vehicle emission API if vehicle details are provided.
6. Routing layer computes route candidates and scores them.
7. Backend returns ranked routes with emissions and travel metrics.
8. Frontend displays the routes on a map with charts and summaries.

## 7. Implementation Plan

### Phase 1: Stabilize the routing engine

Goals:

- keep the fused dataset as the default input,
- make route scoring deterministic,
- standardize route output format,
- and verify comparison between shortest, fastest, and eco routes.

Deliverables:

- route comparison output,
- route scoring function,
- and clean JSON response structure.

### Phase 2: Integrate the emission API

Goals:

- create an adapter around the emission model API,
- define request and response schemas,
- and map predictions into route scoring.

Deliverables:

- emission prediction wrapper,
- pollutant normalization,
- and fallback handling for missing vehicle fields.

### Phase 3: Connect SUMO simulation

Goals:

- complete live traffic simulation,
- map simulation output to road edges,
- and update traffic values continuously.

Deliverables:

- SUMO traffic export,
- edge-level traffic updates,
- and simulation playback or live refresh.

### Phase 4: Build backend APIs

Goals:

- expose routing and emission functions through HTTP endpoints,
- and keep the computation layer separate from the UI.

Deliverables:

- route API,
- emission API,
- simulation API,
- and map data API.

### Phase 5: Build the frontend

Goals:

- create a clean route-planning interface,
- show map overlays,
- and visualize emissions in real time or near real time.

Deliverables:

- responsive frontend,
- route comparison panel,
- pollutant charts,
- and traffic visualization.

### Phase 6: Final demo and documentation

Goals:

- prepare test routes,
- capture screenshots and results,
- and explain the eco-routing impact clearly.

Deliverables:

- final report,
- presentation slides,
- and demo script.

## 8. Recommended Project Strategy

If you want the project to stay realistic and finishable, use this approach:

- use fused data as the base dataset,
- use real-time weather and AQI where available,
- use SUMO for traffic simulation,
- use the emission API for vehicle-level prediction,
- and use the frontend to make it feel live and interactive.

This gives you a stronger project than using only static fused data, while still avoiding the risk of depending entirely on live city data that may not be available at all times.

## 9. Suggested Module Structure

```text
proj/
├── pipeline.py
├── eco_routing.py
├── sumo_integration.py
├── ARCHITECTURE_AND_IMPLEMENTATION_PLAN.md
├── README.md
├── fused_roads.geojson
├── fused_roads.csv
├── fused_roads_with_sumo.geojson
├── sumo_traffic_data.csv
└── cache/
```

## 10. Final Recommendation

The best design is hybrid, not purely fused and not purely real-time.

Use fused data for the road and spatial foundation, then layer real-time or simulated live data on top for traffic, weather, AQI, and emissions. That gives you a stable system, a believable live demo, and a clear technical story for evaluation.