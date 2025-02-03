import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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
selected_team = st.sidebar.selectbox("Select Team", teams)
seasons = df_percentiles[df_percentiles["Team"] == selected_team]["Season"].unique()
selected_season = st.sidebar.selectbox("Select Season", sorted(seasons, reverse=True))

# Filter data for selected team and season
team_data = df_percentiles[(df_percentiles["Team"] == selected_team) & (df_percentiles["Season"] == selected_season)]
# metrics = ['Long Balls','GK Buildup','Circulation','Territory','Wing Play','Crossing','Counters','High Press','Low Block']
metrics = ['Counters','High Press','Low Block','Long Balls','GK Buildup','Circulation','Territory','Wing Play','Crossing',]

# Radar chart using go.Barpolar
fig = go.Figure()
fig.add_trace(go.Barpolar(
    r=team_data[metrics].values.flatten(),
    theta=metrics,
    marker=dict(color="blue", opacity=0.7)
))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False)
st.subheader(f"Playstyle Profile: {selected_team} ({selected_season})")
st.plotly_chart(fig)

# Style development over seasons
st.subheader(f"Style Development Over Seasons")
teams_seasonal = df_percentiles[df_percentiles["Team"] == selected_team].sort_values("Season")
fig2 = px.line(
    teams_seasonal, x="Season", y=metrics, markers=True,
    title=f"{selected_team} Style Evolution"
)
st.plotly_chart(fig2)

# Similar teams using Euclidean distance
st.subheader("Most Similar Teams")
team_vector = team_data[metrics]
df_compare = df_percentiles[metrics]
df_compare['distance'] = np.linalg.norm(df_compare - team_vector, axis=1)
max_distance = df_compare['distance'].max()
df_compare['Similarity'] = (1 - df_compare['distance'] / max_distance) * 100
additional_columns = ['Team','League','Season']
df_compare = df_compare.join(df_base[additional_columns])
closest_teams = df_compare.sort_values("Similarity", ascending=False).head(10)
st.dataframe(closest_teams[["Team", "Season", "League", "Similarity"]])
