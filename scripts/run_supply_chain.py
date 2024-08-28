import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure the script is running from the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from supplychain.simulation import build_supply_chain_from_config, simulate_supply_chain
from supplychain.visualization import visualize_supply_chain

logging.info("Build supply chain from a configuration file")
config_filepath = os.path.join(project_root, 'sim_config.json')
combined_graph_filepath = os.path.join(project_root, 'combined_graph.graphml')  # Path to the GraphML file
G, road_networks = build_supply_chain_from_config(config_filepath, combined_graph_filepath)

logging.info("Simulate the supply chain")
simulate_supply_chain(G)

logging.info("Visualize the supply chain")
visualize_supply_chain(G)
