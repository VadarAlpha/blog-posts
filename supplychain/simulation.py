import json
import osmnx as ox
import simpy
import requests_cache
import logging
from .network import (
    download_road_networks,
    download_interstate_network,
    combine_graphs,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set up requests caching
requests_cache.install_cache(
    "overpass_cache", expire_after=3600
)  # Cache expires after 1 hour


def build_supply_chain_from_config(config_file, combined_graph_filepath):
    # Load the configuration file
    with open(config_file, "r") as f:
        config = json.load(f)

    # Extract locations from the configuration
    locations = config["locations"]
    place_names = list(locations.keys())  # Extract place names

    # Print the extracted place names
    # Log the extracted place names
    logging.info("Place names: %s", place_names)

    # Download the interstate network
    interstates_graph = download_interstate_network(locations)
    # interstates_graph = download_interstate_network(north, south, east, west)

    # Download the road networks for each location
    road_networks = download_road_networks(locations)

    # Combine the road networks with the interstate network
    combined_graph = combine_graphs(
        road_networks + [interstates_graph], combined_graph_filepath
    )

    return combined_graph, road_networks


def simulate_supply_chain(G):
    env = simpy.Environment()

    # Example: Define a simple process for transporting goods
    def transport(env, start_node, end_node):
        # print(f"Starting transport from {start_node} to {end_node} at {env.now}")
        yield env.timeout(10)  # Simulate transport time
        # print(f"Arrived at {end_node} at {env.now}")

    # Add transport processes to the simulation
    for edge in G.edges:
        env.process(transport(env, edge[0], edge[1]))

    env.run(until=100)  # Run the simulation for 100 time units
