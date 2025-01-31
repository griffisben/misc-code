import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import zscore

avail_data = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/AFL-Radars/refs/heads/main/AvailableData.csv")
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

# Define Streamlit layout
st.title("AFL Metric Weighting & Ranking System")

# Create tabs
ranking_system, other = st.tabs(["Metric Weighting & Ranking", "Other"])

# Metric Weighting & Ranking Tab
with ranking_system:
    st.header("Select Metrics & Assign Weights")
    
    pos = st.multiselect('Positions to Include (leave blank for all)', ['Full-Forward','Forward Pocket','Centre Half-Forward','Half-Forward','Wing','Centre','Ruck-Rover','Rover','Ruck','Half-Back','Centre Half-Back','Back-Pocket','Full-Back'])
    if pos == []:
        pos = None
    pattern = r'(^|, )(' + '|'.join(pos) + r')($|, )'
    df = df[df['player_position'].str.contains(pattern, regex=True)]
    
    # Let user select metrics
    vars = df.columns[9:].tolist()
    vars.remove('80sr')
    metrics = st.multiselect("Choose metrics to include:", vars)
    
    if metrics:
        # User assigns weights
        weights = {}
        for metric in metrics:
            weights[metric] = st.slider(f"Weight for {metric}", 0.0, 1.0, 0.5, 0.05)
        
        # Normalize data using z-score
        df_filtered = df.copy()
        df_filtered[metrics] = df_filtered[metrics].apply(zscore, nan_policy='omit')
        
        # Compute weighted z-score ranking
        df_filtered["custom_score"] = df_filtered[metrics].apply(lambda row: sum(row[metric] * weights[metric] for metric in metrics), axis=1)
        
        # Display results
        st.subheader("Ranked Players")
        st.dataframe(df_filtered.sort_values("custom_score", ascending=False)[["player_name","player_team", "player_position", "custom_score"] + metrics])
    else:
        st.warning("Please select at least one metric.")
