import folium
import osmnx as ox
import networkx as nx
import random
import logging
import json
from folium.plugins import MeasureControl

# logging.basicConfig(level=logging.ERROR)

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

def assign_supplier_types(locations, supplier_types):
    return {
        location: {
            "coordinates": coords,
            "supplier_type": "Valve Manufacturer" if location == "Wausau, WI, USA" else random.choice(supplier_types)
        }
        for location, coords in locations.items()
    }

def visualize_supply_chain(G, locations_with_suppliers, color_map, output_file='supplier_map.html'):
    # Initialize the Folium map centered around Wausau with the default OpenStreetMap tiles
    wausau_location = locations_with_suppliers["Wausau, WI, USA"]["coordinates"]
    m = folium.Map(location=wausau_location, zoom_start=4)

    # Add a marker for the manufacturing site (Wausau)
    folium.Marker(
        location=wausau_location,
        popup='Valve Manufacturer',
        icon=folium.Icon(color='black', icon='industry', prefix='fa')
    ).add_to(m)

    for location, details in locations_with_suppliers.items():
        if location == "Wausau, WI, USA":
            continue  # Skip the Wausau plant itself

        start_location = details["coordinates"]
        supplier_type = details["supplier_type"]
        color = color_map[supplier_type]

        # Add a marker for each supplier
        folium.Marker(
            location=start_location,
            popup=f'{supplier_type} ({location})',
            icon=folium.Icon(color=color, icon='warehouse', prefix='fa')
        ).add_to(m)

        # Find the nearest nodes in the graph to the start and end locations
        start_node = ox.distance.nearest_nodes(G, X=start_location[1], Y=start_location[0])
        end_node = ox.distance.nearest_nodes(G, X=wausau_location[1], Y=wausau_location[0])

        # Compute the shortest path
        try:
            shortest_path = nx.shortest_path(G, source=start_node, target=end_node, weight='length')
            logging.info(f"Shortest path for {location} to Wausau computed successfully")
            
            # Get the coordinates of the shortest path
            path_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in shortest_path]
            
            # Plot the route on the map with the assigned color
            folium.PolyLine(
                locations=path_coords,
                color=color,
                weight=4,
                opacity=0.7
            ).add_to(m)
        except nx.NetworkXNoPath:
            logging.warning(f"No path found from {location} to Wausau.")

    # Add a title to the map
    title_html = '''
                 <h3 align="center" style="font-size:20px"><b>Supplier Network Map</b></h3>
                 '''
    m.get_root().html.add_child(folium.Element(title_html))

    # Add a scale bar to the map using MeasureControl
    m.add_child(MeasureControl(primary_length_unit='kilometers'))

    # Save the map to an HTML file
    m.save(output_file)
    logging.info(f"Map saved to {output_file}")
