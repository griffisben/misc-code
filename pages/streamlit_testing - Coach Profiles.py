import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def color_percentile(pc):
    if 1-pc <= 0.1:
        color = ('#01349b', '#d9e3f6')  # Elite
    elif 0.1 < 1-pc <= 0.35:
        color = ('#007f35', '#d9f0e3')  # Above Avg
    elif 0.35 < 1-pc <= 0.66:
        color = ('#9b6700', '#fff2d9')  # Avg
    else:
        color = ('#b60918', '#fddbde')  # Below Avg

    return f'background-color: {color[1]}'

def similar_teams(team, season, metrics):
    df_base = pd.read_csv("https://raw.githubusercontent.com/griffisben/misc-code/refs/heads/main/files/Coaching%20Profiles%20Percentiles.csv")
        
    focal_player = df_base.loc[(df_base.Team == team) & (df_base.Season==season)].iloc[0]
    focal_player_index = df_base.loc[(df_base.Team == team) & (df_base.Season==season)].index[0]
        
    # Select only the columns to compare
    df_compare = df_base[metrics]
    
    # Get the focal player's data
    focal_player_data = df_compare.loc[focal_player_index]
    
    # Calculate the Euclidean distance
    df_compare['distance'] = np.linalg.norm(df_compare - focal_player_data, axis=1)
    
    max_distance = df_compare['distance'].max()
    
    # Convert distances to similarity percentage
    df_compare['Similarity'] = (1 - df_compare['distance'] / max_distance) * 100
    print(max_distance)
    
    # Add additional columns to the result DataFrame
    additional_columns = ['Team','League','Season']
    df_compare = df_compare.join(df_base[additional_columns])
    
    # Sort by similarity percentage (descending order for highest similarity first)
    df_compare_sorted = df_compare.sort_values(by='Similarity', ascending=False)
    
    # Get the most similar players and include the additional columns
    similar_players = df_compare_sorted[additional_columns + ['distance','Similarity']]
    
    similar_players = similar_players.drop_duplicates(subset=['Team','distance'])
    
    similar_players.reset_index(drop=True,inplace=True)
    similar_players.reset_index(inplace=True)
    similar_players.rename(columns={'index':'Rank'},inplace=True)
    similar_players = similar_players.iloc[1:,:]
    similar_players.reset_index(drop=True,inplace=True)
    similar_players['lg_ssn'] = similar_players.League + " " + similar_players.Season

    return similar_players

# Load datasets
@st.cache_data
def load_data():
    df_percentiles = pd.read_csv("https://raw.githubusercontent.com/griffisben/misc-code/refs/heads/main/files/Coaching%20Profiles%20Percentiles.csv")
    df_raw = pd.read_csv("https://raw.githubusercontent.com/griffisben/misc-code/refs/heads/main/files/Coaching%20Profiles.csv")
    return df_percentiles, df_raw

df_percentiles, df_raw = load_data()

# Sidebar selections
st.sidebar.title("Team Playstyle Dashboard")
teams = df_percentiles["Team"].unique()
team = st.sidebar.selectbox("Select Team", teams)
seasons = df_percentiles[df_percentiles["Team"] == team]["Season"].unique()
season = st.sidebar.selectbox("Select Season", sorted(seasons, reverse=True))

# Filter data for selected team and season
team_data = df_percentiles[(df_percentiles["Team"] == team) & (df_percentiles["Season"] == season)]
league = team_data.League.values[0]
metrics = ['Counters','High Press','Low Block','Long Balls','GK Buildup','Circulation','Territory','Wing Play','Crossing',]

text_cs = []
text_inv_cs = []
for m in metrics:
    pc = 1 - team_data[m].values[0]
    if pc <= 0.1:
        color = ('#01349b', '#d9e3f6')  # Elite
    elif 0.1 < pc <= 0.35:
        color = ('#007f35', '#d9f0e3')  # Above Avg
    elif 0.35 < pc <= 0.66:
        color = ('#9b6700', '#fff2d9')  # Avg
    else:
        color = ('#b60918', '#fddbde')  # Below Avg
    text_cs.append(color[0])
    text_inv_cs.append(color[1])
    
# Radar chart using go.Barpolar
fig = go.Figure()
fig.add_trace(go.Barpolar(
    r=team_data[metrics].values.flatten(),
    theta=metrics,
    marker=dict(color=text_inv_cs, line_width=1.5, line_color=text_cs)
))
fig.update_layout(polar=dict(radialaxis=dict(showticklabels=False, visible=True, range=[0, 1])), showlegend=False)
st.subheader(f"Playstyle Profile: {team} ({league} {season})")
st.plotly_chart(fig)

# Style development over seasons
st.subheader(f"Style Development Over Seasons")
teams_seasonal = df_percentiles[df_percentiles["Team"] == team].sort_values("Season")
teams_seasonal['League Season'] = teams_seasonal['League'] + "<br>" + teams_seasonal['Season']
fig2 = px.line(
    teams_seasonal, x="League Season", y=metrics, markers=True,
    title=f"{team} Style Evolution"
)
fig2.update_layout(yaxis_range=[0,1])
st.plotly_chart(fig2)

# Similar teams using Euclidean distance
st.subheader("Most Similar Teams")
# team_vector = team_data[metrics].values.flatten()
# similarities = df_percentiles.copy()
# similarities["Similarity"] = similarities[metrics].apply(lambda row: -np.linalg.norm(row.values - team_vector), axis=1)
# closest_teams = similarities.sort_values("Similarity", ascending=False).head(10)
similar_teams = similar_teams(team, season, metrics)
st.dataframe(similar_teams[['Team','League','Season','Similarity']].head(20))


st.subheader("Team Finder")

gkbuildup_filter = st.slider('GK Buildup', 0.0, 1.0, (0.0,1.0), key='slider2')
circulation_filter = st.slider('Circulation', 0.0, 1.0, (0.0,1.0), key='slider3')
territory_filter = st.slider('Territory', 0.0, 1.0, (0.0,1.0), key='slider4')
wingplay_filter = st.slider('Wing Play', 0.0, 1.0, (0.0,1.0), key='slider5')
crossing_filter = st.slider('Crossing', 0.0, 1.0, (0.0,1.0), key='slider9')
counters_filter = st.slider('Counters', 0.0, 1.0, (0.0,1.0), key='slider6')
highpress_filter = st.slider('High Press', 0.0, 1.0, (0.0,1.0), key='slider7')
lowbloack_filter = st.slider('Low Block', 0.0, 1.0, (0.0,1.0), key='slider8')
longballs_filter = st.slider('Long Balls', 0.0, 1.0, (0.0,1.0), key='slider1')

filtered_teams_table = df_percentiles[
(df_percentiles['GK Buildup'].between(gkbuildup_filter[0],gkbuildup_filter[1])) & 
(df_percentiles['Circulation'].between(circulation_filter[0],circulation_filter[1])) & 
(df_percentiles['Territory'].between(territory_filter[0],territory_filter[1])) & 
(df_percentiles['Wing Play'].between(wingplay_filter[0],wingplay_filter[1])) & 
(df_percentiles['Crossing'].between(crossing_filter[0],crossing_filter[1])) & 
(df_percentiles['Counters'].between(counters_filter[0],counters_filter[1])) & 
(df_percentiles['High Press'].between(highpress_filter[0],highpress_filter[1])) & 
(df_percentiles['Low Block'].between(lowbloack_filter[0],lowbloack_filter[1])) & 
(df_percentiles['Long Balls'].between(longballs_filter[0],longballs_filter[1]))
]

filtered_teams_table = filtered_teams_table[['Team','League','Season','GK Buildup','Circulation','Territory','Wing Play','Crossing','Counters','High Press','Low Block','Long Balls',]]
st.dataframe(filtered_teams_table.style.applymap(color_percentile, subset=filtered_teams_table.columns[3:]))
