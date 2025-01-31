import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Load the dataset
DATA_URL = "https://raw.githubusercontent.com/griffisben/AFL-Radars/refs/heads/main/Player-Data/AFL/2024.csv"
df = pd.read_csv(DATA_URL)

# Define position-to-stat mapping
position_stats = {
    "Full Forwards": ["Goals", "Marks Inside 50", "Contested Marks", "Score Involvements", "Shots at Goal", "Goal Assists", "Pressure Acts"],
    "Key Forwards": ["Marks Inside 50", "Contested Marks", "Score Involvements", "Goals", "Metres Gained"],
    "Small Forwards": ["Score Involvements", "Goal Assists", "Inside 50s", "Pressure Acts", "Tackles Inside 50", "Shots at Goal"],
    "Midfielders": ["Disposals", "Clearances", "Contested Possessions", "Inside 50s", "Metres Gained", "Stoppage Clearances", "Centre Clearances", "Tackles", "Effective Kicks"],
    "Defensive Midfielders": ["Tackles", "Intercepts", "Pressure Acts", "Contest Def Losses", "Ground Ball Gets"],
    "Half-Backs": ["Rebound 50s", "Effective Kicks", "Intercepts", "Marks on Lead", "Pressure Acts", "Metres Gained"],
    "Full-Backs": ["Intercepts", "One Percenters", "Contest Def One-on-Ones", "Spoils", "Rebound 50s", "Tackles"],
    "Rucks": ["Hitouts to Advantage", "Clearances", "Ruck Contests", "Contested Possessions", "Hitout Efficiency"]
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

df_scaled["Custom Rating"] = df_scaled.apply(lambda row: compute_custom_rating(row, weights), axis=1)

# Filter players by position (you may need a 'Position' column in your dataset)
df_filtered = df_scaled  # Adjust this if you have a position column

# Select Best 22 based on highest rating per position
best_22 = {}
for pos in position_stats.keys():
    best_22[pos] = df_filtered.sort_values("Custom Rating", ascending=False).head(1)[["Player", "Custom Rating"]].values.tolist()

# Display Best 22 team
st.subheader("🏉 Best 22 Team")
for pos, player in best_22.items():
    if player:
        st.write(f"**{pos}:** {player[0][0]} (Rating: {round(player[0][1], 2)})")

# Manual Override: User selects a player to replace an auto-selected one
st.sidebar.header("Manual Player Selection")
override_position = st.sidebar.selectbox("Select Position to Override", list(best_22.keys()))
override_player = st.sidebar.selectbox("Select New Player", df_scaled["Player"].unique())

if st.sidebar.button("Replace Player"):
    best_22[override_position] = [[override_player, df_scaled[df_scaled["Player"] == override_player]["Custom Rating"].values[0]]]

# Display updated Best 22 team
st.subheader("🔄 Updated Best 22 Team")
for pos, player in best_22.items():
    if player:
        st.write(f"**{pos}:** {player[0][0]} (Rating: {round(player[0][1], 2)})")