import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity

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
metrics = ["Wing Play", "Territory", "Crossing", "High Press", "Counters", "Low Block", "Long Balls", "Circulation", "GK Buildup"]

# Radar chart
fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=team_data[metrics].values.flatten(),
    theta=metrics,
    fill='toself',
    name=f"{selected_team} ({selected_season})"
))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True)
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

# Similar teams
st.subheader("Most Similar Teams")
team_vector = team_data[metrics].values.reshape(1, -1)
similarities = df_percentiles.copy()
similarities["Similarity"] = cosine_similarity(similarities[metrics].values, team_vector).flatten()
closest_teams = similarities.sort_values("Similarity", ascending=False).head(10)
st.dataframe(closest_teams[["Team", "Season", "League", "Similarity"]])
