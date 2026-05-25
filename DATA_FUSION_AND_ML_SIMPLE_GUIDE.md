# Data Fusion and ML Guide (Kid-Friendly)

## 1) What are we doing right now?

Think of Kolkata roads like a big coloring book.
Each road line is missing many colors (information).
We add colors from different boxes:

- Road shape and length (from map)
- Nearby buildings
- Nearby trees/parks
- Traffic count and speed (currently random in base pipeline)
- Wind
- Air quality (AQI)

After adding all colors, each road gets one final score called carbon_cost.
Lower score means cleaner route.

So data fusion here means: many data sources -> one complete road table.

---

## 2) How fusion works in simple steps

1. Download roads of Kolkata.
2. For each road, draw a 50 meter bubble around it.
3. Count how many buildings are inside the bubble.
4. Count how many green areas are inside the bubble.
5. Add traffic, weather, and AQI.
6. Compute carbon_cost with a formula.
7. Save the fused dataset.

Simple example for one road:

- length = 500 m
- vehicle_count = 100
- building_density = 20
- vegetation_score = 5
- AQI = 120

Formula used now:

carbon_cost = (length * 0.12 * vehicle_count) + (building_density * 5) - (vegetation_score * 3) + (AQI * 0.2)

Result:

carbon_cost = (500 * 0.12 * 100) + (20 * 5) - (5 * 3) + (120 * 0.2)
carbon_cost = 6000 + 100 - 15 + 24 = 6109

---

## 3) Libraries used now (what each one does)

### A) In pipeline.py

1. osmnx
- Downloads city road graph and map features from OpenStreetMap.
- Used for roads, buildings, vegetation.
- Key idea: map data in Python quickly.

2. geopandas
- Works with map tables (GeoDataFrame).
- Used for coordinate conversion, buffering, intersections, spatial index.
- Key idea: spreadsheet + geometry together.

3. pandas
- General table handling and CSV output.
- Used to save final tabular data.

4. numpy
- Generates random traffic values right now.
- Used for vehicle_count and avg_speed simulation.

5. requests
- Calls OpenWeatherMap API for weather and pollution data.

6. logging
- Prints progress and warnings cleanly.

### B) In eco_routing.py

1. networkx
- Builds a road graph and computes shortest paths.
- Used for shortest distance, fastest time, and lowest carbon route.

2. geopandas and osmnx
- Load fused road map and handle map structures.

3. heapq (imported)
- Priority queue utility often used in Dijkstra-style routing.
- Here networkx handles routing internally, so heapq is not central now.

### C) In sumo_integration.py

1. os
- Runs external SUMO commands.

2. osmnx
- Exports OSM network for SUMO.

3. xml.etree.ElementTree
- XML handling utilities (file format used by SUMO).

4. pandas and geopandas
- Process and merge simulation output with fused dataset.

5. traci (inside function)
- Real-time API to control/read SUMO simulation (vehicle count, speed, CO2).

---

## 4) Algorithms used now (simple explanation)

1. Spatial buffer + intersection counting
- For each road, create 50 m buffer.
- Count nearby buildings and green polygons.
- This gives local context around each road.

2. R-tree spatial index
- Fast search trick to avoid checking every building against every road.
- First finds likely candidates, then checks exact intersections.
- Big speed improvement.

3. Weighted scoring formula (rule-based fusion)
- Combines all features into one carbon_cost score.
- Easy to understand and explain.
- But weights are hand-picked, not learned from data.

4. Graph shortest path (NetworkX)
- Same graph, different weight columns:
  - length -> shortest distance route
  - time -> fastest route
  - carbon_cost -> lowest emission route

5. Multi-objective weighted route
- Makes composite_weight from carbon, time, distance.
- Useful when user wants balance, not only one objective.

6. SUMO microscopic traffic simulation
- Simulates vehicles on network and gives realistic speed, occupancy, and CO2.
- Better than random traffic.

---

## 5) Can we use ML here? Yes.

Short answer: yes, absolutely.

Current formula is rule-based.
ML can learn hidden patterns from real/simulated data.

Good targets for ML:

1. Predict carbon_cost_sumo or CO2 directly (regression)
2. Predict vehicle_count and speed by time-of-day (regression)
3. Classify roads into Low/Medium/High emission risk (classification)

---

## 6) XGBoost and Random Forest: how and why

## A) Random Forest

Why use it:
- Easy baseline model
- Handles non-linear patterns
- Works well with mixed numeric features
- Robust without heavy tuning

How to use in this project:
- Input features per road:
  - length, building_density, vegetation_score
  - wind_speed, wind_direction, AQI
  - optional: hour, day, occupancy, avg_speed, vehicle_count
- Target:
  - total_co2_mg from SUMO or carbon_cost_sumo
- Train-test split by time (not random shuffle) if temporal data exists.

When it is good:
- Medium-size data
- Need explainability (feature importance)

## B) XGBoost

Why use it:
- Usually stronger accuracy than Random Forest on tabular data
- Learns complex feature interactions
- Good handling of sparse/missing values

How to use:
- Same features and target as above
- Tune depth, learning rate, estimators
- Evaluate MAE/RMSE

When it is good:
- You want best tabular prediction performance
- You have enough data and can tune parameters

Simple idea:
- Random Forest = many full trees voting
- XGBoost = trees added one by one to fix previous mistakes

---

## 7) Other ML algorithms that can be useful

1. Linear Regression
- Very simple baseline and easy to explain.

2. LightGBM or CatBoost
- Fast gradient boosting alternatives for tabular data.

3. MLP (small neural network)
- Can model non-linearity but usually less reliable than boosting for tabular city data.

4. Graph Neural Networks (GNN)
- Better when road connectivity matters strongly.
- Roads are naturally a graph, so this can be powerful.

---

## 8) Spatiotemporal neural network: how to use here

Spatiotemporal means:
- Spatial = where (road connections and neighbors)
- Temporal = when (time patterns: morning, noon, evening)

Your problem has both, so this is a strong long-term direction.

Good model families:

1. STGCN (Spatio-Temporal Graph Convolutional Network)
2. DCRNN (Diffusion Convolutional Recurrent Neural Network)
3. Graph WaveNet
4. Temporal GAT variants

### What to feed the model

At each time step t (for each road segment):
- vehicle_count_t
- avg_speed_t
- occupancy_t
- AQI_t
- wind_t
- static features: length, building_density, vegetation_score

Graph structure:
- Nodes: junctions or road segments
- Edges: road connectivity from network

Target examples:
- Predict CO2 at t+1 or t+6 steps
- Predict congestion and carbon hotspot 15 minutes ahead

### Why this can beat XGBoost

- XGBoost sees rows mostly independently.
- Spatiotemporal GNN sees neighbor influence plus time trends.
- Traffic and emissions spread across connected roads, so graph-time models match reality better.

### Tradeoff

- Better potential accuracy
- More data and engineering needed
- More compute and harder debugging

---

## 9) Practical roadmap for your project

Phase 1 (quick win)
- Replace random traffic with SUMO outputs consistently.
- Train Random Forest and XGBoost for CO2 prediction.
- Compare against current formula baseline.

Phase 2 (better routing)
- Use predicted CO2 as dynamic edge weight in eco_routing.
- Recompute routes by time-of-day.

Phase 3 (advanced research)
- Build time-series dataset (5 min bins).
- Train STGCN or DCRNN.
- Predict future emissions and route proactively.

---

## 10) Mini example: formula vs ML

Suppose two roads have same length, but one is near a busy junction.
Rule formula may give similar scores.
ML can learn that junction roads create stop-go traffic and higher CO2.
So ML can separate them better.

That is why ML can improve fusion quality.

---

## 11) Important caution

Your current pipeline has a hardcoded API key inside code.
For safety, move keys to environment variables before sharing the project.

---

## 12) Final kid summary

Right now your system is already smart:
- It mixes many city clues into one road score.

With ML, it can become smarter:
- It learns from real data instead of fixed hand rules.

With spatiotemporal neural networks, it can become future-smart:
- It can guess where pollution will go next and choose cleaner routes before traffic gets bad.

---

## 13) Where formula weights come from (simple) and how to tune them

Very important:
- The current formula is a hand-made scoring rule (baseline).
- It is made from domain logic, not a single fixed universal equation.

Current form:

carbon_cost = (length * 0.12 * vehicle_count) + (building_density * 5) - (vegetation_score * 3) + (AQI * 0.2)

### Why these numbers exist

1. 0.12
- Scales distance x traffic into a usable score range.

2. 5 for building_density
- Adds penalty for dense built-up zones.

3. 3 for vegetation_score
- Gives reward (subtraction) for green cover.

4. 0.2 for AQI
- Adds background pollution pressure.

These are starting weights so routing works today.
Later, we should learn better weights from data.

### How to learn better weights from data

Idea:
- Use SUMO/measured CO2 as ground truth.
- Fit a simple regression model.
- Model learns coefficient size automatically.

Kid version:
- Teacher gives answer key (real CO2).
- Model changes marks for each feature until prediction matches answer key better.

### Tiny numeric example

Suppose we have 4 roads with real CO2 from SUMO:

1. Road A: length=300, vehicles=40, buildings=5, vegetation=6, AQI=90, real_CO2=1300
2. Road B: length=500, vehicles=90, buildings=15, vegetation=2, AQI=110, real_CO2=4300
3. Road C: length=250, vehicles=35, buildings=3, vegetation=10, AQI=85, real_CO2=900
4. Road D: length=700, vehicles=120, buildings=20, vegetation=1, AQI=140, real_CO2=7600

Train linear regression using feature columns:
- x1 = length * vehicle_count
- x2 = building_density
- x3 = vegetation_score
- x4 = AQI

Learned equation may become:

predicted_CO2 = (0.108 * x1) + (6.2 * x2) - (4.1 * x3) + (0.28 * x4) + 50

Now weights are data-driven:
- 0.108 instead of 0.12
- 6.2 instead of 5
- 4.1 instead of 3
- 0.28 instead of 0.2

This means your formula has been calibrated to your city data.

### How to use this practically in your project

1. Build dataset from fused roads + SUMO output.
2. Split by time (older time for train, newer time for test).
3. Train baseline linear regression.
4. Compare errors (MAE/RMSE) with hand formula.
5. Then train Random Forest and XGBoost.
6. Pick best model for prediction.
7. Use predicted CO2 as road edge weight in routing.

### Why this is better

- Hand formula is explainable and quick.
- Calibrated formula is still explainable but more accurate.
- Tree models are often most accurate on tabular data.
- Spatiotemporal neural nets are best when you have rich time + graph data.
