import networkx as nx
import pandas as pd
import streamlit as st
import pycountry
import altair as alt

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("https://raw.githubusercontent.com/griffisben/misc-code/refs/heads/main/files/Wyscout%20League%20Movement%20Changes.csv")

def load_league_info():
    return pd.read_csv("https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/refs/heads/main/league_info_lookup.csv")

# Country numeric code lookup
country_numeric_code_lookup = {country.name: country.numeric for country in pycountry.countries}

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

# Load the data
all_changes = load_data()
league_info = load_league_info()

# Merge league info into the changes DataFrame based on the League column
merged_data = pd.merge(all_changes, league_info[['League', 'Country']], left_on='LeagueName_old', right_on='League', how='left')
merged_data = pd.merge(merged_data, league_info[['League', 'Country']], left_on='LeagueName_new', right_on='League', how='left', suffixes=('_old', '_new'))

# Create Graph
G = nx.DiGraph(directed=True)
short_path_data = merged_data[(merged_data['Primary position'] == focal_position) & (merged_data['# Players'] >= min_players)]

# Add edges with weights based on '# Players'
for _, row in short_path_data.iterrows():
    old_league = row['LeagueName_old']
    new_league = row['LeagueName_new']
    num_players = row['# Players']
    
    # Use weight as inverse of # Players to prioritize high-movement paths
    G.add_edge(old_league, new_league, weight=num_players * 0.1)

# Get the shortest path
try:
    shortest_path = nx.shortest_path(G, source=focal_old_league, target=focal_new_league, weight='# Players')
    all_shortest_paths = nx.all_shortest_paths(G, source=focal_old_league, target=focal_new_league, weight='# Players')

    st.subheader("Results")
    st.write(f"Shortest path from {focal_old_league} to {focal_new_league} for position {focal_position}:\n")
    st.write(" -> ".join(shortest_path))
    
    # Calculate metric values along the shortest path
    metric_values = []
    num_players_list = []
    
    for i in range(len(shortest_path) - 1):
        league_old = shortest_path[i]
        league_new = shortest_path[i + 1]
        
        # Filter `all_changes` DataFrame for each pair of leagues and `Primary position`
        filtered_df = all_changes[
            (all_changes['LeagueName_old'] == league_old) &
            (all_changes['LeagueName_new'] == league_new) &
            (all_changes['Primary position'] == focal_position)
        ]
        
        # Get the metric value (handling the case where no value is found)
        metric_value = filtered_df[f"{focal_metric} Change"].values
        if metric_value.size > 0:
            metric_values.extend(metric_value)
        else:
            metric_values.append(None)
        
        num_players_list.append(filtered_df['# Players'].values[0])
    
    # Calculate the final metric value after all transitions
    foc_num = start_metric
    for adj in metric_values:
        foc_num *= (1 + adj) if adj is not None else 1
    
    # Display results
    st.write(f"Metric values along the path: {metric_values}")
    st.write(f"Number of players moving along this path: {num_players_list}")
    
    st.write(f"Change: {round((foc_num - start_metric) / start_metric * 100, 2)}%")
    st.write(f"Starting value: {round(start_metric, 2)}")
    st.write(f"Final value: {round(foc_num, 2)}")
    st.write(f"Season total (at {mins} min): {round(foc_num * (mins / 90), 2)}")
    
except nx.NetworkXNoPath:
    st.error(f"No path found between {focal_old_league} and {focal_new_league}")

# Map Plotting: Display the countries moved between
# Extract the countries involved in the transition path (based on the shortest path)
country_path = []
for i in range(len(shortest_path) - 1):
    league_old = shortest_path[i]
    league_new = shortest_path[i + 1]
    
    # Get the country for the old and new league
    country_old = merged_data[merged_data['LeagueName_old'] == league_old]['Country_old'].values[0]
    country_new = merged_data[merged_data['LeagueName_new'] == league_new]['Country_new'].values[0]
    
    country_path.append(country_old)
    country_path.append(country_new)

# Remove duplicates (to avoid repeating the same country)
country_path = list(set(country_path))

# Map Data
countries_avail = pd.DataFrame({
    'Country': country_path,
    'ISO_Numeric_Code': [country_numeric_code_lookup.get(country, None) for country in country_path]
})

# Remove countries with no valid ISO code
countries_avail = countries_avail.dropna(subset=['ISO_Numeric_Code'])

# Load country shapes for the map
source_countries = alt.topo_feature('https://cdn.jsdelivr.net/npm/world-atlas@2/world/110m.json', 'countries')

# Base map
basemap = alt.Chart(source_countries).mark_geoshape(fill='#fbf9f4', stroke='#4a2e19')

# Create map with color based on countries involved in league transitions
map = alt.Chart(source_countries).mark_geoshape(stroke='#4a2e19').encode(
    color=alt.Color('ISO_Numeric_Code:O', scale=alt.Scale(scheme="goldorange")),
    tooltip=[
        "Country:N",
        "# of Leagues:N"
    ]
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(countries_avail, 'ISO_Numeric_Code', ['Country'])
).properties(
    title="Countries Involved in League Movements"
).project(
    type="naturalEarth1"
)

# Add lines to represent league transitions between countries
lines = []
for i in range(len(shortest_path) - 1):
    league_old = shortest_path[i]
    league_new = shortest_path[i + 1]
    
    # Get coordinates for the old and new country (for simplicity, I'll use the country capital as the point)
    # Ideally, you would use a more precise method to get the location (e.g., capitals or centroids)
    country_old = merged_data[merged_data['LeagueName_old'] == league_old]['Country_old'].values[0]
    country_new = merged_data[merged_data['LeagueName_new'] == league_new]['Country_new'].values[0]
    
    # Assuming you have a method to get coordinates for countries (for simplicity, these are placeholders)
    country_coords_old = (0, 0)  # Replace with real coordinates lookup
    country_coords_new = (1, 1)  # Replace with real coordinates lookup
    
    lines.append({
        'source': country_coords_old,
        'target': country_coords_new
    })

# Display map with transition lines
st.altair_chart(basemap + map, use_container_width=True)
