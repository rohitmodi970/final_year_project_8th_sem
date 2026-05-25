"""
SUMO Integration Script
Loads your fused road data into SUMO for realistic traffic simulation
"""

import os
import random
import osmnx as ox
import xml.etree.ElementTree as ET
import pandas as pd
import geopandas as gpd

# ----------------------------
# STEP 1: Export OSM data
# ----------------------------
def export_osm_for_sumo():
    """Download and save road network in OSM format"""
    print("Downloading road network from OSM...")
    
    place = "Kolkata, India"
    # Download unsimplified graph (required for SUMO)
    G = ox.graph_from_place(place, network_type="drive", simplify=False)
    
    # Save as OSM XML
    ox.save_graph_xml(G, filepath="kolkata_roads.osm")
    print("✓ Saved: kolkata_roads.osm")
    
    return G

# ----------------------------
# STEP 2: Convert to SUMO network
# ----------------------------
def convert_to_sumo_network():
    """Convert OSM file to SUMO network format"""
    print("\nConverting to SUMO network...")
    print("Running: netconvert --osm-files kolkata_roads.osm -o kolkata.net.xml")
    
    # This requires SUMO to be installed
    os.system('netconvert --osm-files kolkata_roads.osm -o kolkata.net.xml --geometry.remove --ramps.guess --junctions.join --tls.guess-signals --tls.discard-simple')
    
    if os.path.exists("kolkata.net.xml"):
        print("✓ Created: kolkata.net.xml")
    else:
        print("❌ Error: SUMO netconvert failed. Make sure SUMO is installed.")
        print("Install: https://sumo.dlr.de/docs/Installing/index.html")

# ----------------------------
# STEP 3: Generate traffic routes using randomTrips
# ----------------------------
def generate_traffic_routes():
    """Generate random trips using SUMO's randomTrips tool"""
    print("\nGenerating random traffic trips...")
    
    # First create the vehicle type definitions
    vtype_xml = """<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    <vType id="car_petrol" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="50" emissionClass="HBEFA3/PC_G_EU4" color="1,0,0"/>
    <vType id="car_diesel" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="50" emissionClass="HBEFA3/PC_D_EU4" color="0,0,1"/>
    <vType id="car_electric" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="50" emissionClass="Energy/zero" color="0,1,0"/>
    <vType id="bus" accel="1.2" decel="4.0" sigma="0.5" length="12" minGap="3" maxSpeed="35" emissionClass="HBEFA3/Bus" color="1,1,0"/>
    <vType id="motorcycle" accel="3.0" decel="5.0" sigma="0.5" length="2.2" minGap="1.5" maxSpeed="60" emissionClass="HBEFA3/LDV" color="1,0,1"/>
    <vType id="truck" accel="1.0" decel="3.5" sigma="0.5" length="8" minGap="3" maxSpeed="40" emissionClass="HBEFA3/HDV" color="0.5,0.5,0.5"/>
</routes>
"""
    
    with open("vtypes.add.xml", "w") as f:
        f.write(vtype_xml)

    try:
        import sumolib
    except ImportError:
        sumolib = None

    if sumolib is not None:
        print("Building valid routes directly from the SUMO network...")
        try:
            net = sumolib.net.readNet("kolkata.net.xml")
            edges = [edge for edge in net.getEdges() if not getattr(edge, "isSpecial", lambda: False)()]
            edges_with_outgoing = [edge for edge in edges if edge.getOutgoing()]

            random.seed(42)
            vehicles = []
            route_id = 0

            for depart in range(0, 300, 2):
                if not edges_with_outgoing:
                    break

                start_edge = random.choice(edges_with_outgoing)
                route_edges = [start_edge]
                current_edge = start_edge

                for _ in range(6):
                    outgoing_edges = list(current_edge.getOutgoing().keys())
                    outgoing_edges = [edge for edge in outgoing_edges if edge not in route_edges]
                    if not outgoing_edges:
                        break
                    current_edge = random.choice(outgoing_edges)
                    route_edges.append(current_edge)

                if len(route_edges) < 2:
                    continue

                route_name = f"route_{route_id}"
                vehicle_type = random.choice(["car_petrol", "car_diesel", "car_electric", "bus", "motorcycle", "truck"])
                vehicles.append(
                    {
                        "route_name": route_name,
                        "vehicle_id": f"veh_{route_id}",
                        "vehicle_type": vehicle_type,
                        "depart": str(depart),
                        "edges": " ".join(edge.getID() for edge in route_edges),
                    }
                )
                route_id += 1

            root = ET.Element(
                "routes",
                {
                    "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                    "xsi:noNamespaceSchemaLocation": "http://sumo.dlr.de/xsd/routes_file.xsd",
                },
            )

            vtypes = ET.fromstring(vtype_xml)
            for child in list(vtypes):
                root.append(child)

            for vehicle in vehicles:
                ET.SubElement(
                    root,
                    "route",
                    id=vehicle["route_name"],
                    edges=vehicle["edges"],
                )
                ET.SubElement(
                    root,
                    "vehicle",
                    id=vehicle["vehicle_id"],
                    type=vehicle["vehicle_type"],
                    depart=vehicle["depart"],
                    route=vehicle["route_name"],
                )

            ET.ElementTree(root).write("traffic.rou.xml", encoding="UTF-8", xml_declaration=True)

            if vehicles:
                print(f"✓ Created: traffic.rou.xml ({len(vehicles)} vehicles)")
                return

            print("⚠ Warning: Could not build route walk from SUMO network; falling back to randomTrips.py")
        except Exception as exc:
            print(f"⚠ Warning: Direct route generation failed: {exc}")
            print("Falling back to randomTrips.py")

    # Generate random trips using SUMO's randomTrips tool as fallback
    print("Running randomTrips.py to generate traffic...")
    err_log = "randomTrips.err"
    # Add more diagnostic flags and relaxed success rate to help networks where many trips fail validation
    cmd = (
        'python "C:\\Program Files (x86)\\Eclipse\\Sumo\\tools\\randomTrips.py" '
        '-n kolkata.net.xml -o trips.trips.xml -b 0 -e 300 -p 1 '
        '--fringe-factor 5 --vehicle-class passenger -s 42 --validate '
        f'--error-log {err_log} --min-success-rate 0.05 --min-distance 50'
    )
    os.system(cmd)

    # If randomTrips produced an error log, show the first few lines for debugging
    if os.path.exists(err_log):
        print(f"\nrandomTrips wrote error log: {err_log}. Showing first 20 lines:")
        try:
            with open(err_log, "r", encoding="utf-8", errors="ignore") as rf:
                for i, line in enumerate(rf):
                    if i >= 20:
                        break
                    print(line.rstrip())
        except Exception:
            print("Could not read randomTrips error log.")

    # Convert trips to routes
    print("Converting trips to routes...")
    os.system('duarouter -n kolkata.net.xml -t trips.trips.xml -o traffic.rou.xml --ignore-errors --additional-files vtypes.add.xml')

    if os.path.exists("traffic.rou.xml"):
        print("✓ Created: traffic.rou.xml")
    else:
        print("⚠ Warning: Could not create routes, will use basic traffic")
        # Fallback to basic route file
        with open("traffic.rou.xml", "w") as f:
            f.write(vtype_xml)

# ----------------------------
# STEP 4: Create SUMO config
# ----------------------------
def create_sumo_config():
    """Create SUMO configuration file"""
    print("\nCreating SUMO configuration...")
    
    config_xml = """<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    
    <input>
        <net-file value="kolkata.net.xml"/>
        <route-files value="traffic.rou.xml"/>
    </input>
    
    <time>
        <begin value="0"/>
        <end value="300"/>
        <step-length value="1"/>
    </time>
    
    <output>
        <emission-output value="emissions.xml"/>
        <summary-output value="summary.xml"/>
        <tripinfo-output value="tripinfo.xml"/>
        <fcd-output value="fcd.xml"/>
    </output>
    
    <processing>
        <collision.action value="warn"/>
        <time-to-teleport value="300"/>
    </processing>
    
    <report>
        <verbose value="true"/>
        <no-step-log value="false"/>
    </report>
    
</configuration>
"""
    
    with open("kolkata.sumocfg", "w") as f:
        f.write(config_xml)
    
    print("✓ Created: kolkata.sumocfg")

# ----------------------------
# STEP 5: Run SUMO simulation
# ----------------------------
def run_sumo_simulation():
    """Run SUMO with TraCI interface to collect real-time data"""
    print("\n" + "="*60)
    print("RUNNING SUMO SIMULATION")
    print("="*60)
    
    try:
        import traci
    except ImportError:
        print("❌ TraCI not found. Install with: pip install traci eclipse-sumo")
        return
    
    sumo_binary = "sumo-gui"  # Use "sumo" for command-line only
    sumo_cmd = [sumo_binary, "-c", "kolkata.sumocfg"]
    
    print("\nStarting SUMO...")
    print("Close SUMO window to finish simulation\n")
    
    traci.start(sumo_cmd)
    
    # Data collection
    edge_data = {}
    step = 0
    
    try:
        while traci.simulation.getMinExpectedNumber() > 0 and step < 300:
            traci.simulationStep()
            step += 1
            
            # Collect data every 60 seconds
            if step % 60 == 0:
                for edge_id in traci.edge.getIDList():
                    if edge_id not in edge_data:
                        edge_data[edge_id] = {
                            'vehicle_count': [],
                            'avg_speed': [],
                            'co2_emission': [],
                            'occupancy': []
                        }

                    edge_data[edge_id]['vehicle_count'].append(
                        traci.edge.getLastStepVehicleNumber(edge_id)
                    )
                    edge_data[edge_id]['avg_speed'].append(
                        traci.edge.getLastStepMeanSpeed(edge_id) * 3.6  # m/s to km/h
                    )
                    edge_data[edge_id]['co2_emission'].append(
                        traci.edge.getCO2Emission(edge_id)
                    )
                    edge_data[edge_id]['occupancy'].append(
                        traci.edge.getLastStepOccupancy(edge_id)
                    )
            
            print(f"Simulation time: {step}s / 300s ({step/3:.1f}%)")
    
    except Exception as e:
        print(f"\n⚠ Simulation ended early: {e}")
        print(f"Collected data for {step} seconds out of 300")
    
    finally:
        traci.close()
    
    print("\n✓ Simulation complete!")
    print(f"Total steps simulated: {step}s")
    
    # Process and save data
    print("\nProcessing simulation data...")
    
    results = []
    for edge_id, data in edge_data.items():
        results.append({
            'edge_id': edge_id,
            'avg_vehicle_count': sum(data['vehicle_count']) / len(data['vehicle_count']),
            'avg_speed_kmh': sum(data['avg_speed']) / len(data['avg_speed']),
            'total_co2_mg': sum(data['co2_emission']),
            'avg_occupancy': sum(data['occupancy']) / len(data['occupancy'])
        })
    
    df = pd.DataFrame(
        results,
        columns=['edge_id', 'avg_vehicle_count', 'avg_speed_kmh', 'total_co2_mg', 'avg_occupancy']
    )
    df.to_csv("sumo_traffic_data.csv", index=False)
    
    print(f"✓ Saved simulation results: sumo_traffic_data.csv")
    print(f"   Records: {len(df)}")

    if df.empty:
        print("⚠ No simulation records were collected (empty results).")
        print("This often means SUMO ran with zero vehicles. Check randomTrips.err for trip validation failures.")
        return

    total_co2_g = df['total_co2_mg'].sum() / 1000 if 'total_co2_mg' in df.columns else 0.0
    print(f"   Total CO2: {total_co2_g:.2f} g")

# ----------------------------
# STEP 6: Merge SUMO data with fused dataset
# ----------------------------
def merge_with_fused_data():
    """Merge SUMO simulation results with your fused dataset"""
    print("\n" + "="*60)
    print("MERGING SUMO DATA WITH FUSED DATASET")
    print("="*60)
    
    # Load fused dataset
    fused = gpd.read_file("fused_roads.geojson")
    print(f"\nLoaded fused dataset: {len(fused)} roads")
    
    # Load SUMO results
    if not os.path.exists("sumo_traffic_data.csv"):
        print("❌ SUMO data not found. Run simulation first.")
        return
    
    sumo_data = pd.read_csv("sumo_traffic_data.csv")
    print(f"Loaded SUMO data: {len(sumo_data)} edges")

    if sumo_data.empty:
        print("⚠ SUMO data is empty. Saving fused dataset without SUMO merge.")
        fused.to_file("fused_roads_with_sumo.geojson", driver="GeoJSON")
        fused.to_csv("fused_roads_with_sumo.csv", index=False)
        print("✓ Saved enhanced dataset:")
        print("  - fused_roads_with_sumo.geojson")
        print("  - fused_roads_with_sumo.csv")
        return
    
    # Merge on edge ID (you may need to map OSM IDs)
    # Note: This is simplified - you'll need to match edge IDs properly
    fused['osmid_str'] = fused['osmid'].astype(str)
    sumo_data['osmid_str'] = sumo_data['edge_id'].str.extract(r'(-?\d+)')[0]
    
    merged = fused.merge(
        sumo_data[['osmid_str', 'avg_vehicle_count', 'avg_speed_kmh', 'total_co2_mg']], 
        on='osmid_str', 
        how='left',
        suffixes=('_old', '_sumo')
    )
    
    print(f"\nMerged dataset: {len(merged)} roads")
    print(f"Matched with SUMO: {merged['avg_vehicle_count'].notna().sum()} roads")
    
    # Recalculate carbon cost with real SUMO data
    merged['carbon_cost_sumo'] = (
        merged['length'] * 0.12 * merged['avg_vehicle_count'].fillna(merged['vehicle_count']) 
        + merged['building_density'] * 5 
        - merged['vegetation_score'] * 3 
        + merged['AQI'] * 0.2
    )
    
    # Save enhanced dataset
    merged.to_file("fused_roads_with_sumo.geojson", driver="GeoJSON")
    merged.to_csv("fused_roads_with_sumo.csv", index=False)
    
    print("\n✓ Saved enhanced dataset:")
    print("  - fused_roads_with_sumo.geojson")
    print("  - fused_roads_with_sumo.csv")
    
    # Statistics (safe: handle missing columns)
    print("\nComparison (Simulated vs SUMO):")

    def mean_for(df, candidates):
        for c in candidates:
            if c in df.columns:
                try:
                    return df[c].mean()
                except Exception:
                    return None
        return None

    veh_old = mean_for(merged, ['vehicle_count'])
    veh_sumo = mean_for(merged, ['avg_vehicle_count'])
    speed_old = mean_for(merged, ['avg_speed', 'avg_speed_kmh', 'speed_kmh', 'speed'])
    speed_sumo = mean_for(merged, ['avg_speed_kmh', 'avg_speed', 'speed_kmh', 'speed'])
    carbon_old = mean_for(merged, ['carbon_cost'])
    carbon_sumo = mean_for(merged, ['carbon_cost_sumo'])

    def fmt(x, unit=""):
        if x is None or (isinstance(x, float) and pd.isna(x)):
            return "n/a"
        return f"{x:.1f}{unit}"

    print(f"  Avg vehicle count: {fmt(veh_old)} → {fmt(veh_sumo)}")
    print(f"  Avg speed: {fmt(speed_old, '')} → {fmt(speed_sumo, ' km/h')}")
    print(f"  Avg carbon cost: {fmt(carbon_old)} → {fmt(carbon_sumo)}")

# ----------------------------
# Main execution
# ----------------------------
if __name__ == "__main__":
    print("="*60)
    print("SUMO INTEGRATION PIPELINE")
    print("="*60)
    print("\nThis script will:")
    print("1. Export OSM road network")
    print("2. Convert to SUMO network format")
    print("3. Generate realistic traffic patterns")
    print("4. Run SUMO simulation")
    print("5. Merge results with your fused dataset")
    print("\nRequirements:")
    print("- SUMO installed (https://sumo.dlr.de)")
    print("- Python packages: traci, eclipse-sumo")
    print("\n" + "="*60)
    
    choice = input("\nRun full pipeline? (y/n): ").lower()
    
    if choice == 'y':
        # Step 1: Export OSM
        export_osm_for_sumo()
        
        # Step 2: Convert to SUMO
        convert_to_sumo_network()
        
        # Step 3: Generate routes
        generate_traffic_routes()
        
        # Step 4: Create config
        create_sumo_config()
        
        # Step 5: Run simulation
        run_sim = input("\nRun SUMO simulation now? (y/n): ").lower()
        if run_sim == 'y':
            run_sumo_simulation()
            
            # Step 6: Merge data
            merge_with_fused_data()
        else:
            print("\nTo run simulation later:")
            print("  sumo-gui -c kolkata.sumocfg")
    else:
        print("\nManual execution:")
        print("1. export_osm_for_sumo()")
        print("2. convert_to_sumo_network()")
        print("3. generate_traffic_routes()")
        print("4. create_sumo_config()")
        print("5. run_sumo_simulation()")
        print("6. merge_with_fused_data()")
