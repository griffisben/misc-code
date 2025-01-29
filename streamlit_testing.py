import streamlit as st
import networkx as nx
import pandas as pd
import altair as alt

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

    # Map visualization using Altair
    st.subheader("League Movement Map")
    path_league_info = league_info[league_info['League'].isin(shortest_path)]
    # region_colors = {region: color for region, color in zip(path_league_info['Region'].unique(), alt.Color('Region:N', scale=alt.Scale(domain=path_league_info['Region'].unique(), range=alt.utils.schemes['category10'])))}
    region_colors = {region: color for region, color in zip(path_league_info['Region'].unique(), alt.Chart('category10').get_color_range())}

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
    movement_data = path_league_info[['League', 'Country']].merge(path_league_info[['League', 'Country']], how='left', left_on='League', right_on='League', suffixes=('_from', '_to'))
    movement_data = movement_data.dropna()
    
    connections = alt.Chart(movement_data).mark_rule(opacity=0.7).encode(
        latitude='Country_from:N',
        longitude='Country_to:N',
        color=alt.Color('Region:N', scale=alt.Scale(domain=list(region_colors.keys()), range=list(region_colors.values())))
    )
    
    st.altair_chart(world_map + connections)

except nx.NetworkXNoPath:
    st.error(f"No path found between {focal_old_league} and {focal_new_league}.")
