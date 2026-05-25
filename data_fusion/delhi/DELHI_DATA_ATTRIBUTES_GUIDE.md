# Delhi Data Attributes Guide

This document explains each dataset in the Delhi folder.
For every attribute, you get:
- What it is
- Why it matters
- How to use/read it
- Example (from first row)

## Simple English: What are attributes/features?

An attribute (or feature) means a column in your data table.

- One row = one record (one item).
- One column = one detail about that item.
- Attribute and feature mean the same thing.

Think like a student table:
- Columns: name, class, marks
- One row: one student

Your project is the same, but with roads, traffic, weather, and air quality.

### Quick examples from Delhi data

1. AQI file
- File: aqi_raw__pm25_ugm3__aqi_index.csv
- Attribute `location` tells where data is from.
- Attribute `pm2_5_ugm3` tells pollution level.
- Attribute `us_epa_aqi` tells air-quality risk score.

2. Roads file
- File: roads_raw__length_m__lanes_count.csv
- Attribute `length` tells road segment length.
- Attribute `highway` tells road type.
- Attribute `oneway` tells if movement is one-way.

3. Traffic file
- File: traffic_simulated__vehicle_count__speed_kmph.csv
- Attribute `vehicle_count_per_hr` tells traffic volume.
- Attribute `avg_speed_kmph` tells average speed.

4. Weather file
- File: weather_raw__wind_speed_mps__wind_dir_deg.csv
- Attribute `wind_speed_mps` tells wind speed.
- Attribute `temperature_C` tells temperature.

### Easy memory trick

- Attribute/feature = question
- Value in row = answer

Example:
- Question: `avg_speed_kmph`
- Answer (from first row): `42`

## 1) aqi_raw__pm25_ugm3__aqi_index.csv
Purpose: Air quality snapshot for Delhi from OpenWeatherMap.

First row summary:
- location=Delhi
- lat=28.6138954
- lon=77.2090057
- pm2_5_ugm3=22.48
- pm10_ugm3=44.44
- no2_ugm3=25.89
- o3_ugm3=22.4
- so2_ugm3=3.88
- co_ugm3=534.41
- openweather_aqi_1to5=2
- us_epa_aqi=72
- source=live_OpenWeatherMap_AirPollution

### location
- What: Name of city/location.
- Why: Identifies which place the measurements belong to.
- How: Use for grouping/filtering records by city.
- Example: Delhi

### lat
- What: Latitude coordinate.
- Why: Required for map plotting and geospatial joins.
- How: Combine with lon to place a point on map.
- Example: 28.6138954

### lon
- What: Longitude coordinate.
- Why: Required for map plotting and geospatial joins.
- How: Combine with lat for geographic location.
- Example: 77.2090057

### pm2_5_ugm3
- What: PM2.5 concentration (micrograms per cubic meter).
- Why: PM2.5 is a key health risk pollutant.
- How: Higher value means worse fine particulate pollution.
- Example: 22.48

### pm10_ugm3
- What: PM10 concentration (ug/m3).
- Why: Indicates larger particulate pollution load.
- How: Compare across time/areas to track dust/traffic effects.
- Example: 44.44

### no2_ugm3
- What: Nitrogen dioxide concentration (ug/m3).
- Why: Strong indicator of vehicle/combustion emissions.
- How: Use as traffic-related pollution proxy.
- Example: 25.89

### o3_ugm3
- What: Ozone concentration (ug/m3).
- Why: Ozone affects respiratory health and is photochemical.
- How: Analyze with weather/sunlight and traffic chemistry.
- Example: 22.4

### so2_ugm3
- What: Sulfur dioxide concentration (ug/m3).
- Why: Tracks sulfur-related combustion sources.
- How: Monitor industrial/fuel sulfur contribution.
- Example: 3.88

### co_ugm3
- What: Carbon monoxide concentration (ug/m3).
- Why: Marker of incomplete combustion, often traffic influenced.
- How: Use in emission-health trend analysis.
- Example: 534.41

### openweather_aqi_1to5
- What: OpenWeather AQI category (1 best, 5 worst).
- Why: Quick categorical quality score.
- How: Use for simple dashboard color bands.
- Example: 2

### us_epa_aqi
- What: US EPA AQI index value.
- Why: Standardized AQI scale used in many reports.
- How: Convert raw pollutants into public risk category.
- Example: 72

### source
- What: Data provider/source label.
- Why: Supports traceability and reproducibility.
- How: Keep in outputs to document provenance.
- Example: live_OpenWeatherMap_AirPollution

## 2) aqi_raw__UNITS_LEGEND.csv
Purpose: Unit/meaning dictionary for AQI columns.

First row summary:
- column=pm2_5_ugm3
- unit=ug/m3
- notes=PM2.5 particulate matter

### column
- What: Name of measured field.
- Why: Links metadata to actual dataset columns.
- How: Join this legend on column name.
- Example: pm2_5_ugm3

### unit
- What: Measurement unit of the column.
- Why: Prevents unit confusion in calculations.
- How: Read before aggregating or converting metrics.
- Example: ug/m3

### notes
- What: Human-readable description.
- Why: Gives domain context to the metric.
- How: Use in reports and table captions.
- Example: PM2.5 particulate matter

## 3) buildings_raw__footprint_m2.csv
Purpose: Building footprint attributes.

First row summary:
- area_m2=0.0
- building=office
- name=CRIS Office - Centre for Railways Information Systems
- addr:street=
- area_unit=square_meters

### area_m2
- What: Building footprint area.
- Why: Used for density and built-up intensity analysis.
- How: Sum or average by zone/road buffer.
- Example: 0.0

### building
- What: Building type/category.
- Why: Distinguishes land-use function (office/residential/etc.).
- How: Segment results by use-type.
- Example: office

### name
- What: Building name, if available.
- Why: Helps identify notable structures.
- How: Use as optional label in maps/tables.
- Example: CRIS Office - Centre for Railways Information Systems

### addr:street
- What: Street address text.
- Why: Improves interpretability and location context.
- How: Keep as optional field; may be blank often.
- Example: (blank)

### area_unit
- What: Unit for area field.
- Why: Confirms spatial measurement scale.
- How: Validate unit before calculations.
- Example: square_meters

## 4) buildings_raw__footprint_m2.geojson
Purpose: Spatial building features with same core attributes plus geometry IDs.

First feature summary:
- element=node
- id=438049077
- area_m2=0.0
- building=office
- name=CRIS Office - Centre for Railways Information Systems
- addr:street=
- area_unit=square_meters

### element
- What: OSM element type (node/way/relation).
- Why: Tells source object kind.
- How: Use for QA or OSM-specific processing.
- Example: node

### id
- What: OSM object identifier.
- Why: Unique key for traceability.
- How: Use for de-duplication and source lookup.
- Example: 438049077

### area_m2
- What: Building area in m2.
- Why: Built-up area quantification.
- How: Aggregate by region or corridor.
- Example: 0.0

### building
- What: Building category.
- Why: Functional classification.
- How: Group by type for analytics.
- Example: office

### name
- What: Named label of building.
- Why: Readability in outputs.
- How: Display in maps/tooltips.
- Example: CRIS Office - Centre for Railways Information Systems

### addr:street
- What: Street attribute.
- Why: Optional context for interpretation.
- How: Fill missing values as null/blank safely.
- Example: (blank)

### area_unit
- What: Unit for area.
- Why: Unit consistency.
- How: Check before combining with other area fields.
- Example: square_meters

## 5) roads_raw__length_m__lanes_count.csv
Purpose: Road-network attributes (non-geometry tabular export).

First row summary:
- length=17.64053854240796
- name=
- highway=residential
- lanes=
- maxspeed=
- oneway=False
- length_unit=meters
- crs=EPSG:3857

### length
- What: Length of road segment.
- Why: Needed for exposure weighting and network analysis.
- How: Use as weight when aggregating traffic/emissions.
- Example: 17.64053854240796

### name
- What: Road/street name.
- Why: Human identification.
- How: Optional label for reporting.
- Example: (blank)

### highway
- What: OSM road classification.
- Why: Proxy for hierarchy/capacity (residential, primary, etc.).
- How: Use for stratified routing analysis.
- Example: residential

### lanes
- What: Number of lanes.
- Why: Strong determinant of capacity and potential flow.
- How: Use in traffic/emission modeling features.
- Example: (blank)

### maxspeed
- What: Speed limit metadata.
- Why: Influences congestion and emission factors.
- How: Use if present; handle missing values.
- Example: (blank)

### oneway
- What: One-way flag for segment.
- Why: Important for routing validity.
- How: Respect this in pathfinding/simulation.
- Example: False

### length_unit
- What: Unit for length.
- Why: Confirms linear unit.
- How: Keep as metadata for reproducibility.
- Example: meters

### crs
- What: Coordinate reference system name.
- Why: Required for correct distance/area calculations.
- How: Reproject only when needed for analysis.
- Example: EPSG:3857

## 6) roads_raw__length_m__lanes_count.geojson
Purpose: Spatial roads with graph-edge identifiers.

First feature summary:
- u=60890393
- v=6436786516
- key=0
- length=17.64053854240796
- name=
- highway=residential
- lanes=
- maxspeed=
- oneway=False
- length_unit=meters
- crs=EPSG:3857

### u
- What: Start node ID of road edge.
- Why: Defines directed graph edge structure.
- How: Pair with v/key to uniquely identify edge.
- Example: 60890393

### v
- What: End node ID of road edge.
- Why: Defines connectivity in network graph.
- How: Use with u for adjacency/path calculations.
- Example: 6436786516

### key
- What: Multi-edge key between same u and v.
- Why: Distinguishes parallel edges.
- How: Keep when joining with simulated traffic by edge.
- Example: 0

### length
- What: Edge length in meters.
- Why: Route cost and weighting factor.
- How: Use in shortest/eco routing objective.
- Example: 17.64053854240796

### name
- What: Road name.
- Why: Display/readability.
- How: Optional in UI and reports.
- Example: (blank)

### highway
- What: OSM road class.
- Why: Indicates typical traffic function.
- How: Feature for speed/emission estimation.
- Example: residential

### lanes
- What: Lane count.
- Why: Capacity indicator.
- How: Model feature where available.
- Example: (blank)

### maxspeed
- What: Posted speed field.
- Why: Performance and emissions relevance.
- How: Use with caution due to missing values.
- Example: (blank)

### oneway
- What: One-way movement rule.
- Why: Route feasibility constraint.
- How: Enforce during network traversal.
- Example: False

### length_unit
- What: Unit of length.
- Why: Unit transparency.
- How: Maintain for documentation.
- Example: meters

### crs
- What: CRS descriptor.
- Why: Spatial compatibility across layers.
- How: Reproject before geospatial joins if CRS differs.
- Example: EPSG:3857

## 7) traffic_simulated__vehicle_count__speed_kmph.csv
Purpose: Simulated traffic intensity and speed by road edge.

First row summary:
- edge_osmid=(60890393, 6436786516, 0)
- vehicle_count_per_hr=68
- avg_speed_kmph=42

### edge_osmid
- What: Edge identifier tuple matching road graph edge (u, v, key).
- Why: Primary join key to road network.
- How: Join with roads edge IDs to map traffic values spatially.
- Example: (60890393, 6436786516, 0)

### vehicle_count_per_hr
- What: Vehicles passing per hour (simulated).
- Why: Core traffic volume feature.
- How: Use as emission activity factor.
- Example: 68

### avg_speed_kmph
- What: Average vehicle speed in km/h.
- Why: Strong predictor of fuel use and emissions.
- How: Combine with traffic counts for carbon-cost modeling.
- Example: 42

## 8) traffic_simulated__UNITS_LEGEND.csv
Purpose: Unit/source metadata for simulated traffic fields.

First row summary:
- column=vehicle_count_per_hr
- unit=vehicles/hour
- source=simulated (uniform random 20-200)

### column
- What: Traffic field name.
- Why: Maps metadata to numeric column.
- How: Use in automatic report legends.
- Example: vehicle_count_per_hr

### unit
- What: Unit for column.
- Why: Prevents interpretation errors.
- How: Include in axis labels.
- Example: vehicles/hour

### source
- What: Origin/method of generation.
- Why: Communicates data realism and assumptions.
- How: Mark as synthetic in publications.
- Example: simulated (uniform random 20-200)

## 9) vegetation_raw__area_m2__type_category.csv
Purpose: Vegetation area and type attributes.

First row summary:
- area_m2=0.0
- veg_type=natural:tree
- name=
- area_unit=square_meters

### area_m2
- What: Vegetation feature area.
- Why: Basis for green-cover quantification.
- How: Aggregate by road buffer or zone.
- Example: 0.0

### veg_type
- What: Vegetation category/class.
- Why: Distinguishes ecological role (tree, grass, etc.).
- How: Group to compute type-wise green metrics.
- Example: natural:tree

### name
- What: Feature name if present.
- Why: Optional descriptive context.
- How: Use only for labeling.
- Example: (blank)

### area_unit
- What: Unit for area value.
- Why: Ensures consistency in comparisons.
- How: Verify before merging with external area data.
- Example: square_meters

## 10) vegetation_raw__area_m2__type_category.geojson
Purpose: Spatial vegetation features with source IDs.

First feature summary:
- element=node
- id=545764554
- area_m2=0.0
- veg_type=natural:tree
- name=
- area_unit=square_meters

### element
- What: OSM element type.
- Why: Source structure awareness.
- How: Use for data quality checks.
- Example: node

### id
- What: OSM object ID.
- Why: Unique identifier for traceability.
- How: Use for dedupe/source auditing.
- Example: 545764554

### area_m2
- What: Area in square meters.
- Why: Green-cover metric.
- How: Summarize over study zones.
- Example: 0.0

### veg_type
- What: Vegetation category.
- Why: Ecological segmentation.
- How: Compare distributions by type.
- Example: natural:tree

### name
- What: Optional feature name.
- Why: Human readability.
- How: Label only when populated.
- Example: (blank)

### area_unit
- What: Area unit metadata.
- Why: Unit consistency.
- How: Keep unchanged in exports.
- Example: square_meters

## 11) weather_raw__wind_speed_mps__wind_dir_deg.csv
Purpose: Weather conditions used for environmental context.

First row summary:
- location=Delhi
- wind_speed_mps=3.09
- wind_dir_deg=60
- temperature_K=300.22
- temperature_C=27.07
- humidity_pct=47
- description=haze
- source=live_OpenWeatherMap

### location
- What: City/location name.
- Why: Reference for weather context.
- How: Link weather row to city-level analysis.
- Example: Delhi

### wind_speed_mps
- What: Wind speed in meters/second.
- Why: Influences pollutant dispersion.
- How: Use in pollution spread interpretation.
- Example: 3.09

### wind_dir_deg
- What: Wind direction in degrees.
- Why: Indicates downwind/upwind patterns.
- How: Use for directional pollution analysis.
- Example: 60

### temperature_K
- What: Absolute temperature in Kelvin.
- Why: Standard scientific unit.
- How: Use in physical/environmental formulas.
- Example: 300.22

### temperature_C
- What: Temperature in Celsius.
- Why: Human-readable weather context.
- How: Prefer for dashboards and narrative reports.
- Example: 27.07

### humidity_pct
- What: Relative humidity percentage.
- Why: Affects atmospheric chemistry and comfort.
- How: Include as a covariate in AQI interpretation.
- Example: 47

### description
- What: Textual weather condition.
- Why: Quick qualitative context.
- How: Display in summaries.
- Example: haze

### source
- What: Weather data provider tag.
- Why: Provenance and reproducibility.
- How: Keep in all downstream tables.
- Example: live_OpenWeatherMap

## 12) weather_raw__UNITS_LEGEND.csv
Purpose: Unit/notes metadata for weather fields.

First row summary:
- column=wind_speed_mps
- unit=meters/second
- notes=from OpenWeatherMap wind.speed

### column
- What: Weather metric name.
- Why: Connects legend to data column.
- How: Use to auto-generate variable glossary.
- Example: wind_speed_mps

### unit
- What: Unit string.
- Why: Correct interpretation and plotting labels.
- How: Attach to chart/table headers.
- Example: meters/second

### notes
- What: Short data-source meaning.
- Why: Clarifies extraction origin.
- How: Include in methodology appendix.
- Example: from OpenWeatherMap wind.speed

---

## Practical usage examples (cross-file)

1. Join traffic to roads
- How: Match traffic edge_osmid with roads (u, v, key).
- Why: Needed to map speed/volume to each segment.

2. Build eco-routing cost
- How: Combine road length + traffic volume + speed + AQI/weather context.
- Why: Produces segment-level environmental cost.

3. Add green mitigation signal
- How: Aggregate vegetation area near road segments and merge into road table.
- Why: Represents potential local cooling/air-quality buffering effects.

4. Keep units explicit
- How: Always read corresponding UNITS_LEGEND files.
- Why: Prevents mixed-unit modeling errors.
