import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

with st.sidebar:
    league = st.selectbox('League', avail_data.Competition.unique().tolist())
    season = st.selectbox('Season', sorted(avail_data[avail_data.Competition==league].Season.tolist(),reverse=True))
    mins = st.number_input('Minimum Time On Ground %', 0, 100, 60, 1)

# Load the dataset
df = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/AFL-Radars/refs/heads/main/Player-Data/{league}/{season}.csv")
df = df.dropna(subset=['player_position']).reset_index(drop=True)
df['possessions'] = df['contested_possessions']+df['uncontested_possessions']
if league == 'AFL':
    df['kick_efficiency'] = df['effective_kicks']/df['kicks']*100
    df['handball_efficiency'] = (df['effective_disposals']-df['effective_kicks'])/df['handballs']*100
    df['hitout_efficiency'] = df['hitouts_to_advantage']/df['hitouts']*100
df['pct_contested_poss'] = df['contested_possessions']/(df['possessions'])*100
df['pct_marks_contested'] = df['contested_marks']/(df['marks'])*100
df['points'] = (df['goals']*6)+(df['behinds'])
df['points_per_shot'] = df['points']/df['shots_at_goal']
df['points_per_shot'] = [0 if df['shots_at_goal'][i]==0 else df['points'][i]/df['shots_at_goal'][i] for i in range(len(df))]

df = df[df['PctOfSeason']>=mins/100].reset_index(drop=True)

# Define position-to-stat mapping with exact column names
position_stats = {
    "Full Forwards": ["goals", "marks_inside_fifty", "contested_marks", "score_involvements", "shots_at_goal", "goal_assists", "pressure_acts"],
    "Key Forwards": ["marks_inside_fifty", "contested_marks", "score_involvements", "goals", "metres_gained"],
    "Small Forwards": ["score_involvements", "goal_assists", "inside_fifties", "pressure_acts", "tackles_inside_fifty", "shots_at_goal"],
    "Midfielders": ["disposals", "clearances", "contested_possessions", "inside_fifties", "metres_gained", "stoppage_clearances", "centre_clearances", "tackles", "effective_kicks"],
    "Defensive Midfielders": ["tackles", "intercepts", "pressure_acts", "contest_def_losses", "ground_ball_gets"],
    "Half-Backs": ["rebounds", "effective_kicks", "intercepts", "marks_on_lead", "pressure_acts", "metres_gained"],
    "Full-Backs": ["intercepts", "one_percenters", "contest_def_one_on_ones", "spoils", "rebounds", "tackles"],
    "Rucks": ["hitouts_to_advantage", "clearances", "ruck_contests", "contested_possessions", "hitout_efficiency"]
}

# Sidebar: User selects position
st.sidebar.header("Customize Position Weightings")
position_group = st.sidebar.selectbox("Select Position", list(position_stats.keys()))

# Sidebar: User-defined weightings for selected position
weights = {}
for stat in position_stats[position_group]:
    weights[stat] = st.sidebar.slider(f"Weight for {stat}", 0.0, 1.0, 0.5, 0.05)

# Normalize relevant stats
scaler = MinMaxScaler()
df_scaled = df.copy()
for pos, stats in position_stats.items():
    df_scaled[stats] = scaler.fit_transform(df_scaled[stats])

# Compute custom rating
def compute_custom_rating(row, stat_weights):
    return sum(row[stat] * stat_weights.get(stat, 0) for stat in stat_weights)

df_scaled["custom_rating"] = df_scaled.apply(lambda row: compute_custom_rating(row, weights), axis=1)

# Select Best 22 based on highest rating per position
best_22 = {}
for pos in position_stats.keys():
    best_22[pos] = df_scaled.sort_values("custom_rating", ascending=False).head(1)[["player", "custom_rating"]].values.tolist()

# Display Best 22 team
st.subheader("🏉 Best 22 Team")
for pos, player in best_22.items():
    if player:
        st.write(f"**{pos}:** {player[0][0]} (Rating: {round(player[0][1], 2)})")

# Manual Override: User selects a player to replace an auto-selected one
st.sidebar.header("Manual Player Selection")
override_position = st.sidebar.selectbox("Select Position to Override", list(best_22.keys()))
override_player = st.sidebar.selectbox("Select New Player", df_scaled["player"].unique())

if st.sidebar.button("Replace Player"):
    best_22[override_position] = [[override_player, df_scaled[df_scaled["player"] == override_player]["custom_rating"].values[0]]]

# Display updated Best 22 team
st.subheader("🔄 Updated Best 22 Team")
for pos, player in best_22.items():
    if player:
        st.write(f"**{pos}:** {player[0][0]} (Rating: {round(player[0][1], 2)})")
