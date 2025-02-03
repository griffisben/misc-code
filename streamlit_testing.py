import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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
    marker=dict(color=text_cs, opacity=0.7)
))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False)
st.subheader(f"Playstyle Profile: {team} ({season})")
st.plotly_chart(fig)

# Style development over seasons
st.subheader(f"Style Development Over Seasons")
teams_seasonal = df_percentiles[df_percentiles["Team"] == team].sort_values("Season")
fig2 = px.line(
    teams_seasonal, x="Season", y=metrics, markers=True,
    title=f"{team} Style Evolution"
)
st.plotly_chart(fig2)

# Similar teams using Euclidean distance
st.subheader("Most Similar Teams")
# team_vector = team_data[metrics].values.flatten()
# similarities = df_percentiles.copy()
# similarities["Similarity"] = similarities[metrics].apply(lambda row: -np.linalg.norm(row.values - team_vector), axis=1)
# closest_teams = similarities.sort_values("Similarity", ascending=False).head(10)
similar_teams = similar_teams(team, season, metrics)
st.dataframe(similar_teams[['Team','League','Season','Similarity']].head(20))
