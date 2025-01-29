import streamlit as st
import networkx as nx
import pandas as pd
import altair as alt
import pycountry

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("https://raw.githubusercontent.com/griffisben/misc-code/refs/heads/main/files/Wyscout%20League%20Movement%20Changes.csv")

def load_league_info():
    return pd.read_csv("https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/refs/heads/main/league_info_lookup.csv")

# Country numeric code lookup
country_numeric_code_lookup = {country.name: country.numeric for country in pycountry.countries}

all_changes = load_data()
league_info = load_league_info()

# Merge league info into the changes DataFrame based on the League column
merged_data = pd.merge(all_changes, league_info[['League', 'Country']], left_on='LeagueName_old', right_on='League', how='left')
merged_data = pd.merge(merged_data, league_info[['League', 'Country']], left_on='LeagueName_new', right_on='League', how='left', suffixes=('_old', '_new'))

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
short_path_data = merged_data[(merged_data['Primary position'] == focal_position) & (merged_data['# Players'] >= min_players)]

for _, row in short_path_data.iterrows():
    G.add_edge(row['LeagueName_old'], row['LeagueName_new'], weight=row['# Players'] * 0.1)

# Calculate shortest path
try:
    shortest_path = nx.shortest_path(G, source=focal_old_league, target=focal_new_league, weight='# Players')
    metric_values, num_players_list = [], []

    for i in range(len(shortest_path) - 1):
        filtered_df = merged_data[(merged_data['LeagueName_old'] == shortest_path[i]) &
                                  (merged_data['LeagueName_new'] == shortest_path[i + 1]) &
                                  (merged_data['Primary position'] == focal_position)]
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

    # Plotting the movement of leagues on the map using Altair
    st.subheader("League Movement Map")

    # Get the country data for the leagues involved in the movement
    path_league_info = league_info[league_info['League'].isin(shortest_path)]
    path_league_info['ISO_Numeric_Code'] = path_league_info['Country'].map(country_numeric_code_lookup)

    # Fetch the world map data
    source_countries = alt.topo_feature('https://raw.githubusercontent.com/vega/vega-datasets/master/data/world-110m.json', 'countries')

    # Create the basemap
    basemap = alt.Chart(source_countries).mark_geoshape(fill='#fbf9f4', stroke='#4a2e19')

    # Create the map with color based on ISO Numeric Code
    map = alt.Chart(source_countries).mark_geoshape(stroke='#4a2e19').encode(
        color=alt.Color('ISO_Numeric_Code:Q', scale=alt.Scale(scheme="goldorange")),
        tooltip=[
            "Country:N",
            "ISO_Numeric_Code:Q"
        ],
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(path_league_info, 'ISO_Numeric_Code', ['Country'])
    ).properties(
        title="League Movement By Country"
    ).project(
        type="naturalEarth1"
    )

    # Display the map
    st.altair_chart(basemap + map, use_container_width=True)

except nx.NetworkXNoPath:
    st.error(f"No path found between {focal_old_league} and {focal_new_league}.")
