import networkx as nx
import osmnx as ox
import os
import time
import logging

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

def download_road_networks(locations):
    graphs = []
    for place in locations:
        filename = f"{place.replace(', ', '_').replace(' ', '_').lower()}.graphml"
        logging.info(f"Processing place: {place}")
        if os.path.exists(filename):
            logging.info(f"Loading graph from file: {filename}")
            graph = ox.load_graphml(filename)
        else:
            logging.info(f"Downloading and building graph for: {place}")
            graph = download_graph_with_retries(ox.graph_from_place, place, network_type='drive')
            logging.info(f"Saving graph to file: {filename}")
            ox.save_graphml(graph, filename)
        graphs.append(graph)
        logging.info(f"Graph for {place} processed successfully")
    return graphs

def download_interstate_network(north, south, east, west):
    filename = 'interstates.graphml'
    if os.path.exists(filename):
        logging.info(f"Loading graph from file: {filename}")
        interstates_graph = ox.load_graphml(filename)
    else:
        logging.info("Downloading interstates within the bounding box")
        interstates_graph = download_graph_with_retries(
            ox.graph_from_bbox, north=north, south=south, east=east, west=west, custom_filter='["highway"~"motorway"]'
        )
        logging.info(f"Saving graph to file: {filename}")
        ox.save_graphml(interstates_graph, filename)
    logging.info("Interstates graph processed successfully")
    return interstates_graph

def create_multidigraph(road_networks):
    G = nx.MultiDiGraph()
    for graph in road_networks:
        G = nx.compose(G, graph)
    return G

def connect_locations(G, interstates_graph):
    G = nx.compose(G, interstates_graph)
    return G

def combine_graphs(graphs, combined_graph_filepath):
    combined_graph = nx.compose_all(graphs)
    logging.info("Combined graph created successfully")
    ox.save_graphml(combined_graph, filepath=combined_graph_filepath)
    logging.info("Combined graph saved successfully")
    return combined_graph
