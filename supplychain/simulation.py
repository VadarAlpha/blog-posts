import json
import simpy
import osmnx as ox
from .network import download_road_networks, download_interstate_network, create_multidigraph, connect_locations, combine_graphs

def build_supply_chain_from_config(config_file, combined_graph_filepath):
    # Load the configuration file
    with open(config_file, 'r') as f:
        config = json.load(f)

    # Extract locations from the configuration
    locations = config['locations']
    place_names = list(locations.keys())  # Extract place names

    # Print the extracted place names
    print("Place names:", place_names)

    # Geocode the place names to get their geometries
    gdf = ox.geocode_to_gdf(place_names)

    # Print the geocoded geometries
    print("Geocoded geometries:\n", gdf)

    # Determine bounding box for interstates
    north = gdf.geometry.bounds.maxy.max()
    south = gdf.geometry.bounds.miny.min()
    east = gdf.geometry.bounds.maxx.max()
    west = gdf.geometry.bounds.minx.min()

    # Print the bounding box coordinates
    print("Bounding box - North:", north, "South:", south, "East:", east, "West:", west)

    # Create the road network graph
    road_networks = ox.graph_from_bbox(north, south, east, west, network_type='drive')
    G = create_multidigraph(road_networks)

    return G, road_networks

def simulate_supply_chain(G):
    env = simpy.Environment()
    
    # Example: Define a simple process for transporting goods
    def transport(env, start_node, end_node):
        print(f'Starting transport from {start_node} to {end_node} at {env.now}')
        yield env.timeout(10)  # Simulate transport time
        print(f'Arrived at {end_node} at {env.now}')
    
    # Add transport processes to the simulation
    for edge in G.edges:
        env.process(transport(env, edge[0], edge[1]))
    
    env.run(until=100)  # Run the simulation for 100 time units
