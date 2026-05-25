# Data Fusion Pipeline Documentation

## Overview
This pipeline fuses multiple geospatial and environmental datasets to create a comprehensive carbon emission analysis for Kolkata's road network. It integrates road infrastructure, building density, vegetation coverage, traffic patterns, weather conditions, and air quality data.

---

## Pipeline Workflow

### 1. **Road Network Download**
- **Source**: OpenStreetMap via OSMnx
- **Location**: Kolkata, India
- **Network Type**: Drivable roads only
- **Total Roads**: 90,915 road segments
- **CRS**: EPSG:3857 (Web Mercator in meters)

**Sample Road Data:**
```
Road ID: 52151691
Length: 10.43 meters
Geometry: LineString coordinates
```

---

### 2. **Building Dataset Download**
- **Source**: OpenStreetMap via OSMnx
- **Query**: All features tagged as "building"
- **Total Buildings**: 191,350 buildings
- **Processing**: 
  - For each road, creates a 50-meter buffer zone
  - Uses spatial indexing (R-tree) for efficient queries
  - Counts buildings intersecting with buffer zone

**Sample Building Density:**
```
Road 1 (osmid: 52151691):  5 buildings within 50m
Road 2 (osmid: 115880793): 15 buildings within 50m
```

**Algorithm Optimization:**
- **Old approach**: 90,915 roads × 191,350 buildings = ~17 billion checks ⚠️
- **New approach**: Spatial index pre-filters candidates, reduces to ~2 million actual checks ✅
- **Performance gain**: From hours to ~78 seconds

---

### 3. **Vegetation Dataset Download**
- **Source**: OpenStreetMap via OSMnx
- **Tags Queried**:
  - `landuse`: forest, grass, meadow
  - `natural`: wood, tree, grassland
  - `leisure`: park, garden
- **Total Polygons**: 898 vegetation areas
- **Processing**: Same 50-meter buffer approach with spatial indexing

**Sample Vegetation Scores:**
```
Road 1 (osmid: 52151691):  0 vegetation areas
Road 2 (osmid: 115880793): 0 vegetation areas
```

---

### 4. **Traffic Data Simulation**
- **Method**: Random generation (simulated data)
- **Vehicle Count**: Random integer between 20-200 vehicles
- **Average Speed**: Random integer between 20-60 km/h

**Sample Traffic Data:**
```
Road 1: 146 vehicles, avg speed 51 km/h
Road 2: 168 vehicles, avg speed 27 km/h
```

---

### 5. **Real-Time Weather Data**
- **Source**: OpenWeatherMap API
- **Location**: Kolkata
- **Data Retrieved**:
  - Wind speed (m/s)
  - Wind direction (degrees)

**Sample Weather Data:**
```
Wind Speed: 2.08 m/s
Wind Direction: Not shown in sample
```

---

### 6. **Air Quality Index (AQI)**
- **Source**: OpenWeatherMap Air Pollution API
- **Method**:
  1. Fetches PM2.5 concentration for Kolkata (22.5726°N, 88.3639°E)
  2. Converts PM2.5 to AQI using US EPA formula:
     - 0-12 µg/m³ → AQI 0-50 (Good)
     - 12.1-35.4 µg/m³ → AQI 51-100 (Moderate)
     - 35.5-55.4 µg/m³ → AQI 101-150 (Unhealthy for Sensitive Groups)
     - 55.5-150.4 µg/m³ → AQI 151-200 (Unhealthy)
     - 150.5+ µg/m³ → AQI 201+ (Very Unhealthy)

**Sample AQI:**
```
Current AQI: 176 (Unhealthy)
Applied to all roads uniformly
```

---

### 7. **Carbon Emission Calculation**

**Formula:**
```
carbon_cost = (length × 0.12 × vehicle_count) 
            + (building_density × 5) 
            - (vegetation_score × 3) 
            + (AQI × 0.2)
```

**Factors:**
- **Road Length × Vehicle Count**: Direct emissions from traffic
- **Emission Factor**: 0.12 kg CO₂ per meter per vehicle
- **Building Density**: +5 points per building (heat island effect, energy use)
- **Vegetation**: -3 points per vegetation area (carbon absorption)
- **AQI**: +0.2 per AQI unit (existing pollution context)

**Sample Calculations:**

**Road 1:**
```
Length: 10.43 m
Vehicles: 146
Building Density: 5
Vegetation: 0
AQI: 176

Calculation:
= (10.43 × 0.12 × 146) + (5 × 5) - (0 × 3) + (176 × 0.2)
= 182.73 + 25 + 0 + 35.2
= 242.93
```

**Road 2:**
```
Length: 155.72 m
Vehicles: 168
Building Density: 15
Vegetation: 0
AQI: 176

Calculation:
= (155.72 × 0.12 × 168) + (15 × 5) - (0 × 3) + (176 × 0.2)
= 3,138.60 + 75 + 0 + 35.2
= 3,249.60
```

---

## Output Files

### 1. **fused_roads.geojson**
- Geographic format (can be opened in QGIS, ArcGIS, etc.)
- Contains geometry and all attributes
- Size: ~90,915 features

### 2. **fused_roads.csv**
- Tabular format for analysis
- Contains all computed attributes

**Key Columns:**
- `osmid`: Unique road identifier
- `length`: Road segment length (meters)
- `building_density`: Buildings within 50m
- `vegetation_score`: Vegetation areas within 50m
- `vehicle_count`: Simulated traffic volume
- `avg_speed`: Simulated average speed (km/h)
- `wind_speed`: Current wind speed (m/s)
- `wind_direction`: Wind direction (degrees)
- `AQI`: Air Quality Index
- `carbon_cost`: Computed emission score

---

## Sample Final Dataset

| osmid     | length  | building_density | vegetation_score | vehicle_count | avg_speed | wind_speed | AQI | carbon_cost |
|-----------|---------|------------------|------------------|---------------|-----------|------------|-----|-------------|
| 52151691  | 10.43   | 5                | 0                | 146           | 51        | 2.08       | 176 | 242.94      |
| 115880793 | 155.72  | 15               | 0                | 168           | 27        | 2.08       | 176 | 3249.60     |

---

## Performance Metrics

- **Total Execution Time**: ~5 minutes
- **Road Network Download**: ~20 seconds
- **Building Download**: ~10 seconds
- **Building Density Calculation**: ~78 seconds
- **Vegetation Download**: ~98 seconds
- **Vegetation Score Calculation**: ~48 seconds
- **Traffic Simulation**: <1 second
- **Weather API**: <1 second
- **AQI API**: <1 second
- **Carbon Calculation**: <1 second
- **File Export**: ~3 seconds

---

## Key Optimizations Applied

### 1. **Spatial Indexing (R-tree)**
Before each intersection check, the spatial index quickly filters candidates based on bounding boxes:
- **Without indexing**: Check all 191,350 buildings for each of 90,915 roads
- **With indexing**: Check only ~10-50 nearby candidates per road

### 2. **Batch Processing**
Instead of updating DataFrame row-by-row (`edges.at[idx, col] = value`), values are collected in a list and assigned once:
```python
# Old (slow): edges.at[idx, "building_density"] = count
# New (fast): building_counts.append(count) → edges["building_density"] = building_counts
```

### 3. **API Integration**
Switched from unreliable OpenAQ API to OpenWeatherMap Air Pollution API, which provides consistent PM2.5 data that's converted to AQI.

---

## Use Cases

1. **Urban Planning**: Identify high-emission corridors for targeted interventions
2. **Green Infrastructure**: Prioritize roads with low vegetation for tree planting
3. **Traffic Management**: Correlate building density with emission levels
4. **Environmental Monitoring**: Track how AQI affects overall road-level emissions
5. **Policy Making**: Data-driven decisions for sustainable transportation

---

## Future Enhancements

1. **Real Traffic Data**: Replace simulated data with actual traffic APIs (Google Traffic, TomTom)
2. **Time Series**: Run pipeline hourly/daily to track temporal changes
3. **Route Optimization**: Use carbon_cost for eco-friendly route planning
4. **Predictive Modeling**: ML models to predict emissions based on features
5. **Interactive Visualization**: Web dashboard with maps and filters
6. **More Environmental Factors**: Temperature, humidity, noise pollution
7. **Multi-City Support**: Extend to other cities for comparative analysis

---

## Dependencies

```
osmnx>=1.9.1
geopandas>=0.14.0
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
shapely>=2.0.0
```

---

## API Keys Required

- **OpenWeatherMap API**: Free tier (1000 calls/day)
  - Weather data endpoint
  - Air pollution endpoint

---

## Credits

**Data Sources:**
- OpenStreetMap (roads, buildings, vegetation)
- OpenWeatherMap (weather & air quality)

**Author**: Pipeline implementation for Kolkata urban environmental analysis
**Date**: March 5, 2026
