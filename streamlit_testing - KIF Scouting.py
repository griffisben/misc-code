import seaborn as sns
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from statistics import mean
from math import pi
import streamlit as st
sns.set_style("white")
import warnings
warnings.filterwarnings('ignore')
import matplotlib
from PIL import Image
from highlight_text import fig_text
import urllib.request
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
import plotly.express as px
import plotly.figure_factory as ff
from plotly.graph_objects import Layout
from vega_datasets import data
import pycountry
import altair as alt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA

colorscales = px.colors.named_colorscales()
colorscales2 = [f"{cc}_r" for cc in colorscales]
colorscales += colorscales2

country_numeric_code_lookup = {country.name: country.numeric for country in pycountry.countries}

@st.cache_data(ttl=60*15)

def NormalizeData(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data)) * 100

def prep_similarity_df(geo_input, region, tiers, time_frame):
    sim_lg_lookup = pd.read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup.csv')

    if geo_input == 'Region':
        if region==[]:
            sim_lg_lookup = sim_lg_lookup.sort_values(by=['Season'],ascending=False)
        else:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Region.isin(region)].sort_values(by=['Season'],ascending=False)
        if tiers != []:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Tier.isin(tiers)]
    if geo_input == 'Country':
        if region==[]:
            sim_lg_lookup = sim_lg_lookup.sort_values(by=['Season'],ascending=False)
        else:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Country.isin(region)].sort_values(by=['Season'],ascending=False)
        if tiers != []:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Tier.isin(tiers)]
    if geo_input == 'Continent':
        if region==[]:
            sim_lg_lookup = sim_lg_lookup.sort_values(by=['Season'],ascending=False)
        else:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Continent.isin(region)].sort_values(by=['Season'],ascending=False)
        if tiers != []:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Tier.isin(tiers)]
    if geo_input == 'League':
        if region==[]:
            sim_lg_lookup = sim_lg_lookup.sort_values(by=['Season'],ascending=False)
        else:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.League.isin(region)].sort_values(by=['Season'],ascending=False)

    sim_lg_lookup_recent = sim_lg_lookup.drop_duplicates(subset=['League','Country'])
    sim_lg_lookup_recent2 = sim_lg_lookup.drop(sim_lg_lookup_recent.index)
    sim_lg_lookup_recent2 = sim_lg_lookup_recent2.drop_duplicates(subset=['League','Country'])
    sim_lg_lookup_recent_last2 = pd.concat([sim_lg_lookup_recent,sim_lg_lookup_recent2],ignore_index=True)
    sim_lg_lookup_recent.reset_index(drop=True,inplace=True)
    sim_lg_lookup_recent2.reset_index(drop=True,inplace=True)
    
    if time_frame == 'Current Season':
        sim_lg_lookup = sim_lg_lookup_recent
    if time_frame == 'Prior Season':
        sim_lg_lookup = sim_lg_lookup_recent2
    if time_frame == 'Current & Prior Seasons':
        sim_lg_lookup = sim_lg_lookup_recent_last2
    
    dfs = []
    char_replacements = str.maketrans({" ": "%20", "ü": "u", "ó": "o", "ö": "o", "ã": "a", "ç": "c"})
    for _, row in sim_lg_lookup.iterrows():
        full_league_name = f"{row['League']} {row['Season']}"
        formatted_name = full_league_name.translate(char_replacements)
        url = f'https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Main%20App/{formatted_name}.csv'

        try:
            df = pd.read_csv(url)
            df['League'] = full_league_name
            df = df.dropna(subset=['Position', 'Team within selected timeframe']).reset_index(drop=True)
            clean_df = load_league_data(df, full_league_name)
            dfs.append(clean_df)
        except:
            st.write(f'Error: {full_league_name}')
    full_similarity_df_raw = pd.concat(dfs, ignore_index=True)
    
    replace_dict = {
        'LAMF': 'LWF',
        'RAMF': 'RWF',
        'LCB3': 'LCB',
        'RCB3': 'RCB',
        'LCB5': 'LCB',
        'RCB5': 'RCB',
        'LB5': 'LB',
        'RB5': 'RB',
        'RCMF3': 'RCMF',
        'LCMF3': 'LCMF',
    }
    
    full_similarity_df_raw['Main Position'] = full_similarity_df_raw['Main Position'].replace(replace_dict)
    return full_similarity_df_raw

def prep_similarity_df_filters(geo_input, region, tiers, time_frame):
    sim_lg_lookup = pd.read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup.csv')

    if geo_input == 'Region':
        if region==[]:
            sim_lg_lookup = sim_lg_lookup.sort_values(by=['Season'],ascending=False)
        else:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Region.isin(region)].sort_values(by=['Season'],ascending=False)
        if tiers != []:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Tier.isin(tiers)]
        sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Season.isin(time_frame)]
    if geo_input == 'Country':
        if region==[]:
            sim_lg_lookup = sim_lg_lookup.sort_values(by=['Season'],ascending=False)
        else:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Country.isin(region)].sort_values(by=['Season'],ascending=False)
        if tiers != []:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Tier.isin(tiers)]
        sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Season.isin(time_frame)]
    if geo_input == 'Continent':
        if region==[]:
            sim_lg_lookup = sim_lg_lookup.sort_values(by=['Season'],ascending=False)
        else:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Continent.isin(region)].sort_values(by=['Season'],ascending=False)
        if tiers != []:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Tier.isin(tiers)]
        sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.Season.isin(time_frame)]
    if geo_input == 'League':
        sim_lg_lookup['League-Season'] = sim_lg_lookup.League + " " + sim_lg_lookup.Season
        if region==[]:
            sim_lg_lookup = sim_lg_lookup.sort_values(by=['Season'],ascending=False)
        else:
            sim_lg_lookup = sim_lg_lookup[sim_lg_lookup.League.isin(region)].sort_values(by=['Season'],ascending=False)
        sim_lg_lookup = sim_lg_lookup[sim_lg_lookup['League-Season'].isin(time_frame)]        
    
    dfs = []
    char_replacements = str.maketrans({" ": "%20", "ü": "u", "ó": "o", "ö": "o", "ã": "a", "ç": "c"})
    for _, row in sim_lg_lookup.iterrows():
        full_league_name = f"{row['League']} {row['Season']}"
        formatted_name = full_league_name.translate(char_replacements)
        url = f'https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Main%20App/{formatted_name}.csv'

        try:
            df = pd.read_csv(url)
            df['League'] = full_league_name
            df = df.dropna(subset=['Position', 'Team within selected timeframe']).reset_index(drop=True)
            clean_df = load_league_data(df, full_league_name)
            dfs.append(clean_df)
        except:
            st.write(f'Error: {full_league_name}')
    full_similarity_df_raw = pd.concat(dfs, ignore_index=True)
    
    replace_dict = {
        'LAMF': 'LWF',
        'RAMF': 'RWF',
        'LCB3': 'LCB',
        'RCB3': 'RCB',
        'LCB5': 'LCB',
        'RCB5': 'RCB',
        'LB5': 'LB',
        'RB5': 'RB',
        'RCMF3': 'RCMF',
        'LCMF3': 'LCMF',
    }
    
    full_similarity_df_raw['Main Position'] = full_similarity_df_raw['Main Position'].replace(replace_dict)
    return full_similarity_df_raw

def prep_player_research_table(geo_input, region, tiers, time_frame, mins, pos_select, min_age, max_age):
    df = prep_similarity_df_filters(geo_input, region, tiers, time_frame)
    return create_player_research_table(df, mins, pos_select, min_age, max_age)

def similar_players_search(df, ws_id, pos, pca_transform, compare_metrics, mins, age_band):
    df_base = pd.DataFrame()
    df_filtered_base = filter_by_position_long(df, pos)
    df_filtered_base = df_filtered_base[df_filtered_base['Minutes played']>=mins]
    
    # FORWARD
    fwd1 = "Non-penalty goals per 90"
    fwd2 = "npxG per 90"
    fwd3 = "Assists per 90"
    fwd4 = "xA per 90"
    fwd5 = "Successful dribbles, %"
    fwd6 = "Goal conversion, %"
    fwd7 = "Shot assists per 90"
    fwd8 = "Second assists per 90"
    fwd9 = "Progressive runs per 90"
    fwd10 = "Progressive passes per 90"
    fwd11 = "Touches in box per 90"
    fwd12 = "Aerial duels won, %"
    # MIDFIELD
    mid1 = "Accurate short / medium passes, %"
    mid2 = "Accurate long passes, %"
    mid3 = "Accurate smart passes, %"
    mid4 = "Shot assists per 90"
    mid5 = "xA per 90"
    mid6 = "Assists per 90"
    mid7 = "Second assists per 90"
    mid8 = "Third assists per 90"
    mid9 = "Progressive passes per 90"
    mid10 = "Progressive runs per 90"
    mid11 = "Duels won, %"
    mid12 = "pAdj Tkl+Int per 90"
    #DEFENDER
    def1 = "Defensive duels per 90"
    def2 = "PAdj Sliding tackles"
    def3 = "Defensive duels won, %"
    def4 = "Fouls per 90" ##########
    def5 = "Cards per 90"
    def6 = "Shots blocked per 90"
    def7 = "PAdj Interceptions"
    def8 = "Aerial duels won, %"
    def9 = "Accurate long passes, %"
    def10 = "1st, 2nd, 3rd assists"
    def11 = "Progressive passes per 90"
    def12 = "Progressive runs per 90"
    #GOALKEEPER
    gk1 = "Conceded goals per 90" #yes
    gk2 = "Save rate, %" #yes
    gk3 = "Dribbles per 90"
    gk4 = "Pct of passes being short" #yes
    gk5 = "Clean sheets, %"
    gk6 = "Exits per 90"
    gk7 = "Aerial duels per 90"
    gk8 = "Passes per 90" #############
    gk9 = "Accurate long passes, %" #yes
    gk10 = "Prevented goals per 90" #yes
    #EXTRA
    extra = "Accurate passes, %"
    extra2 = 'Shots per 90'
    extra3 = 'Accurate crosses, %'
    extra4 = 'Smart passes per 90'
    extra5 = 'xA per Shot Assist'
    extra6 = 'Accelerations per 90'
    extra7 = 'Aerial duels won per 90'
    extra8 = 'Fouls suffered per 90'
    extra9 = 'npxG per shot'
    extra10 = 'Key passes per 90'
    extra11 = 'Deep completed crosses per 90'
    extra12 = 'Offensive duels won, %'
    extra13 = 'Passes to final third per 90'
    extra14 = 'Shots on target, %'
    extra15 = 'Accurate short / medium passes, %'
    extra16 = 'Passes per 90'
    extra17 = 'Aerial duels per 90'
    extra18 = 'Received passes per 90'
    extra19 = 'Passes to final third per 90'
    extra20 = 'Prog passes and runs per 90'
    extra21 = 'Set pieces per 90'
    extra22 = 'Passes to penalty area per 90'
    extra23 = 'Pct of passes being smart'
    extra24 = 'Short / medium passes per 90'
    extra25 = 'Successful dribbles per 90'
    
    
    # Define metrics grouped by position
    metrics = {
        "mid": [mid1, mid2, mid3, mid4, mid5, mid6, mid7, mid8, mid9, mid10, mid11, mid12],
        "fwd": [fwd1, fwd2, fwd3, fwd4, fwd5, fwd6, fwd7, fwd8, fwd9, fwd10, fwd11, fwd12],
        "def": [def1, def2, def3, def4, def5, def6, def7, def8, def9, def10, def11, def12],
        "gk":  [gk1, gk2, gk3, gk4, gk5, gk6, gk7, gk8, gk9, gk10],
        "extra": [
            extra, extra2, extra3, extra4, extra5, extra6, extra7, extra8, extra9, extra10,
            extra11, extra12, extra13, extra14, extra15, extra16, extra17, extra18, extra19,
            extra20, extra21, extra22, extra23, extra24, extra25
        ]
    }
    
    # Normalizing function
    def NormalizeData(data):
        return (data - data.min()) / (data.max() - data.min())

    leagues = df.League.unique().tolist()
    for z in range(len(leagues)):
        dfProspect = df_filtered_base[(df_filtered_base['League'] == leagues[z])].copy()
        dfProspect = dfProspect.reset_index(drop=True)
        
        # Compute z-scores and create new columns dynamically
        for group, group_metrics in metrics.items():
            for idx, metric in enumerate(group_metrics, start=1):
                col_name = f"{group}pct{idx}"
                dfProspect[col_name] = stats.zscore(dfProspect[metric])
                
                # Invert values for metrics where lower is better (e.g., fouls, cards, conceded goals)
                if metric in [def4, def5, gk1, extra23]:
                    dfProspect[col_name] *= -1
        
        # Normalize the newly created z-score columns
        zscore_columns = dfProspect.columns[dfProspect.columns.str.endswith('pct')]
        for col in zscore_columns:
            dfProspect[col] += abs(dfProspect[col].min())  # Shift to start at 0
            dfProspect[col] = NormalizeData(dfProspect[col])  # Normalize
        
        # Concatenate with base DataFrame
        df_base = pd.concat([df_base, dfProspect], ignore_index=True)
    
    
    
    # Assuming df is your DataFrame and focal_player is the row of your focal player
    df_base = filter_by_position_long(df_base, pos)
    focal_player = df_base.loc[(df_base['Wyscout id'] == ws_id)].iloc[0]
    focal_player_index = df_base[(df_base['Wyscout id'] == ws_id)].index[0]
    
    # Remove any identifiers or non-numeric columns if necessary
    if compare_metrics == "all":
        columns_to_compare = [
            '1st, 2nd, 3rd assists','Accelerations per 90','Accurate crosses, %','Accurate long passes, %','Accurate passes, %','Accurate short / medium passes, %','Accurate smart passes, %','Aerial duels per 90','Aerial duels won per 90','Aerial duels won, %','Assists per 90','Cards per 90','Clean sheets, %','Conceded goals per 90','Deep completed crosses per 90','Defensive duels per 90','Defensive duels won, %','Dribbles per 90','Duels won, %','Exits per 90','Fouls per 90','Fouls suffered per 90','Goal conversion, %','Key passes per 90','Non-penalty goals per 90','npxG per 90','npxG per shot','Offensive duels won, %','PAdj Interceptions','PAdj Sliding tackles','pAdj Tkl+Int per 90','Passes per 90','Passes to final third per 90','Passes to penalty area per 90','Pct of passes being short','Pct of passes being smart','Prevented goals per 90','Prog passes and runs per 90','Progressive passes per 90','Progressive runs per 90','Received passes per 90','Save rate, %','Second assists per 90','Set pieces per 90','Short / medium passes per 90','Shot assists per 90','Shots blocked per 90','Shots on target, %','Shots per 90','Smart passes per 90','Successful dribbles, %','Third assists per 90','Touches in box per 90','xA per 90','xA per Shot Assist','Crosses per 90',
        ]
    elif compare_metrics == "ST":
        columns_to_compare = ['Accurate short / medium passes, %','Aerial duels won, %','Assists per 90','Goal conversion, %','Key passes per 90','Non-penalty goals per 90','npxG per 90','npxG per shot','Offensive duels won, %','pAdj Tkl+Int per 90','Received passes per 90','Shot assists per 90','Shots on target, %','Shots per 90','Touches in box per 90','xA per 90','Fouls suffered per 90',
        ]
    elif compare_metrics == "W":
        columns_to_compare = ['1st, 2nd, 3rd assists','Accelerations per 90','Accurate short / medium passes, %','Assists per 90','Deep completed crosses per 90','Defensive duels per 90','Dribbles per 90','Fouls suffered per 90','Goal conversion, %','Key passes per 90','Non-penalty goals per 90','npxG per 90','npxG per shot','Offensive duels won, %','pAdj Tkl+Int per 90','Passes to final third per 90','Passes to penalty area per 90','Pct of passes being smart','Progressive passes per 90','Progressive runs per 90','Received passes per 90','Shot assists per 90','Shots on target, %','Shots per 90','Smart passes per 90','Successful dribbles, %','Touches in box per 90','xA per 90','xA per Shot Assist','Accurate crosses, %','Crosses per 90',
        ]
    elif compare_metrics == "CAM":
        columns_to_compare = ['Accurate short / medium passes, %','Assists per 90','Defensive duels per 90','Dribbles per 90','Fouls suffered per 90','Key passes per 90','Non-penalty goals per 90','npxG per 90','npxG per shot','Offensive duels won, %','pAdj Tkl+Int per 90','Passes per 90','Passes to final third per 90','Passes to penalty area per 90','Pct of passes being smart','Progressive passes per 90','Received passes per 90','Set pieces per 90','Shot assists per 90','Shots per 90','Successful dribbles, %','Touches in box per 90','xA per 90','xA per Shot Assist',
        ]
    elif compare_metrics == "CM":
        columns_to_compare = ['1st, 2nd, 3rd assists','Accelerations per 90','Accurate long passes, %','Accurate short / medium passes, %','Aerial duels per 90','Aerial duels won, %','Assists per 90','Defensive duels per 90','Defensive duels won, %','Fouls per 90','Fouls suffered per 90','Key passes per 90','Offensive duels won, %','PAdj Interceptions','PAdj Sliding tackles','Passes per 90','Passes to final third per 90','Passes to penalty area per 90','Pct of passes being short','Pct of passes being smart','Progressive passes per 90','Progressive runs per 90','Received passes per 90','Shot assists per 90','Shots per 90','Successful dribbles, %','Touches in box per 90','xA per 90',
        ]
    elif compare_metrics == "DM":
        columns_to_compare = ['1st, 2nd, 3rd assists','Accelerations per 90','Accurate long passes, %','Accurate short / medium passes, %','Aerial duels per 90','Aerial duels won, %','Defensive duels per 90','Defensive duels won, %','Dribbles per 90','Duels won, %','Fouls per 90','Offensive duels won, %','PAdj Interceptions','PAdj Sliding tackles','pAdj Tkl+Int per 90','Passes per 90','Passes to final third per 90','Pct of passes being short','Progressive passes per 90','Progressive runs per 90','Received passes per 90','Shots blocked per 90',
        ]
    elif compare_metrics == "FB":
        columns_to_compare = ['1st, 2nd, 3rd assists','Accelerations per 90','Accurate long passes, %','Accurate short / medium passes, %','Aerial duels per 90','Aerial duels won, %','Defensive duels per 90','Defensive duels won, %','Dribbles per 90','Duels won, %','Fouls per 90','Offensive duels won, %','PAdj Interceptions','PAdj Sliding tackles','pAdj Tkl+Int per 90','Passes per 90','Passes to final third per 90','Pct of passes being short','Progressive passes per 90','Progressive runs per 90','Received passes per 90','Shots blocked per 90','Deep completed crosses per 90','Fouls suffered per 90','Shots per 90','xA per 90','Accurate crosses, %','Crosses per 90',
        ]
    elif compare_metrics == "CB":
        columns_to_compare = ['1st, 2nd, 3rd assists','Accelerations per 90','Accurate long passes, %','Accurate short / medium passes, %','Aerial duels per 90','Aerial duels won, %','Defensive duels per 90','Defensive duels won, %','Fouls per 90','PAdj Interceptions','PAdj Sliding tackles','pAdj Tkl+Int per 90','Passes per 90','Passes to final third per 90','Pct of passes being short','Progressive passes per 90','Progressive runs per 90','Received passes per 90','Shots blocked per 90',
        ]
    elif compare_metrics == "GK":
        columns_to_compare = ['Accurate long passes, %','Accurate short / medium passes, %','Aerial duels per 90','Aerial duels won, %','Clean sheets, %','Conceded goals per 90','Exits per 90','Pct of passes being short','Prevented goals per 90','Received passes per 90','Save rate, %',
        ]
    else:
        columns_to_compare = compare_metrics
    
    
    
    # Select only the columns to compare
    df_compare = df_base[columns_to_compare]
    
    # Get the focal player's data
    focal_player_data = df_compare.loc[[focal_player_index]]
    
    # Calculate the Cosine Similarity
    if pca_transform == 'Yes':
        pca = PCA(n_components=0.95)
        df_compare_pca = pca.fit_transform(df_compare)
        focal_player_data_pca = pca.transform(focal_player_data)
        df_compare['similarity_percentage'] = cosine_similarity(df_compare_pca, focal_player_data_pca).flatten()
    if pca_transform == 'No':
        df_compare['similarity_percentage'] = cosine_similarity(df_compare, focal_player_data).flatten()
    
    # Add additional columns to the result DataFrame
    additional_columns = ['Player', 'Age', 'Passport country', 'Team within selected timeframe', 'Minutes played', 'Position', 'League','On loan','Market value']
    df_compare = df_compare.join(df_base[additional_columns])
    
    # Sort by similarity percentage (descending order for highest similarity first)
    df_compare_sorted = df_compare.sort_values(by='similarity_percentage', ascending=False)
    
    # Get the most similar players and include the additional columns
    similar_players = df_compare_sorted[additional_columns + ['similarity_percentage']].rename(columns={'Team within selected timeframe':'Team','similarity_percentage':'Similarity %'})
    
    similar_players = similar_players.drop_duplicates(subset=['Player','Age','Team','Minutes played','Position'])
    
    print(f"{player} age: {int(similar_players.Age.iloc[0])}")
    print(f"{player} minutes: {similar_players['Minutes played'].iloc[0]}")
    
    similar_players.reset_index(drop=True,inplace=True)
    similar_players.reset_index(inplace=True)
    similar_players.rename(columns={'index':'Rank'},inplace=True)
    similar_players = similar_players.iloc[1:,:]
    similar_players = similar_players[(similar_players.Age>=age_band[0]) & (similar_players.Age<=age_band[1])]
    similar_players['Age'] = similar_players['Age'].astype(int)
    

    return similar_players[['Rank','Similarity %','Player','Age','Passport country','Team','Minutes played','Position','League','On loan','Market value']], focal_player['Full name'], int(focal_player['Age']), focal_player['Main Position'], focal_player['Team within selected timeframe']


def get_numeric_code(country_name):
    return int(country_numeric_code_lookup[country_name])

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
def color_percentile_100(pc):
    if 100-pc <= 10:
        color = ('#01349b', '#d9e3f6')  # Elite
    elif 10 < 100-pc <= 35:
        color = ('#007f35', '#d9f0e3')  # Above Avg
    elif 35 < 100-pc <= 66:
        color = ('#9b6700', '#fff2d9')  # Avg
    else:
        color = ('#b60918', '#fddbde')  # Below Avg

    return f'background-color: {color[1]}'


def read_csv(link):
    return pd.read_csv(link)
def _update_slider(value):
    for i in range(1, 34):
        st.session_state[f"slider{i}"] = value

from mplsoccer import VerticalPitch, FontManager
import matplotlib.patheffects as path_effects


def filter_by_position(df, position, include_in_sample=None):
    if include_in_sample:
        return df[df['Main Position'].isin(include_in_sample)]
    else:
        fw = ["CF", "WF", "AMF"]
        if position == "Forward":
            return df[df['Main Position'].str.contains('|'.join(fw), na=False)]
        
        stw = ["CF", "WF", "LAMF", "RAMF"]
        if position == "Strikers and Wingers":
            return df[df['Main Position'].str.contains('|'.join(stw), na=False)]
        
        fwns = ["WF", "AMF"]
        if position == "Forwards no ST":
            return df[df['Main Position'].str.contains('|'.join(fwns), na=False)]
        
        wing = ["WF", "LAMF", "RAMF"]
        if position == "Winger":
            return df[df['Main Position'].str.contains('|'.join(wing), na=False)]
    
        mids = ["DMF", "CMF", "AMF"]
        if position == "Midfielder":
            return df[df['Main Position'].str.contains('|'.join(mids), na=False)]
    
        cms = ["CMF", "AMF"]
        if position == "Midfielder no DM":
            return df[df['Main Position'].str.contains('|'.join(cms), na=False)]
    
        dms = ["CMF", "DMF"]
        if position == "Midfielder no CAM":
            return df[df['Main Position'].str.contains('|'.join(dms), na=False)]
    
        fbs = ["LB", "RB", "WB"]
        if position == "Fullback":
            return df[df['Main Position'].str.contains('|'.join(fbs), na=False)]
    
        defs = ["LB", "RB", "WB", "CB", "DMF"]
        if position == "Defenders":
            return df[df['Main Position'].str.contains('|'.join(defs), na=False)]
    
        cbdm = ["CB", "DMF"]
        if position == "CBs & DMs":
            return df[df['Main Position'].str.contains('|'.join(cbdm), na=False)]
    
        cf = ["CF"]
        if position == "CF":
            return df[df['Main Position'].str.contains('|'.join(cf), na=False)]
    
        cb = ["CB"]
        if position == "CB":
            return df[df['Main Position'].str.contains('|'.join(cb), na=False)]
    
        gk = ["GK"]
        if position == "GK":
            return df[df['Main Position'].str.contains('|'.join(gk), na=False)]
    
        else:
            return df
def filter_by_position_long(df, position):
    fw = ["CF", "WF", "AMF"]
    if position == "Forwards (AM, W, CF)":
        return df[df['Main Position'].str.contains('|'.join(fw), na=False)]
    
    stw = ["CF", "WF", "LAMF", "RAMF"]
    if position == "Strikers and Wingers":
        return df[df['Main Position'].str.contains('|'.join(stw), na=False)]
    
    fwns = ["WF", "AMF"]
    if position == "Forwards no ST (AM, W)":
        return df[df['Main Position'].str.contains('|'.join(fwns), na=False)]
    
    wing = ["WF", "LAMF", "RAMF"]
    if position == "Wingers":
        return df[df['Main Position'].str.contains('|'.join(wing), na=False)]

    mids = ["DMF", "CMF", "AMF"]
    if position == "Central Midfielders (DM, CM, CAM)":
        return df[df['Main Position'].str.contains('|'.join(mids), na=False)]

    cms = ["CMF", "AMF"]
    if position == "Central Midfielders no DM (CM, CAM)":
        return df[df['Main Position'].str.contains('|'.join(cms), na=False)]

    dms = ["CMF", "DMF"]
    if position == "Central Midfielders no CAM (DM, CM)":
        return df[df['Main Position'].str.contains('|'.join(dms), na=False)]

    fbs = ["LB", "RB", "WB"]
    if position == "Fullbacks (FBs/WBs)":
        return df[df['Main Position'].str.contains('|'.join(fbs), na=False)]

    defs = ["LB", "RB", "WB", "CB", "DMF"]
    if position == "Defenders (CB, FB/WB, DM)":
        return df[df['Main Position'].str.contains('|'.join(defs), na=False)]

    cbdm = ["CB", "DMF"]
    if position == "CBs & DMs":
        return df[df['Main Position'].str.contains('|'.join(cbdm), na=False)]

    cf = ["CF"]
    if position == "Strikers":
        return df[df['Main Position'].str.contains('|'.join(cf), na=False)]

    cb = ["CB"]
    if position == "Centre-Backs":
        return df[df['Main Position'].str.contains('|'.join(cb), na=False)]

    gk = ["GK"]
    if position == "Goalkeepers":
        return df[df['Main Position'].str.contains('|'.join(gk), na=False)]

    else:
        return df


def contract_expirations(contract_exp_date):
    expirations = df['Contract expires'].unique()
    expirations[expirations == 0] = np.nan
    
    expirations = pd.DataFrame({'Expiration':pd.to_datetime(expirations)}).sort_values(by=['Expiration']).reset_index(drop=True)
    exp_datetime = expirations[expirations.Expiration <= pd.to_datetime([contract_exp_date])[0]].Expiration
    exp_dates = []
    for i in range(len(exp_datetime)):
        exp_dates+=[exp_datetime[i].strftime('%Y-%m-%d')]
    return exp_dates

def load_league_data(data, league_season):
    df = data
    df = df[df['League']==league_season].reset_index(drop=True)

    df['Lateral passes per 90'] = df['Passes per 90'] - df['Vertical passes per 90'] - df['Back passes per 90']
    df['pAdj Tkl+Int per 90'] = df['PAdj Sliding tackles'] + df['PAdj Interceptions']
    df['1st, 2nd, 3rd assists'] = df['Assists per 90'] + df['Second assists per 90'] + df['Third assists per 90']
    df['xA per Shot Assist'] = df['xA per 90'] / df['Shot assists per 90'].replace(0, np.nan)
    df['Aerial duels won per 90'] = df['Aerial duels per 90'] * (df['Aerial duels won, %']/100)
    df['Cards per 90'] = df['Yellow cards per 90'] + df['Red cards per 90']
    df['Clean sheets, %'] = df['Clean sheets'] / df['Matches played']
    df['npxG'] = df['xG'] - (.76 * df['Penalties taken'])
    df['npxG per 90'] = df['npxG'] / (df['Minutes played'] / 90)
    df['npxG per shot'] = df['npxG'] / (df['Shots'] - df['Penalties taken']).replace(0,np.nan)
    df['Passes to final third & deep completions'] = df['Passes to final third per 90'] + df['Deep completions per 90']
    df['Pct of passes being short'] = df['Short / medium passes per 90'] / df['Passes per 90'] * 100
    df['Prog passes and runs per 90'] = df['Progressive passes per 90'] + df['Progressive runs per 90']
    df['Set pieces per 90'] = df['Corners per 90'] + df['Free kicks per 90']
    df['Pct of passes being smart'] = df['Smart passes per 90'] / df['Passes per 90'] * 100
    df['Pct of passes being lateral'] = df['Lateral passes per 90'] / df['Passes per 90'] * 100
    df['Goals prevented %'] = (df['xG against per 90'] - df['Conceded goals per 90']) / df['xG against per 90'] * 100
    df['Successful crosses per 90'] = df['Crosses per 90'] * (df['Accurate crosses, %']/100)
    df['Successful passes to penalty area per 90'] = df['Passes to penalty area per 90'] * (df['Accurate passes to penalty area, %']/100)
    df['Successful progressive passes per 90'] = df['Progressive passes per 90'] * (df['Accurate progressive passes, %']/100)
    df['Successful through passes per 90'] = df['Through passes per 90'] * (df['Accurate through passes, %']/100)
    df['Successful smart passes per 90'] = df['Smart passes per 90'] * (df['Accurate smart passes, %']/100)
    df['Successful dribbles per 90'] = df['Dribbles per 90'] * (df['Successful dribbles, %']/100)
    df['Successful passes to final third per 90'] = df['Passes to final third per 90'] * (df['Accurate passes to final third, %']/100)

    df = df.dropna(subset=['Position']).reset_index(drop=True)

    df['Main Position'] = df['Position'].str.split().str[0].str.rstrip(',')
    df.fillna(0,inplace=True)
    position_replacements = {
        'LAMF': 'LWF',
        'RAMF': 'RWF',
        'LCB3': 'LCB',
        'RCB3': 'RCB',
        'LCB5': 'LCB',
        'RCB5': 'RCB',
        'LB5': 'LB',
        'RB5': 'RB',
        # 'RWB': 'RB',
        # 'LWB': 'LB',
        'LCMF3': 'LCMF',
        'RCMF3': 'RCMF',
    }
    df['Main Position'] = df['Main Position'].replace(position_replacements)

    return df


def make_rankings(formation, mins, data, role_position_df, leagues, exp_contracts, expiration_date,
                  min_age, max_age, num, normalize_to_100, chosen_team, nationality_chosen
                 ):
    formation_positions = {442:['GK','RCB','LCB','RB','LB','RCM','LCM','RW','LW','RS','LS',],
                            4231:['GK','RCB','LCB','RB','LB','RCM','LCM','CAM','RW','LW','ST'],
                            433:['GK','RCB','LCB','RB','LB','RCM','CM','LCM','RW','LW','ST'],
                            343:['GK','RCB','CB','LCB','RB','LB','RCM','LCM','RW','LW','ST'],
                           4222:['GK','RCB','LCB','RB','LB','RCM','LCM','RAM','LAM','RS','LS',],
                          }
    df = data
    
    ###
    expirations = df['Contract expires'].unique()
    expirations[expirations == 0] = np.nan
    
    expirations = pd.DataFrame({'Expiration':pd.to_datetime(expirations)}).sort_values(by=['Expiration']).reset_index(drop=True)
    exp_datetime = expirations[expirations.Expiration <= pd.to_datetime([expiration_date])[0]].Expiration
    exp_dates = []
    for i in range(len(exp_datetime)):
        exp_dates+=[exp_datetime[i].strftime('%Y-%m-%d')]
    ###
    
    cols = ['Player', 'Team', 'Age', 'Pos.', 'Score',
           'Minutes played', 'Contract expires', 'Squad Position','Passport country']
    rank_list = pd.DataFrame(columns=cols)
    
    all_cols = ['Player', 'Team', 'Team within selected timeframe', 'Position', 'Age', 'Market value', 'Contract expires', 'Passport country', 'Matches played', 'Minutes played', 'Goals', 'xG', 'Assists', 'xA', 'Duels per 90', 'Duels won, %', 'Birth country', 'Passport country', 'Foot', 'Height', 'Weight', 'On loan', 'Successful defensive actions per 90', 'Defensive duels per 90', 'Defensive duels won, %', 'Aerial duels per 90', 'Aerial duels won, %', 'Sliding tackles per 90', 'PAdj Sliding tackles', 'Shots blocked per 90', 'Interceptions per 90', 'PAdj Interceptions', 'Fouls per 90', 'Yellow cards', 'Yellow cards per 90', 'Red cards', 'Red cards per 90', 'Successful attacking actions per 90', 'Goals per 90', 'Non-penalty goals', 'Non-penalty goals per 90', 'xG per 90', 'Head goals', 'Head goals per 90', 'Shots', 'Shots per 90', 'Shots on target, %', 'Goal conversion, %', 'Assists per 90', 'Crosses per 90', 'Accurate crosses, %', 'Crosses from left flank per 90', 'Accurate crosses from left flank, %', 'Crosses from right flank per 90', 'Accurate crosses from right flank, %', 'Crosses to goalie box per 90', 'Dribbles per 90', 'Successful dribbles, %', 'Offensive duels per 90', 'Offensive duels won, %', 'Touches in box per 90', 'Progressive runs per 90', 'Accelerations per 90', 'Received passes per 90', 'Received long passes per 90', 'Fouls suffered per 90', 'Passes per 90', 'Accurate passes, %', 'Forward passes per 90', 'Accurate forward passes, %', 'Back passes per 90', 'Accurate back passes, %', 'Lateral passes per 90', 'Accurate lateral passes, %', 'Short / medium passes per 90', 'Accurate short / medium passes, %', 'Long passes per 90', 'Accurate long passes, %', 'Average pass length, m', 'Average long pass length, m', 'xA per 90', 'Shot assists per 90', 'Second assists per 90', 'Third assists per 90', 'Smart passes per 90', 'Accurate smart passes, %', 'Key passes per 90', 'Passes to final third per 90', 'Accurate passes to final third, %', 'Passes to penalty area per 90', 'Accurate passes to penalty area, %', 'Through passes per 90', 'Accurate through passes, %', 'Deep completions per 90', 'Deep completed crosses per 90', 'Progressive passes per 90', 'Accurate progressive passes, %', 'Conceded goals', 'Conceded goals per 90', 'Shots against', 'Shots against per 90', 'Clean sheets', 'Save rate, %', 'xG against', 'xG against per 90', 'Prevented goals', 'Prevented goals per 90', 'Back passes received as GK per 90', 'Exits per 90', 'Aerial duels per 90.1', 'Free kicks per 90', 'Direct free kicks per 90', 'Direct free kicks on target, %', 'Corners per 90', 'Penalties taken', 'Penalty conversion, %', 'League', 'pAdj Tkl+Int per 90', '1st, 2nd, 3rd assists', 'xA per Shot Assist', 'Aerial duels won per 90', 'Cards per 90', 'Clean sheets, %', 'npxG', 'npxG per 90', 'npxG per shot', 'Passes to final third & deep completions', 'Head goals as pct of all goals', 'Prog passes and runs per 90', 'Main Position', 'midpct1', 'midpct2', 'midpct3', 'midpct4', 'midpct5', 'midpct6', 'midpct7', 'midpct8', 'midpct9', 'midpct10', 'midpct11', 'midpct12', 'fwdpct1', 'fwdpct2', 'fwdpct3', 'fwdpct4', 'fwdpct5', 'fwdpct6', 'fwdpct7', 'fwdpct8', 'fwdpct9', 'fwdpct10', 'fwdpct11', 'fwdpct12', 'defpct1', 'defpct2', 'defpct3', 'defpct4', 'defpct5', 'defpct6', 'defpct7', 'defpct8', 'defpct9', 'defpct10', 'defpct11', 'defpct12', 'gkpct1', 'gkpct2', 'gkpct3', 'gkpct4', 'gkpct5', 'gkpct6', 'gkpct7', 'gkpct8', 'gkpct9', 'gkpct10', 'extrapct', 'extrapct2', 'extrapct3', 'extrapct4', 'extrapct5', 'extrapct6', 'extrapct7', 'extrapct8', 'extrapct9', 'extrapct10', 'extrapct11', 'extrapct12', 'extrapct13', 'extrapct14', 'extrapct15', 'extrapct16', 'extrapct17', 'extrapct18', 'extrapct19', 'extrapct20',
                'CM Score', 'CAM Score', 'Traditional Winger Score', 'Inverted Winger Score', 'Ball Playing CB Score', 'CB Score',
                'Advanced Playmaker Score', 'Deep-Lying Playmaker Score', 'Playmaking Winger Score', 'Focal Point Striker Score',
                'Link-Up Striker Score', 'Playmaking Striker Score', 'Advanced Striker Score', 'Deep-Lying Striker Score',
                'Defensive Mid Score', 'Progressive Midfielder Score', 'Box-to-Box Score', 'Attacking FB Score', 'Second Striker Score', 'Inside Forward Score',
               'Shot-Stopping Distributor Score', 'Spurs LCB Score', 'Number 6 Score', 'Defensive FB Score', 'KVO CAM Score',
                'Inverted FB Score', 'Possession Enabler Score','Wide CAM Score']
    full_prospect_df = pd.DataFrame(columns=all_cols)
    
    
    rank_11 = role_position_df[role_position_df['formation']==formation].copy().reset_index(drop=True)
    
    for q in range(len(rank_11)):
        pos_ = rank_11.pos_[q]
        pos = rank_11.pos[q]
        pos_buckets = rank_11.pos_bucket[q]
        foot = rank_11.foot[q]
        main_pos = rank_11.main_position[q]
        
        
        for z in range(len(leagues)):
            dfProspect = df[(df['Minutes played']>=mins)].copy()
            dfProspect = filter_by_position(dfProspect, pos)
            dfProspect = dfProspect.reset_index(drop=True)
    
            #############################################################################
            #############################################################################
            ## Variables I'll z-score. ignore the variable names lol, those have been copy/pasted for months now and are poorly named
    
            # FORWARD
            fwd1 = "Non-penalty goals per 90"
            fwd2 = "npxG per 90"
            fwd3 = "Assists per 90"
            fwd4 = "xA per 90"
            fwd5 = "Successful dribbles, %"
            fwd6 = "Goal conversion, %"
            fwd7 = "Shot assists per 90"
            fwd8 = "Second assists per 90"
            fwd9 = "Progressive runs per 90"
            fwd10 = "Progressive passes per 90"
            fwd11 = "Touches in box per 90"
            fwd12 = "Aerial duels won, %"
            # MIDFIELD
            mid1 = "Accurate short / medium passes, %"
            mid2 = "Accurate long passes, %"
            mid3 = "Accurate smart passes, %"
            mid4 = "Shot assists per 90"
            mid5 = "xA per 90"
            mid6 = "Assists per 90"
            mid7 = "Second assists per 90"
            mid8 = "Third assists per 90"
            mid9 = "Progressive passes per 90"
            mid10 = "Progressive runs per 90"
            mid11 = "Duels won, %"
            mid12 = "pAdj Tkl+Int per 90"
            #DEFENDER
            def1 = "Defensive duels per 90"
            def2 = "PAdj Sliding tackles"
            def3 = "Defensive duels won, %"
            def4 = "Fouls per 90" ##########
            def5 = "Cards per 90"
            def6 = "Shots blocked per 90"
            def7 = "PAdj Interceptions"
            def8 = "Aerial duels won, %"
            def9 = "Accurate long passes, %"
            def10 = "1st, 2nd, 3rd assists"
            def11 = "Progressive passes per 90"
            def12 = "Progressive runs per 90"
            #GOALKEEPER
            gk1 = "Conceded goals per 90" #a2
            gk2 = "Save rate, %" #a3
            gk3 = "Dribbles per 90"
            gk4 = "Pct of passes being short" #b3
            gk5 = "Clean sheets, %"
            gk6 = "Exits per 90" #a5
            gk7 = "Aerial duels per 90"
            gk8 = "Passes per 90" #b2
            gk9 = "Accurate long passes, %" #b5
            gk10 = "Prevented goals per 90" #a4
            gk11 = 'Shots against per 90' #a1
            gk12 = 'Pct of passes being lateral' #b4
            gk13 = 'Received passes per 90' #b1
            gk14 = "Goals prevented %" #a4
            #EXTRA
            extra = "Accurate passes, %"
            extra2 = 'Shots per 90'
            extra3 = 'Accurate crosses, %'
            extra4 = 'Smart passes per 90'
            extra5 = 'xA per Shot Assist'
            extra6 = 'Accelerations per 90'
            extra7 = 'Aerial duels won per 90'
            extra8 = 'Fouls suffered per 90'
            extra9 = 'npxG per shot'
            extra10 = 'Key passes per 90'
            extra11 = 'Deep completed crosses per 90'
            extra12 = 'Offensive duels won, %'
            extra13 = 'Passes to final third per 90'
            extra14 = 'Shots on target, %'
            extra15 = 'Accurate short / medium passes, %'
            extra16 = 'Passes per 90'
            extra17 = 'Aerial duels per 90'
            extra18 = 'Received passes per 90' #b1
            extra19 = 'Passes to final third per 90'
            extra20 = 'Prog passes and runs per 90'
            extra21 = 'Set pieces per 90'
            extra22 = 'Passes to penalty area per 90'
            extra23 = 'Pct of passes being smart'
            extra24 = 'Short / medium passes per 90'
            
            # normalizing function
            def NormalizeData(data):
                return (data - np.min(data)) / (np.max(data) - np.min(data))
    
            # all the z-score creations. I could turn this into a loop but haven't yet
            dfProspect["midpct1"] = stats.zscore(dfProspect[mid1])
            dfProspect["midpct2"] = stats.zscore(dfProspect[mid2])
            dfProspect["midpct3"] = stats.zscore(dfProspect[mid3])
            dfProspect["midpct4"] = stats.zscore(dfProspect[mid4])
            dfProspect["midpct5"] = stats.zscore(dfProspect[mid5])
            dfProspect["midpct6"] = stats.zscore(dfProspect[mid6])
            dfProspect["midpct7"] = stats.zscore(dfProspect[mid7])
            dfProspect["midpct8"] = stats.zscore(dfProspect[mid8])
            dfProspect["midpct9"] = stats.zscore(dfProspect[mid9])
            dfProspect["midpct10"] = stats.zscore(dfProspect[mid10])
            dfProspect["midpct11"] = stats.zscore(dfProspect[mid11])
            dfProspect["midpct12"] = stats.zscore(dfProspect[mid12])
            dfProspect["fwdpct1"] = stats.zscore(dfProspect[fwd1])
            dfProspect["fwdpct2"] = stats.zscore(dfProspect[fwd2])
            dfProspect["fwdpct3"] = stats.zscore(dfProspect[fwd3])
            dfProspect["fwdpct4"] = stats.zscore(dfProspect[fwd4])
            dfProspect["fwdpct5"] = stats.zscore(dfProspect[fwd5])
            dfProspect["fwdpct6"] = stats.zscore(dfProspect[fwd6])
            dfProspect["fwdpct7"] = stats.zscore(dfProspect[fwd7])
            dfProspect["fwdpct8"] = stats.zscore(dfProspect[fwd8])
            dfProspect["fwdpct9"] = stats.zscore(dfProspect[fwd9])
            dfProspect["fwdpct10"] = stats.zscore(dfProspect[fwd10])
            dfProspect["fwdpct11"] = stats.zscore(dfProspect[fwd11])
            dfProspect["fwdpct12"] = stats.zscore(dfProspect[fwd12])
            dfProspect["defpct1"] = stats.zscore(dfProspect[def1])
            dfProspect["defpct2"] = stats.zscore(dfProspect[def2])
            dfProspect["defpct3"] = stats.zscore(dfProspect[def3])
            dfProspect["defpct4"] = stats.zscore(dfProspect[def4]) * -1 ######
            dfProspect["defpct5"] = stats.zscore(dfProspect[def5]) * -1 ########
            dfProspect["defpct6"] = stats.zscore(dfProspect[def6])
            dfProspect["defpct7"] = stats.zscore(dfProspect[def7])
            dfProspect["defpct8"] = stats.zscore(dfProspect[def8])
            dfProspect["defpct9"] = stats.zscore(dfProspect[def9])
            dfProspect["defpct10"] = stats.zscore(dfProspect[def10])
            dfProspect["defpct11"] = stats.zscore(dfProspect[def11])
            dfProspect["defpct12"] = stats.zscore(dfProspect[def12])
            dfProspect["gkpct1"] = 1-stats.zscore(dfProspect[gk1]) * -1 #####
            dfProspect["gkpct2"] = stats.zscore(dfProspect[gk2])
            dfProspect["gkpct3"] = stats.zscore(dfProspect[gk3])
            dfProspect["gkpct4"] = stats.zscore(dfProspect[gk4])
            dfProspect["gkpct5"] = stats.zscore(dfProspect[gk5])
            dfProspect["gkpct6"] = stats.zscore(dfProspect[gk6])
            dfProspect["gkpct7"] = stats.zscore(dfProspect[gk7])
            dfProspect["gkpct8"] = stats.zscore(dfProspect[gk8])
            dfProspect["gkpct9"] = stats.zscore(dfProspect[gk9])
            dfProspect["gkpct10"] = stats.zscore(dfProspect[gk10])
            dfProspect["gkpct11"] = stats.zscore(dfProspect[gk11])
            dfProspect["gkpct12"] = stats.zscore(dfProspect[gk12])
            dfProspect["gkpct13"] = stats.zscore(dfProspect[gk13])
            dfProspect["gkpct14"] = stats.zscore(dfProspect[gk14])
            dfProspect["extrapct"] = stats.zscore(dfProspect[extra])
            dfProspect["extrapct2"] = stats.zscore(dfProspect[extra2])
            dfProspect["extrapct3"] = stats.zscore(dfProspect[extra3])
            dfProspect["extrapct4"] = stats.zscore(dfProspect[extra4])
            dfProspect["extrapct5"] = stats.zscore(dfProspect[extra5])
            dfProspect["extrapct6"] = stats.zscore(dfProspect[extra6])
            dfProspect["extrapct7"] = stats.zscore(dfProspect[extra7])
            dfProspect["extrapct8"] = stats.zscore(dfProspect[extra8])
            dfProspect["extrapct9"] = stats.zscore(dfProspect[extra9])
            dfProspect["extrapct10"] = stats.zscore(dfProspect[extra10])
            dfProspect["extrapct11"] = stats.zscore(dfProspect[extra11])
            dfProspect["extrapct12"] = stats.zscore(dfProspect[extra12])
            dfProspect["extrapct13"] = stats.zscore(dfProspect[extra13])
            dfProspect["extrapct14"] = stats.zscore(dfProspect[extra14])
            dfProspect["extrapct15"] = stats.zscore(dfProspect[extra15])
            dfProspect["extrapct16"] = stats.zscore(dfProspect[extra16])
            dfProspect["extrapct17"] = stats.zscore(dfProspect[extra17])
            dfProspect["extrapct18"] = stats.zscore(dfProspect[extra18])
            dfProspect["extrapct19"] = stats.zscore(dfProspect[extra19])
            dfProspect["extrapct20"] = stats.zscore(dfProspect[extra20])
            dfProspect["extrapct21"] = stats.zscore(dfProspect[extra21])
            dfProspect["extrapct22"] = stats.zscore(dfProspect[extra22])
            dfProspect["extrapct23"] = 1-stats.zscore(dfProspect[extra23]) * -1 #####
            dfProspect["extrapct24"] = stats.zscore(dfProspect[extra24])
            
            # The first line in this loop is how I get the z-scores to start at 0. I checked the distribution chart at the bottom, and it's the same shape of course
            # the second line normalizes
            for i in range(dfProspect.columns.tolist().index('midpct1'),len(dfProspect.columns)):
                dfProspect.iloc[:,i] = dfProspect.iloc[:,i] + abs(dfProspect.iloc[:,i].min())
                dfProspect.iloc[:,i] = NormalizeData(dfProspect.iloc[:,i])
    
    
            #############################################################################
            #############################################################################
            ## Section with all the scores. Of course, very much a fluid thing now as I play around and calibrate
            ## And I also want to make buckets like ball winning, passing, etc and then use those instead of individual metrics
    
            dfProspect['Shot-Stopping Distributor Score'] = (
                (.4 * dfProspect['gkpct10']) +   # psxG+-
                (.1 * dfProspect['gkpct2']) +   # save %
                (.2 * dfProspect['gkpct4']) +  # pct passes being short
                (.15 * dfProspect['gkpct4']) +  # short/medium passes
                (.15 * dfProspect['gkpct9'])     # long pass %
            )
            dfProspect['CM Score'] = (
                (.1 * dfProspect['extrapct4']) +   # smart passes
                (.1 * dfProspect['midpct4']) +  # shot assist
                (.125 * dfProspect['defpct10']) +   # 1/2/3 assists
                (.05 * dfProspect['extrapct10']) +  # key passes
                (.075 * dfProspect['fwdpct1']) +     # np Goals
                (.15 * dfProspect['defpct3']) +     # def duels won %
                (.15 * dfProspect['midpct12']) +     # padj tkl+int
                (.1 * dfProspect['defpct4']) +      # fouls
                (.05 * dfProspect['extrapct'])   # pass cmp%
            )
            dfProspect['Possession Enabler Score'] = (
                (.25 * dfProspect['extrapct15']) +   # short/medium pass %
                (.3 * dfProspect['gkpct4']) +  # pct of passes being short/medium
                (.1 * dfProspect['defpct4']) +  # fouls (inverse)
                (.2 * dfProspect['extrapct23']) +     # pct of passes being smart passes (inverse)
                (.15 * dfProspect['gkpct8'])   # passes
            )
            dfProspect['CAM Score'] = (
                (.15 * dfProspect['extrapct4']) +   # smart passes
                (.2 * dfProspect['midpct4']) +  # shot assist
                (.15 * dfProspect['extrapct10']) +  # key passes
                (.1 * dfProspect['fwdpct2']) +     # npxg
                (.05 * dfProspect['fwdpct1']) +  # np G
                (.1 * dfProspect['fwdpct4']) +     # xA
                (.1 * dfProspect['fwdpct5']) +       # dribble %
                (.15 * dfProspect['extrapct12'])    # offesnsive duel %
            )
            dfProspect['Traditional Winger Score'] = (
                (.15 * dfProspect['extrapct6']) +   # accelerations
                (.2 * dfProspect['midpct4']) +  # shot assist
                (.1 * dfProspect['fwdpct4']) +     # xA
                (.175 * dfProspect['fwdpct5']) +      # dribble %
                (.175 * dfProspect['extrapct11']) +   # deep completed cross
                (.1 * dfProspect['extrapct3'])     # cross cmp %
            )
            dfProspect['Inverted Winger Score'] = (
                (.1 * dfProspect['midpct4']) +  # shot assist
                (.1 * dfProspect['extrapct11']) +   # deep completed cross
                (.15 * dfProspect['fwdpct2']) +     # npxG
                (.15 * dfProspect['fwdpct5']) +      # dribble %
                (.25 * dfProspect['extrapct2']) +    # shots
                (.15 * dfProspect['fwdpct11'])     # pen area touches
            )
            dfProspect['Ball Playing CB Score'] = (
                (.1 * dfProspect['defpct3']) +   # def duel win %
                (.1 * dfProspect['defpct8']) +     # aerial win %
                (.2 * dfProspect['gkpct8']) +   # passes
                (.2 * dfProspect['defpct11']) +     # prog passes
                (.2 * dfProspect['extrapct13']) +     # passes to final third + deep completions
                (.2 * dfProspect['midpct2'])   # long pass cmp %
            )
            dfProspect['Spurs LCB Score'] = (
                (.2 * dfProspect['defpct3']) +   # def duel win %
                (.15 * dfProspect['defpct4']) +     # fls
                (.25 * dfProspect['extrapct20']) +   # Prog passes and runs
                (.2 * dfProspect['gkpct8']) +   # passes
                (.15 * dfProspect['extrapct15']) +     # short cmp %
                (.05 * dfProspect['midpct2'])   # long pass cmp %
            )
            dfProspect['CB Score'] = (
                (.1 * dfProspect['defpct2']) +   # tackles
                (.1 * dfProspect['defpct7']) +  # interceptions
                (.15 * dfProspect['defpct8']) +   # aerial win %
                (.45 * dfProspect['defpct3']) +  # def duel win %
                (.2 * dfProspect['defpct4'])       # fouls
            )
            dfProspect['Defensive FB Score'] = (
                (.1 * dfProspect['defpct2']) +   # tackles
                (.1 * dfProspect['defpct7']) +  # interceptions
                (.15 * dfProspect['extrapct3']) +   # aerial win %
                (.45 * dfProspect['defpct3']) +  # def duel win %
                (.2 * dfProspect['defpct4'])       # fouls
            )
            dfProspect['Inverted FB Score'] = (
                (.1 * dfProspect['defpct3']) +   # def duel win %
                (.35 * dfProspect['gkpct8']) +   # passes
                (.2 * dfProspect['defpct11']) +     # prog passes
                (.2 * dfProspect['midpct12']) +     # padj tkl+interceptions
                (.15 * dfProspect['gkpct4'])   # Pct of passes being short
            )
            dfProspect['Defensive Mid Score'] = (
                (.1 * dfProspect['defpct2']) +   # tackles
                (.1 * dfProspect['defpct7']) +  # interceptions
                (.15 * dfProspect['defpct8']) +   # aerial win %
                (.45 * dfProspect['defpct3']) +  # def duel win %
                (.2 * dfProspect['defpct4'])       # fouls
            )
            dfProspect['Number 6 Score'] = (
                (.3 * dfProspect['defpct3']) +   # def duel win %
                (.1 * dfProspect['defpct4']) +     # fls
                (.2 * dfProspect['gkpct4']) +   # Pct of passes being short
                (.25 * dfProspect['extrapct15']) +     # short cmp %
                (.15 * dfProspect['extrapct12'])   # off duel win %
            )
            dfProspect['Advanced Playmaker Score'] = (
                (.15 * dfProspect['extrapct4']) +   # smart passes
                (.25 * dfProspect['extrapct10']) +   # key passes
                (.25 * dfProspect['midpct4']) +     # shot assists
                (.2 * dfProspect['extrapct13']) +     # passes to final third + deep completions
                (.15 * dfProspect['fwdpct4'])   # xA
            )
            dfProspect['Deep-Lying Playmaker Score'] = (
                (.1 * dfProspect['defpct3']) +   # def duel win %
                (.1 * dfProspect['extrapct10']) +   # key passes
                (.15 * dfProspect['midpct4']) +     # shot assists
                (.25 * dfProspect['defpct11']) +     # prog passes
                (.25 * dfProspect['extrapct13']) +     # passes to final third + deep completions
                (.15 * dfProspect['defpct10'])   # 1/2/3 assists
            )
            dfProspect['Playmaking Winger Score'] = (
                (.15 * dfProspect['extrapct4']) +   # smart passes
                (.2 * dfProspect['extrapct10']) +   # key passes
                (.2 * dfProspect['midpct4']) +     # shot assists
                (.15 * dfProspect['defpct11']) +     # prog passes
                (.2 * dfProspect['extrapct13']) +     # passes to final third + deep completions
                (.1 * dfProspect['defpct10'])   # 1/2/3 assists
            )
            dfProspect['Focal Point Striker Score'] = (
                (.225 * dfProspect['defpct8']) +   # aerial win%
                (.05 * dfProspect['fwdpct1']) +  # np G
                (.225 * dfProspect['fwdpct2']) +     # npxG
                (.2 * dfProspect['extrapct14']) +    # SoT %
                (.3 * dfProspect['fwdpct11'])     # pen area touches
            )
            dfProspect['Link-Up Striker Score'] = (
                (.25 * dfProspect['extrapct15']) +   # short/med pass cmp %
                (.1 * dfProspect['midpct4']) +  # shot assist
                (.1 * dfProspect['extrapct10']) +  # key passes
                (.1 * dfProspect['fwdpct1']) +     # np Goals
                (.1 * dfProspect['fwdpct2']) +     # npxG
                (.1 * dfProspect['extrapct12']) +   # offesnsive duel %
                (.25 * dfProspect['extrapct18'])    # received passes
            )
            dfProspect['BFC Striker Score'] = (
                (.15 * dfProspect['extrapct15']) +   # short/med pass cmp %
                (.1 * dfProspect['midpct4']) +  # shot assist
                (.05 * dfProspect['extrapct10']) +  # key passes
                (.1 * dfProspect['fwdpct2']) +     # npxG
                (.2 * dfProspect['fwdpct6']) +    # Goal Conversion %
                (.1 * dfProspect['extrapct18']) +   # received passes
                (.15 * dfProspect['extrapct12']) +   # offesnsive duel %
                (.15 * dfProspect['midpct12']) +     # padj tkl+interceptions
                (.1 * dfProspect['defpct12'])      # prog runs
            )
            dfProspect['Playmaking Striker Score'] = (
                (.1 * dfProspect['extrapct4']) +   # smart passes
                (.2 * dfProspect['extrapct10']) +   # key passes
                (.2 * dfProspect['midpct4']) +     # shot assists
                (.15 * dfProspect['defpct11']) +     # prog passes
                (.2 * dfProspect['extrapct13']) +     # passes to final third + deep completions
                (.15 * dfProspect['fwdpct4'])   # xA
            )
            dfProspect['Advanced Striker Score'] = (
                (.1 * dfProspect['fwdpct5']) +   # dribble %
                (.15 * dfProspect['fwdpct1']) +  # np G
                (.2 * dfProspect['fwdpct2']) +     # npxG
                (.1 * dfProspect['fwdpct6']) +    # Goal Conversion %
                (.2 * dfProspect['fwdpct11']) +     # pen area touches
                (.15 * dfProspect['fwdpct4']) +  # xA
                (.1 * dfProspect['defpct12'])     # prog runs
            )
            dfProspect['Inside Forward Score'] = (
                (.1 * dfProspect['fwdpct5']) +   # dribble %
                (.15 * dfProspect['fwdpct1']) +  # np G
                (.2 * dfProspect['fwdpct2']) +     # npxG
                (.1 * dfProspect['fwdpct6']) +    # Goal Conversion %
                (.2 * dfProspect['fwdpct11']) +     # pen area touches
                (.15 * dfProspect['fwdpct4']) +  # xA
                (.1 * dfProspect['defpct12'])     # prog runs
            )
            dfProspect['Deep-Lying Striker Score'] = (
                (.15 * dfProspect['extrapct18']) +   # received passes
                (.2 * dfProspect['fwdpct1']) +  # np G
                (.2 * dfProspect['fwdpct2']) +     # npxG
                (.2 * dfProspect['midpct4']) +   # shot assists
                (.1 * dfProspect['defpct10']) +     # 1+2+3 assists
                (.15 * dfProspect['defpct12'])     # prog runs
            )
            dfProspect['Progressive Midfielder Score'] = (
                (.15 * dfProspect['extrapct18']) +   # received passes
                (.2 * dfProspect['extrapct19']) +     # passes to final third
                (.225 * dfProspect['defpct11']) +     # prog passes
                (.1 * dfProspect['extrapct12']) +  # off duel win %
                (.1 * dfProspect['extrapct6']) +   # accelerations
                (.225 * dfProspect['defpct12'])     # prog runs
            )
            dfProspect['Box-to-Box Score'] = (
                (.1 * dfProspect['midpct12']) +   # pAdj Tkl+Int
                (.225 * dfProspect['defpct3']) +   # def duel win %
                (.225 * dfProspect['extrapct12']) +  # off duel win %
                (.1 * dfProspect['extrapct19']) +     # passes to final third
                (.1 * dfProspect['extrapct19']) +     # minutes
                (.25 * dfProspect['defpct12'])   # prog runs
            )
            dfProspect['Attacking FB Score'] = (
                (.075 * dfProspect['extrapct6']) +   # accelerations
                (.1 * dfProspect['fwdpct4']) +     # xA
                (.2 * dfProspect['extrapct12']) +      # off duel win %
                (.25 * dfProspect['extrapct13']) +     # passes to final third + deep completions
                (.075 * dfProspect['extrapct3']) +     # cross cmp %
                (.2 * dfProspect['defpct12']) +     # prog runs
                (.1 * dfProspect['fwdpct5'])    # dribble %
            )
            dfProspect['Second Striker Score'] = (
                (.1 * dfProspect['fwdpct5']) +   # dribble %
                (.15 * dfProspect['fwdpct1']) +  # np G
                (.2 * dfProspect['fwdpct2']) +     # npxG
                (.1 * dfProspect['fwdpct6']) +    # Goal Conversion %
                (.2 * dfProspect['fwdpct11']) +     # pen area touches
                (.15 * dfProspect['fwdpct4']) +  # xA
                (.1 * dfProspect['defpct12'])     # prog runs
            )
            dfProspect['KVO CAM Score'] = (
                (.1 * dfProspect['fwdpct5']) +   # dribble %
                (.05 * dfProspect['defpct1']) +  # defensive duels
                (.05 * dfProspect['extrapct21']) +     # set pieces
                (.125 * dfProspect['extrapct4']) +   # smart passes
                (.1 * dfProspect['extrapct10']) +   # key passes
                (.15 * dfProspect['midpct4']) +     # shot assists
                (.1 * dfProspect['defpct11']) +     # prog passes
                (.1 * dfProspect['fwdpct4']) +  # xA
                (.125 * dfProspect['extrapct22']) +  # passes to box
                (.1 * dfProspect['defpct12'])     # prog runs
            )
            dfProspect['Wide CAM Score'] = (
                (.1 * dfProspect['extrapct6']) +   # accelerations
                (.2 * dfProspect['midpct4']) +  # shot assist
                (.15 * dfProspect['fwdpct4']) +     # xA
                (.15 * dfProspect['fwdpct5']) +      # dribble %
                (.1 * dfProspect['extrapct11']) +   # deep completed cross
                (.05 * dfProspect['fwdpct11']) +     # pen area touches
                (.15 * dfProspect['extrapct3'])     # cross cmp %
            )
            
            if foot != 'either':
                dfProspect = dfProspect[dfProspect['Foot']==foot]
            if main_pos != 'any':
                dfProspect = dfProspect[dfProspect['Main Position'].str.contains(main_pos)]
    
    
            ranks = dfProspect[["Player", "Main Position", "Team within selected timeframe", "Age", 'Contract expires', 'Minutes played','Passport country',
                                "CM Score", 'CAM Score', 'Traditional Winger Score', 'Inverted Winger Score', 'Ball Playing CB Score',
                                'CB Score', 'Advanced Playmaker Score', 'Focal Point Striker Score', 'Link-Up Striker Score', 'Deep-Lying Striker Score',
                                'Advanced Striker Score', 'Playmaking Winger Score', 'Box-to-Box Score', 'Playmaking Striker Score',
                                   'Attacking FB Score', 'Deep-Lying Playmaker Score', 'Second Striker Score', 'Progressive Midfielder Score',
                               'Defensive Mid Score', 'Shot-Stopping Distributor Score', 'Spurs LCB Score', 'Number 6 Score', 'Defensive FB Score',
                               'KVO CAM Score', 'Inverted FB Score', 'Inside Forward Score',  'Possession Enabler Score','Wide CAM Score']]
            ranks = ranks.rename(columns={'Team within selected timeframe': 'Team'})
    
            if normalize_to_100 == 'Yes':
                for i in range(7,len(ranks.columns)):
                    ranks.iloc[:,i] = NormalizeData(ranks.iloc[:,i])
    
            # make the table
            ranks['Score'] = round(ranks['%s Score' %pos_]*100,1)
            ranks.sort_values(by=['Score', 'Age'], ascending=[False,True], inplace=True)
            ranks = ranks.reset_index(drop=True)
            ranks = ranks[['Player', 'Team', 'Age', 'Main Position', 'Score', 'Minutes played','Contract expires','Passport country']]
            ranks = ranks.rename(columns={'Main Position': 'Player Pos.'})
            ranks.index = ranks.index+1
            ranks['Squad Position'] = rank_11.pos_role[q]
            if exp_contracts == 'y':
                ranks = ranks[ranks['Contract expires'].isin(exp_dates)]
            ranks = ranks[ranks['Age'].between(min_age,max_age)]
            ranks['Formation Pos.'] = formation_positions[formation][q]
            
            rank_list = pd.concat([rank_list,ranks])
    
    rank_list.Age = rank_list.Age.astype(int)
    rank_list = rank_list.reset_index().rename(columns={'index':'Role Rank'})
    
    rank_list_final = pd.DataFrame(columns=rank_list.columns)
    if chosen_team != 'N/A':
        rank_list = rank_list[rank_list['Team']==chosen_team].reset_index(drop=True)
    if nationality_chosen != "":
        rank_list['Passport country'] = rank_list['Passport country'].fillna("")
        rank_list = rank_list[rank_list['Passport country'].str.contains(nationality_chosen)].reset_index(drop=True)
    
    for q in range(len(rank_11)):
        rank_list_final = pd.concat([rank_list_final,rank_list[rank_list['Squad Position']==rank_11.pos_role[q]].sort_values(by=['Score','Age'],ascending=[False,True]).head(num)])
    rank_list = rank_list_final.copy()
    return rank_list

#######################################################################################################################################
def rank_column(df, column_name):
    return stats.rankdata(df[column_name], "average") / len(df[column_name])
def rank_column_inverse(df, column_name):
    return 1-stats.rankdata(df[column_name], "average") / len(df[column_name])


def get_label_rotation(angle, offset):
    # Rotation must be specified in degrees :(
    rotation = np.rad2deg(angle + offset)+90
    if angle <= np.pi/2:
        alignment = "center"
        rotation = rotation + 180
    elif 4.3 < angle < np.pi*2:  # 4.71239 is 270 degrees
        alignment = "center"
        rotation = rotation - 180
    else: 
        alignment = "center"
    return rotation, alignment


def add_labels(angles, values, labels, offset, ax, text_colors):

    # This is the space between the end of the bar and the label
    padding = .05

    # Iterate over angles, values, and labels, to add all of them.
    for angle, value, label, text_col in zip(angles, values, labels, text_colors):
        angle = angle

        # Obtain text rotation and alignment
        rotation, alignment = get_label_rotation(angle, offset)

        # And finally add the text
        ax.text(
            x=angle, 
            y=1.05,
            s=label, 
            ha=alignment, 
            va="center", 
            rotation=rotation,
            color=text_col,
        )
def add_labels_dist(angles, values, labels, offset, ax, text_colors, raw_vals_full):

    # This is the space between the end of the bar and the label
    padding = .05

    # Iterate over angles, values, and labels, to add all of them.
    for i, (angle, value, label, text_col) in enumerate(zip(angles, values, labels, text_colors)):
        angle = angle
        
        # Obtain text rotation and alignment
        rotation, alignment = get_label_rotation(angle, offset)

        # And finally add the text
        ax.text(
            x=angle, 
            y=1.05,
            s=label, 
            ha=alignment, 
            va="center", 
            rotation=rotation,
            color=text_col,
        )
        
        data_to_use = raw_vals_full.iloc[:,i+1].tolist()
        mean_val = np.mean(data_to_use)
        std_dev = 0.5*np.std(data_to_use)
        mean_percentile = stats.percentileofscore(data_to_use, mean_val)
        std_dev_up_percentile = stats.percentileofscore(data_to_use, mean_val+std_dev)
        std_dev_down_percentile = stats.percentileofscore(data_to_use, mean_val-std_dev)
        
        ax.hlines(mean_percentile/100, angle - 0.055, angle + 0.055, colors='black', linestyles='dotted', linewidth=2, alpha=0.8, zorder=3)
        ax.hlines(std_dev_up_percentile/100, angle - 0.055, angle + 0.055, colors=text_col, linestyles='dotted', linewidth=2, alpha=0.8, zorder=3)
        ax.hlines(std_dev_down_percentile/100, angle - 0.055, angle + 0.055, colors=text_col, linestyles='dotted', linewidth=2, alpha=0.8, zorder=3)

def scout_report(data_frame, gender, league, season, xtra, template, pos, player_pos, pos_in_sample, mins, minplay, compares, name, ws_name, team, age, sig, extra_text, custom_radar, dist_labels, logo_dict, metric_selections=None):
    plt.clf()
    df = data_frame
    df = df[df['League']==full_league_name].reset_index(drop=True)

    # Filter data
    dfProspect = df[(df['Minutes played'] >= mins)].copy()
    fallback_raw_valsdf = dfProspect[(dfProspect['Player']==ws_name) & (dfProspect['Team within selected timeframe']==team) & (dfProspect['Age']==age)]
    dfProspect = filter_by_position(dfProspect, pos, include_in_sample=pos_in_sample)
    raw_valsdf = dfProspect[(dfProspect['Player']==ws_name) & (dfProspect['Team within selected timeframe']==team) & (dfProspect['Age']==age)]
    if len(raw_valsdf)==0:
        dfProspect = pd.concat([dfProspect,fallback_raw_valsdf],ignore_index=True)
        raw_valsdf = dfProspect[(dfProspect['Player']==ws_name) & (dfProspect['Team within selected timeframe']==team) & (dfProspect['Age']==age)]
    raw_valsdf_full = dfProspect.copy()
    
    fwd1  = 'Non-penalty goals per 90'
    fwd2  = 'npxG per 90'
    fwd3  = 'Assists per 90'
    fwd4  = 'xA per 90'
    fwd5  = 'Successful dribbles, %'
    fwd6  = 'Goal conversion, %'
    fwd7  = 'Shot assists per 90'
    fwd8  = 'Second assists per 90'
    fwd9  = 'Progressive runs per 90'
    fwd10  = 'Progressive passes per 90'
    fwd11  = 'Touches in box per 90'
    fwd12  = 'Aerial duels won, %'
    mid1  = 'Accurate short / medium passes, %'
    mid2  = 'Accurate long passes, %'
    mid3  = 'Accurate smart passes, %'
    mid4  = 'Shot assists per 90'
    mid5  = 'xA per 90'
    mid6  = 'Assists per 90'
    mid7  = 'Second assists per 90'
    mid8  = 'Third assists per 90'
    mid9  = 'Progressive passes per 90'
    mid10  = 'Progressive runs per 90'
    mid11  = 'Duels won, %'
    mid12  = 'pAdj Tkl+Int per 90'
    def1  = 'Successful defensive actions per 90'
    def2  = 'PAdj Sliding tackles'
    def3  = 'Defensive duels won, %'
    def4  = 'Fouls per 90'
    def5  = 'Cards per 90'
    def6  = 'Shots blocked per 90'
    def7  = 'PAdj Interceptions'
    def8  = 'Aerial duels won, %'
    def9  = 'Accurate long passes, %'
    def10  = '1st, 2nd, 3rd assists'
    def11  = 'Progressive passes per 90'
    def12  = 'Progressive runs per 90'
    gk1  = 'Conceded goals per 90'
    gk2  = 'Prevented goals per 90'
    gk3  = 'Shots against per 90'
    gk4  = 'Save rate, %'
    gk5  = 'Clean sheets, %'
    gk6  = 'Exits per 90'
    gk7  = 'Aerial duels per 90'
    gk8  = 'Passes per 90'
    gk9  = 'Accurate long passes, %'
    gk10  = 'Average long pass length, m'
    gk11  = 'Pct of passes being short'
    gk12  = 'Pct of passes being lateral'
    gk13  = 'Received passes per 90'
    gk14  = 'Goals prevented %'
    extra  = 'Accurate passes, %'
    extra2  = 'Shots per 90'
    extra3  = 'Accurate crosses, %'
    extra4  = 'Smart passes per 90'
    extra5  = 'xA per Shot Assist'
    extra6  = 'Accelerations per 90'
    extra7  = 'Aerial duels won per 90'
    extra8  = 'Fouls suffered per 90'
    extra9  = 'npxG per shot'
    extra10  = 'Crosses per 90'
    extra11 = 'Successful crosses per 90'
    extra12 = 'Successful passes to penalty area per 90'
    extra13 = 'Successful progressive passes per 90'
    extra14 = 'Successful through passes per 90'
    extra15 = 'Successful smart passes per 90'
    extra16 = 'Successful dribbles per 90'
    extra17 = 'Key passes per 90'
    extra18 = 'Defensive duels per 90'
    extra19 = 'Head goals per 90'
    extra20 = 'Successful passes to final third per 90'
    extra21 = 'Accurate progressive passes, %'

    df_pros = dfProspect

    ranked_columns = [
        'midpct1', 'midpct2', 'midpct3', 'midpct4', 'midpct5', 'midpct6', 'midpct7',
        'midpct8', 'midpct9', 'midpct10', 'midpct11', 'midpct12',
        'fwdpct1', 'fwdpct2', 'fwdpct3', 'fwdpct4', 'fwdpct5', 'fwdpct6', 'fwdpct7',
        'fwdpct8', 'fwdpct9', 'fwdpct10', 'fwdpct11', 'fwdpct12',
        'gkpct2', 'gkpct4', 'gkpct5', 'gkpct6', 'gkpct7',
        'gkpct8', 'gkpct9', 'gkpct10', 'gkpct11', 'gkpct12', 'gkpct13', 'gkpct14',
        'defpct1','defpct2','defpct3','defpct6','defpct7','defpct8','defpct9','defpct10','defpct11','defpct12',
        'extrapct','extrapct2','extrapct3','extrapct4','extrapct5','extrapct6','extrapct7','extrapct8','extrapct9','extrapct10',
        'extrapct11','extrapct12','extrapct13','extrapct14','extrapct15','extrapct16','extrapct17','extrapct18','extrapct19','extrapct20','extrapct21',
    ]
    inverse_ranked_columns = [
        'defpct4','defpct5','gkpct1','gkpct3'
    ]
    ranked_columns_r = [
        mid1, mid2, mid3, mid4, mid5, mid6, mid7,
        mid8, mid9, mid10, mid11, mid12,
        fwd1, fwd2, fwd3, fwd4, fwd5, fwd6, fwd7,
        fwd8, fwd9, fwd10, fwd11, fwd12,
        gk2, gk4, gk5, gk6, gk7, gk8, gk9, gk10, gk11, gk12, gk13, gk14,
        def1,def2,def3,def6,def7,def8,def9,def10,def11,def12,
        extra,extra2,extra3,extra4,extra5,extra6,extra7,extra8,extra9,extra10,
        extra11,extra12,extra13,extra14,extra15,extra16,extra17,extra18,extra19,extra20,extra21,
    ]
    inverse_ranked_columns_r = [
        def4,def5,gk1,gk3
    ]
    
    dfProspect[ranked_columns] = 0.0
    dfProspect[inverse_ranked_columns] = 0.0

    for column, column_r in zip(ranked_columns, ranked_columns_r):
        dfProspect[column] = rank_column(dfProspect, column_r)
    for column, column_r in zip(inverse_ranked_columns, inverse_ranked_columns_r):
        dfProspect[column] = rank_column_inverse(dfProspect, column_r)

    ######################################################################

    dfRadarMF = dfProspect[(dfProspect['Player']==ws_name) & (dfProspect['Team within selected timeframe']==team) & (dfProspect['Age']==age)].reset_index(drop=True)
    dfRadarMF = dfRadarMF.fillna(0)
    player_full_name = dfRadarMF['Full name'].values[0]
    # Define a dictionary to map old column names to new ones
    if custom_radar == 'n':
        column_mapping = {
            'strikers': {
                'extrapct11' : 'Crosses',
                'extrapct12' : 'Passes\nto box',
                'extrapct14' : 'Through\npasses',
                'extrapct15' : 'Smart\npasses',
                'extrapct13' : 'Prog.\npasses',
                
                'fwdpct7' : 'Shot assists',
                'fwdpct4' : 'xA',
                'fwdpct3' : 'Assists',
                'extrapct17' : 'Key\npasses',
                
                'extrapct6' : 'Accelerations',
                'fwdpct9' : 'Prog.\nruns',
                'extrapct16' : 'Dribbles',
                
                'extrapct7' : 'Aerial\nwins',
                'fwdpct12' : 'Aerial\nwin %',
                'extrapct18' : 'Defensive\nduels',
                'defpct3' : 'Def. duel\nwin %',
                'midpct12' : 'pAdj\nTkl+Int',
                
                'extrapct2' : 'Shots',
                'fwdpct2' : 'npxG',
                'extrapct9' : 'npxG/shot',
                'fwdpct1' : 'Non-pen\ngoals',
                'extrapct19' : 'Head\ngoals',
                'fwdpct6' : 'Goal\nconv. %',
                'fwdpct11' : 'Touches\nin box',
            },
            'wingers': {
                'extrapct3' : 'Cross\nCmp %',
                'extrapct11' : 'Crosses',
                'extrapct12' : 'Passes\nto box',
                'extrapct14' : 'Through\npasses',
                'extrapct15' : 'Smart\npasses',
                'extrapct13' : 'Prog.\npasses',
                
                'fwdpct7' : 'Shot\nassists',
                'fwdpct4' : 'xA',
                'fwdpct3' : 'Assists',
                'extrapct17' : 'Key\npasses',
                
                'extrapct6' : 'Accelerations',
                'fwdpct9' : 'Prog.\nruns',
                'extrapct16' : 'Dribbles',
                'fwdpct5' : 'Dribble\nwin %',
                
                'extrapct7' : 'Aerial\nwins',
                'fwdpct12' : 'Aerial\nwin %',
                'extrapct18' : 'Defensive\nduels',
                'defpct3' : 'Def. duel\nwin %',
                'midpct12' : 'pAdj\nTkl+Int',
                
                'extrapct2' : 'Shots',
                'fwdpct2' : 'npxG',
                'extrapct9' : 'npxG/shot',
                'fwdpct1' : 'Non-pen\ngoals',
                'extrapct19' : 'Head\ngoals',
                'fwdpct6' : 'Goal\nconv. %',
                'fwdpct11' : 'Touches\nin box',
            },
            'midfielders': {
                'gkpct11' : '% passes\nbeing short',
                'midpct2' : 'Long pass\ncmp %',
                'midpct1' : 'Short&med\ncmp %',
                'extrapct13' : 'Prog.\npasses',
                'extrapct20' : 'Passes to\nfinal 3rd',
                
                'extrapct11' : 'Crosses',
                'extrapct12' : 'Passes\nto box',
                'extrapct14' : 'Through\npasses',
                'extrapct15' : 'Smart\npasses',
                
                'fwdpct7' : 'Shot\nassists',
                'fwdpct4' : 'xA',
                'fwdpct3' : 'Assists',
                'extrapct17' : 'Key\npasses',
                
                'fwdpct9' : 'Prog.\nruns',
                'extrapct16' : 'Dribbles',
                
                'extrapct7' : 'Aerial\nwins',
                'fwdpct12' : 'Aerial\nwin %',
                'extrapct18' : 'Defensive\nduels',
                'defpct3' : 'Def. duel\nwin %',
                'defpct7' : 'PAdj\nInt.',
                'defpct2' : 'PAdj\nTackles',
                
                'extrapct2' : 'Shots',
                'fwdpct2' : 'npxG',
                'extrapct9' : 'npxG/shot',
                'fwdpct1' : 'Non-pen\ngoals',
                'fwdpct6' : 'Goal\nconv. %',
                'fwdpct11' : 'Touches\nin box',
            },
            'fullbacks': {
                'extrapct3' : 'Cross\nCmp %',
                'extrapct11' : 'Crosses',
                'extrapct12' : 'Passes\nto box',
                'extrapct14' : 'Through\npasses',

                'extrapct20' : 'Passes to\nfinal 3rd',
                'extrapct13' : 'Prog.\npasses',
                
                'fwdpct7' : 'Shot\nassists',
                'fwdpct4' : 'xA',
                'extrapct17' : 'Key\npasses',
                'defpct10' : '1, 2, 3\nassists',
                
                'fwdpct9' : 'Prog.\nruns',
                'extrapct16' : 'Dribbles',
                
                'extrapct7' : 'Aerial\nwins',
                'fwdpct12' : 'Aerial\nwin %',
                'extrapct18' : 'Defensive\nduels',
                'defpct3' : 'Def. duel\nwin %',
                'defpct7' : 'PAdj\nInt.',
                'defpct2' : 'PAdj\nTackles',
                
                'extrapct2' : 'Shots',
                'fwdpct2' : 'npxG',
                'fwdpct11' : 'Touches\nin box',
            },
            'centerbacks': {
                'gkpct8' : 'Passes',
                'gkpct11' : '% passes\nbeing short',
                'midpct2' : 'Long pass\ncmp %',
                'extrapct20' : 'Passes to\nfinal 3rd',
                'extrapct13' : 'Prog.\npasses',

                'extrapct11' : 'Crosses',
                'extrapct14' : 'Through\npasses',
                'fwdpct4' : 'xA',
                'defpct10' : '1, 2, 3\nassists',
                
                'fwdpct9' : 'Prog.\nruns',
                
                'extrapct7' : 'Aerial\nwins',
                'fwdpct12' : 'Aerial\nwin %',
                'defpct3' : 'Def. duel\nwin %',
                'midpct12' : 'pAdj\nTkl+Int',
                'defpct4' : 'Fouls',
                
                'extrapct2' : 'Shots',
                'fwdpct2' : 'npxG',
                'fwdpct11' : 'Touches\nin box',
            },
            'goalkeepers': {
                'gkpct8' : 'Passes',
                'gkpct13' : 'Received\npasses',
                'gkpct12' : '% passes\nbeing lateral',
                'midpct2' : 'Long pass\ncmp %',
                'fwdpct10' : 'Prog. passes',
                'extrapct21' : 'Prog. pass\ncmp %',
                
                'gkpct3' : 'Shots against',
                'gkpct1' : 'Conceded goals',
                'gkpct4' : 'Save %',
                'gkpct2' : 'Prevented goals',
                'gkpct14' : 'Goals prevented %',
                'gkpct6' : 'Exits',
            }
        }
        if template == 'strikers':
            raw_vals = raw_valsdf[["Player",
                               extra11,extra12,extra14,extra15,extra13,fwd7 ,fwd4 ,fwd3 ,extra17,extra6 ,fwd9 ,extra16 ,extra7 ,fwd12 ,extra18,def3 ,mid12 ,extra2 ,fwd2 ,extra9 ,fwd1 ,extra19,fwd6 ,fwd11
                              ]]
            raw_vals_full = raw_valsdf_full[["Player",
                               extra11,extra12,extra14,extra15,extra13,fwd7 ,fwd4 ,fwd3 ,extra17,extra6 ,fwd9 ,extra16 ,extra7 ,fwd12 ,extra18,def3 ,mid12 ,extra2 ,fwd2 ,extra9 ,fwd1 ,extra19,fwd6 ,fwd11
                              ]]
        if template == 'wingers':
            raw_vals = raw_valsdf[["Player",
                                extra3 ,extra11,extra12,extra14,extra15,extra13,fwd7 ,fwd4 ,fwd3 ,extra17,extra6 ,fwd9 ,extra16,fwd5 ,extra7 ,fwd12 ,extra18,def3 ,mid12 ,extra2 ,fwd2 ,extra9 ,fwd1 ,extra19,fwd6 ,fwd11
                              ]]
            raw_vals_full = raw_valsdf_full[["Player",
                                extra3 ,extra11,extra12,extra14,extra15,extra13,fwd7 ,fwd4 ,fwd3 ,extra17,extra6 ,fwd9 ,extra16,fwd5 ,extra7 ,fwd12 ,extra18,def3 ,mid12 ,extra2 ,fwd2 ,extra9 ,fwd1 ,extra19,fwd6 ,fwd11
                              ]]
        if template == 'midfielders':
            raw_vals = raw_valsdf[["Player",
                                gk11 ,mid2 ,mid1, extra13, extra20 ,extra11,extra12,extra14,extra15,fwd7 ,fwd4 ,fwd3,extra17,fwd9 ,extra16 ,extra7 ,fwd12 ,extra18,def3 ,def7 ,def2 ,extra2 ,fwd2 ,extra9 ,fwd1 ,fwd6 ,fwd11
                              ]]
            raw_vals_full = raw_valsdf_full[["Player",
                                gk11 ,mid2 ,mid1, extra13, extra20 ,extra11,extra12,extra14,extra15,fwd7 ,fwd4 ,fwd3,extra17,fwd9 ,extra16 ,extra7 ,fwd12 ,extra18,def3 ,def7 ,def2 ,extra2 ,fwd2 ,extra9 ,fwd1 ,fwd6 ,fwd11
                              ]]
        if template == 'fullbacks':
            raw_vals = raw_valsdf[["Player",
                                extra3 ,extra11,extra12,extra14,extra20,extra13,fwd7 ,fwd4 ,extra17,def10 ,fwd9 ,extra16 ,extra7 ,fwd12 ,extra18,def3 ,def7 ,def2 ,extra2 ,fwd2 ,fwd11
                              ]]
            raw_vals_full = raw_valsdf_full[["Player",
                                extra3 ,extra11,extra12,extra14,extra20,extra13,fwd7 ,fwd4 ,extra17,def10 ,fwd9 ,extra16 ,extra7 ,fwd12 ,extra18,def3 ,def7 ,def2 ,extra2 ,fwd2 ,fwd11
                              ]]
        if template == 'centerbacks':
            raw_vals = raw_valsdf[["Player",
                                gk8 ,gk11 ,mid2, extra20, extra13 ,extra11,extra14,fwd4 ,def10 ,fwd9 ,extra7 ,fwd12 ,def3 ,mid12 ,def4 ,extra2 ,fwd2 ,fwd11
                              ]]
            raw_vals_full = raw_valsdf_full[["Player",
                                gk8 ,gk11 ,mid2, extra20, extra13 ,extra11,extra14,fwd4 ,def10 ,fwd9 ,extra7 ,fwd12 ,def3 ,mid12 ,def4 ,extra2 ,fwd2 ,fwd11
                              ]]
        if template == 'goalkeepers':
            raw_vals = raw_valsdf[["Player",
                                gk8 ,gk13 ,gk12 ,mid2 ,fwd10 ,extra21,gk3 ,gk1 ,gk4 ,gk2 ,gk14 ,gk6 ,
                              ]]
            raw_vals_full = raw_valsdf_full[["Player",
                                gk8 ,gk13 ,gk12 ,mid2 ,fwd10 ,extra21,gk3 ,gk1 ,gk4 ,gk2 ,gk14 ,gk6 ,
                              ]]
        if template in column_mapping:
            selected_columns = column_mapping[template]
            dfRadarMF = dfRadarMF[['Player'] + list(selected_columns.keys())]
            dfRadarMF.rename(columns=selected_columns, inplace=True)
    if custom_radar == 'y':
        all_possible_vars = ['Received passes per 90','Passes per 90','Pct of passes being short','Pct of passes being lateral','Accurate passes, %','Accurate short / medium passes, %','Accurate long passes, %','Crosses per 90','Accurate crosses, %','Smart passes per 90','Shot assists per 90','xA per 90','xA per Shot Assist','Assists per 90','Second assists per 90','Third assists per 90','1st, 2nd, 3rd assists','Progressive passes per 90','Progressive runs per 90','Shots per 90','npxG per 90','Non-penalty goals per 90','npxG per shot','Goal conversion, %','Successful dribbles, %','Accelerations per 90','Touches in box per 90','Fouls suffered per 90','Successful defensive actions per 90','Duels won, %','Defensive duels won, %','pAdj Tkl+Int per 90','PAdj Sliding tackles','PAdj Interceptions','Shots blocked per 90','Aerial duels per 90','Aerial duels won, %','Aerial duels won per 90','Fouls per 90','Shots against per 90','Conceded goals per 90','Save rate, %','Prevented goals per 90','Goals prevented %','Clean sheets, %','Exits per 90','Average long pass length, m']
        names = ['Received\nPasses','Passes','% of Passes\nBeing Short','% of Passes\nBeing Lateral','Pass\nCmp %','Short & Med\nPass %','Long\nPass %','Crosses','Cross\nCompletion %','Smart\nPasses','Shot\nAssists','Expected\nAssists (xA)','xA per\nShot Assist','Assists','Second\nAssists','Third\nAssists','Assists &\n2nd/3rd Assists','Prog.\nPasses','Prog.\nCarries','Shots','npxG','Non-Pen\nGoals','npxG\nper shot','Goals/Shot\non Target %','Dribble\nSuccess %','Acceleration\nwith Ball','Touches in\nPen Box','Fouls\nDrawn','Defensive\nActions','Duel Win%','Defensive\nDuels Won %','Tackles & Int\n(pAdj)','Tackles\n(pAdj)','Interceptions\n(pAdj)','Shot\nBlocks','Aerial\nDuels','Aerial\nWin %','Aerial Duels\nWon','Fouls','Shots\nAgainst','Goals\nConceded','Save %','Prevented\nGoals','Goals\nPrevented %','Clean\nSheets %','Coming Off\nLine','Long Pass\nLength (m)']
        base_var_names = ['gkpct13','gkpct8','gkpct11','gkpct12','extrapct','midpct1','midpct2','extrapct10','extrapct3','extrapct4','midpct4','midpct5','extrapct5','midpct6','midpct7','midpct8','defpct10','midpct9','midpct10','extrapct2','fwdpct2','fwdpct1','extrapct9','fwdpct6','fwdpct5','extrapct6','fwdpct11','extrapct8','defpct1','midpct11','defpct3','midpct12','defpct2','defpct7','defpct6','gkpct7','defpct8','extrapct7','defpct4','gkpct3','gkpct1','gkpct4','gkpct2','gkpct14','gkpct5','gkpct6','gkpct10']
        ix_selected = []
        for i, l in enumerate(all_possible_vars):
            if l in metric_selections:
                ix_selected+=[i]
        metric_rename = []
        for ix in ix_selected:
            metric_rename+=[names[ix]]
        base_vars = []
        for ix in ix_selected:
            base_vars+=[base_var_names[ix]]
        column_mapping = dict(zip(base_vars, metric_rename))

        use_these_cols = ["Player"]+metric_selections
        raw_vals = raw_valsdf[use_these_cols]
        raw_vals_full = raw_valsdf_full[use_these_cols]
        
        selected_columns = column_mapping
        dfRadarMF = dfRadarMF[['Player'] + list(selected_columns.keys())]
        dfRadarMF.rename(columns=selected_columns, inplace=True)

        v_passing = ['Received passes per 90','Passes per 90','Pct of passes being short','Pct of passes being lateral','Accurate passes, %','Accurate short / medium passes, %','Accurate long passes, %','Crosses per 90','Accurate crosses, %']
        v_playmaking = ['Smart passes per 90','Shot assists per 90','xA per 90','xA per Shot Assist','Assists per 90','Second assists per 90','Third assists per 90','1st, 2nd, 3rd assists','Progressive passes per 90','Progressive runs per 90']
        v_shooting = ['Shots per 90','npxG per 90','Non-penalty goals per 90','npxG per shot','Goal conversion, %']
        v_attacking = ['Successful dribbles, %','Accelerations per 90','Touches in box per 90','Fouls suffered per 90']
        v_defending = ['Successful defensive actions per 90','Duels won, %','Defensive duels won, %','pAdj Tkl+Int per 90','PAdj Sliding tackles','PAdj Interceptions','Shots blocked per 90','Aerial duels per 90','Aerial duels won, %','Aerial duels won per 90','Fouls per 90']
        v_goalkeeping = ['Shots against per 90','Conceded goals per 90','Save rate, %','Prevented goals per 90','Goals prevented %','Clean sheets, %','Exits per 90','Average long pass length, m']
        
        passing_l = 0
        playmaking_l = 0
        shooting_l = 0
        attacking_l = 0
        defending_l = 0
        goalkeeping_l = 0

        for i, l in enumerate(v_passing):
            if l in metric_selections:
                passing_l+=1
        for i, l in enumerate(v_playmaking):
            if l in metric_selections:
                playmaking_l+=1
        for i, l in enumerate(v_shooting):
            if l in metric_selections:
                shooting_l+=1
        for i, l in enumerate(v_attacking):
            if l in metric_selections:
                attacking_l+=1
        for i, l in enumerate(v_defending):
            if l in metric_selections:
                defending_l+=1
        for i, l in enumerate(v_goalkeeping):
            if l in metric_selections:
                goalkeeping_l+=1
        
    ###########################################################################

    df1 = dfRadarMF.T.reset_index()

    df1.columns = df1.iloc[0] 

    df1 = df1[1:]
    df1 = df1.reset_index()
    df1 = df1.rename(columns={'Player': 'Metric',
                        ws_name: 'Value',
                             'index': 'Group'})

    if custom_radar == 'y':
        for i in range(len(df1)):
            if df1['Group'][i] <= passing_l:
                df1['Group'][i] = 'Passing'
            elif df1['Group'][i] <= passing_l+playmaking_l:
                df1['Group'][i] = 'Playmaking'
            elif df1['Group'][i] <= passing_l+playmaking_l+shooting_l:
                df1['Group'][i] = 'Shooting'
            elif df1['Group'][i] <= passing_l+playmaking_l+shooting_l+attacking_l:
                df1['Group'][i] = 'Attacking'
            elif df1['Group'][i] <= passing_l+playmaking_l+shooting_l+attacking_l+defending_l:
                df1['Group'][i] = 'Defending'
            elif df1['Group'][i] <= passing_l+playmaking_l+shooting_l+attacking_l+defending_l+goalkeeping_l:
                df1['Group'][i] = 'Goalkeeping'
    if custom_radar == 'n':
        if template == 'strikers':
            for i in range(len(df1)):
                if df1['Group'][i] <= 5:
                    df1['Group'][i] = 'Passing'
                elif df1['Group'][i] <= 9:
                    df1['Group'][i] = 'Creativity'
                elif df1['Group'][i] <= 12:
                    df1['Group'][i] = 'Shooting'
                elif df1['Group'][i] <= 17:
                    df1['Group'][i] = 'Ball Movement'
                elif df1['Group'][i] <= 24:
                    df1['Group'][i] = 'Defense'
    
        if template == 'wingers':
            for i in range(len(df1)):
                if df1['Group'][i] <= 6:
                    df1['Group'][i] = 'Passing'
                elif df1['Group'][i] <= 10:
                    df1['Group'][i] = 'Creativity'
                elif df1['Group'][i] <= 14:
                    df1['Group'][i] = 'Shooting'
                elif df1['Group'][i] <= 19:
                    df1['Group'][i] = 'Ball Movement'
                elif df1['Group'][i] <= 26:
                    df1['Group'][i] = 'Defense'
    
        if template == 'midfielders':
            for i in range(len(df1)):
                if df1['Group'][i] <= 5:
                    df1['Group'][i] = 'Passing'
                elif df1['Group'][i] <= 9:
                    df1['Group'][i] = 'Creativity'
                elif df1['Group'][i] <= 13:
                    df1['Group'][i] = 'Shooting'
                elif df1['Group'][i] <= 15:
                    df1['Group'][i] = 'Ball Movement'
                elif df1['Group'][i] <= 21:
                    df1['Group'][i] = 'Defense'
                elif df1['Group'][i] <= 27:
                    df1['Group'][i] = 'Direct'
                    
        if template == 'fullbacks':
            for i in range(len(df1)):
                if df1['Group'][i] <= 4:
                    df1['Group'][i] = 'Passing'
                elif df1['Group'][i] <= 6:
                    df1['Group'][i] = 'Creativity'
                elif df1['Group'][i] <= 10:
                    df1['Group'][i] = 'Shooting'
                elif df1['Group'][i] <= 12:
                    df1['Group'][i] = 'Ball Movement'
                elif df1['Group'][i] <= 18:
                    df1['Group'][i] = 'Defense'
                elif df1['Group'][i] <= 21:
                    df1['Group'][i] = 'Direct'
                    
        if template == 'centerbacks':
            for i in range(len(df1)):
                if df1['Group'][i] <= 5:
                    df1['Group'][i] = 'Passing'
                elif df1['Group'][i] <= 9:
                    df1['Group'][i] = 'Creativity'
                elif df1['Group'][i] <= 10:
                    df1['Group'][i] = 'Shooting'
                elif df1['Group'][i] <= 15:
                    df1['Group'][i] = 'Ball Movement'
                elif df1['Group'][i] <= 18:
                    df1['Group'][i] = 'Defense'
                    
        if template == 'goalkeepers':
            for i in range(len(df1)):
                if df1['Group'][i] <= 6:
                    df1['Group'][i] = 'Defending'
                elif df1['Group'][i] <= 12:
                    df1['Group'][i] = 'Attacking'


    #####################################################################

    ### This link below is where I base a lot of my radar code off of
    ### https://www.python-graph-gallery.com/circular-barplot-with-groups

    #### I DEFINED THE LABEL AND ROTATION HERE


    # Grab the group values
    GROUP = df1["Group"].values
    VALUES = df1["Value"].values
    LABELS = df1["Metric"].values
    OFFSET = np.pi / 2

    PAD = 2
    ANGLES_N = len(VALUES) + PAD * len(np.unique(GROUP))
    ANGLES = np.linspace(0, 2 * np.pi, num=ANGLES_N, endpoint=False)
    WIDTH = (2 * np.pi) / len(ANGLES)

    offset = 0
    IDXS = []

    if custom_radar == 'n':
        template_group_sizes = {
            'strikers': [5,4,3,5,7],
            'wingers': [6,4,4,5,7],
            'midfielders': [5,4,4,2,6,6],
            'fullbacks': [4,2,4,2,6,3],
            'centerbacks': [5,4,1,5,3],
            'goalkeepers': [6,6],
        }
    if custom_radar == 'y':
        len_list = [passing_l,playmaking_l,shooting_l,attacking_l,defending_l,goalkeeping_l]
        len_list = [i for i in len_list if i != 0]
        template_group_sizes = {
            'custom': len_list,
        }

    GROUPS_SIZE = template_group_sizes.get(template, [])



    for size in GROUPS_SIZE:
        IDXS += list(range(offset + PAD, offset + size + PAD))
        offset += size + PAD

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": "polar"})
    ax.set_theta_offset(OFFSET)
    ax.set_ylim(-.5, 1)
    ax.set_frame_on(False)
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])


    COLORS = [f"C{i}" for i, size in enumerate(GROUPS_SIZE) for _ in range(size)]

    ax.bar(
        ANGLES[IDXS], VALUES, width=WIDTH, color=COLORS,
        edgecolor="#4A2E19", linewidth=1
    )

    offset = 0 
    for group, size in zip(GROUPS_SIZE, GROUPS_SIZE):
        # Add line below bars
        x1 = np.linspace(ANGLES[offset + PAD], ANGLES[offset + size + PAD - 1], num=50)
        ax.plot(x1, [-.02] * 50, color="#4A2E19")


        # Add reference lines at 20, 40, 60, and 80
        x2 = np.linspace(ANGLES[offset], ANGLES[offset + PAD - 1], num=50)
        ax.plot(x2, [.2] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [.4] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [.60] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [.80] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [1] * 50, color="#bebebe", lw=0.8)

        offset += size + PAD
        
    text_cs = []
    text_inv_cs = []
    for i, bar in enumerate(ax.patches):
        pc = 1 - bar.get_height()

        if pc <= 0.1:
            color = ('#01349b', '#d9e3f6')  # Elite
        elif 0.1 < pc <= 0.35:
            color = ('#007f35', '#d9f0e3')  # Above Avg
        elif 0.35 < pc <= 0.66:
            color = ('#9b6700', '#fff2d9')  # Avg
        else:
            color = ('#b60918', '#fddbde')  # Below Avg

        if bar_colors == 'Benchmarking Percentiles':
            bar.set_color(color[1])
            bar.set_edgecolor(color[0])

        text_cs.append(color[0])
        text_inv_cs.append(color[1])
        
    callout_text = ''
    title_note = ''

    if callout == 'Per 90':
        callout_text = "per 90'"
        title_note = ' & Per 90 Values'
    elif callout == 'Percentile':
        callout_text = 'percentile'

    for i, bar in enumerate(ax.patches):
        if bar_colors == 'Metric Groups':
            if callout == 'Per 90':
                value_format = f'{round(raw_vals.iloc[0][i+1], 2)}'
            else:
                value_format = format(bar.get_height() * 100, '.0f')
            color = 'black'
            face = 'white'
        elif bar_colors == 'Benchmarking Percentiles':
            if callout == 'Per 90':
                value_format = f'{round(raw_vals.iloc[0][i+1], 2)}'
            else:
                value_format = format(bar.get_height() * 100, '.0f')
            color = text_inv_cs[i]
            face = text_cs[i]

        ax.annotate(value_format,
                    (bar.get_x() + bar.get_width() / 2, bar.get_height() - 0.1),
                    ha='center', va='center', size=10, xytext=(0, 8),
                    textcoords='offset points', color=color, zorder=4,
                    bbox=dict(boxstyle="round", fc=face, ec="black", lw=1))

    if dist_labels == 'Yes':
        add_labels_dist(ANGLES[IDXS], VALUES, LABELS, OFFSET, ax, text_cs, raw_vals_full)
    if dist_labels == 'No':
        add_labels(ANGLES[IDXS], VALUES, LABELS, OFFSET, ax, text_cs)

    PAD = 0.02
    ax.text(0.15, 0 + PAD, "0", size=10, color='#4A2E19')
    ax.text(0.15, 0.2 + PAD, "20", size=10, color='#4A2E19')
    ax.text(0.15, 0.4 + PAD, "40", size=10, color='#4A2E19')
    ax.text(0.15, 0.6 + PAD, "60", size=10, color='#4A2E19')
    ax.text(0.15, 0.8 + PAD, "80", size=10, color='#4A2E19')
    ax.text(0.15, 1 + PAD, "100", size=10, color='#4A2E19')

    plt.suptitle(f'{player_full_name.replace("  "," ")} ({age}, {player_pos}, {minplay} mins.), {team}\n{season} {league} Percentile Rankings{title_note}',
                 fontsize=17,
                 fontfamily="DejaVu Sans",
                color="#4A2E19", #4A2E19
                 fontweight="bold", fontname="DejaVu Sans",
                x=0.5,
                y=.97)

    if dist_labels == 'Yes':
        dist_text = "\nBlack dot line = metric mean\nColored dot line = +/- 0.5 std. deviations"
    if dist_labels == 'No':
        dist_text = ""
    plt.annotate(f"Bars are percentiles | Values shown are {callout_text} values\nAll values are per 90 minutes | %s\nCompared to %s %s, %i+ mins\nData: Wyscout | Sample Size: %i players{dist_text}" %(extra_text, league, compares, mins, len(dfProspect)),
                 xy = (0, -.09), xycoords='axes fraction',
                ha='left', va='center',
                fontsize=9, fontfamily="DejaVu Sans",
                color="#4A2E19", fontweight="regular", fontname="DejaVu Sans",
                ) 

    try:
        clubpath = logo_dict[raw_valsdf['Team within selected timeframe'].values[0]]
        image = Image.open(urllib.request.urlopen(clubpath))
        newax = fig.add_axes([.44,.43,0.15,0.15], anchor='C', zorder=1)
        newax.imshow(image)
        newax.axis('off')
    except:
        pass

    ax.set_facecolor('#fbf9f4')
    fig = plt.gcf()
    fig.patch.set_facecolor('#fbf9f4')
    fig.set_size_inches(12, (12*.9)) #length, height
    
    fig_text(
        0.88, 0.055, "\n\n\n\n\n<Elite (Top 10%)>\n<Above Average (11-35%)>\n<Average (36-66%)>\n<Below Average (Bottom 35%)>", color="#4A2E19",
        highlight_textprops=[{"color": '#01349b'},
                             {'color' : '#007f35'},
                             {"color" : '#9b6700'},
                             {'color' : '#b60918'},
                            ],
        size=10, fig=fig, ha='right',va='center'
    )



    return fig

def create_player_research_table(df_basic, mins, pos, min_age, max_age):
    dfProspect = df_basic[(df_basic['Minutes played'] >= mins)].copy()
    dfProspect = filter_by_position_long(dfProspect, pos)
    
    ########## PROSPECT RESEARCH ##########
    #######################################
    
    # FORWARD
    fwd1 = "Non-penalty goals per 90"
    fwd2 = "npxG per 90"
    fwd3 = "Assists per 90"
    fwd4 = "xA per 90"
    fwd5 = "Successful dribbles, %"
    fwd6 = "Goal conversion, %"
    fwd7 = "Shot assists per 90"
    fwd8 = "Second assists per 90"
    fwd9 = "Progressive runs per 90"
    fwd10 = "Progressive passes per 90"
    fwd11 = "Touches in box per 90"
    fwd12 = "Aerial duels won, %"
    # MIDFIELD
    mid1 = "Accurate short / medium passes, %"
    mid2 = "Accurate long passes, %"
    mid3 = "Passes per 90" ## changed from smart pass cmp %
    mid4 = "Shot assists per 90"
    mid5 = "xA per 90"
    mid6 = "Assists per 90"
    mid7 = "Second assists per 90"
    mid8 = "Third assists per 90"
    mid9 = "Progressive passes per 90"
    mid10 = "Progressive runs per 90"
    mid11 = "Duels won, %"
    mid12 = "pAdj Tkl+Int per 90"
    #DEFENDER
    def1 = "Successful defensive actions per 90"
    def2 = "PAdj Sliding tackles"
    def3 = "Defensive duels won, %"
    def4 = "Fouls per 90"
    def5 = "Cards per 90"
    def6 = "Shots blocked per 90"
    def7 = "PAdj Interceptions"
    def8 = "Aerial duels won, %"
    def9 = "Accurate long passes, %"
    def10 = "1st, 2nd, 3rd assists"
    def11 = "Progressive passes per 90"
    def12 = "Progressive runs per 90"
    #GOALKEEPER
    gk1 = "Conceded goals per 90" #a2
    gk2 = "Save rate, %" #a3
    gk3 = "Dribbles per 90"
    gk4 = "Pct of passes being short" #b3
    gk5 = "Clean sheets, %"
    gk6 = "Exits per 90" #a5
    gk7 = "Aerial duels per 90"
    gk8 = "Passes per 90" #b2
    gk9 = "Accurate long passes, %" #b5
    gk10 = "Prevented goals per 90" #a4
    gk11 = 'Shots against per 90' #a1
    gk12 = 'Pct of passes being lateral' #b4
    gk13 = 'Received passes per 90' #b1
    gk14 = 'Goals prevented %' #b1
    #EXTRA
    extra = "Accurate passes, %"
    extra2 = 'Shots per 90'
    extra3 = 'Accurate crosses, %'
    extra4 = 'Smart passes per 90'
    extra5 = 'xA per Shot Assist'
    extra6 = 'Accelerations per 90'
    extra7 = 'Aerial duels won per 90'
    extra8 = 'Fouls suffered per 90'
    extra9 = 'npxG per shot'
    extra10 = 'Crosses per 90'
    extra11 = 'Successful dribbles per 90'
    
    ranked_columns = [
        'midpct1', 'midpct2', 'midpct3', 'midpct4', 'midpct5', 'midpct6', 'midpct7',
        'midpct8', 'midpct9', 'midpct10', 'midpct11', 'midpct12',
        'fwdpct1', 'fwdpct2', 'fwdpct3', 'fwdpct4', 'fwdpct5', 'fwdpct6', 'fwdpct7',
        'fwdpct8', 'fwdpct9', 'fwdpct10', 'fwdpct11', 'fwdpct12',
        'gkpct2', 'gkpct4', 'gkpct5', 'gkpct6', 'gkpct7',
        'gkpct8', 'gkpct9', 'gkpct10', 'gkpct11', 'gkpct12', 'gkpct13', 'gkpct14',
        'defpct1','defpct2','defpct3','defpct6','defpct7','defpct8','defpct9','defpct10','defpct11','defpct12',
        'extrapct','extrapct2','extrapct3','extrapct4','extrapct5','extrapct6','extrapct7','extrapct8','extrapct9','extrapct10','extrapct11',
    ]
    inverse_ranked_columns = [
        'defpct4','defpct5','gkpct1','gkpct3'
    ]
    ranked_columns_r = [
        mid1, mid2, mid3, mid4, mid5, mid6, mid7,
        mid8, mid9, mid10, mid11, mid12,
        fwd1, fwd2, fwd3, fwd4, fwd5, fwd6, fwd7,
        fwd8, fwd9, fwd10, fwd11, fwd12,
        gk2, gk4, gk5, gk6, gk7, gk8, gk9, gk10, gk11, gk12, gk13, gk14,
        def1,def2,def3,def6,def7,def8,def9,def10,def11,def12,
        extra,extra2,extra3,extra4,extra5,extra6,extra7,extra8,extra9,extra10,extra11,
    ]
    inverse_ranked_columns_r = [
        def4,def5,gk1,gk3
    ]
    
    dfProspect[ranked_columns] = 0.0
    dfProspect[inverse_ranked_columns] = 0.0
    
    for column, column_r in zip(ranked_columns, ranked_columns_r):
        # dfProspect[column] = rank_column(dfProspect, column_r)
        dfProspect[column] = dfProspect[column_r]
    for column, column_r in zip(inverse_ranked_columns, inverse_ranked_columns_r):
        # dfProspect[column] = rank_column_inverse(dfProspect, column_r)
        dfProspect[column] = dfProspect[column_r]
    
    final = dfProspect[['Player','Age','League','Position','Team within selected timeframe','Birth country',
    'fwdpct1','fwdpct2','fwdpct5','fwdpct6','fwdpct11','midpct1','midpct3','midpct4','midpct5','midpct6','midpct7','midpct8','midpct9','midpct10','midpct11','midpct12','defpct1','defpct2','defpct3','defpct4','defpct5','defpct6','defpct7','defpct8','defpct9','defpct10',
                        'gkpct1','gkpct2','gkpct3','gkpct4','gkpct6','gkpct8','gkpct9', 'gkpct11', 'gkpct12', 'gkpct13', 'gkpct14',
                        'extrapct','extrapct2','extrapct3','extrapct4','extrapct5','extrapct6','extrapct7','extrapct8','extrapct9','extrapct10','extrapct11',
    ]]
    
    final.rename(columns={'fwdpct1': "Non-penalty goals per 90",
    'fwdpct2': "npxG per 90",
    'fwdpct5': "Successful dribbles, %",
    'fwdpct6': "Goal conversion, %",
    'fwdpct11': "Touches in box per 90",
    'midpct1': "Accurate short / medium passes, %",
    'midpct3': "Passes per 90",
    'midpct4': "Shot assists per 90",
    'midpct5': "xA per 90",
    'midpct6': "Assists per 90",
    'midpct7': "Second assists per 90",
    'midpct8': "Third assists per 90",
    'midpct9': "Progressive passes per 90",
    'midpct10': "Progressive runs per 90",
    'midpct11': "Duels won, %",
    'midpct12': "pAdj Tkl+Int per 90",
    'defpct1': "Successful defensive actions per 90",
    'defpct2': "PAdj Sliding tackles",
    'defpct3': "Defensive duels won, %",
    'defpct4': "Fouls per 90",
    'defpct5': "Cards per 90",
    'defpct6': "Shots blocked per 90",
    'defpct7': "PAdj Interceptions",
    'defpct8': "Aerial duels won, %",
    'defpct9': "Accurate long passes, %",
    'defpct10': "1st, 2nd, 3rd assists",
    'gkpct3': 'Shots against per 90',
    'gkpct1': "Conceded goals per 90",
    'gkpct4': "Save rate, %",
    'gkpct14': "Goals prevented %",
    'gkpct2': 'Prevented goals per 90',
    'gkpct6': "Exits per 90",
    'gkpct13': 'Received\nPasses',
    'gkpct8': "Passes",
    'gkpct11': "% of Passes\nBeing Short",
    'gkpct12': "% of Passes\nBeing Lateral",
    'gkpct9': "Long Pass\nCmp %",
    'extrapct': "Accurate passes, %",
    'extrapct2': "Shots per 90",
    'extrapct3': "Accurate crosses, %",
    'extrapct4': "Smart passes per 90",
    'extrapct5': "xA per Shot Assist",
    'extrapct6': "Accelerations per 90",
    'extrapct7': "Aerial duels won per 90",
    'extrapct8': "Fouls suffered per 90",
    'extrapct9': "npxG per shot",
    'extrapct10': "Crosses per 90",
    'extrapct11': 'Successful dribbles per 90',
    'Team within selected timeframe': 'Team',
    }, inplace=True)
    
    
    final.Age = final.Age.astype(int)
    final.sort_values(by=['Age'], inplace=True)
    final = final[final['Age'].between(min_age,max_age)].reset_index(drop=True)
    final.fillna(0,inplace=True)
    
    return final

#######################################################################################################################################
formation_positions = {442:['GK','RCB','LCB','RB','LB','RCM','LCM','RW','LW','RS','LS',],
                      4231:['GK','RCB','LCB','RB','LB','RCM','LCM','CAM','RW','LW','ST'],
                      433:['GK','RCB','LCB','RB','LB','RCM','CM','LCM','RW','LW','ST'],
                      343:['GK','RCB','CB','LCB','RB','LB','RCM','LCM','RW','LW','ST'],
                       4222:['GK','RCB','LCB','RB','LB','RCM','LCM','RAM','LAM','RS','LS',],
                      }

rank_11_base = read_csv('https://raw.githubusercontent.com/griffisben/misc-code/main/RoleRanksApp/Ranking_XI.csv')
role_position_lookup = read_csv('https://raw.githubusercontent.com/griffisben/misc-code/main/RoleRanksApp/Role_Positions_Lookup.csv')

with st.expander('Instructions'):
    st.write('''
    1) Select whether you want Men's or Women's competitions  \n
    2) Select your league  \n
    3) Select the season for your competition. "24-25", "2024", etc.  \n
    4) Select the base formation you want for the roles. There are only a few loaded, as this is not an exhaustive list and all roles can be generated in these formation. These are rough so that we can get different *general* shapes and combinations (like 2-3 CBs, 2-3 CMs, CAM, 1-2 STs, & wingers or no wingers. I may add more formations later  \n
    5) Input a minimum minutes threshold. Only players who have played at least this many minutes will be included in the sample. Beware of small sample sizes/variance issues for players with less than around 720 minutes. The app will never allow fewer than 400 minutes, and even this is a low number of minutes anyway.  \n
    6) Select an age range for the Best XI roles. This can account for all ages (keep at 0-45), a minimum age (move the left-most slider to your desired minimum), a maximum age (move the right-most slider to your desired maximum), or a specific range of ages (move both sliders to your desired range, minimum & maximum)... note that players with no age in Wyscout are given age = 0; this is more of an issue in "lower" level nations/leagues  \n
    7) Select if you want only players with contracts expiring on or before a specific date to be included. This feature can help you find potential free transfers. Please note that these are from Wyscout, which are pulled from Transfermarkt, and may not be totally accurate (some players also have no contract expiration date noted and are therefore not included if you slecet "Yes" for this option, so beware of the data quality here)  \n
    8) Enter your desired contract expiration date if needed  \n
    9) Select the number of players you want to see for each role. Please note that if you select more than 7, the Best XI image will only show the top 7, however the table will still show you all players  \n
    10) Select whether you want to normalize role-ranking scores from 0 (lowest score) to 100 (top score), or if you want the raw role-ranking scores (which range from 0 to 100, with 0 meaning the player has the lowest recorded numbers in every included metric, and 100 meaning the player has recorded the highest number in every metric, but 100 is then a much rarer score and sometimes the best player can score in the 70s)  \n
    11) If you want to only see players of specific nationalities (that also meet the minutes, age, and contract filters above), select your nations. Leave blank if you want to see all players regardless of nationality  \n
    12) Choose all of your roles by position. Once you've made any changes, click the "Update Roles" button  \n
    13) Select whether you want to show players from all teams, or if you want to create a single team's depth chart. Please note that if you create a depth chart, the player scores are all still ranked against all players in that position in the league, not just the team  \n  \n
    Tabs:  \n
    1) Role Ranking Image - this tab is the default, and shows the Best XI nased on all your selected criteria  \n
    2) Role Ranking Table - this tab allows you to view the Best XI in table format. Remember that if you selected more than a Top 7, this tab will have all players, not just the top 7 shown on the image  \n
    3) Player Radar Generation - this tab is where you can add a player's name and age in order to create their radar. Select how you want to color the radar's bars & if you want the player's actual per 90 data to be called out on each bar or if you want the percentiles instead. Then click "Submit Options" to generate their radar  \n
    Pre-Made vs Custom Radar - the default setting here is the pre-made radar, which is a general template based on a player's position (attacking, defensive, CB, GK). However, you can also select your own metrics to include in the radar instead! First, select "Custom", and then click Submit. Then you can choose what metrics you want to include in your custom radar. Click submit again to generate the radar with your selected metrics. Every once in a while, Streamlit will whack out and if there's no image generating, make sure to check your player name & age again, sometimes the age changes randomly, sometimes the name disappears. When in doubt, clikc "Run" at the top or "Submit Options".  \n
    4) Player List - this is a simple list of all players in the league & basic info like age, minutes, and positions that you can use for the Radar generation.  \n
    4) Similar Player Search - this tab helps you find similar players to a focal player, using Cosine similarity. You can use the 'Player List' tab to find a Wyscout ID for a focal player, then ensure that their league is included in the sample (region, country, continent, or league).  \n
    6) Player Search, Filters - this tab allows you to define a position group that you want to find players for, and then set minimum percentile filters that players must meet in order to be shown in a table. This way, you can find players meeting specific requirements, instead of just relying on the role-scores to find players for you.  \n
    7) Player Search, Results - this tab shows a table of players who meet your filterin criteria set in the Player Search, Filters tab. Please note that the League, Season, Minutes Played, and Age Range filters on the sidebar will pass to this table as well.  \n
    8) Scatter Plots - this tab allows you to plot players in 2 variables, grouped by position, and offers you a third variable for coloring the points. First, choose the position grouping you want (strikers, wingers, etc), then choose the X, Y, and Color variables. Finally, choose the color palette you want to color points by. There are 2 options for each palette, the regular one, and the one ending in "_r", which is reversed. Thus, the rdylgn palette is red-yellow-green, and rdylgn_r is green-yellow-red, from lowest to highest. For a basic overview of palettes, please consult https://matplotlib.org/stable/users/explain/colors/colormaps.html#sequential  \n
    9) Role Score Definitions & Calculations - this tab houses the definitions of roughly what each role should do (in my opinion, and it is rough), and the metrics & weights that I used to calculate each role
    ''')


logo_dict_df = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Wyscout_Logo_Dict.csv')
logo_dict = pd.Series(logo_dict_df['Team logo'].values,index=logo_dict_df['Team']).to_dict()
ws_pos_compare_groups = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/WyscoutPositionsComparisons.csv')

with st.sidebar:
    st.header('Choose Gender')
    gender = st.selectbox('Gender', ('Men','Women'))
if gender == 'Men':
    lg_lookup = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup.csv')
if gender == 'Women':
    lg_lookup = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup_women.csv')
##########

legaues = lg_lookup.League.unique().tolist()
with st.sidebar:
    lg = st.selectbox('League', options=legaues, index=legaues.index('Danish 1. Division'))

with st.sidebar:
    st.header('Choose Basic Options')    
    season = st.selectbox('Season', (sorted(lg_lookup[lg_lookup.League == lg].Season.unique().tolist(),reverse=True)))
    formation = st.selectbox('Fomation', (4231, 433, 442, 343, 4222))
    mins = st.number_input('Minimum Minutes Played', 300, 2000, 900)
    ages = st.slider('Age Range', 0, 45, (0, 45))
    exp_contracts_ = st.selectbox('Only Expiring Contracts?  \n(Will only show players with contracts expiring, via Wyscout)', (['No','Yes']))
    if exp_contracts_ == 'Yes':
        exp_contracts = 'y'
        expiration_date = st.date_input("Contract Expires On Or Before", datetime.date(2024, 8, 1), format='YYYY-MM-DD')
    else:
        exp_contracts = 'n'
        expiration_date = '2024-08-01'
    number_of_players = st.slider('Top X Players Per Role  \n(Image limited to 7, table will show all X)', 1, 20, 5)
    normalize_to_100 = st.selectbox('Normalize Scores so #1 = 100?', (['Yes','No']))
    nationality_chosen = st.multiselect("Only Players of Certain Nationalities?  \nLeave blank for all players", ["Afghanistan","Albania","Algeria","Andorra","Angola","Antigua and Barbuda","Argentina","Armenia","Aruba","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bermuda","Bolivia","Bonaire","Bosnia and Herzegovina","Botswana","Brazil","British Virgin Islands","Brunei Darussalam","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Canada","Cape Verde Islands","Cayman Islands","Central African Republic","Chad","Chile","China PR","Chinese Taipei","Cocos (keeling) islands","Colombia","Comoros","Congo","Congo DR","Cook Islands","Costa Rica","Côte d'Ivoire","Croatia","Cuba","Curaçao","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","England","Equatorial Guinea","Eritrea","Estonia","Eswatini","Ethiopia","Faroe Islands","Fiji","Finland","France","France, metropolitan","French Guiana","Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Great Britain","Greece","Grenada","Guadeloupe","Guam","Guatemala","Guernsey","Guinea","Guinea-Bissau","Guyana","Haiti","Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran","Iraq","Isle of Man","Israel","Italy","Jamaica","Japan","Jersey","Jordan","Kazakhstan","Kenya","Korea DPR","Korea Republic","Kosovo","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Macao","Madagascar","Malawi","Malaysia","Mali","Malta","Martinique","Mauritania","Mauritius","Mayotte","Mexico","Moldova","Monaco","Mongolia","Montenegro","Montserrat","Morocco","Mozambique","Myanmar","Namibia","Nepal","Netherlands","New Caledonia","New Zealand","Nicaragua","Niger","Nigeria","North Macedonia","Northern Ireland","Norway","Oman","Pakistan","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Puerto Rico","Qatar","Republic of Ireland","Réunion","Romania","Russia","Rwanda","Samoa","San Marino","São Tomé e Príncipe","Saudi Arabia","Scotland","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Sint Maarten","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","South Sudan","Spain","Sri Lanka","St. Kitts and Nevis","St. Lucia","St. Vincent and the Grenadines","Sudan","Suriname","Sweden","Switzerland","Syria","Tahiti","Tajikistan","Tanzania","Thailand","Timor-Leste","Togo","Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Turks and Caicos Islands","Uganda","Ukraine","United Arab Emirates","United States","Uruguay","US Virgin Islands","Uzbekistan","Vanuatu","Venezuela","Vietnam","Wales","Yemen","Zambia","Zanzibar","Zimbabwe",])
    chosen_nations = '|'.join(nationality_chosen)
    
    with st.form('Role-Positions'):
        st.header('Role-Positions')
        submitted = st.form_submit_button("Update Roles")
        pos1 = st.selectbox(formation_positions[formation][0], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][0]].pos_role.tolist()))
        pos2 = st.selectbox(formation_positions[formation][1], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][1]].pos_role.tolist()), index=1)
        pos3 = st.selectbox(formation_positions[formation][2], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][2]].pos_role.tolist()), index=2)
        pos4 = st.selectbox(formation_positions[formation][3], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][3]].pos_role.tolist()))
        pos5 = st.selectbox(formation_positions[formation][4], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][4]].pos_role.tolist()))
        pos6 = st.selectbox(formation_positions[formation][5], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][5]].pos_role.tolist()), index=1)
        pos7 = st.selectbox(formation_positions[formation][6], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][6]].pos_role.tolist()), index=2)
        pos8 = st.selectbox(formation_positions[formation][7], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][7]].pos_role.tolist()))
        pos9 = st.selectbox(formation_positions[formation][8], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][8]].pos_role.tolist()), index=3)
        pos10 = st.selectbox(formation_positions[formation][9], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][9]].pos_role.tolist()), index=1)
        pos11 = st.selectbox(formation_positions[formation][10], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][10]].pos_role.tolist()))

chosen_roles = [pos1,pos2,pos3,pos4,pos5,pos6,pos7,pos8,pos9,pos10,pos11]
role_position_df = pd.DataFrame()
for i in range(0,11):
    role_position_df = pd.concat([role_position_df,role_position_lookup[(role_position_lookup.pos_role == chosen_roles[i]) & (role_position_lookup.form_pos == formation_positions[formation][i])]], ignore_index=True)
role_position_df['formation'] = formation

full_league_name = f"{lg} {season}"
update_date = lg_lookup[(lg_lookup.League==lg) & (lg_lookup.Season==season)].Date.values[0]

    
if gender == 'Men':
    df = pd.read_csv(f'https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Main%20App/{full_league_name.replace(" ","%20").replace("ü","u").replace("ó","o").replace("ö","o").replace("ã","a").replace("ç","c")}.csv')
elif gender == 'Women':
    df = pd.read_csv(f'https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Main%20App/Women/{full_league_name.replace(" ","%20").replace("ü","u").replace("ó","o").replace("ö","o").replace("ã","a").replace("ç","c")}.csv')
df['League'] = full_league_name
df = df.dropna(subset=['Position','Team within selected timeframe', 'Age']).reset_index(drop=True)


clean_df = load_league_data(df, full_league_name)
df_basic = clean_df.copy()

with st.sidebar:
    one_team_choice = st.selectbox('One Team Depth Chart?', (['No','Yes']))
    if one_team_choice == 'Yes':
        chosen_team = st.selectbox('Team', (sorted(clean_df['Team within selected timeframe'].unique().tolist())))
        team_text = f' {chosen_team} Depth Chart'
    else:
        chosen_team = 'N/A'
        if number_of_players > 7:
            num = 7
        else:
            num = number_of_players
        team_text = f' Top {num} Players Per Role'

rank_list = make_rankings(formation, mins, clean_df, role_position_df, [lg], exp_contracts, expiration_date,
                          min_age=ages[0], max_age=ages[1], num=number_of_players, normalize_to_100=normalize_to_100, chosen_team=chosen_team, nationality_chosen=chosen_nations)
show_ranks = rank_list[['Player','Team','Age','Squad Position','Player Pos.','Score','Role Rank','Formation Pos.']].copy()



path_eff = [path_effects.Stroke(linewidth=0.5, foreground='#fbf9f4'), path_effects.Normal()]

show_ranks2 = show_ranks.copy()
def make_fig(ages,exp_contracts,rank_11_base,show_ranks2,season,lg,normalize_to_100,team_text,chosen_nations):
    plt.clf()
    show_ranks = show_ranks2
    pitch = VerticalPitch(pitch_type='opta', pitch_color='#fbf9f4', line_color='#fbf9f4', line_zorder=1, half=False)
    fig, axs = pitch.grid(endnote_height=0.045, endnote_space=0, figheight=12,
                          title_height=0.045, title_space=0,
                          axis=False,
                          grid_height=0.86)
    fig.set_facecolor('#fbf9f4')
    
    if ages[0] == 0 and ages[1] == 45:
        age_text = f'Minimum {mins} minutes played'
    elif ages[0] == 0:
        age_text = f'Min. {mins} minutes played | U{ages[1]} players only'
    elif ages[1] == 45:
        age_text = f'Min. {mins} minutes played | Players {ages[0]} & older'
    else:
        age_text = f'Min. {mins} minutes played | Players between {ages[0]} & {ages[1]}'
    
    if exp_contracts == 'y':
        exp_text = f'Players out of contract by {expiration_date} (per Wyscout)'
    else:
        exp_text = ''
    
    if exp_text == '':
        sub_title_text = age_text
    else:
        sub_title_text = f"{age_text} | {exp_text}"

    if chosen_nations != "":
        nation_text = f"Only nationalities: {chosen_nations.replace('|',', ')}\n"
    else:
        nation_text = ""
    
    for i in range(0,11):
        X = rank_11_base[(rank_11_base.form_pos == formation_positions[formation][i]) & (rank_11_base.formation == formation)].x.values[0]
        Y = rank_11_base[(rank_11_base.form_pos == formation_positions[formation][i]) & (rank_11_base.formation == formation)].y.values[0]
    
        
        adj = -4
    
        show_players = len(show_ranks[show_ranks['Formation Pos.']==formation_positions[formation][i]].head(7))
        for j in range(show_players):
            player = show_ranks[show_ranks['Formation Pos.']==formation_positions[formation][i]].Player.iloc[j]
            age = show_ranks[show_ranks['Formation Pos.']==formation_positions[formation][i]].Age.iloc[j]
            pteam = show_ranks[show_ranks['Formation Pos.']==formation_positions[formation][i]].Team.iloc[j]
            score = show_ranks[show_ranks['Formation Pos.']==formation_positions[formation][i]].Score.iloc[j]
            role_rank = int(show_ranks[show_ranks['Formation Pos.']==formation_positions[formation][i]]['Role Rank'].iloc[j])
    
            if j == 0:
                pos_desc = show_ranks[show_ranks['Formation Pos.']==formation_positions[formation][i]]['Squad Position'].iloc[0]
                axs['pitch'].text(Y, X+6.25, pos_desc,
                                 ha='center', va='center', color='#4a2e19', size=11, zorder=3,
                                  weight='bold', path_effects=path_eff)
        
            axs['pitch'].text(Y, X-adj, f"{player} ({age}, {pteam}) {score}, #{role_rank}",
                             ha='center', va='center', color='#4c94f6', size=9, zorder=3,
                              weight='bold', path_effects=path_eff)
            adj += 2
    
    axs['title'].text(0.5, 1.5, f'{season} {lg},{team_text}',
                     ha='center',va='bottom', size=20, weight='bold', color='#4a2e19')
    axs['title'].text(0.5, 1.35, f'Data via Wyscout | {lg_lookup[(lg_lookup.League==lg) & (lg_lookup.Season==season)].Date.values[0]}',
                     ha='center',va='top', size=12, color='#4a2e19')
    axs['title'].text(0.5, .95, f"{nation_text}{sub_title_text}",
                     ha='center',va='top', size=12, color='#4a2e19')

    if normalize_to_100 == 'Yes':
        axs['endnote'].text(0.5, -.3, f"Scores are gnerated by weighting z-scores of various metrics important to each role-position\nScores normalized so that the top player's score is 100 and the worst score is 0",
                         ha='center',va='top', size=10, color='#4a2e19')
    else:
        axs['endnote'].text(0.5, -.3, f"Scores are gnerated by weighting z-scores of various metrics important to each role-position",
                         ha='center',va='top', size=10, color='#4a2e19')
    return fig

show_ranks = show_ranks[['Player','Team','Age','Squad Position','Player Pos.','Score','Role Rank']].copy()

image_tab, table_tab, radar_tab, all_player_list_tab, similarity_tab, filter_tab, filter_table_tab, scatter_tab,ranking_tab,  notes_tab, map_tab = st.tabs(['Role Ranking Image', 'Role Ranking Table', 'Player Radar Generation', 'Player List', 'Similar Player Search', 'Player Search, Filters', 'Player Search, Results', 'Scatter Plots', 'Custom Player Ranking Model', 'Role Score Definitions & Calculations', 'Available Leagues'])

with image_tab:
    fig = make_fig(ages,exp_contracts,rank_11_base,show_ranks2,season,lg,normalize_to_100,team_text,chosen_nations)
    st.pyplot(fig)

with table_tab:
    with st.expander('All Roles'):
       show_ranks
    with st.expander(chosen_roles[0]):
       show_ranks[show_ranks['Squad Position']==chosen_roles[0]]
    with st.expander(chosen_roles[1]):
       show_ranks[show_ranks['Squad Position']==chosen_roles[1]]
    with st.expander(chosen_roles[2]):
       show_ranks[show_ranks['Squad Position']==chosen_roles[2]]
    with st.expander(chosen_roles[3]):
       show_ranks[show_ranks['Squad Position']==chosen_roles[3]]
    with st.expander(chosen_roles[4]):
       show_ranks[show_ranks['Squad Position']==chosen_roles[4]]
    with st.expander(chosen_roles[5]):
       show_ranks[show_ranks['Squad Position']==chosen_roles[5]]
    with st.expander(chosen_roles[6]):
       show_ranks[show_ranks['Squad Position']==chosen_roles[6]]
    with st.expander(chosen_roles[7]):
       show_ranks[show_ranks['Squad Position']==chosen_roles[7]]
    with st.expander(chosen_roles[8]):
       show_ranks[show_ranks['Squad Position']==chosen_roles[8]]
    with st.expander(chosen_roles[9]):
       show_ranks[show_ranks['Squad Position']==chosen_roles[9]]
    with st.expander(chosen_roles[10]):
       show_ranks[show_ranks['Squad Position']==chosen_roles[10]]

with radar_tab:
    with st.form('Custom Radar Option'):
        custom_radar_yn = st.selectbox('Pre-Made Radar, or Custom Radar?', ('Pre-Made', 'Custom'))
        if custom_radar_yn == 'Custom':
            custom_radar_q = 'y'
            metric_selections = st.multiselect("Select the metrics you want on the radar", ['Received passes per 90','Passes per 90','Pct of passes being short','Pct of passes being lateral','Accurate passes, %','Accurate short / medium passes, %','Accurate long passes, %','Crosses per 90','Accurate crosses, %','Smart passes per 90','Shot assists per 90','xA per 90','xA per Shot Assist','Assists per 90','Second assists per 90','Third assists per 90','1st, 2nd, 3rd assists','Progressive passes per 90','Progressive runs per 90','Shots per 90','npxG per 90','Non-penalty goals per 90','npxG per shot','Goal conversion, %','Successful dribbles, %','Accelerations per 90','Touches in box per 90','Fouls suffered per 90','Successful defensive actions per 90','Duels won, %','Defensive duels won, %','pAdj Tkl+Int per 90','PAdj Sliding tackles','PAdj Interceptions','Shots blocked per 90','Aerial duels per 90','Aerial duels won, %','Aerial duels won per 90','Fouls per 90','Shots against per 90','Conceded goals per 90','Save rate, %','Prevented goals per 90','Goals prevented %','Clean sheets, %','Exits per 90','Average long pass length, m'], ['Received passes per 90','Passes per 90','Pct of passes being short','Pct of passes being lateral','Accurate passes, %','Accurate short / medium passes, %','Accurate long passes, %','Crosses per 90','Accurate crosses, %','Smart passes per 90','Shot assists per 90','xA per 90','xA per Shot Assist'])
        else:
            custom_radar_q = 'n'
        submitted = st.form_submit_button("Submit Options")
    with st.form('Player Radar Options'):
        bar_colors = st.selectbox('Bar Color Scheme', ('Benchmarking Percentiles', 'Metric Groups'))
        callout = st.selectbox('Data Labels on Bars', ('Per 90', 'Percentile'))
        dist_labels = st.selectbox('Distribution Label Lines on Bars?', ('Yes', 'No'))
        chosen_template = st.selectbox('Radar Template', ('Strikers','Wingers','Midfielders','Fullbacks','Centerbacks','Goalkeepers'))
        compare_default_or_positions = st.selectbox('Only Compare Against Same Position?', ('Yes','Choose custom comparison group'))
        if compare_default_or_positions == 'Choose custom comparison group':
            comparison_positions = st.multiselect('Positions to Compare Against', ['Strikers', 'Wingers', 'Attacking Midfielders', 'Central Midfielders', 'Defensive Midfielders', 'FBs & WBs', 'Center Backs', 'Goalkeepers'])
        else:
            comparison_positions = 'n/a'
        player = st.text_input("Player's Radar to Generate", "")
        page = st.number_input("Age of the player to generate (to guarantee the correct player)", step=1)
        submitted = st.form_submit_button("Submit Options")
        
        dfxxx = df_basic[df_basic['Minutes played']>=mins].copy().reset_index(drop=True)
        dfxxx = dfxxx[dfxxx['League']==full_league_name].reset_index(drop=True)
        df1 = dfxxx[['Wyscout id', 'Player', 'Team within selected timeframe', 'Position', 'Age', 'Minutes played']]
        df1 = df1.dropna(subset=['Position', 'Team within selected timeframe', 'Age']).reset_index(drop=True)
        df1 = df1.dropna(subset=['Position']).reset_index(drop=True)
        df1['Age'] = df1['Age'].astype(int)
        df1['Main Position'] = df1['Position'].str.split().str[0].str.rstrip(',')
        df1 = df1.dropna(subset=['Main Position']).reset_index(drop=True)
        position_replacements = {
            'LAMF': 'LWF',
            'RAMF': 'RWF',
            'LCB3': 'LCB',
            'RCB3': 'RCB',
            'LCB5': 'LCB',
            'RCB5': 'RCB',
            'LB5': 'LB',
            'RB5': 'RB',
            # 'RWB': 'RB',
            # 'LWB': 'LB',
            'LCM3': 'LCMF',
            'RCM3': 'RCMF'
        }
    
        df1['Main Position'] = df1['Main Position'].replace(position_replacements)
    
        ws_pos = ['LCMF3','RCMF3','LAMF','LW','RB','LB','LCMF','DMF','RDMF','RWF','AMF','LCB','RWB','CF','LWB','GK','LDMF','RCMF','LWF','RW','RAMF','RCB','CB','RCB3','LCB3','RB5','RWB5','LB5','LWB5']
        poses = ['Midfielder','Midfielder','Winger','Winger','Fullback','Fullback','Midfielder','Midfielder no CAM','Midfielder no CAM','Winger','Midfielder no DM','CB','Fullback','CF','Fullback','GK','Midfielder no CAM','Midfielder','Winger','Winger','Winger','CB','CB','CB','CB','Fullback','Fullback','Fullback','Fullback']
        template = ['midfielders','midfielders','wingers','wingers','fullbacks','fullbacks','midfielders','midfielders','midfielders','wingers','midfielders','centerbacks','wingers','strikers','fullbacks','goalkeepers','midfielders','midfielders','wingers','wingers','wingers','centerbacks','centerbacks','centerbacks','centerbacks','fullbacks','fullbacks','fullbacks','fullbacks',]
        compares = ['Central Midfielders','Central Midfielders','Wingers','Wingers','Fullbacks','Fullbacks','Central Midfielders','Central & Defensive Mids','Central & Defensive Mids','Wingers','Central & Attacking Mids','Center Backs','Fullbacks','Strikers','Fullbacks','Goalkeepers','Central & Defensive Mids','Central Midfielders','Wingers','Wingers','Wingers','Center Backs','Center Backs','Center Backs','Center Backs','Fullbacks','Fullbacks','Fullbacks','Fullbacks']
    
        xtratext = lg_lookup[(lg_lookup.League==lg) & (lg_lookup.Season==season)].Date.values[0]

        try:
            gen = df1[(df1['Player']==player) & (df1['Age']==page)]
            ix = ws_pos.index(gen['Main Position'].values[0])
            minplay = int(gen['Minutes played'].values[0])
            player_pos_compare_group = ws_pos_compare_groups[ws_pos_compare_groups.ws_pos==ws_pos[ix]].compare_positions.values[0]
    
            if comparison_positions=='n/a':
                player_pos_arg = ws_pos_compare_groups[ws_pos_compare_groups.compare_positions==player_pos_compare_group].ws_pos.tolist()
                compares_text = compares[ix]
            else:
                player_pos_arg = ws_pos_compare_groups[ws_pos_compare_groups.compare_positions.isin(comparison_positions)].ws_pos.tolist()
                if len(comparison_positions) > 2:
                    compares_text = f"{', '.join(comparison_positions[:-1])}, and {comparison_positions[-1]}"
                elif len(comparison_positions) == 2:
                    compares_text = f"{comparison_positions[0]} and {comparison_positions[1]}"
                elif len(comparison_positions) == 1:
                    compares_text = f"{comparison_positions[0]}"
                else:
                    compares_text = compares[ix]
    
    
            if custom_radar_q == 'n':
                radar_img = scout_report(
                    data_frame = df_basic, ##
                    gender = gender, ##
                    league = lg, ##
                    season = season, ##
                    xtra = ' current',
                    template = chosen_template.lower(),
                    pos = poses[ix],
                    player_pos = ws_pos[ix],
                    pos_in_sample = player_pos_arg,
                    compares = compares_text,
                    mins = mins,
                    minplay=minplay,
                    name = gen['Player'].values[0],
                    ws_name = gen['Player'].values[0],
                    team = gen['Team within selected timeframe'].values[0],
                    age = gen['Age'].values[0],
                    sig = '',
                    extra_text = xtratext,
                    custom_radar='n',
                    dist_labels=dist_labels,
                    logo_dict=logo_dict,
                )
            if custom_radar_q == 'y':
                radar_img = scout_report(
                    data_frame = df_basic, ##
                    gender = gender, ##
                    league = lg, ##
                    season = season, ##
                    xtra = ' current',
                    template = 'custom',
                    pos = poses[ix],
                    player_pos = ws_pos[ix],
                    pos_in_sample = player_pos_arg,
                    compares = compares_text,
                    mins = mins,
                    minplay=minplay,
                    name = gen['Player'].values[0],
                    ws_name = gen['Player'].values[0],
                    team = gen['Team within selected timeframe'].values[0],
                    age = gen['Age'].values[0],
                    sig = '',
                    extra_text = xtratext,
                    custom_radar='y',
                    metric_selections=metric_selections,
                    dist_labels=dist_labels,
                    logo_dict=logo_dict,
                )
            st.pyplot(radar_img.figure)
        except:
            st.text("Please enter a valid name & age.  \nPlease check spelling as well.  \nIf you're  using a custom radar, try Running again.\nAnd if you have chosen a custom sample group of positions, ensure the focal player is in the chosen positions")

with all_player_list_tab:
    if chosen_team == 'N/A':
        player_list_df = clean_df.copy()
        player_list_df = player_list_df.sort_values(by=['Player']).reset_index(drop=True)
        player_list_df = player_list_df[['Wyscout id','Full name','Player','Age','Team within selected timeframe','Position','Minutes played','On loan','Passport country']].rename(columns={'Player':'Radar Name','Team within selected timeframe':'Team','Position':'Positions'})
        player_list_df
    if chosen_team != 'N/A':
        player_list_df = clean_df.copy()
        player_list_df = player_list_df[player_list_df['Team within selected timeframe']==chosen_team].sort_values(by=['Player']).reset_index(drop=True)
        player_list_df = player_list_df[['Wyscout id','Full name','Player','Age','Team within selected timeframe','Position','Minutes played','On loan','Passport country']].rename(columns={'Player':'Radar Name','Team within selected timeframe':'Team','Position':'Positions'})
        player_list_df


with similarity_tab:
    with st.form('Similar Player Search'):
        submitted = st.form_submit_button("Find Similar Players")
        similar_player_lg_lookup = pd.read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup.csv')
        geo_input = st.selectbox("Geography Region", ('League','Country',"Region",'Continent'))
        geo_mapping = {
            'Region': 'Nordics',
            'Country': 'Denmark',
            'Continent': 'Europe',
            'League': 'Danish 1. Division'
        }
        default_region_area = geo_mapping.get(geo_input, 'Unknown')
        region = st.multiselect(f"{geo_input}(s) to include (leave blank to include all)", similar_player_lg_lookup[geo_input].unique().tolist(), default=default_region_area)
        tiers = st.multiselect("Tiers to include (leave blank to include all)", ('1','2','3','4','5','6','Youth'))
        time_frame = st.selectbox('Time Frame', ('Current Season','Prior Season','Current & Prior Seasons'))  ### Current Season | Prior Season | Current & Prior Seasons
        wyscout_id = st.text_input("Player's Wyscout ID (get from 'Player List' tab)", "")
        sim_pos = st.selectbox('Positions', ('Strikers', 'Strikers and Wingers', 'Forwards (AM, W, CF)',
                                'Forwards no ST (AM, W)', 'Wingers', 'Central Midfielders (DM, CM, CAM)',
                                'Central Midfielders no CAM (DM, CM)', 'Central Midfielders no DM (CM, CAM)', 'Fullbacks (FBs/WBs)',
                                'Defenders (CB, FB/WB, DM)', 'Centre-Backs', 'CBs & DMs','Goalkeepers'))
        pca_transform = st.selectbox('Dimensionality Reduction? (recommended: can help produce better matches)', ('Yes','No'))
        custom_metric_comparison = st.selectbox('Pre-Made or Custom Metrics to Compare By?', ('Pre-Made','Custom'))
        if custom_metric_comparison == 'Custom':
            compare_metrics = st.multiselect("Select the metrics you want on the radar", ['Received passes per 90','Passes per 90','Pct of passes being short','Pct of passes being lateral','Accurate passes, %','Accurate short / medium passes, %','Accurate long passes, %','Crosses per 90','Accurate crosses, %','Smart passes per 90','Shot assists per 90','xA per 90','xA per Shot Assist','Assists per 90','Second assists per 90','Third assists per 90','1st, 2nd, 3rd assists','Progressive passes per 90','Progressive runs per 90','Shots per 90','npxG per 90','Non-penalty goals per 90','npxG per shot','Goal conversion, %','Successful dribbles, %','Accelerations per 90','Touches in box per 90','Fouls suffered per 90','Successful defensive actions per 90','Duels won, %','Defensive duels won, %','pAdj Tkl+Int per 90','PAdj Sliding tackles','PAdj Interceptions','Shots blocked per 90','Aerial duels per 90','Aerial duels won, %','Aerial duels won per 90','Fouls per 90','Shots against per 90','Conceded goals per 90','Save rate, %','Prevented goals per 90','Goals prevented %','Clean sheets, %','Exits per 90','Average long pass length, m'], ['Received passes per 90','Passes per 90','Pct of passes being short','Pct of passes being lateral','Accurate passes, %','Accurate short / medium passes, %','Accurate long passes, %','Crosses per 90','Accurate crosses, %','Smart passes per 90','Shot assists per 90','xA per 90','xA per Shot Assist'])
        if custom_metric_comparison == 'Pre-Made':
            compare_metrics = st.selectbox('Metric Comparison Group', ('all','ST','W','CAM','CM','DM','FB','CB','GK'))

        if wyscout_id=='':
            st.write('Please enter a player ID')
        else:
            full_similarity_df_raw = prep_similarity_df(geo_input, region, tiers, time_frame)
    try:
        similar_players_df, player_name, player_age, player_position, player_team = similar_players_search(
            df=full_similarity_df_raw,
            ws_id=int(wyscout_id),
            pos=sim_pos,
            pca_transform=pca_transform,
            compare_metrics=compare_metrics,
            mins=mins,
            age_band=ages
        )
        st.write(f"Players similar to {player_name} ({player_age}, {player_position}, {player_team})")
        if len(similar_players_df)>0:
            st.dataframe(similar_players_df.style.applymap(color_percentile, subset=similar_players_df.columns[1]))
    except:
        st.write("Please enter a player's ID. Make sure the Region & Time Frame includes the league the focal player plays in")

with filter_tab:
    with st.form('Position Filter Min Filters'):
        submitted = st.form_submit_button("Submit Position & Geography Choices")
        pos_select_filters = st.selectbox('Positions', ('Strikers', 'Strikers and Wingers', 'Forwards (AM, W, CF)',
                                'Forwards no ST (AM, W)', 'Wingers', 'Central Midfielders (DM, CM, CAM)',
                                'Central Midfielders no CAM (DM, CM)', 'Central Midfielders no DM (CM, CAM)', 'Fullbacks (FBs/WBs)',
                                'Defenders (CB, FB/WB, DM)', 'Centre-Backs', 'CBs & DMs','Goalkeepers'))
        similar_player_lg_lookup_filters = pd.read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup.csv')
        geo_input_filters = st.selectbox("Geography Region", ('League','Country',"Region",'Continent'))
        geo_mapping_filters = {
            'Region': 'Nordics',
            'Country': 'Denmark',
            'Continent': 'Europe',
            'League': 'Danish 1. Division'
        }
        default_region_area_filters = geo_mapping_filters.get(geo_input_filters, 'Unknown')
        region_filters = st.multiselect(f"{geo_input_filters}(s) to include (leave blank to include all)", similar_player_lg_lookup_filters[geo_input_filters].unique().tolist(), default=default_region_area_filters)
        tiers_filters = st.multiselect("Tiers to include (leave blank to include all)", ('1','2','3','4','5','6','Youth'))

    if geo_input_filters == 'League':
        with st.form('Time Frame Filters, League'):
            similar_player_lg_lookup_filters['League-Season'] = similar_player_lg_lookup_filters.League + " " + similar_player_lg_lookup_filters.Season
            submitted = st.form_submit_button("Submit Seasons")
            time_frame_filters = st.multiselect('League-Seasons', (similar_player_lg_lookup_filters[similar_player_lg_lookup_filters.League.isin(region_filters)].sort_values(by=['Country','Tier','Season'],ascending=[True,True,False])['League-Season'].tolist()), default='Danish 1. Division 24-25')
    
    if geo_input_filters != 'League':
        with st.form('Time Frame Filters, Non-League'):
            submitted = st.form_submit_button("Submit Seasons")
            time_frame_filters = st.multiselect('League-Seasons', (sorted(similar_player_lg_lookup_filters.Season.unique().tolist(), reverse=True)), default='24-25')
    ######
    try:
        print(f"SELECTED OPTIONS:\nGeography Region: {geo_input_filters}\nArea: {region_filters}\nTiers: {tiers_filters}\nTime Frame: {time_frame_filters}\nPosition(s): {pos_select_filters}")
    except:
        geo_input_filters='League',
        region_filters='Danish 1. Division',
        tiers_filters=[],
        time_frame_filters='Danish 1. Division 24-25'
        pos_select_filters = 'Strikers'
    raw_df_for_filtering = prep_player_research_table(geo_input_filters, region_filters, tiers_filters, time_frame_filters, mins, pos_select_filters, ages[0], ages[1])
    min_dict = raw_df_for_filtering.min()[6:]
    max_dict = raw_df_for_filtering.max()[6:]
    #########

with filter_tab:
    st.button("Reset Sliders", on_click=_update_slider, kwargs={"value": 0.0})
    with st.form('Minimum Percentile Filters'):
        submitted = st.form_submit_button("Submit Filters")
        # pos_select_filters = st.selectbox('Positions', ('Strikers', 'Strikers and Wingers', 'Forwards (AM, W, CF)',
        #                         'Forwards no ST (AM, W)', 'Wingers', 'Central Midfielders (DM, CM, CAM)',
        #                         'Central Midfielders no CAM (DM, CM)', 'Central Midfielders no DM (CM, CAM)', 'Fullbacks (FBs/WBs)',
        #                         'Defenders (CB, FB/WB, DM)', 'Centre-Backs', 'CBs & DMs','Goalkeepers'))

            
        if ['slider1','slider2','slider3','slider4','slider5','slider6','slider7','slider8','slider9','slider10','slider11','slider12','slider13','slider14','slider15','slider16','slider17','slider18','slider19','slider20','slider21','slider22','slider23','slider24','slider25','slider26','slider27','slider28','slider29','slider30','slider31','slider32','slider33','slider34','slider35','slider36','slider37','slider38','slider39'] not in st.session_state:
            pass
        short = st.slider('Short & Medium Pass Cmp %', min_dict['Accurate short / medium passes, %'], max_dict['Accurate short / medium passes, %'], key='slider1')
        long = st.slider('Long Pass Cmp %', min_dict['Accurate long passes, %'], max_dict['Accurate long passes, %'], key='slider2')
        passestot = st.slider('Passes per 90', min_dict['Passes per 90'], max_dict['Passes per 90'], key='slider3')
        smart = st.slider('Smart Passes per 90', min_dict['Smart passes per 90'], max_dict['Smart passes per 90'], key='slider4')
        crosspct = st.slider('Cross Cmp %', min_dict['Accurate crosses, %'], max_dict['Accurate crosses, %'], key='slider5')
        crosses = st.slider('Crosses per 90', min_dict['Crosses per 90'], max_dict['Crosses per 90'], key='slider6')
        shotassist = st.slider('Shot Assists per 90', min_dict['Shot assists per 90'], max_dict['Shot assists per 90'], key='slider7')
        xa = st.slider('xA per 90', min_dict['xA per 90'], max_dict['xA per 90'], key='slider8')
        xasa = st.slider('xA per Shot Assist', min_dict['xA per Shot Assist'], max_dict['xA per Shot Assist'], key='slider9')
        ast = st.slider('Assists per 90', min_dict['Assists per 90'], max_dict['Assists per 90'], key='slider10')
        ast2 = st.slider('Second Assists per 90', min_dict['Second assists per 90'], max_dict['Second assists per 90'], key='slider11')
        ast123 = st.slider('1st, 2nd, & 3rd Assists per 90', min_dict['1st, 2nd, 3rd assists'], max_dict['1st, 2nd, 3rd assists'], key='slider12')
        npxg = st.slider('npxG per 90', min_dict['npxG per 90'], max_dict['npxG per 90'], key='slider13')
        npg = st.slider('Non-Pen Goals per 90', min_dict['Non-penalty goals per 90'], max_dict['Non-penalty goals per 90'], key='slider14')
        gc = st.slider('Goals per Shot on Target', min_dict['Goal conversion, %'], max_dict['Goal conversion, %'], key='slider15')
        npxgshot = st.slider('npxG per shot', min_dict['npxG per shot'], max_dict['npxG per shot'], key='slider16')
        shots = st.slider('Shots per 90', min_dict['Shots per 90'], max_dict['Shots per 90'], key='slider17')
        boxtouches = st.slider('Touches in Penalty Box per 90', min_dict['Touches in box per 90'], max_dict['Touches in box per 90'], key='slider18')
        drib = st.slider('Dribble Success %', min_dict['Successful dribbles, %'], max_dict['Successful dribbles, %'], key='slider19')
        num_dribs = st.slider('Successful dribbles per 90', min_dict['Successful dribbles per 90'], max_dict['Successful dribbles per 90'], key='slider19a')
        accel = st.slider('Accelerations per 90', min_dict['Accelerations per 90'], max_dict['Accelerations per 90'], key='slider20')
        progcarry = st.slider('Progressive Carries per 90', min_dict['Progressive runs per 90'], max_dict['Progressive runs per 90'], key='slider21')
        progpass = st.slider('Progressive Passes per 90', min_dict['Progressive passes per 90'], max_dict['Progressive passes per 90'], key='slider22')
        aerial = st.slider('Aerial Win %', min_dict['Aerial duels won, %'], max_dict['Aerial duels won, %'], key='slider23')
        aerialswon = st.slider('Aerials Won per 90', min_dict['Aerial duels won per 90'], max_dict['Aerial duels won per 90'], key='slider24')
        defduels = st.slider('Defensive Duels Success %', min_dict['Defensive duels won, %'], max_dict['Defensive duels won, %'], key='slider25')
        defend = st.slider('Successful Defensive Actions per 90', min_dict['Successful defensive actions per 90'], max_dict['Successful defensive actions per 90'], key='slider26')
        tklint = st.slider('Tackles & Interceptions per 90', min_dict['pAdj Tkl+Int per 90'], max_dict['pAdj Tkl+Int per 90'], key='slider27')
        tkl = st.slider('Sliding Tackles per 90', min_dict['PAdj Sliding tackles'], max_dict['PAdj Sliding tackles'], key='slider28')
        intercept = st.slider('Interceptions per 90', min_dict['PAdj Interceptions'], max_dict['PAdj Interceptions'], key='slider29')
        shotblock = st.slider('Shots Blocked per 90', min_dict['Shots blocked per 90'], max_dict['Shots blocked per 90'], key='slider30')
        foul = st.slider('Fouls Committed per 90', min_dict['Fouls per 90'], max_dict['Fouls per 90'], key='slider31')
        fouldraw = st.slider('Fouls Drawn per 90', min_dict['Fouls suffered per 90'], max_dict['Fouls suffered per 90'], key='slider32')
        cards = st.slider('Cards per 90', min_dict['Cards per 90'], max_dict['Cards per 90'], key='slider33')
        if pos_select_filters == 'Goalkeepers':
            concede = st.slider('Conceded goals per 90', min_dict['Conceded goals per 90'], max_dict['Conceded goals per 90'], key='slider34')
            saverate = st.slider('Save rate, %', min_dict['Save rate, %'], max_dict['Save rate, %'], key='slider35')
            exits = st.slider('Exits per 90', min_dict['Exits per 90'], max_dict['Exits per 90'], key='slider36')
            psxg = st.slider('Prevented goals per 90', min_dict['Prevented goals per 90'], max_dict['Prevented goals per 90'], key='slider37')
            gppct = st.slider('Goals prevented %', min_dict['Goals prevented %'], max_dict['Goals prevented %'], key='slider38')
            shotsfaced = st.slider('Shots against per 90', min_dict['Shots against per 90'], max_dict['Shots against per 90'], key='slider39')

with filter_table_tab:
    st.write(f"SELECTED OPTIONS:  \nGeography: {geo_input_filters}  \nArea: {', '.join(region_filters)}  \nTiers: {', '.join(tiers_filters)}  \nLeague-Seasons: {', '.join(time_frame_filters)}  \nPosition(s): {pos_select_filters}")
    # final = create_player_research_table(df_basic, mins, pos_select, ages[0], ages[1])
    final = raw_df_for_filtering
    player_research_table = final[(final['Accurate short / medium passes, %']>=short) &
                 (final['Accurate long passes, %']>=long) &
                  (final['Smart passes per 90']>=smart) &
                 (final['Passes per 90']>=passestot) &
                  (final['Crosses per 90']>=crosses) &
                  (final['Accurate crosses, %']>=crosspct) &
                  (final['Shot assists per 90']>=shotassist) &
                  (final['xA per 90']>=xa) &
                  (final['xA per Shot Assist']>=xasa) &
                  (final['Assists per 90']>=ast) &
                  (final['Second assists per 90']>=ast2) &
                  (final['1st, 2nd, 3rd assists']>=ast123) &
                  (final['npxG per 90']>=npxg) &
                  (final['Non-penalty goals per 90']>=npg) &
                  (final['Goal conversion, %']>=gc) &
                  (final['npxG per shot']>=npxgshot) &
                  (final['Shots per 90']>=shots) &
                  (final['Touches in box per 90']>=boxtouches) &
                  (final['Successful dribbles, %']>=drib) &
                  (final['Successful dribbles per 90']>=num_dribs) &
                  (final['Accelerations per 90']>=accel) &
                  (final['Progressive runs per 90']>=progcarry) &
                  (final['Progressive passes per 90']>=progpass) &
                  (final['Successful defensive actions per 90']>=defend) &
                  (final['Defensive duels won, %']>=defduels) &
                  (final['pAdj Tkl+Int per 90']>=tklint) &
                  (final['PAdj Sliding tackles']>=tkl) &
                  (final['PAdj Interceptions']>=intercept) &
                  (final['Aerial duels won, %']>=aerial) &
                  (final['Aerial duels won per 90']>=aerialswon) &
                  (final['Shots blocked per 90']>=shotblock) &
                  (final['Fouls per 90']>=foul) &
                  (final['Fouls suffered per 90']>=fouldraw) &
                  (final['Cards per 90']>=cards)
                    ].reset_index(drop=True)
    if pos_select_filters == 'Goalkeepers':
        player_research_table = player_research_table[(player_research_table['Conceded goals per 90']>=concede) &
            (player_research_table['Save rate, %']>=saverate) &
            (player_research_table['Exits per 90']>=exits) &
            (player_research_table['Prevented goals per 90']>=psxg) &
            (player_research_table['Goals prevented %']>=gppct) &
            (player_research_table['Shots against per 90']>=shotsfaced)
             ].reset_index(drop=True)
    
    st.dataframe(player_research_table.style.applymap(color_percentile, subset=player_research_table.columns[6:]))

with scatter_tab:
    scatter_df = clean_df.copy()

    with st.form("Scatter Options"):
        submitted = st.form_submit_button("Submit Options")

        pos_select_scatter = st.selectbox('Positions', ('Strikers', 'Strikers and Wingers', 'Forwards (AM, W, CF)',
                                'Forwards no ST (AM, W)', 'Wingers', 'Central Midfielders (DM, CM, CAM)',
                                'Central Midfielders no CAM (DM, CM)', 'Central Midfielders no DM (CM, CAM)', 'Fullbacks (FBs/WBs)',
                                'Defenders (CB, FB/WB, DM)', 'Centre-Backs', 'CBs & DMs', 'Goalkeepers'))
        
        xx = st.selectbox('X-Axis Variable', ['Age']+(scatter_df.columns[18:len(scatter_df.columns)-1].tolist()))
        yy = st.selectbox('Y-Axis Variable', ['Age']+(scatter_df.columns[18:len(scatter_df.columns)-1].tolist()))
        cc = st.selectbox('Point Color Variable', ['Age']+(scatter_df.columns[18:len(scatter_df.columns)-1].tolist()))
        cscale = st.selectbox('Point Colorscale', colorscales, index=78)

        dfProspect_scatter = scatter_df[(scatter_df['Minutes played'] >= mins) & (scatter_df['League'] == full_league_name)].copy()
        dfProspect_scatter = filter_by_position_long(dfProspect_scatter, pos_select_scatter)
        
    if ages[0] == 0 and ages[1] == 45:
        age_text_scatter = f''
    elif ages[0] == 0:
        age_text_scatter = f'U{ages[1]} players only, '
    elif ages[1] == 45:
        age_text_scatter = f'Players {ages[0]} & older, '
    else:
        age_text_scatter = f'Players between {ages[0]} & {ages[1]}, '

    fig_scatter = px.scatter(
        dfProspect_scatter,
        x = xx,
        y = yy,
        color = cc,
        color_continuous_scale = cscale,
        text = 'Player',
        hover_data=['Team', 'Age', 'Position', 'Minutes played'],
        hover_name = 'Player',
        title = '%s %s, %s & %s <br><sup>%s%s min. %i minutes played | %s</sup>' %(season,lg,xx,yy,age_text_scatter,pos_select_scatter,mins,update_date),
        width=900,
        height=700)
    fig_scatter.update_traces(textposition='top right', marker=dict(size=10, line=dict(width=1, color='black')))
    
    fig_scatter.add_hline(y=dfProspect_scatter[yy].median(), name='Median', line_width=0.5)
    fig_scatter.add_vline(x=dfProspect_scatter[xx].median(), name='Median', line_width=0.5)
    
    st.plotly_chart(fig_scatter, theme=None, use_container_width=False)

with ranking_tab:
    with st.form('Geo Selection for Ranking'):
        submitted = st.form_submit_button("Submit League Choice(s)")
        similar_player_lg_lookup_ranking = pd.read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup.csv')
        geo_input_ranking = st.selectbox("Geography Region", ('League','Country',"Region",'Continent'))
        geo_mapping_ranking = {
            'Region': 'Nordics',
            'Country': 'Denmark',
            'Continent': 'Europe',
            'League': 'Danish 1. Division'
        }
        default_region_area_ranking = geo_mapping_ranking.get(geo_input_ranking, 'Unknown')
        region_ranking = st.multiselect(f"{geo_input_filters}(s) to include (leave blank to include all)", similar_player_lg_lookup_ranking[geo_input_ranking].unique().tolist(), default=default_region_area_ranking)
        tiers_rankings = st.multiselect("Tiers to include (leave blank to include all)", ('1','2','3','4','5','6','Youth'))

    if geo_input_ranking == 'League':
        with st.form('Time Frame Filters, League Ranking'):
            similar_player_lg_lookup_ranking['League-Season'] = similar_player_lg_lookup_ranking.League + " " + similar_player_lg_lookup_ranking.Season
            submitted = st.form_submit_button("Submit Seasons")
            time_frame_ranking = st.multiselect('League-Seasons', (similar_player_lg_lookup_ranking[similar_player_lg_lookup_ranking.League.isin(region_ranking)].sort_values(by=['Country','Tier','Season'],ascending=[True,True,False])['League-Season'].tolist()), default='Danish 1. Division 24-25')
    
    if geo_input_ranking != 'League':
        with st.form('Time Frame Filters, Non-League Ranking'):
            submitted = st.form_submit_button("Submit Seasons")
            time_frame_ranking = st.multiselect('League-Seasons', (sorted(similar_player_lg_lookup_ranking.Season.unique().tolist(), reverse=True)), default='24-25')

    try:
        print(f"SELECTED OPTIONS:\nGeography Region: {geo_input_filters}\nArea: {region_filters}\nTiers: {tiers_filters}\nTime Frame: {time_frame_filters}\nPosition(s): {pos_select_filters}")
    except:
        geo_input_ranking='League',
        region_ranking='Danish 1. Division',
        tiers_rankings=[],
        time_frame_ranking='Danish 1. Division 24-25'
    
    with st.form('Position and Metric Selections Ranking'):
        submitted = st.form_submit_button("Submit Positions & Metrics")
        rank_pos = st.multiselect('Positions to Include (leave blank for all)', ['Strikers', 'Wingers', 'Attacking Midfielders', 'Central Midfielders', 'Defensive Midfielders', 'FBs & WBs', 'Center Backs', 'Goalkeepers'])
        vars = clean_df.columns[19:-1].tolist()
        metrics = st.multiselect("Choose metrics to include:", vars)

    ranking_df = prep_similarity_df_filters(geo_input_ranking, region_ranking, tiers_rankings, time_frame_ranking)
    ranking_df = ranking_df[ranking_df['Minutes played']>=mins]
    ranking_df['Age'] = ranking_df['Age'].astype(int)

    if rank_pos != []:
        player_pos_arg = ws_pos_compare_groups[ws_pos_compare_groups.compare_positions.isin(rank_pos)].ws_pos.tolist()
        ranking_df = ranking_df[ranking_df['Primary position'].isin(player_pos_arg)]
        
    if metrics:
        # User assigns weights
        with st.form('Metric Weightings'):
            submitted = st.form_submit_button("Submit Metric Weightings")
            weights = {}
            for metric in metrics:
                weights[metric] = st.slider(f"Weight for {metric}", 0.0, 1.0, 0.5, 0.05)
        
        # Normalize data using z-score
        df_filtered = ranking_df.copy()
        for metric in metrics:
            df_filtered[f'{metric} raw'] = df_filtered[metric]
        df_filtered[metrics] = df_filtered[metrics].apply(stats.zscore, nan_policy='omit')
        for metric in metrics:
            df_filtered[metric] = df_filtered[metric] + abs(df_filtered[metric].min())
            df_filtered[metric] = NormalizeData(df_filtered[metric])
            
        # Compute weighted z-score ranking
        df_filtered["Score"] = df_filtered[metrics].apply(lambda row: sum(row[metric] * weights[metric] for metric in metrics), axis=1)
        min_score = df_filtered["Score"].min()
        max_score = df_filtered["Score"].max()
        df_filtered["Score"] = round((df_filtered["Score"] - min_score) / (max_score - min_score) * 100,2)
        for metric in metrics:
            df_filtered[metric] = round(df_filtered[f'{metric} raw'],2)

        # Display results
        st.write("Normalized Weighted Z-Score Player Rankings")
        rank_df_final_choice = df_filtered.sort_values("Score", ascending=False)[["Wyscout id","Player","Team","Age","Main Position","Minutes played","Score",] + metrics]
        st.dataframe(rank_df_final_choice.style.applymap(color_percentile_100, subset=rank_df_final_choice.columns[6]))


with notes_tab:
    with st.expander('Shot-Stopping Distributor'):
        st.write('''
        A goalkeeper who is not only good at stopping shots & saving goals, but is able to play with the ball at their feet. A true modern goalkeeper.  \n
        40% Post-shot xG +/-  \n
        20% Short passes per 90  \n
        15% Percentage of passes that are short  \n
        15% Long pass completion %
        10% Save %  \n
        ''')
    with st.expander('Ball Playing CB'):
        st.write('''
        A CB built for a possession system. They need to be comfortable on the ball and be able to spray long passes as well as anchor buildup phases.  \n
        20% Long pass completion %  \n
        20% Passes to the final third + deep completions  \n
        20% Progressive passes  \n
        20% Passes  \n
        10% Aerial win %  \n
        10% Defensive duel win %
        ''')
    with st.expander('Defensive CB'):
        st.write('''
        A CB whose primary focus is defending. The most important attribute they possess is winning their duels. The best of them don't commit fouls in dangerous areas, defeating the whole purpose of their strong defense.  \n
        45% Defensive duel win %  \n
        20% Fouls (reverse-coded; more = bad)  \n
        15% Aerial win %  \n
        10% Possession-adjusted tackles  \n
        10% Possession-adjusted interceptions
        ''')
    with st.expander('Wide CB'):
        st.write('''
        A CB who operates more in the half-spaces further up the pitch than a classic ball-playing CB. Because of that, they need to both impact possessions as well as be defensively solid without being prone to fouling because they will be needed in transition more than other CB roles.  \n
        25% Progressive passes & carries  \n
        20% Passes  \n
        20% Defensive duel win %  \n
        15% Fouls (reverse-coded; more = bad)  \n
        15% Short pass completion %  \n
        5% Long pass completion %
        ''')
    with st.expander('Attacking FB'):
        st.write('''
        A FB who is able to bomb up the flanks and whose primary goal is to progress the ball into dangerous areas and pin back their opposite fullback.  \n
        25% Passes to final third & passes completed within 20m of the goal  \n
        20% Progressive carries  \n
        20% Offensive duel win %  \n
        10% Dribble win %  \n
        10% Expected assists (xA)  \n
        7.5% Accelerations with the ball  \n
        7.5% Cross completion %
        ''')
    with st.expander('Inverted FB'):
        st.write('''
        A FB who is able to invert into midfield & impact the game from central areas. They are tasked with enabling possession but given their position, still have to be strong defensively like a DM.  \n
        35% Passes attempted  \n
        20% Progressive passes  \n
        20% Possession-adjusted tackles+interceptions  \n
        15% Percentage of passes that are short  \n
        10% Defensive duel win %
        ''')
    with st.expander('Defensive FB'):
        st.write('''
        A FB who is mainly tasked with defending. Their primary goal is to lock down their flank, rather than get forward to impact near the box or cross.  \n
        45% Defensive duel win %  \n
        20% Fouls (reverse-coded; more = bad)  \n
        15% Aerial win %  \n
        10% Possession-adjusted tackles  \n
        10% Possession-adjusted interceptions
        ''')
    with st.expander('Possession Enabler'):
        st.write('''
        A DM or CM who is tasked primarily with retaining & recycling possession. These players will be extremely tidy on the ball and relish passing laterally to facilitate their team's possessions. Risky forward/long balls may be a part of this player's arsenal but will be played sparingly.  \n
        30% Percentage of passes that are short  \n
        25% Short pass completion %  \n
        20% Percentage of passes that are not 'smart' (Wyscout defines as risky passes looking to open attacking opportunities)  \n
        15% Passes attempted  \n
        10% Fouls (reverse-coded; more = bad)
        ''')
    with st.expander('Defensive Mid'):
        st.write('''
        A DM or CM who is very defensively-minded and able to be a rock in front of their CBs. They are tasked with winning the ball back cleanly, both on the ground and in the air, and are often able to use their size advantage over opposing CMs & CAMs to do so. What they do after winning the ball back (safe pass, splitting vertical, big carry etc) is not important for this model.  \n
        45% Defensive duel win %  \n
        20% Fouls (reverse-coded; more = bad)  \n
        15% Aerial win %  \n
        10% Possession-adjusted tackles  \n
        10% Possession-adjusted interceptions
        ''')
    with st.expander('Number 6'):
        st.write('''
        A DM or CM who can not only regain possession, but retain possession with ease. They are not the creative spark of the team, but typically the strong single-pivot in a 3-player midfield. This role is somewhat of a cross between the Defensive Mid and the Possession Enabler. They typically stamp their mark on a high % of their team's possessions as well.  \n
        30% Defensive duel win %  \n
        25% Short pass completion %  \n
        20% Percentage of passes that are short  \n
        15% Attacking duel win % (includes dribbles, ball shields when being pressed, etc.)  \n
        10% Fouls (reverse-coded; more = bad)
        ''')
    with st.expander('Deep-Lying Playmaker'):
        st.write('''
        A player who is vital in a team's creation from deep positions. They will be involved in creative passing as well as progressing play into more dangerous areas into the feet of more advanced players, instead of heavily involved in the final ball. Because they sit in deep positions, they have to be somewhat capable in defense, even if their main duties are in possession instead of out of possession.  \n
        25% Passes into the final third + deep completions (within 20m of goal)  \n
        25% Progressive passes  \n
        15% Shot assists  \n
        15% Assists + 2nd + 3rd assists  \n
        10% Key passes  \n
        10% Defensive duel win %
        ''')
    with st.expander('Progressive Midfielder'):
        st.write('''
        A midfielder whose main focus is simply moving the play up the pitch. They will progress and break lines with passes and carries, helping to shift from buildup to attacking phases. They are a key cog in their team's play, and should see a high number of touches because of that.  \n
        22.5% Progressive carries  \n
        22.5% Progressive passes  \n
        20% Passes into the final third  \n
        15% Received passes  \n
        10% Attacking duel win % (includes dribbles, ball shields when being pressed, etc.)  \n
        10% Accelerations with the ball
        ''')
    with st.expander('Box-to-Box Midfielder'):
        st.write('''
        Similar to the Progressive Midfielder in that they help progress play, the box-to-box midfielder is normally one of the best players on the pitch at winning duels... whether that's beating their man while carrying or shielding the ball near the attacking box, or winning the ball back near their own box, they are capable of impacting play at both boxes. They normally have plenty of stamina, and we can use minutes played as a simple proxy for that.  \n
        25% Progressive carries  \n
        22.5% Attacking duel win % (includes dribbles, ball shields when being pressed, etc.)  \n
        22.5% Defensive duel win %  \n
        10% Passes into the final third  \n
        10% Possession-adjusted tackles+interceptions  \n
        10% Minutes played
        ''')
    with st.expander('Advanced Playmaker'):
        st.write('''
        The team's most advanced playmaker, a player who is creative enough to supply their teammates with lots of quality chances. They consistently create good opportunities for others, and while they may create for themselves, this is not the most important part of their role.  \n
        25% Key passes  \n
        25% Shot assists  \n
        20% Passes into the final third + deep completions (within 20m of goal)  \n
        15% Smart passes  \n
        15% Expected assists (xA)
        ''')
    with st.expander('Classic CAM'):
        st.write('''
        A player who operates high up the field, impacting both creation and shooting. Similar to the advanced playmaker, they will be able to provide for their teammates, although this is not their sole role, as they also have to be able to create opportunities to shoot themselves.  \n
        20% Shot assists  \n
        15% Key passes  \n
        15% Smart passes  \n
        15% Attacking duel win % (includes dribbles, ball shields when being pressed, etc.)  \n
        10% Dribble win %  \n
        10% Expected assists (xA)  \n
        10% Non-penalty expected goals (npxG)  \n
        5% Non-penalty goals (npG)
        ''')
    with st.expander('Wide CAM'):
        st.write('''
        An attacking midfielder who loves to drift wide, operating heavily in half-spaces and on the flanks interplaying with wingers & FBs. They will thus be tasked with creation from wide areas, so will need to be able to cross as well as carry into the box looking for cutbacks or drawing defenders to open up space for wingers.  \n
        20% Shot assists  \n
        15% Expected assists (xA)  \n
        15% Dribble win %  \n
        15% Cross completion %  \n
        15% Deep completed crosses  \n
        10% Accelerations with the ball  \n
        5% Touches in the box
        ''')
    with st.expander('Second Striker'):
        st.write('''
        An attacking midfielder who is one of the main scoring threats on their team. They can make late runs into the box as well as sit in the box, using movement to create space for a shot. They should be a little creative, but their main role is scoring.  \n
        20% non-penalty xG (npxG)  \n
        20% Touches in the box  \n
        15% Non-penalty goals  \n
        15% Expected assists (xA)  \n
        10% Goal conversion %  \n
        10% Dribble win %  \n
        10% Progressive carries
        ''')
    with st.expander('Playmaking Winger'):
        st.write('''
        A player who is vital in a team's creation from deep positions. They will be involved in creative passing as well as progressing play into more dangerous areas into the feet of more advanced players, instead of heavily involved in the final ball. Because they sit in deep positions, they have to be somewhat capable in defense, even if their main duties are in possession instead of out of possession.  \n
        20% Key passes  \n
        20% Shot assists  \n
        20% Passes into the final third + deep completions (within 20m of goal)  \n
        15% Progressive passes  \n
        15% Smart passes  \n
        10% Assists + 2nd + 3rd assists
        ''')
    with st.expander('Inverted Winger'):
        st.write('''
        A winger who like to cut inside and impact play closer to the the box, if not inside of it. They are still expected to create for teammates, but will try to create for themselves just as frequently. They are a threat to score off the wing.  \n
        25% Shots  \n
        15% non-penalty xG (npxG)  \n
        15% Touches in the box  \n
        15% Dribble win %  \n
        10% Shot assists  \n
        10% Deep completed crosses (within 20m of goal)
        ''')
    with st.expander('Traditional Winger'):
        st.write('''
        A classic wide player who relishes sprinting up the flank, beating players on the dribble, and sending in a cross. These players can cause havoc with their pace/acceleration, dribbling, and crossing.  \n
        20% Shot assists  \n
        17.5% Dribble win %  \n
        17.5% Deep completed crosses (within 20m of goal)  \n
        15% Accelerations with the ball  \n
        10% Expected assists (xA)  \n
        10% Cross completion %
        ''')
    with st.expander('Inside Forward'):
        st.write('''
        Almost acting as a wide striker, these players are wingers who cut inside similarly to inverted wingers but with a much greater emphasis on getting into the box and scoring. These players should be clinical first and foremost.  \n
        20% Touches in the penalty box  \n
        20% Non-penalty expected goals (npxG)  \n
        15% Non-penalty goals  \n
        15% Expected assists (xA)  \n
        10% Goal conversion %  \n
        10% Dribble win %  \n
        10% Progressive carries
        ''')
    with st.expander('Advanced Striker'):
        st.write('''
        This striker should be the main scoring threat in the team. They operate in the box, but are also able to carry the ball themselves in behind the defense. Most of their game revolves arund shooting & scoring, but given where they operate & their role, the best of them will be able to draw defenders onto them in order to create space for teammates, allowing them to generate a few assists on top of their goal tally.  \n
        20% Touches in the penalty box  \n
        20% Non-penalty expected goals (npxG)  \n
        15% Non-penalty goals  \n
        15% Expected assists (xA)  \n
        10% Goal conversion %  \n
        10% Dribble win %  \n
        10% Progressive carries
        ''')
    with st.expander('Deep-Lying Striker'):
        st.write('''
        A striker who can score, but usually site a bit deeper than other strikers so that they can carry into space. They are also involved in linking up play to others running behind them into space created by dropping off the back line, possibly drawing a CB with them. Given their deeper starting location, they are usually a little more involved in their team's play, receiving more passes than other strikers.  \n
        20% Non-penalty expected goals (npxG)  \n
        20% Non-penalty goals  \n
        20% Shot assists  \n
        15% Received passes  \n
        15% Progressive carries  \n
        10% Assists + 2nd & 3rd assists
        ''')
    with st.expander('Target Man'):
        st.write('''
        A striker who is the focal point for long balls & crosses, they are able to win balls in the air and shoot. While some may have other elements to their game, this specific role revolves around winning aerials, shooting, and scoring, all within the box.  \n
        30% Touches in the penalty box  \n
        22.5% Aerial Win %  \n
        22.5% Non-penalty expected goals (npxG)  \n
        20% Shot on target %  \n
        5% Non-penalty goals
        ''')
    with st.expander('Playmaking Striker'):
        st.write('''
        A striker who is a key playmaker for their team. This is close to a false 9. This type of striker will be able to drop deep or sit deep, occupying attacking midfield zones & helping to progress play and create dangerous chances for their teammates. Usually, this type of striker pairs well with wingers who like to cut in, allowing them to receive passes from the strier, in the areas where the striker has just created space. There's not shooting metrics involved in this role, as this is purely a playmaking role, focusing on creating for others.  \n
        20% Shot assists  \n
        20% Key passes  \n
        20% Passes into the final third + deep completions  \n
        15% Expected assists (xA)  \n
        15% Progressive passes  \n
        10% Smart passes
        ''')
    with st.expander('Link-Up Striker'):
        st.write('''
        A striker that is an important cog to their team to progress possession through, but instead of the striker making progressive actions, they are the ones receiving them. They will then lay passes off to teammates, but will also get into the box again to be a scoring threat.  \n
        25% Short pass completion %  \n
        25% Received passes  \n
        10% Shot assists  \n
        10% Key passes  \n
        10% Non-penalty expected goals (npxG)  \n
        10% Non-penalty goals  \n
        10% Attacking duel win % (includes dribbles, ball shields when being pressed, etc.)
        ''')

with map_tab:
    if gender == 'Men':
        available_leagues_df = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup.csv')
    if gender == 'Women':
        available_leagues_df = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup_women.csv')

    available_leagues_df.Country.replace({
        'England':'United Kingdom',
        'Scotland':'United Kingdom',
        'Wales':'United Kingdom',
        'Northern Ireland':'United Kingdom',
        'Bolivia':'Bolivia, Plurinational State of',
        'Czech Republic':'Czechia',
        'Korea Republic':'Korea, Republic of',
        'Kosovo':'Serbia',
        'Moldova':'Moldova, Republic of',
        'Republic of Ireland':'Ireland',
        'Russia':'Russian Federation',
        'Turkey':'Türkiye',
        'UAE':'United Arab Emirates',
    'Vietnam':'Viet Nam',
    'China PR':'China',
    },inplace=True)
    
    countries_avail = available_leagues_df.groupby(['Country','League']).ws_id.count().reset_index().groupby('Country')['League'].agg(', '.join).reset_index()
    lgs = available_leagues_df.groupby(['Country','League'])['Season'].count().reset_index().groupby(['Country']).League.count().reset_index().rename(columns={'League':'# of Leagues'})
    countries_avail = countries_avail.merge(lgs).rename(columns={'League':'Leagues'})
    
    countries_lookup = pd.DataFrame.from_dict(country_numeric_code_lookup,orient='index').reset_index().rename(columns={'index':'Country',0:'ISO_Numeric_Code'})
    countries_avail = countries_lookup.merge(countries_avail,how='outer')
    countries_avail['ISO_Numeric_Code'] = countries_avail['ISO_Numeric_Code'].astype(int)
    #########
    
    #########
    source_countries = alt.topo_feature(data.world_110m.url, 'countries')
    basemap = alt.Chart(source_countries).mark_geoshape(fill='#fbf9f4',stroke='#4a2e19')
    map = alt.Chart(source_countries).mark_geoshape(stroke='#4a2e19').encode(
        color=alt.Color('# of Leagues:Q', scale=alt.Scale(scheme="goldorange")),
        tooltip=[
            "Country:N",
            "Leagues:N",
            "# of Leagues:Q"
        ],
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(countries_avail, 'ISO_Numeric_Code', ["Country","Leagues",'# of Leagues'])
    ).properties(
        # width=800,
        # height=600,
        title=alt.Title(text=f"Available {gender}'s Leagues By Country",
                       subtitle="Hover over each country to see the leagues loaded into the app. Darker red indicates more leagues available")
    
    ).project(
        type="naturalEarth1"
    )
    
    st.altair_chart(basemap+map, use_container_width=True)
    #########
