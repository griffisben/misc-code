import streamlit as st
import networkx as nx
import pandas as pd
import altair as alt
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

# Caching graph creation and data filtering
@st.cache_data
def create_graph(focal_position, min_players):
    G = nx.DiGraph(directed=True)
    short_path_data = all_changes[(all_changes['Primary position'] == focal_position) & (all_changes['# Players'] >= min_players)]
    
    for _, row in short_path_data.iterrows():
        G.add_edge(row['LeagueName_old'], row['LeagueName_new'], weight=row['# Players'] * 0.1)
    
    return G, short_path_data

G, short_path_data = create_graph(focal_position, min_players)

# Calculate shortest path
with st.spinner('Calculating shortest path and metrics...'):
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

        # Map visualization using Altair
        st.subheader("League Movement Map")
        path_league_info = league_info[league_info['League'].isin(shortest_path)]
        category10_colors = plt.cm.tab10.colors
        region_colors = {region: category10_colors[i % len(category10_colors)] for i, region in enumerate(path_league_info['Region'].unique())}

        country_data = path_league_info[['Country', 'Region']].drop_duplicates()
        
        background = alt.topo_feature("https://vega.github.io/vega-datasets/data/world-110m.json", "countries")
        world_map = alt.Chart(background).mark_geoshape(
            stroke='white',
            strokeWidth=0.5
        ).encode(
            color=alt.Color('Region:N', scale=alt.Scale(domain=list(region_colors.keys()), range=list(region_colors.values())), legend=alt.Legend(title="Region"))
        ).transform_lookup(
            lookup='id',
            from_=alt.LookupData(country_data, 'Country', ['Region'])
        ).project('naturalEarth1').properties(width=800, height=500)

        # Create league movement lines
        movement_data = pd.DataFrame(columns=['League_from', 'Country_from', 'League_to', 'Country_to'])
        for i in range(len(shortest_path) - 1):
            league_from = shortest_path[i]
            league_to = shortest_path[i + 1]
            
            country_from = path_league_info[path_league_info['League'] == league_from]['Country'].values[0]
            country_to = path_league_info[path_league_info['League'] == league_to]['Country'].values[0]
            
            movement_data = movement_data.append({
                'League_from': league_from,
                'Country_from': country_from,
                'League_to': league_to,
                'Country_to': country_to
            }, ignore_index=True)

        connections = alt.Chart(movement_data).mark_rule(opacity=0.7).encode(
            longitude='Country_from:N',
            latitude='Country_from:N',
            longitude2='Country_to:N',
            latitude2='Country_to:N',
            color=alt.Color('Region:N', scale=alt.Scale(domain=list(region_colors.keys()), range=list(region_colors.values())))
        )

        st.altair_chart(world_map + connections)

    except nx.NetworkXNoPath:
        st.error(f"No path found between {focal_old_league} and {focal_new_league}.")
