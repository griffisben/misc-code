import streamlit as st
import networkx as nx
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("https://raw.githubusercontent.com/griffisben/misc-code/refs/heads/main/files/Wyscout%20League%20Movement%20Changes.csv")

def load_league_info():
    return pd.read_csv("https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/refs/heads/main/league_info_lookup.csv")

all_changes = load_data()
league_info = load_league_info()

# Streamlit UI
st.title("Soccer League Movement Analysis")

# Sidebar Inputs
st.sidebar.header("User Inputs")
focal_old_league = st.sidebar.selectbox("Select starting league:", sorted(all_changes['LeagueName_old'].unique()))
focal_new_league = st.sidebar.selectbox("Select target league:", sorted(all_changes['LeagueName_new'].unique()))
focal_position = st.sidebar.selectbox("Select position:", sorted(all_changes['Primary position'].unique()))
focal_metric = st.sidebar.selectbox("Select metric:", [col.replace(" Change", "") for col in all_changes.columns if "Change" in col])
min_players = st.sidebar.slider("Minimum players per transition:", 1, 10, 3)
start_metric = st.sidebar.number_input("Starting metric value:", value=1.00, step=0.01)
mins = st.sidebar.number_input("Minutes played per season:", value=2700, step=1)

# Create Graph
G = nx.DiGraph(directed=True)
short_path_data = all_changes[(all_changes['Primary position'] == focal_position) & (all_changes['# Players'] >= min_players)]

for _, row in short_path_data.iterrows():
    G.add_edge(row['LeagueName_old'], row['LeagueName_new'], weight=row['# Players'] * 0.1)

# Calculate shortest path
try:
    shortest_path = nx.shortest_path(G, source=focal_old_league, target=focal_new_league, weight='# Players')
    metric_values, num_players_list = [], []

    for i in range(len(shortest_path) - 1):
        filtered_df = all_changes[(all_changes['LeagueName_old'] == shortest_path[i]) &
                                  (all_changes['LeagueName_new'] == shortest_path[i + 1]) &
                                  (all_changes['Primary position'] == focal_position)]
        metric_value = filtered_df[f"{focal_metric} Change"].values
        
        if metric_value.size > 0:
            metric_values.extend(metric_value)
            num_players_list.append(filtered_df['# Players'].values[0])
        else:
            metric_values.append(None)
            num_players_list.append(0)

    foc_num = start_metric
    for adj in metric_values:
        foc_num *= (1 + adj) if adj is not None else 1
    
    # Display results
    st.subheader("Results")
    st.write(f"**Shortest Path:** {' → '.join(shortest_path)}")
    st.write(f"**Metric Change:** {round((foc_num - start_metric) / start_metric * 100, 2)}%")
    st.write(f"**Starting Value:** {round(start_metric, 2)}")
    st.write(f"**Final Value:** {round(foc_num, 2)}")
    st.write(f"**Season Total ({mins} min):** {round(foc_num * (mins / 90), 2)}")

    # Map visualization
    st.subheader("League Movement Map")
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    
    path_league_info = league_info[league_info['League'].isin(shortest_path)]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    world.boundary.plot(ax=ax, linewidth=1, color='gray')
    
    region_colors = {
        region: color for region, color in zip(path_league_info['Region'].unique(), plt.cm.Set1.colors)
    }
    
    for _, row in path_league_info.iterrows():
        ax.text(row['Country'], row['League'], row['League'], fontsize=8, ha='right')
        ax.scatter(row['Country'], row['League'], color=region_colors.get(row['Region'], 'black'), s=100, label=row['Region'])
    
    plt.legend(loc='lower left', bbox_to_anchor=(0, -0.3), ncol=3, fontsize=8)
    st.pyplot(fig)

except nx.NetworkXNoPath:
    st.error(f"No path found between {focal_old_league} and {focal_new_league}.")
