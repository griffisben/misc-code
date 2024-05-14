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
@st.cache_data(ttl=6*60*60)
def read_csv(link):
    return pd.read_csv(link)
from mplsoccer import VerticalPitch, FontManager
import matplotlib.patheffects as path_effects


def filter_by_position(df, position):
    fw = ["CF", "RW", "LW", "AMF"]
    if position == "Forward":
        return df[df['Main Position'].str.contains('|'.join(fw), na=False)]
    
    stw = ["CF", "RW", "LW", "LAMF", "RAMF"]
    if position == "Strikers and Wingers":
        return df[df['Main Position'].str.contains('|'.join(stw), na=False)]
    
    fwns = ["RW", "LW", "AMF"]
    if position == "Forwards no ST":
        return df[df['Main Position'].str.contains('|'.join(fwns), na=False)]
    
    wing = ["RW", "LW", "WF", "LAMF", "RAMF"]
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

    df['pAdj Tkl+Int per 90'] = df['PAdj Sliding tackles'] + df['PAdj Interceptions']
    df['1st, 2nd, 3rd assists'] = df['Assists per 90'] + df['Second assists per 90'] + df['Third assists per 90']
    df['xA per Shot Assist'] = df['xA per 90'] / df['Shot assists per 90']
    df['Aerial duels won per 90'] = df['Aerial duels per 90'] * (df['Aerial duels won, %']/100)
    df['Cards per 90'] = df['Yellow cards per 90'] + df['Red cards per 90']
    df['Clean sheets, %'] = df['Clean sheets'] / df['Matches played']
    df['npxG'] = df['xG'] - (.76 * df['Penalties taken'])
    df['npxG per 90'] = df['npxG'] / (df['Minutes played'] / 90)
    df['npxG per shot'] = df['npxG'] / (df['Shots'] - df['Penalties taken'])
    df['Passes to final third & deep completions'] = df['Passes to final third per 90'] + df['Deep completions per 90']
    df['Pct of passes being short'] = df['Short / medium passes per 90'] / df['Passes per 90'] * 100
    df['Prog passes and runs per 90'] = df['Progressive passes per 90'] + df['Progressive runs per 90']
    df['Set pieces per 90'] = df['Corners per 90'] + df['Free kicks per 90']
    df['Pct of passes being smart'] = df['Smart passes per 90'] / df['Passes per 90'] * 100

    df = df.dropna(subset=['Position']).reset_index(drop=True)

    df['Main Position'] = df['Position'].str.split().str[0].str.rstrip(',')
    df.fillna(0,inplace=True)
    position_replacements = {
        'LAMF': 'LW',
        'RAMF': 'RW',
        'LCB3': 'LCB',
        'RCB3': 'RCB',
        'LCB5': 'LCB',
        'RCB5': 'RCB',
        'LB5': 'LB',
        'RB5': 'RB',
        'RWB': 'RB',
        'LWB': 'LB'
    }
    df['Main Position'] = df['Main Position'].replace(position_replacements)

    return df


def make_rankings(formation, mins, data, role_position_df, leagues, exp_contracts, expiration_date,
                  min_age, max_age, num, normalize_to_100, chosen_team
                 ):
    formation_positions = {442:['GK','RCB','LCB','RB','LB','RCM','LCM','RW','LW','RS','LS',],
                          4231:['GK','RCB','LCB','RB','LB','RCM','LCM','CAM','RW','LW','ST'],
                          433:['GK','RCB','LCB','RB','LB','RCM','CM','LCM','RW','LW','ST']
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
           'Minutes played', 'Contract expires', 'Squad Position']
    rank_list = pd.DataFrame(columns=cols)
    
    all_cols = ['Player', 'Team', 'Team within selected timeframe', 'Position', 'Age', 'Market value', 'Contract expires', 'Matches played', 'Minutes played', 'Goals', 'xG', 'Assists', 'xA', 'Duels per 90', 'Duels won, %', 'Birth country', 'Passport country', 'Foot', 'Height', 'Weight', 'On loan', 'Successful defensive actions per 90', 'Defensive duels per 90', 'Defensive duels won, %', 'Aerial duels per 90', 'Aerial duels won, %', 'Sliding tackles per 90', 'PAdj Sliding tackles', 'Shots blocked per 90', 'Interceptions per 90', 'PAdj Interceptions', 'Fouls per 90', 'Yellow cards', 'Yellow cards per 90', 'Red cards', 'Red cards per 90', 'Successful attacking actions per 90', 'Goals per 90', 'Non-penalty goals', 'Non-penalty goals per 90', 'xG per 90', 'Head goals', 'Head goals per 90', 'Shots', 'Shots per 90', 'Shots on target, %', 'Goal conversion, %', 'Assists per 90', 'Crosses per 90', 'Accurate crosses, %', 'Crosses from left flank per 90', 'Accurate crosses from left flank, %', 'Crosses from right flank per 90', 'Accurate crosses from right flank, %', 'Crosses to goalie box per 90', 'Dribbles per 90', 'Successful dribbles, %', 'Offensive duels per 90', 'Offensive duels won, %', 'Touches in box per 90', 'Progressive runs per 90', 'Accelerations per 90', 'Received passes per 90', 'Received long passes per 90', 'Fouls suffered per 90', 'Passes per 90', 'Accurate passes, %', 'Forward passes per 90', 'Accurate forward passes, %', 'Back passes per 90', 'Accurate back passes, %', 'Lateral passes per 90', 'Accurate lateral passes, %', 'Short / medium passes per 90', 'Accurate short / medium passes, %', 'Long passes per 90', 'Accurate long passes, %', 'Average pass length, m', 'Average long pass length, m', 'xA per 90', 'Shot assists per 90', 'Second assists per 90', 'Third assists per 90', 'Smart passes per 90', 'Accurate smart passes, %', 'Key passes per 90', 'Passes to final third per 90', 'Accurate passes to final third, %', 'Passes to penalty area per 90', 'Accurate passes to penalty area, %', 'Through passes per 90', 'Accurate through passes, %', 'Deep completions per 90', 'Deep completed crosses per 90', 'Progressive passes per 90', 'Accurate progressive passes, %', 'Conceded goals', 'Conceded goals per 90', 'Shots against', 'Shots against per 90', 'Clean sheets', 'Save rate, %', 'xG against', 'xG against per 90', 'Prevented goals', 'Prevented goals per 90', 'Back passes received as GK per 90', 'Exits per 90', 'Aerial duels per 90.1', 'Free kicks per 90', 'Direct free kicks per 90', 'Direct free kicks on target, %', 'Corners per 90', 'Penalties taken', 'Penalty conversion, %', 'League', 'pAdj Tkl+Int per 90', '1st, 2nd, 3rd assists', 'xA per Shot Assist', 'Aerial duels won per 90', 'Cards per 90', 'Clean sheets, %', 'npxG', 'npxG per 90', 'npxG per shot', 'Passes to final third & deep completions', 'Head goals as pct of all goals', 'Prog passes and runs per 90', 'Main Position', 'midpct1', 'midpct2', 'midpct3', 'midpct4', 'midpct5', 'midpct6', 'midpct7', 'midpct8', 'midpct9', 'midpct10', 'midpct11', 'midpct12', 'fwdpct1', 'fwdpct2', 'fwdpct3', 'fwdpct4', 'fwdpct5', 'fwdpct6', 'fwdpct7', 'fwdpct8', 'fwdpct9', 'fwdpct10', 'fwdpct11', 'fwdpct12', 'defpct1', 'defpct2', 'defpct3', 'defpct4', 'defpct5', 'defpct6', 'defpct7', 'defpct8', 'defpct9', 'defpct10', 'defpct11', 'defpct12', 'gkpct1', 'gkpct2', 'gkpct3', 'gkpct4', 'gkpct5', 'gkpct6', 'gkpct7', 'gkpct8', 'gkpct9', 'gkpct10', 'extrapct', 'extrapct2', 'extrapct3', 'extrapct4', 'extrapct5', 'extrapct6', 'extrapct7', 'extrapct8', 'extrapct9', 'extrapct10', 'extrapct11', 'extrapct12', 'extrapct13', 'extrapct14', 'extrapct15', 'extrapct16', 'extrapct17', 'extrapct18', 'extrapct19', 'extrapct20',
                'CM Score', 'CAM Score', 'Traditional Winger Score', 'Inverted Winger Score', 'Ball Playing CB Score', 'CB Score',
                'Advanced Playmaker Score', 'Deep-Lying Playmaker Score', 'Playmaking Winger Score', 'Focal Point Striker Score',
                'Link-Up Striker Score', 'Playmaking Striker Score', 'Advanced Striker Score', 'Deep-Lying Striker Score',
                'Defensive Mid Score', 'Progressive Midfielder Score', 'Box-to-Box Score', 'Attacking FB Score', 'Second Striker Score', 'Inside Forward Score',
               'Shot-Stopping Distributor Score', 'Spurs LCB Score', 'Number 6 Score', 'Defensive FB Score', 'KVO CAM Score', 'Inverted FB Score', 'Possession Enabler Score']
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
                (.15 * dfProspect['fwdpct1']) +     # np Goals
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
                (.075 * dfProspect['extrapct10']) +  # key passes
                (.2 * dfProspect['fwdpct2']) +     # npxG
                (.125 * dfProspect['fwdpct5']) +      # dribble %
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
                (.15 * dfProspect['extrapct10']) +   # key passes
                (.1 * dfProspect['midpct4']) +     # shot assists
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
                (.2 * dfProspect['extrapct10']) +   # key passes
                (.15 * dfProspect['defpct10']) +     # 1+2+3 assists
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
            
            if foot != 'either':
                dfProspect = dfProspect[dfProspect['Foot']==foot]
            if main_pos != 'any':
                dfProspect = dfProspect[dfProspect['Main Position'].str.contains(main_pos)]
    
    
            ranks = dfProspect[["Player", "Main Position", "Team within selected timeframe", "Age", 'Contract expires', 'Minutes played',
                                "CM Score", 'CAM Score', 'Traditional Winger Score', 'Inverted Winger Score', 'Ball Playing CB Score',
                                'CB Score', 'Advanced Playmaker Score', 'Focal Point Striker Score', 'Link-Up Striker Score', 'Deep-Lying Striker Score',
                                'Advanced Striker Score', 'Playmaking Winger Score', 'Box-to-Box Score', 'Playmaking Striker Score',
                                   'Attacking FB Score', 'Deep-Lying Playmaker Score', 'Second Striker Score', 'Progressive Midfielder Score',
                               'Defensive Mid Score', 'Shot-Stopping Distributor Score', 'Spurs LCB Score', 'Number 6 Score', 'Defensive FB Score',
                               'KVO CAM Score', 'Inverted FB Score', 'Inside Forward Score',  'Possession Enabler Score']]
            ranks = ranks.rename(columns={'Team within selected timeframe': 'Team'})
    
            if normalize_to_100 == 'Yes':
                for i in range(6,len(ranks.columns)):
                    ranks.iloc[:,i] = NormalizeData(ranks.iloc[:,i])
    
            # make the table
            ranks['Score'] = round(ranks['%s Score' %pos_]*100,1)
            ranks.sort_values(by=['Score', 'Age'], ascending=[False,True], inplace=True)
            ranks = ranks.reset_index(drop=True)
            ranks = ranks[['Player', 'Team', 'Age', 'Main Position', 'Score', 'Minutes played','Contract expires']]
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

def scout_report(data_frame, gender, league, season, xtra, template, pos, player_pos, mins, minplay, compares, name, ws_name, team, age, sig, extra_text):
    plt.clf()
    df = data_frame
    df = df[df['League']==full_league_name].reset_index(drop=True)

    # Filter data
    dfProspect = df[(df['Minutes played'] >= mins)].copy()
    dfProspect = filter_by_position(dfProspect, pos)
    raw_valsdf = dfProspect[(dfProspect['Player']==ws_name) & (dfProspect['Team within selected timeframe']==team) & (dfProspect['Age']==age)]

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
    # DEFENDER
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
    # GOALKEEPER
    gk1 = "Conceded goals per 90"
    gk2 = "Prevented goals per 90"
    gk3 = "Shots against per 90"
    gk4 = "Save rate, %"
    gk5 = "Clean sheets, %"
    gk6 = "Exits per 90"
    gk7 = "Aerial duels per 90"
    gk8 = "Passes per 90"
    gk9 = "Accurate long passes, %"
    gk10 = "Average long pass length, m"
    # OTHERS
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

    df_pros = dfProspect

    ranked_columns = [
        'midpct1', 'midpct2', 'midpct3', 'midpct4', 'midpct5', 'midpct6', 'midpct7',
        'midpct8', 'midpct9', 'midpct10', 'midpct11', 'midpct12',
        'fwdpct1', 'fwdpct2', 'fwdpct3', 'fwdpct4', 'fwdpct5', 'fwdpct6', 'fwdpct7',
        'fwdpct8', 'fwdpct9', 'fwdpct10', 'fwdpct11', 'fwdpct12',
        'defpct1','defpct2','defpct3','defpct6','defpct7','defpct8','defpct9','defpct10','defpct11','defpct12',
        'extrapct','extrapct2','extrapct3','extrapct4','extrapct5','extrapct6','extrapct7','extrapct8','extrapct9','extrapct10',
    ]
    inverse_ranked_columns = [
        'defpct4','defpct5'
    ]
    ranked_columns_r = [
        mid1, mid2, mid3, mid4, mid5, mid6, mid7,
        mid8, mid9, mid10, mid11, mid12,
        fwd1, fwd2, fwd3, fwd4, fwd5, fwd6, fwd7,
        fwd8, fwd9, fwd10, fwd11, fwd12,
        def1,def2,def3,def6,def7,def8,def9,def10,def11,def12,
        extra,extra2,extra3,extra4,extra5,extra6,extra7,extra8,extra9,extra10,
    ]
    inverse_ranked_columns_r = [
        def4,def5
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
    column_mapping = {
        'attacking': {
            'midpct1': "Short & Med\nPass %",
            'midpct2': "Long\nPass %",
            'midpct3': "Smart\nPass %",
            'extrapct3': 'Cross\nCompletion %',
            'midpct4': "Shot\nAssists",
            'midpct5': "Expected\nAssists (xA)",
            'extrapct5': 'xA per\nShot Assist',
            'midpct6': "Assists",
            'midpct7': "Second\nAssists",
            'extrapct4': 'Smart\nPasses',
            'fwdpct2': "npxG",
            'fwdpct1': "Non-Pen\nGoals",
            'fwdpct6': "Goals/Shot\non Target %",
            'extrapct9': 'npxG\nper shot',
            'extrapct2': "Shots",
            'fwdpct11': 'Touches in\nPen Box',
            'fwdpct5': "Dribble\nSuccess %",
            'extrapct6': 'Acceleration\nwith Ball',
            'midpct10': "Prog.\nCarries",
            'midpct9': "Prog.\nPasses",
            'defpct1': "Defensive\nActions",
            'midpct12': "Tackles & Int\n(pAdj)",
            'defpct8': 'Aerial\nWin %'
        },
        'defensive': {
            'defpct1': 'Defensive\nActions',
            'defpct2': "Tackles\n(pAdj)",
            'defpct3': "Defensive\nDuels Won %",
            'defpct6': "Shot Blocks",
            'defpct7': "Interceptions\n(pAdj)",
            'extrapct7': 'Aerial Duels\nWon',
            'defpct8': "Aerial\nWin %",
            'defpct9': "Long\nPass %",
            'extrapct10': 'Crosses',
            'extrapct3': 'Cross\nCompletion %',
            'defpct10': "Assists &\n2nd/3rd Assists",
            'defpct11': "Prog.\nPasses",
            'defpct12': "Prog.\nCarries",
            'fwdpct5': "Dribble\nSucces %",
            'extrapct6': 'Acceleration\nwith Ball',
            'midpct5': "Expected\nAssists",
            'defpct4': "Fouls",
            'defpct5': "Cards",
            'extrapct8': 'Fouls Drawn'
        },
        'cb': {
            'defpct1': 'Defensive\nActions',
            'defpct2': "Tackles\n(pAdj)",
            'defpct3': "Defensive\nDuels Won %",
            'defpct6': "Shot Blocks",
            'defpct7': "Interceptions\n(pAdj)",
            'extrapct7': 'Aerial Duels\nWon',
            'defpct8': "Aerial\nWin %",
            'defpct9': "Long\nPass %",
            'defpct10': "Assists &\n2nd/3rd Assists",
            'defpct11': "Prog.\nPasses",
            'defpct12': "Prog.\nCarries",
            'fwdpct5': "Dribble\nSucces %",
            'extrapct6': 'Acceleration\nwith Ball',
            'midpct5': "Expected\nAssists",
            'defpct4': "Fouls",
            'defpct5': "Cards",
            'extrapct8': 'Fouls Drawn'
        }
    }
    if template == 'attacking':
        raw_vals = raw_valsdf[["Player",
                           mid1, mid2, mid3, extra3,
                           mid4,mid5,extra5, mid6, mid7,extra4,
                               fwd2,fwd1,fwd6,extra9,extra2,fwd11,
                           fwd5,extra6,mid10,mid9,
                               def1,mid12,def8
                          ]]
    if template == 'defensive':
        raw_vals = raw_valsdf[["Player",
                           def1, def2, def3, def6,def7,extra7,def8,
                           def9,extra10,extra3, def10, def11,def12,fwd5,extra6,mid5,
                           def4,def5,extra8,
                          ]]

    if template == 'cb':
        raw_vals = raw_valsdf[["Player",
                           def1, def2, def3, def6,def7,extra7,def8,
                           def9, def10, def11,def12,fwd5,extra6,mid5,
                           def4,def5,extra8,
                          ]]

    if template in column_mapping:
        selected_columns = column_mapping[template]
        dfRadarMF = dfRadarMF[['Player'] + list(selected_columns.keys())]
        dfRadarMF.rename(columns=selected_columns, inplace=True)
#         raw_vals = raw_valsdf[['Player'] + list(selected_columns.values())]



#         if template == 'gk':
#             dfRadarMF = dfRadarMF[["Player",
#                                    'gkpct1','gkpct2','gkpct3','gkpct4','gkpct5',
#                                    'gkpct6','gkpct7','gkpct8','gkpct9','gkpct10'
#                                   ]]
#             dfRadarMF.rename(columns={'gkpct1': 'Goals\nConceded',
#                                       'gkpct2': "Goals Prevented\nvs Expected",
#                                       'gkpct3': "Shots Against",
#                                       'gkpct4': "Save %",
#                                       'gkpct5': "Clean Sheet %",
#                                       'gkpct6': 'Att. Cross Claims\nor Punches',
#                                       'gkpct7': "Aerial Wins",
#                                       'gkpct8': "Passes",
#                                       'gkpct9': 'Long Passes',
#                                       'gkpct10': "Long\nPass %",
#                                      }, inplace=True)
#             print('Number of players comparing to:',len(dfProspect))

    ###########################################################################

    df1 = dfRadarMF.T.reset_index()

    df1.columns = df1.iloc[0] 

    df1 = df1[1:]
    df1 = df1.reset_index()
    df1 = df1.rename(columns={'Player': 'Metric',
                        ws_name: 'Value',
                             'index': 'Group'})

    if template == 'attacking':
        for i in range(len(df1)):
            if df1['Group'][i] <= 4:
                df1['Group'][i] = 'Passing'
            elif df1['Group'][i] <= 10:
                df1['Group'][i] = 'Creativity'
            elif df1['Group'][i] <= 16:
                df1['Group'][i] = 'Shooting'
            elif df1['Group'][i] <= 20:
                df1['Group'][i] = 'Ball Movement'
            elif df1['Group'][i] <= 23:
                df1['Group'][i] = 'Defense'

    if template == 'defensive':
        for i in range(len(df1)):
            if df1['Group'][i] <= 7:
                df1['Group'][i] = 'Defending'
            elif df1['Group'][i] <= 16:
                df1['Group'][i] = 'Attacking'
            elif df1['Group'][i] <= 19:
                df1['Group'][i] = 'Fouling'

    if template == 'cb':
        for i in range(len(df1)):
            if df1['Group'][i] <= 7:
                df1['Group'][i] = 'Defending'
            elif df1['Group'][i] <= 14:
                df1['Group'][i] = 'Attacking'
            elif df1['Group'][i] <= 17:
                df1['Group'][i] = 'Fouling'



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

    template_group_sizes = {
        'attacking': [4, 6, 6, 4, 3],
        'defensive': [7, 9, 3],
        'cb': [7, 7, 3],
        'gk': [5, 5]
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
                    textcoords='offset points', color=color,
                    bbox=dict(boxstyle="round", fc=face, ec="black", lw=1))

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

    plt.annotate(f"Bars are percentiles | Values shown are {callout_text} values\nAll values are per 90 minutes | %s\nCompared to %s %s, %i+ mins\nData: Wyscout | %s\nSample Size: %i players" %(extra_text, league, compares, mins, sig, len(dfProspect)),
                 xy = (0, -.075), xycoords='axes fraction',
                ha='left', va='center',
                fontsize=9, fontfamily="DejaVu Sans",
                color="#4A2E19", fontweight="regular", fontname="DejaVu Sans",
                ) 

    if season in ['23-24','2024']:
        clubpath = raw_valsdf['Team logo'].values[0]
        image = Image.open(urllib.request.urlopen(clubpath))
        newax = fig.add_axes([.44,.43,0.15,0.15], anchor='C', zorder=1)
        newax.imshow(image)
        newax.axis('off')

    ax.set_facecolor('#fbf9f4')
    fig = plt.gcf()
    fig.patch.set_facecolor('#fbf9f4')
    fig.set_size_inches(12, (12*.9)) #length, height
    
    fig_text(
        0.88, 0.055, "Created by Ben Griffis\n(@BeGriffis on Twitter)\n\n<Elite (Top 10%)>\n<Above Average (11-35%)>\n<Average (36-66%)>\n<Below Average (Bottom 35%)>", color="#4A2E19",
        highlight_textprops=[{"color": '#01349b'},
                             {'color' : '#007f35'},
                             {"color" : '#9b6700'},
                             {'color' : '#b60918'},
                            ],
        size=10, fig=fig, ha='right',va='center'
    )



    return fig
#######################################################################################################################################
formation_positions = {442:['GK','RCB','LCB','RB','LB','RCM','LCM','RW','LW','RS','LS',],
                      4231:['GK','RCB','LCB','RB','LB','RCM','LCM','CAM','RW','LW','ST'],
                      433:['GK','RCB','LCB','RB','LB','RCM','CM','LCM','RW','LW','ST']
                      }

rank_11_base = read_csv('https://raw.githubusercontent.com/griffisben/misc-code/main/RoleRanksApp/Ranking_XI.csv')
role_position_lookup = read_csv('https://raw.githubusercontent.com/griffisben/misc-code/main/RoleRanksApp/Role_Positions_Lookup.csv')

st.title('Best XI Players')
st.subheader("All data from Wyscout. Created by Ben Griffis (@BeGriffis on Twitter)")
st.subheader("Note: you are allowed to use any of the images you create here in your own work, but you MUST give me credit and not alter the images to remove my signature and Wyscout's name.")
with st.expander('Instructions'):
    st.write('''
    This app is a tool to help you find players who might be performing well in specific roles, and then lets you generate a player's performance radar so that you can see how their data stacks up against others in their position.  \n
    Follow these steps to generate a Best XI ranking image and player radars:  \n
    1) Select whether you want Men's or Women's competitions  \n
    2) Select the season your competition is in. "23-24", "22-23", etc. are leagues which follow Fifa's calendar, i.e. roughly August/September to May/June. "2024", "2023", etc are leagues running from roughly February to November. South America and East Asia are examples  \n
    3) Select your league  \n
    4) Select the base formation you want for the roles. There are only a few loaded, as this is not an exhaustive list and all roles can be generated in these formation. I may add more formations later  \n
    5) Input a minimum minutes threshold. Only players who have played at least this many minutes will be included in the sample. Beware of small sample sizes/variance issues for players with less than around 720 minutes  \n
    6) Select an age range for the Best XI roles. This can account for all ages (keep at 0-45), a minimum age (move the left-most slider to your desired minimum), a maximum age (move the right-most slider to your desired maximum), or a specific range of ages (move both sliders to your desired range, minimum & maximum)  \n
    7) Select if you want only players with contraccts expiring on or before a specific date to be included. This feature can help you find potential free transfers. Please note that these are from Wyscout, which are pulled from Transfermarkt, and may not be totally accurate (some players also have no contract expiration date noted and are therefore not included if you slecet "Yes" for this option  \n
    7a) Enter your desired contract expiration date if needed  \n
    8) Select the number of players you want to see for each role. Please note that if you select more than 7, the Best XI image will only show the top 7, however the table will still show you all players  \n
    9) Select whether you want to normalize role-ranking scores from 0 (lowest score) to 100 (top score), or if you want the raw role-ranking scores (which range from 0 to 100, with 0 meaning the player has the lowest recorded numbers in every included metric, and 100 meaning the player has recorded the highest number in every metric)  \n
    10) Choose all of your roles by position. Once you've made any changes, click the "Update Roles" button  \n
    11) Select whether you want to show players from all teams, or if you want to create a single team's depth chart. Please note that if you create a depth chart, the player scores are all still ranked against all players in that position in the league, not just the team  \n  \n
    Tabs:  \n
    1) Role Ranking Image - this tab is the default, and shows the Best XI nased on all your selected criteria  \n
    2) Role Ranking Table - this tab allows you to view the Best XI in table format. Remember that if you selected more than a Top 7, this tab will have all players, not just the top 7 shown on the image  \n
    3) Player Radar Generation - this tab is where you can add a player's name and age in order to create their radar. Select how you want to color the radar's bars & if you want the player's actual per 90 data to be called out on each bar or if you want the percentiles instead. Then click "Submit Options" to generate their radar  \n
    4) Role Score Definitions & Calculations - this tab houses the definitions of roughly what each role should do (in my opinion, and it is rough), and the metrics & weights that I used to calculate each role
    ''')


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
    lg = st.selectbox('League', (legaues))

with st.sidebar:
    st.header('Choose Basic Options')    
    season = st.selectbox('Season', (lg_lookup[lg_lookup.League == lg].Season.unique().tolist()))
    formation = st.selectbox('Fomation', (4231, 433, 442))
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

    with st.form('Role-Positions'):
        st.header('Role-Positions')
        submitted = st.form_submit_button("Update Roles")
        pos1 = st.selectbox(formation_positions[formation][0], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][0]].pos_role.tolist()))
        pos2 = st.selectbox(formation_positions[formation][1], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][1]].pos_role.tolist()))
        pos3 = st.selectbox(formation_positions[formation][2], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][2]].pos_role.tolist()), index=2)
        pos4 = st.selectbox(formation_positions[formation][3], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][3]].pos_role.tolist()), index=1)
        pos5 = st.selectbox(formation_positions[formation][4], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][4]].pos_role.tolist()))
        pos6 = st.selectbox(formation_positions[formation][5], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][5]].pos_role.tolist()), index=0)
        pos7 = st.selectbox(formation_positions[formation][6], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][6]].pos_role.tolist()), index=3)
        pos8 = st.selectbox(formation_positions[formation][7], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][7]].pos_role.tolist()), index=1)
        pos9 = st.selectbox(formation_positions[formation][8], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][8]].pos_role.tolist()))
        pos10 = st.selectbox(formation_positions[formation][9], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][9]].pos_role.tolist()), index=1)
        pos11 = st.selectbox(formation_positions[formation][10], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][10]].pos_role.tolist()), index=0)

chosen_roles = [pos1,pos2,pos3,pos4,pos5,pos6,pos7,pos8,pos9,pos10,pos11]
role_position_df = pd.DataFrame()
for i in range(0,11):
    role_position_df = pd.concat([role_position_df,role_position_lookup[(role_position_lookup.pos_role == chosen_roles[i]) & (role_position_lookup.form_pos == formation_positions[formation][i])]], ignore_index=True)
role_position_df['formation'] = formation

full_league_name = f"{lg} {season}"
    
if gender == 'Men':
    df = pd.read_csv(f'https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Main%20App/{full_league_name.replace(" ","%20").replace("ü","u").replace("ó","o").replace("ö","o")}.csv')
elif gender == 'Women':
    df = pd.read_csv(f'https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Main%20App/Women/{full_league_name.replace(" ","%20").replace("ü","u").replace("ó","o").replace("ö","o")}.csv')
df['League'] = full_league_name
df = df.dropna(subset=['Position','Team within selected timeframe', 'Age']).reset_index(drop=True)


clean_df = load_league_data(df, full_league_name)
df_basic = clean_df.copy()

with st.sidebar:
    one_team_choice = st.selectbox('One Team Depth Chart?', (['No','Yes']))
    if one_team_choice == 'Yes':
        chosen_team = st.selectbox('League', (sorted(clean_df['Team within selected timeframe'].unique().tolist())))
        team_text = f' {chosen_team} Depth Chart'
    else:
        chosen_team = 'N/A'
        if number_of_players > 7:
            num = 7
        else:
            num = number_of_players
        team_text = f' Top {num} Players Per Role'

rank_list = make_rankings(formation, mins, clean_df, role_position_df, [lg], exp_contracts, expiration_date,
                          min_age=ages[0], max_age=ages[1], num=number_of_players, normalize_to_100=normalize_to_100, chosen_team=chosen_team)
show_ranks = rank_list[['Player','Team','Age','Squad Position','Player Pos.','Score','Role Rank','Formation Pos.']].copy()



path_eff = [path_effects.Stroke(linewidth=0.5, foreground='#fbf9f4'), path_effects.Normal()]

pitch = VerticalPitch(pitch_type='opta', pitch_color='#fbf9f4', line_color='#fbf9f4', line_zorder=1, half=False)
fig, axs = pitch.grid(endnote_height=0.045, endnote_space=0, figheight=12,
                      title_height=0.045, title_space=0,
                      axis=False,
                      grid_height=0.86)
fig.set_facecolor('#fbf9f4')

if ages[0] == 0 and ages[1] == 45:
    age_text = f'Minimum {mins}% of season played'
elif ages[0] == 0:
    age_text = f'Min. {mins}% of season played | U{ages[1]} players only'
elif ages[1] == 45:
    age_text = f'Min. {mins}% of season played | Players {ages[0]} & older'
else:
    age_text = f'Min. {mins}% of season played | Players between {ages[0]} & {ages[1]}'

if exp_contracts == 'y':
    exp_text = f'Players out of contract by {expiration_date} (per Wyscout)'
else:
    exp_text = ''

if exp_text == '':
    sub_title_text = age_text
else:
    sub_title_text = f"{age_text} | {exp_text}"

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
axs['title'].text(0.5, 1.35, f'Data via Wyscout | {lg_lookup[(lg_lookup.League==lg) & (lg_lookup.Season==season)].Date.values[0]} | Created by Ben Griffis (@BeGriffis on Twitter)',
                 ha='center',va='top', size=12, color='#4a2e19')
axs['title'].text(0.5, .95, sub_title_text,
                 ha='center',va='top', size=12, color='#4a2e19')
axs['title'].text(0.5, .6, f'Generated on best11roleranks.streamlit.app',
                 ha='center',va='top', size=12, style='italic', color='#4a2e19')

if normalize_to_100 == 'Yes':
    axs['endnote'].text(0.5, -.3, f"Scores are gnerated by weighting z-scores of various metrics important to each role-position\nScores normalized so that the top player's score is 100 and the worst score is 0",
                     ha='center',va='top', size=10, color='#4a2e19')
else:
    axs['endnote'].text(0.5, -.3, f"Scores are gnerated by weighting z-scores of various metrics important to each role-position",
                     ha='center',va='top', size=10, color='#4a2e19')


show_ranks = show_ranks[['Player','Team','Age','Squad Position','Player Pos.','Score','Role Rank']].copy()

image_tab, table_tab, radar_tab, notes_tab = st.tabs(['Role Ranking Image', 'Role Ranking Table', 'Player Radar Generation', 'Role Score Definitions & Calculations'])

with image_tab:
    fig

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
    with st.form('Player Radar Options'):
        bar_colors = st.selectbox('Bar Color Scheme', ('Benchmarking Percentiles', 'Metric Groups'))
        callout = st.selectbox('Data Labels on Bars', ('Per 90', 'Percentile'))
        player = st.text_input("Player's Radar to Generate", "")
        page = st.number_input("Age of the player to generate (to guarantee the correct player)", step=1)
        submitted = st.form_submit_button("Submit Options")
        
        dfxxx = df_basic[df_basic['Minutes played']>=mins].copy().reset_index(drop=True)
        dfxxx = dfxxx[dfxxx['League']==full_league_name].reset_index(drop=True)
        df1 = dfxxx[['Player', 'Team within selected timeframe', 'Position', 'Age', 'Minutes played']]
        df1 = df1.dropna(subset=['Position', 'Team within selected timeframe', 'Age']).reset_index(drop=True)
        df1 = df1.dropna(subset=['Position']).reset_index(drop=True)
        df1['Age'] = df1['Age'].astype(int)
        df1['Main Position'] = df1['Position'].str.split().str[0].str.rstrip(',')
        df1 = df1.dropna(subset=['Main Position']).reset_index(drop=True)
        position_replacements = {
            'LAMF': 'LW',
            'RAMF': 'RW',
            'LCB3': 'LCB',
            'RCB3': 'RCB',
            'LCB5': 'LCB',
            'RCB5': 'RCB',
            'LB5': 'LB',
            'RB5': 'RB',
            'RWB': 'RB',
            'LWB': 'LB',
            'LCM3': 'LCMF',
            'RCM3': 'RCMF'
        }
    
        df1['Main Position'] = df1['Main Position'].replace(position_replacements)
    
        ws_pos = ['LCMF3','RCMF3','LAMF','LW','RB','LB','LCMF','DMF','RDMF','RWF','AMF','LCB','RWB','CF','LWB','GK','LDMF','RCMF','LWF','RW','RAMF','RCB','CB','RCB3','LCB3','RB5','RWB5','LB5','LWB5']
        poses = ['Midfielder','Midfielder','Winger','Winger','Fullback','Fullback','Midfielder','Midfielder no CAM','Midfielder no CAM','Winger','Midfielder no DM','CB','Fullback','CF','Fullback','GK','Midfielder no CAM','Midfielder','Winger','Winger','Winger','CB','CB','CB','CB','Fullback','Fullback','Fullback','Fullback']
        template = ['attacking','attacking','attacking','attacking','defensive','defensive','attacking','attacking','attacking','attacking','attacking','cb','defensive','attacking','defensive','gk','attacking','attacking','attacking','attacking','attacking','cb','cb','cb','cb','defensive','defensive','defensive','defensive']
        compares = ['Central Midfielders','Central Midfielders','Wingers','Wingers','Fullbacks','Fullbacks','Central Midfielders','Central & Defensive Mids','Central & Defensive Mids','Wingers','Central & Attacking Mids','Center Backs','Fullbacks','Strikers','Fullbacks','Goalkeepers','Central & Defensive Mids','Central Midfielders','Wingers','Wingers','Wingers','Center Backs','Center Backs','Center Backs','Center Backs','Fullbacks','Fullbacks','Fullbacks','Fullbacks']
    
        xtratext = lg_lookup[(lg_lookup.League==lg) & (lg_lookup.Season==season)].Date.values[0]

        try:
            gen = df1[(df1['Player']==player) & (df1['Age']==page)]
            ix = ws_pos.index(gen['Main Position'].values[0])
            minplay = int(gen['Minutes played'].values[0])

            
            radar_img = scout_report(
                data_frame = df_basic, ##
                gender = gender, ##
                league = lg, ##
                season = season, ##
                xtra = ' current',
                template = template[ix], ##
                pos = poses[ix],
                player_pos = ws_pos[ix],
                compares = compares[ix],
                mins = mins,
                minplay=minplay,
                name = gen['Player'].values[0],
                ws_name = gen['Player'].values[0],
                team = gen['Team within selected timeframe'].values[0],
                age = gen['Age'].values[0],
                sig = 'Twitter: @BeGriffis',
                extra_text = xtratext,
            )
            st.pyplot(radar_img.figure)
        except:
            st.text("Please enter a valid name & age.  \nPlease check spelling as well.  \nIf you entered a GK, I'm sorry but I have not built GK radars yet... my apologies!")

    
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


