# Algorithms Reference

This document explains the main algorithms and methods used in the project.

For each item, the notes below answer:

- Why we use it
- What it does
- A simple example
- Whether we are using an existing algorithm/tool or developing our own logic

## 1. Road Graph Construction

### Why

We need a graph so roads can be searched like a network instead of a plain table.

### What

Roads become nodes and edges in a graph structure.

### Example

Road A connects to Road B, Road B connects to Road C, so a route can be found from A to C.

### Use or develop?

We use existing tools for graph creation, mainly OSMnx and NetworkX. The graph-building process is configured by us, but the underlying graph idea is an existing standard method.

### Where it appears in Phase 1

- [phase1_pipeline.py](../phase1_pipeline.py) uses OSMnx to download the road graph and convert it into a GeoDataFrame.
- The earlier city-specific pipeline in [data_fusion/pipeline2.py](../data_fusion/pipeline2.py) follows the same pattern.

## 2. Spatial Buffer Query

### Why

We need to know which buildings or vegetation lie near a road segment.

### What

A buffer creates a 50-meter zone around each road, then nearby features are counted inside that zone.

### Example

If a road has 12 buildings within 50 meters, its building density becomes 12.

### Use or develop?

We use a standard spatial analysis method from GeoPandas/Shapely. The exact buffering rule and radius are chosen by us.

### Where it appears in Phase 1

- [phase1_pipeline.py](../phase1_pipeline.py) counts buildings and vegetation within a 50 m buffer around each road.
- [data_fusion/pipeline2.py](../data_fusion/pipeline2.py) uses the same 50 m buffer logic.

## 3. Spatial Indexing with R-tree

### Why

We need the pipeline to run fast on a large city dataset.

### What

The spatial index narrows down candidate buildings or vegetation before doing exact intersection checks.

### Example

Instead of checking every building against every road, the index first returns only the likely nearby ones.

### Use or develop?

We use an existing spatial indexing algorithm provided by the geospatial stack. We are not inventing the indexing method ourselves.

### Where it appears in Phase 1

- [phase1_pipeline.py](../phase1_pipeline.py) uses `sindex.intersection(...)` to speed up nearby-feature lookup.
- [data_fusion/pipeline2.py](../data_fusion/pipeline2.py) uses the same optimization.

## 4. Intersection Counting

### Why

We need a simple measure of local building density and green coverage around each road.

### What

After buffering, we count how many polygons intersect the buffer.

### Example

If 8 vegetation polygons intersect a road buffer, that road gets vegetation_score = 8.

### Use or develop?

We use standard geometric intersection operations and apply them in our own pipeline.

### Where it appears in Phase 1

- [phase1_pipeline.py](../phase1_pipeline.py) checks which buffered roads intersect the candidate building and vegetation polygons.

## 5. AQI Conversion from PM2.5

### Why

The air-quality API gives PM2.5 concentration, but the routing model needs a pollution index.

### What

We convert PM2.5 concentration into an AQI-like score using breakpoints.

### Example

If PM2.5 falls in the moderate range, the code maps it to a corresponding AQI band.

### Use or develop?

The breakpoint idea is standard. The specific simplified conversion used in the project is our implementation.

### Where it appears in Phase 1

- [phase1_pipeline.py](../phase1_pipeline.py) converts PM2.5 into an AQI-style score.
- [data_fusion/pipeline2.py](../data_fusion/pipeline2.py) also computes a US EPA-style AQI value.

## 6. Carbon Cost Formula

### Why

We need one score that combines traffic, environment, and air quality so routes can be compared.

### What

The formula combines distance, vehicle count, buildings, vegetation, and AQI into a single road-level score.

### Example

If one road is longer and more crowded, it gets a higher carbon cost.

### Use or develop?

This is our project-specific scoring formula. It is developed by us for this application.

### Where it appears in Phase 1

- [phase1_pipeline.py](../phase1_pipeline.py) computes `carbon_cost` for every road edge.
- [data_fusion/pipeline2.py](../data_fusion/pipeline2.py) uses the same formula with the fused attributes.

## 7. Shortest Path Routing

### Why

We need a baseline route so the eco-route can be compared against a normal route.

### What

It finds the path with minimum distance.

### Example

If route A is 5 km and route B is 7 km, shortest-path routing prefers route A.

### Use or develop?

We use the standard NetworkX shortest-path algorithm.

### Where it appears in the project

- [eco_routing.py](../eco_routing.py) uses `nx.shortest_path(...)` with `length` as the weight.

## 8. Fastest-Time Routing

### Why

We want a comparison against common GPS behavior.

### What

It finds the route with the least travel time.

### Example

A road with higher speed but slightly longer distance may be selected over a shorter congested road.

### Use or develop?

We use standard graph shortest-path logic with time as the edge weight.

### Where it appears in the project

- [eco_routing.py](../eco_routing.py) uses `nx.shortest_path(...)` with `time` as the weight.

## 9. Lowest-Carbon Routing

### Why

This is the core eco-routing goal.

### What

It selects the path with the lowest total carbon cost.

### Example

If one route passes through dense traffic and low-green areas, and another has slightly more distance but lower carbon cost, the second route wins.

### Use or develop?

This is our routing objective built on top of standard graph search.

### Where it appears in the project

- [eco_routing.py](../eco_routing.py) uses `nx.shortest_path(...)` with `carbon_cost` as the weight.

## 10. Balanced Multi-Objective Routing

### Why

Users may not want the absolute lowest-carbon route if it is much slower.

### What

It mixes distance, time, and carbon into a composite score.

### Example

The route may be 50% carbon, 30% time, and 20% distance.

### Use or develop?

This is our custom multi-objective scoring rule.

### Where it appears in the project

- [eco_routing.py](../eco_routing.py) builds `composite_weight` from carbon, time, and distance.

## 11. SUMO Microscopic Traffic Simulation

### Why

Random traffic values are not realistic enough for a live routing system.

### What

SUMO simulates individual vehicles, congestion, speed changes, and emissions.

### Example

A bus stuck at a signal contributes different traffic and emissions than an empty road segment.

### Use or develop?

We use the external SUMO simulator instead of building a traffic simulator from scratch.

### Where it appears in the project

- [sumo_integration.py](../sumo_integration.py) runs or prepares the SUMO simulation pipeline.

## 12. Vehicle Emission Prediction API

### Why

We need pollutant estimates that depend on the vehicle type and its specification.

### What

The API predicts pollutants such as CO2, NOx, VOC, and SO2.

### Example

An electric vehicle should produce much lower emissions than a diesel truck.

### Use or develop?

We use your emission model API as an external component, but the integration logic is our project work.

### Where it appears in the project

- the emission API is a separate service/module you can plug into Phase 1 and route scoring later.

## Short summary

- Existing methods we use: OSMnx, GeoPandas buffers, R-tree indexing, NetworkX shortest path, SUMO
- Our custom logic: carbon cost formula, balanced routing, integration flow, score aggregation

## Best rule for this project

If an algorithm already exists as a standard geospatial or graph method, we use it.

If the project needs a routing score or a decision rule specific to eco-routing, we develop that part ourselves.