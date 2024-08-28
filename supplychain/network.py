import networkx as nx
import osmnx as ox
import os
import time
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def download_graph_with_retries(query_func, *args, retries=3, delay=60, **kwargs):
    for attempt in range(retries):
        try:
            return query_func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error downloading graph: {e}")
            if attempt < retries - 1:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise


def get_bounding_box(locations):
    min_lat, min_lon, max_lat, max_lon = (
        float("inf"),
        float("inf"),
        float("-inf"),
        float("-inf"),
    )
    for lat, lon in locations.values():
        min_lat, min_lon = min(min_lat, lat), min(min_lon, lon)
        max_lat, max_lon = max(max_lat, lat), max(max_lon, lon)

    logging.info("Bounding box coordinates extracted successfully")
    logging.info(
        f"Bounding box coordinates - min_lat: {min_lat}, min_lon: {min_lon}, max_lat: {max_lat}, max_lon: {max_lon}"
    )
    return min_lat, min_lon, max_lat, max_lon


def download_road_networks(locations):
    graphs = []
    for place in locations.keys():
        filename = f"{place.replace(', ', '_').replace(' ', '_').lower()}.graphml"
        logging.info(f"Processing place: {place}")
        if os.path.exists(filename):
            logging.info(f"Loading graph from file: {filename}")
            graph = ox.load_graphml(filename)
        else:
            logging.info(f"Downloading and building graph for: {place}")
            graph = download_graph_with_retries(
                ox.graph_from_place, place, network_type="drive"
            )
            logging.info(f"Saving graph to file: {filename}")
            ox.save_graphml(graph, filename)
        graphs.append(graph)
        logging.info(f"Graph for {place} processed successfully")
    return graphs


def download_interstate_network(locations):
    min_lat, min_lon, max_lat, max_lon = get_bounding_box(locations)
    filename = "interstates.graphml"
    if os.path.exists(filename):
        logging.info(f"Loading graph from file: {filename}")
        interstates_graph = ox.load_graphml(filename)
    else:
        logging.info("Downloading interstates within the bounding box")
        interstates_graph = download_graph_with_retries(
            ox.graph_from_bbox,
            north=max_lat,
            south=min_lat,
            east=max_lon,
            west=min_lon,
            custom_filter='["highway"~"motorway"]',
        )
        logging.info(f"Saving graph to file: {filename}")
        ox.save_graphml(interstates_graph, filename)
    logging.info("Interstates graph processed successfully")
    return interstates_graph


def combine_graphs(graphs, combined_graph_filepath):
    # Combine all the graphs into one
    combined_graph = nx.compose_all(graphs)
    logging.info("Combined graph created successfully")

    # Save the combined graph to a file
    ox.save_graphml(combined_graph, filepath=combined_graph_filepath)
    logging.info("Combined graph saved successfully")

    return combined_graph


# Main workflow
if __name__ == "__main__":
    # Load configuration from sim_config.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, os.pardir))

    config_filepath = os.path.join(project_root, "notebooks", "sim_config.json")
    with open(config_filepath, "r") as f:
        config = json.load(f)

    locations = config["locations"]

    # Download road networks for the specified locations
    road_networks = download_road_networks(locations)

    # Download the interstate network within the bounding box
    interstates_graph = download_interstate_network(locations)

    # Combine the road networks into a single graph
    combined_graph = nx.compose_all(road_networks)

    # Combine the single graph with the interstate network
    combined_graph = nx.compose(combined_graph, interstates_graph)

    # Save the combined graph
    combined_graph_filepath = "combined_graph.graphml"
    ox.save_graphml(combined_graph, combined_graph_filepath)
    logging.info("Combined graph saved successfully")
