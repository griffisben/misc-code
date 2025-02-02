import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# Load Data
@st.cache_data
def load_data():
    url = "https://github.com/griffisben/misc-code/raw/refs/heads/main/Events/Danish%201.%20Division%20as%20of%2012-12-24%20with%20All%20Info.parquet"
    df = pd.read_parquet(url)
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("Filters")
team = st.sidebar.selectbox("Select Team", df["Team"].unique())

# Filter matches based on team
team_matches = df[df["Team"] == team]["Match"].unique()
match = st.sidebar.selectbox("Select Match", team_matches)

# Filter players based on team and match
team_match_players = df[(df["Team"] == team) & (df["Match"] == match)]["playerName"].unique()
players = st.sidebar.multiselect("Select Players", team_match_players)

event_types = st.sidebar.multiselect("Select Event Types", ["Pass", "Shot", "Tackle", "Interception", "Dribble"])

# Filter Data
filtered_df = df[(df["Team"] == team) & (df["Match"] == match)]
if players:
    filtered_df = filtered_df[filtered_df["playerName"].isin(players)]
if event_types:
    type_map = {"Pass": 1, "Shot": [13, 14, 15, 16], "Tackle": 7, "Interception": 8, "Dribble": 3}
    selected_ids = [type_map[event] for event in event_types]
    selected_ids = [x if isinstance(x, list) else [x] for x in selected_ids]
    selected_ids = [item for sublist in selected_ids for item in sublist]
    filtered_df = filtered_df[filtered_df["typeId"].isin(selected_ids)]

# Draw Pitch
pitch = Pitch(pitch_type='opta', pitch_color='#fbf9f4', line_color='#4A2E19', line_zorder=2, half=False)
fig, axs = pitch.grid(endnote_height=0.045, endnote_space=0, figheight=12,
                      title_height=0.045, title_space=0,
                      axis=False,
                      grid_height=0.86)
fig.set_facecolor('#fbf9f4')

# Define colors for event types
cmp_color = 'blue'

# Plot Events
for _, row in filtered_df.iterrows():
    if row['typeId'] == 1:  # Passes (Comet style)
        pitch.lines(row['x'], row['y'], row['endX'], row['endY'],
                    comet=True, alpha=0.3, lw=4, color=cmp_color, ax=axs['pitch'])
        pitch.scatter(row['endX'], row['endY'], s=30, c=cmp_color, zorder=2, ax=axs['pitch'])
    elif row['typeId'] in [13, 14, 15, 16]:  # Shots
        pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='red', s=100 * row.get('xG', 0.05))
    elif row['typeId'] == 7:  # Tackles
        pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='green', marker='x')
    elif row['typeId'] == 8:  # Interceptions
        pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='purple', marker='s')
    elif row['typeId'] == 3:  # Dribbles
        pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='orange', marker='D')

st.pyplot(fig)
