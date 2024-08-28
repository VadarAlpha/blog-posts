import sys
import os
import json
import logging

# Add the root directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.append(project_root)

from supplychain.simulation import build_supply_chain_from_config, simulate_supply_chain
from supplychain.visualization import visualize_supply_chain, assign_supplier_types


def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("Build supply chain from a configuration file")
    config_filepath = os.path.join(project_root, "notebooks", "sim_config.json")
    combined_graph_filepath = os.path.join(
        project_root, "combined_graph.graphml"
    )  # Path to the GraphML file
    visualization_filepath = os.path.join(project_root, "supply_chain_graph.html")

    # Check if config file exists
    if not os.path.exists(config_filepath):
        logging.error(f"Configuration file not found: {config_filepath}")
        sys.exit(1)

    # Load configuration
    with open(config_filepath, "r") as f:
        config = json.load(f)

    G, road_networks = build_supply_chain_from_config(
        config_filepath, combined_graph_filepath
    )

    logging.info("Simulate the supply chain")
    simulate_supply_chain(G)

    # Assign supplier types to locations
    locations_with_suppliers = assign_supplier_types(
        config["locations"], config["supplier_types"]
    )

    # Visualize the graph
    visualize_supply_chain(
        G, locations_with_suppliers, config["color_map"], visualization_filepath
    )


if __name__ == "__main__":
    main()
