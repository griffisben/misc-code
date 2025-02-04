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

# Sidebar Selection Mode
st.sidebar.header("Match or Individual Player Season")
mode = st.sidebar.radio("Select View", ["Match View", "Player Season View"])

# Sidebar Filters
st.sidebar.header("Filters")
team = st.sidebar.selectbox("Select Team", sorted(df["Team"].unique()))

if mode == "Match View":
    # Filter matches based on team
    team_matches = df[df["Team"] == team]["Match"].unique()
    match = st.sidebar.selectbox("Select Match", team_matches)
    
    # Filter players based on team and match
    team_match_players = df[(df["Team"] == team) & (df["Match"] == match)]["playerName"].unique().tolist()
    team_match_players.remove('0')
    team_match_players = sorted(team_match_players)
    players = st.sidebar.multiselect("Select Players", team_match_players)
    
    filtered_df = df[(df["Team"] == team) & (df["Match"] == match)]
    if players:
        filtered_df = filtered_df[filtered_df["playerName"].isin(players)]
else:
    # Player Season View
    team_players = df[df["Team"] == team]["playerName"].unique().tolist()
    team_players.remove('0')
    team_players = sorted(team_players)
    player = st.sidebar.selectbox("Select Player", team_players)
    filtered_df = df[(df["Team"] == team) & (df["playerName"] == player)]

# Event Type Filters
event_types = st.sidebar.multiselect("Select Event Types", ["Pass", "Shot", "Tackle", "Interception", "Dribble", "Aerial", "Missed Tackle", "Ball Recovery", "Blocked Pass"])
include_set_pieces = st.sidebar.checkbox("Include Set Piece Passes/Shots", value=True)
pass_types = st.sidebar.multiselect("Select Pass Types", ["Complete", "Incomplete", "Shot Assist"])

# Apply Event Type Filters
if event_types:
    type_map = {"Pass": 1, "Shot": [13, 14, 15, 16], "Dribble": 3, "Tackle": 7, "Interception": 8, "Aerial": 44, "Ball Recovery": 49, "Blocked Pass": 74, "Missed Tackle": [45, 83]}
    selected_ids = [type_map[event] for event in event_types]
    selected_ids = [x if isinstance(x, list) else [x] for x in selected_ids]
    selected_ids = [item for sublist in selected_ids for item in sublist]
    filtered_df = filtered_df[filtered_df["typeId"].isin(selected_ids)]

if not include_set_pieces:
    filtered_df = filtered_df[~((filtered_df["typeId"] == 1) & (filtered_df[["FK", "GK", "ThrowIn", "Corner", "KickOff"]].sum(axis=1) > 0))]
    filtered_df = filtered_df[~((filtered_df["typeId"].between(13, 16)) & (filtered_df["Corner"] == 1))]

if pass_types:
    if "Complete" not in pass_types:
        filtered_df = filtered_df[~((filtered_df["typeId"] == 1) & (filtered_df["outcome"] == 1) & (filtered_df["assist"] != 1) & (filtered_df["keyPass"] != 1))]
    if "Incomplete" not in pass_types:
        filtered_df = filtered_df[~((filtered_df["typeId"] == 1) & (filtered_df["outcome"] == 0))]
    if "Shot Assist" not in pass_types:
        filtered_df = filtered_df[~((filtered_df["typeId"] == 1) & ((filtered_df["assist"] == 1) | (filtered_df["keyPass"] == 1)))]

# Draw Pitch
pitch = Pitch(pitch_type='opta', pitch_color='#fbf9f4', line_color='#4A2E19', line_zorder=0, half=False)
fig, axs = pitch.grid(endnote_height=0.045, endnote_space=0, figheight=12,
                      title_height=0.045, title_space=0,
                      axis=False,
                      grid_height=0.86)
fig.set_facecolor('#fbf9f4')

# Define colors for event types
cmp_color = '#4c94f6'
inc_color = 'silver'
key_color = '#f6ba00'
won_color = 'tab:blue'
lost_color = 'tab:orange'

# Plot Events
for _, row in filtered_df.iterrows():
    if row['typeId'] == 1:  # Passes (Comet style)
        pass_color = cmp_color if row['outcome'] == 1 else inc_color
        if row.get('assist', 0) == 1 or row.get('keyPass', 0) == 1:
            pass_color = key_color
        pitch.lines(row['x'], row['y'], row['endX'], row['endY'],
                    comet=True, alpha=0.3, lw=5, color=pass_color, ax=axs['pitch'])
        pitch.scatter(row['endX'], row['endY'], s=45, ec='k', lw=.3, c=pass_color, zorder=2, ax=axs['pitch'])
    elif row['typeId'] in [13, 14, 15]:  # Shots
        pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='lightgrey', ec='k', s=(500 * row.get('xG', 0.05))+30)
    elif row['typeId'] in [16]:  # Goals
        pitch.scatter(row['x'], row['y'], ax=axs['pitch'], marker='*', color='gold', ec='k', s=(1100 * row.get('xG', 0.05))+75, zorder=3)
    elif row['typeId'] == 7:  # Tackles
        pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='tab:blue', ec='k', marker='D', s=65)
    elif row['typeId'] in [45, 83]:  # Missed Tackles
        pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='tab:orange', ec='k', marker='D', s=65)
    elif row['typeId'] == 8:  # Interceptions
        pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='tab:blue', ec='k', marker='s', s=65)
    elif row['typeId'] == 3:  # Dribbles
        dribble_color = won_color if row['outcome'] == 1 else lost_color
        pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color=dribble_color, ec='k', marker='>', s=65)
    elif row['typeId'] == 44:  # Aerials
        aerial_color = won_color if row['outcome'] == 1 else lost_color
        pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color=aerial_color, ec='k', marker='^', s=65)
    elif row['typeId'] == 49:  # Ball Recoveries
        pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='k', marker='x', s=65)
    elif row['typeId'] == 74:  # Blocked Passes
        pitch.scatter(row['x'], row['y'], ax=axs['pitch'], color='silver', ec='k', marker='<', s=65)

st.pyplot(fig)

filtered_df[['playerName','typeId','timeMin','timeSec','outcome','xT','xG','xGA','Sequence','Gamestate']]
