# Project Explained for 7th Grade

This is a super simple guide to what this project does. Think of it like a smart map that tries to pick roads that are less polluting.

## Big picture (short story)
- We start with a city map of roads.
- We add extra information like traffic, air quality, buildings, trees, and weather.
- We estimate how much pollution cars make on each road.
- We simulate traffic in a tool called SUMO to get more realistic traffic numbers.
- We then pick routes that are shorter and cleaner.

## Main phases (steps)
### Phase 1: Data Fusion
- "Fusion" means mixing different kinds of data together.
- We take roads and add things like:
  - How many buildings are near the road
  - How many trees are near the road
  - Traffic counts (simulated)
  - Air quality (AQI)
  - Weather
- The output is a file called `fused_roads.geojson`.

### Phase 2: Emissions (Pollution)
- We use a trained model to estimate how much pollution a vehicle makes per kilometer.
- This adds new columns like CO2 and other gases to the roads.
- The output is `fused_roads_with_emissions.geojson`.

### Phase 3: SUMO Traffic Simulation
- SUMO is a traffic simulator (like a video game for cars).
- We put the city roads into SUMO, generate trips, and run the simulation.
- This gives more realistic traffic speed and vehicle count.
- The output is `fused_roads_with_sumo.geojson`.

## Key words (very simple meanings)
- **OSM (OpenStreetMap)**: A free map of the world made by people.
- **OSMnx**: A tool that downloads roads from OSM.
- **GeoJSON**: A file format for maps (roads, points, shapes).
- **CSV**: A table in a file (like rows and columns in Excel).
- **Road network**: All roads connected like a big graph.
- **Node**: A point on the road map (like an intersection).
- **Edge**: A road segment between two nodes.
- **Graph**: A math way to store nodes and edges.
- **Routing**: Finding a path from start to end.
- **Eco-routing**: Routing that tries to be cleaner, not just shorter.
- **AQI**: Air Quality Index. Higher means worse air.
- **Vegetation**: Trees or green areas.
- **Building density**: How many buildings are near a road.
- **Weather**: Wind, temperature, humidity.
- **Emission**: Pollution from vehicles (like CO2).
- **CO2**: A gas that causes global warming.
- **Model**: A trained math machine that makes predictions.
- **Pipeline**: Steps that run one after another to create results.
- **SUMO**: Traffic simulator that runs cars on roads.
- **TraCI**: A tool to talk to SUMO while it runs.
- **Random trips**: Random routes created for cars in the simulation.
- **Merged dataset**: A file where two sets of data are joined together.

## What the files mean (common outputs)
- `fused_roads.geojson`: Roads + environment data.
- `fused_roads_with_sumo.geojson`: Roads + SUMO traffic data.
- `fused_roads_with_emissions.geojson`: Roads + pollution data.
- `sumo_traffic_data.csv`: Traffic stats from SUMO.

## How to use the route finder (simple)
- The route script loads the best dataset it can find.
- It needs two node IDs (start and end).
- Then it compares routes like:
  - Shortest route
  - Fastest route
  - Lowest emissions route

## If something goes wrong (simple tips)
- If SUMO says 0 trips, it means no cars were created.
- If the model fails to load, install `scikit-learn`.
- If you are stuck, re-run a phase one by one.

## Why this is useful
- It helps us think about cleaner routes.
- It shows how traffic and pollution are linked.
- It is a good science and computer project.
