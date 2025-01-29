import streamlit as st
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from pyvis.network import Network

# Step 1: Load the CSV file from the URL
st.title("Soccer League Movement Analysis")
url = "https://raw.githubusercontent.com/griffisben/misc-code/refs/heads/main/files/Wyscout%20League%20Movement%20Changes.csv"
all_changes = pd.read_csv(url)
    
# Step 2: Get user inputs
focal_old_league = st.sidebar.selectbox('Select the starting league', all_changes['LeagueName_old'].unique())
focal_new_league = st.sidebar.selectbox('Select the target league', all_changes['LeagueName_new'].unique())
focal_position = st.sidebar.selectbox('Select the position', all_changes['Primary position'].unique())
focal_metric = st.sidebar.selectbox("Select metric:", [col.replace(" Change", "") for col in all_changes.columns if "Change" in col])
min_players = st.sidebar.slider('Minimum number of players', 1, 10, 4)
start_metric = st.sidebar.number_input('Starting metric value', value=2.4, step=0.01)
    
# Create graph
G = nx.DiGraph(directed=True)

short_path_data = all_changes[(all_changes['Primary position'] == focal_position) & (all_changes['# Players'] >= min_players)]

# Add edges to graph
for _, row in short_path_data.iterrows():
    old_league = row['LeagueName_old']
    new_league = row['LeagueName_new']
    num_players = row['# Players']
    G.add_edge(old_league, new_league, weight=num_players * 0.1)

# Get shortest path
try:
    shortest_path = nx.shortest_path(G, source=focal_old_league, target=focal_new_league, weight='# Players')
    all_shortest_paths = nx.all_shortest_paths(G, source=focal_old_league, target=focal_new_league, weight='# Players')

    # Calculate metrics along the path
    metric_values = []
    num_players_list = []
    for i in range(len(shortest_path) - 1):
        league_old = shortest_path[i]
        league_new = shortest_path[i + 1]
        
        filtered_df = all_changes[
            (all_changes['LeagueName_old'] == league_old) &
            (all_changes['LeagueName_new'] == league_new) &
            (all_changes['Primary position'] == focal_position)
        ]
        
        metric_value = filtered_df[f"{focal_metric} Change"].values
        
        if metric_value.size > 0:
            metric_values.extend(metric_value)
        else:
            metric_values.append(None)

        num_players_list += [filtered_df['# Players'].values[0]]

    # Compute the change
    foc_num = start_metric
    for adj in metric_values:
        foc_num = foc_num * (1 + adj)

    # Display results
    st.subheader(f"Analysis from {focal_old_league} to {focal_new_league}")
    st.write(f"Shortest path for a {focal_position}, with at least {min_players} players for each move:")
    st.write(" -> ".join(shortest_path))
    st.write(f"Change: {round((foc_num - start_metric) / start_metric * 100, 2)}%")
    st.write(f"{round(start_metric, 2)}: {focal_old_league} {focal_metric}")
    st.write(f"{round(foc_num, 2)}: Possible {focal_new_league} {focal_metric}")

except nx.NetworkXNoPath:
    st.write(f"No path found between {focal_old_league} and {focal_new_league}")

