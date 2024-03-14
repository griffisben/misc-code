import seaborn as sns
import pandas as pd
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

def load_league_data(data):
    df = data

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

    df = df.dropna(subset=['Position']).reset_index(drop=True)

    df['Main Position'] = df['Position'].str.split().str[0].str.rstrip(',')
    df.fillna(0,inplace=True)
    leagues = [lg]
    df['Minutes played'] /= 90 * max(df['Matches played'])
    return df


def make_rankings(formation, mins, data, role_position_df, leagues, exp_contracts):
    formation_positions = {442:['GK','RCB','LCB','RB','LB','RCM','LCM','RM','LM','RS','LS',],
                          4231:['GK','RCB','LCB','RB','LB','RCM','LCM','CAM','RW','LW','ST'],
                          433:['GK','RCB','LCB','RB','LB','RCM','CM','LCM','RW','LW','ST']
                          }
    df = data
    cols = ['Player', 'Team', 'Age', 'Pos.', 'Score',
           'Minutes played', 'Contract expires', 'Squad Position']
    rank_list = pd.DataFrame(columns=cols)
    
    all_cols = ['Player', 'Team', 'Team within selected timeframe', 'Position', 'Age', 'Market value', 'Contract expires', 'Matches played', 'Minutes played', 'Goals', 'xG', 'Assists', 'xA', 'Duels per 90', 'Duels won, %', 'Birth country', 'Passport country', 'Foot', 'Height', 'Weight', 'On loan', 'Successful defensive actions per 90', 'Defensive duels per 90', 'Defensive duels won, %', 'Aerial duels per 90', 'Aerial duels won, %', 'Sliding tackles per 90', 'PAdj Sliding tackles', 'Shots blocked per 90', 'Interceptions per 90', 'PAdj Interceptions', 'Fouls per 90', 'Yellow cards', 'Yellow cards per 90', 'Red cards', 'Red cards per 90', 'Successful attacking actions per 90', 'Goals per 90', 'Non-penalty goals', 'Non-penalty goals per 90', 'xG per 90', 'Head goals', 'Head goals per 90', 'Shots', 'Shots per 90', 'Shots on target, %', 'Goal conversion, %', 'Assists per 90', 'Crosses per 90', 'Accurate crosses, %', 'Crosses from left flank per 90', 'Accurate crosses from left flank, %', 'Crosses from right flank per 90', 'Accurate crosses from right flank, %', 'Crosses to goalie box per 90', 'Dribbles per 90', 'Successful dribbles, %', 'Offensive duels per 90', 'Offensive duels won, %', 'Touches in box per 90', 'Progressive runs per 90', 'Accelerations per 90', 'Received passes per 90', 'Received long passes per 90', 'Fouls suffered per 90', 'Passes per 90', 'Accurate passes, %', 'Forward passes per 90', 'Accurate forward passes, %', 'Back passes per 90', 'Accurate back passes, %', 'Lateral passes per 90', 'Accurate lateral passes, %', 'Short / medium passes per 90', 'Accurate short / medium passes, %', 'Long passes per 90', 'Accurate long passes, %', 'Average pass length, m', 'Average long pass length, m', 'xA per 90', 'Shot assists per 90', 'Second assists per 90', 'Third assists per 90', 'Smart passes per 90', 'Accurate smart passes, %', 'Key passes per 90', 'Passes to final third per 90', 'Accurate passes to final third, %', 'Passes to penalty area per 90', 'Accurate passes to penalty area, %', 'Through passes per 90', 'Accurate through passes, %', 'Deep completions per 90', 'Deep completed crosses per 90', 'Progressive passes per 90', 'Accurate progressive passes, %', 'Conceded goals', 'Conceded goals per 90', 'Shots against', 'Shots against per 90', 'Clean sheets', 'Save rate, %', 'xG against', 'xG against per 90', 'Prevented goals', 'Prevented goals per 90', 'Back passes received as GK per 90', 'Exits per 90', 'Aerial duels per 90.1', 'Free kicks per 90', 'Direct free kicks per 90', 'Direct free kicks on target, %', 'Corners per 90', 'Penalties taken', 'Penalty conversion, %', 'League', 'pAdj Tkl+Int per 90', '1st, 2nd, 3rd assists', 'xA per Shot Assist', 'Aerial duels won per 90', 'Cards per 90', 'Clean sheets, %', 'npxG', 'npxG per 90', 'npxG per shot', 'Passes to final third & deep completions', 'Head goals as pct of all goals', 'Prog passes and runs per 90', 'Main Position', 'midpct1', 'midpct2', 'midpct3', 'midpct4', 'midpct5', 'midpct6', 'midpct7', 'midpct8', 'midpct9', 'midpct10', 'midpct11', 'midpct12', 'fwdpct1', 'fwdpct2', 'fwdpct3', 'fwdpct4', 'fwdpct5', 'fwdpct6', 'fwdpct7', 'fwdpct8', 'fwdpct9', 'fwdpct10', 'fwdpct11', 'fwdpct12', 'defpct1', 'defpct2', 'defpct3', 'defpct4', 'defpct5', 'defpct6', 'defpct7', 'defpct8', 'defpct9', 'defpct10', 'defpct11', 'defpct12', 'gkpct1', 'gkpct2', 'gkpct3', 'gkpct4', 'gkpct5', 'gkpct6', 'gkpct7', 'gkpct8', 'gkpct9', 'gkpct10', 'extrapct', 'extrapct2', 'extrapct3', 'extrapct4', 'extrapct5', 'extrapct6', 'extrapct7', 'extrapct8', 'extrapct9', 'extrapct10', 'extrapct11', 'extrapct12', 'extrapct13', 'extrapct14', 'extrapct15', 'extrapct16', 'extrapct17', 'extrapct18', 'extrapct19', 'extrapct20',
                'CM Score', 'CAM Score', 'Traditional Winger Score', 'Inverted Winger Score', 'Ball Playing CB Score', 'CB Score',
                'Advanced Playmaker Score', 'Deep-Lying Playmaker Score', 'Playmaking Winger Score', 'Focal Point Striker Score',
                'Link-Up Striker Score', 'Playmaking Striker Score', 'Advanced Striker Score', 'Deep-Lying Striker Score',
                'Defensive Mid Score', 'Progressive Midfielder Score', 'Box-to-Box Score', 'Attacking FB Score', 'Second Striker Score',
               'Shot-Stopping Distributor Score', 'Spurs LCB Score', 'Number 6 Score', 'Defensive FB Score', 'KVO CAM Score', 'Inverted FB Score']
    full_prospect_df = pd.DataFrame(columns=all_cols)
    
    
    rank_11 = role_position_df[role_position_df['formation']==formation].copy().reset_index(drop=True)
    
    for q in range(len(rank_11)):
        pos_ = rank_11.pos_[q]
        pos = rank_11.pos[q]
        pos_buckets = rank_11.pos_bucket[q]
        foot = rank_11.foot[q]
        num = rank_11.num[q]
        main_pos = rank_11.main_position[q]
        
        
        for z in range(len(leagues)):
            dfProspect = df[(df['Minutes played']>=mins) & (df['League']==leagues[z])].copy()
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
    
            # The first line in this loop is how I get the z-scores to start at 0. I checked the distribution chart at the bottom, and it's the same shape of course
            # the second line normalizes
            for i in range(141,209):
                dfProspect.iloc[:,i] = dfProspect.iloc[:,i] + abs(dfProspect.iloc[:,i].min())
                dfProspect.iloc[:,i] = NormalizeData(dfProspect.iloc[:,i])
    
    
            #############################################################################
            #############################################################################
            ## Section with all the scores. Of course, very much a fluid thing now as I play around and calibrate
            ## And I also want to make buckets like ball winning, passing, etc and then use those instead of individual metrics
    
            dfProspect['Shot-Stopping Distributor Score'] = (
                (.5 * dfProspect['gkpct10']) +   # psxG+-
                (.2 * dfProspect['gkpct2']) +   # save %
                (.15 * dfProspect['gkpct4']) +  # pct passes being short
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
                (.1 * dfProspect['extrapct15']) +     # short cmp %
                (.1 * dfProspect['midpct2'])   # long pass cmp %
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
    #         full_prospect_df = full_prospect_df.append(dfProspect)
            
        
    #     full_prospect_df = full_prospect_df.drop_duplicates()
    
    
            ranks = dfProspect[["Player", "Main Position", "Team within selected timeframe", "Age", 'Contract expires', 'Minutes played',
                                "CM Score", 'CAM Score', 'Traditional Winger Score', 'Inverted Winger Score', 'Ball Playing CB Score',
                                'CB Score', 'Advanced Playmaker Score', 'Focal Point Striker Score', 'Link-Up Striker Score', 'Deep-Lying Striker Score',
                                'Advanced Striker Score', 'Playmaking Winger Score', 'Box-to-Box Score', 'Playmaking Striker Score',
                                   'Attacking FB Score', 'Deep-Lying Playmaker Score', 'Second Striker Score', 'Progressive Midfielder Score',
                               'Defensive Mid Score', 'Shot-Stopping Distributor Score', 'Spurs LCB Score', 'Number 6 Score', 'Defensive FB Score',
                               'KVO CAM Score', 'Inverted FB Score']]
            ranks = ranks.rename(columns={'Team within selected timeframe': 'Team'})
    
            # Final normalize, so that we get #1 player to be 100, instead of like, 60ish
            for i in range(6,len(ranks.columns)):
                ranks.iloc[:,i] = NormalizeData(ranks.iloc[:,i])
    
            # make the table
            ranks['Score'] = round(ranks['%s Score' %pos_]*100,1)
            ranks.sort_values(by=['Score', 'Age'], ascending=[False,True], inplace=True)
            ranks = ranks.reset_index(drop=True)
            ranks = ranks[['Player', 'Team', 'Age', 'Main Position', 'Score', 'Minutes played','Contract expires']]
            ranks = ranks.rename(columns={'Main Position': 'Pos.'})
            ranks.index = ranks.index+1
            ranks['Squad Position'] = rank_11.pos_role[q]
            if exp_contracts == 'y':
                ranks = ranks[ranks['Contract expires'].isin(exp_dates)]
            ranks = ranks[ranks['Age'].between(min_age,max_age)]
    
            rank_list = pd.concat([rank_list,ranks])
    
    # rank_list.to_csv('player ranks.csv')
    rank_list.Age = rank_list.Age.astype(int)
    rank_list = rank_list.reset_index().rename(columns={'index':'Role Rank'})
    
    rank_list_final = pd.DataFrame(columns=rank_list.columns)
    
    for q in range(len(rank_11)):
        rank_list_final = pd.concat([rank_list_final,rank_list[rank_list['Squad Position']==rank_11.pos_role[q]].sort_values(by=['Score','Age'],ascending=[False,True]).head(num)])
    rank_list = rank_list_final.copy()
    return rank_list

#######################################################################################################################################
#######################################################################################################################################
formation_positions = {442:['GK','RCB','LCB','RB','LB','RCM','LCM','RW','LW','RS','LS',],
                      4231:['GK','RCB','LCB','RB','LB','RCM','LCM','CAM','RW','LW','ST'],
                      433:['GK','RCB','LCB','RB','LB','RCM','CM','LCM','RW','LW','ST']
                      }

rank_11_base = read_csv('https://raw.githubusercontent.com/griffisben/misc-code/main/RoleRanksApp/Ranking_XI.csv')
role_position_lookup = read_csv('https://raw.githubusercontent.com/griffisben/misc-code/main/RoleRanksApp/Role_Positions_Lookup.csv')

st.title('Best XI Players')
st.subheader("All data from Wyscout")
st.subheader('Created by Ben Griffis (Twitter: @BeGriffis)')

with st.sidebar:
    st.header('Choose Gender')
    gender = st.selectbox('Gender', ('Men','Women'))
if gender == 'Men':
    lg_lookup = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup.csv')
    df = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/WS_Data.csv')
if gender == 'Women':
    lg_lookup = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup_women.csv')
    df = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/WS_Data_Women.csv')
df = df.dropna(subset=['Position','Team within selected timeframe', 'Age']).reset_index(drop=True)
##########

with st.sidebar:
    st.header('Choose Basic Options')
    with st.expander('Note on Seasons'):
        st.write('''
        Please note that with prior seasons, the players & leagues are correct but the team names can sometimes be off. Ages are also current ages, not ages in the season... I'm working on remedying this.
        ''')

    season = st.selectbox('Season', (['23-24','2023','22-23','2022','21-22']))
    lg_lookup_ssn = lg_lookup[lg_lookup.Season==season]
    lg = st.selectbox('League', (lg_lookup_ssn.League.tolist()))
    formation = st.selectbox('Fomation', (433, 4231, 442))
    mins = st.number_input('Minimum % of Season Played', 30, 75, 40)
    exp_contracts_ = st.selectbox('Only Expiring Contracts?', (['No','Yes']))
    exp_contracts = 'y' if exp_contracts_ == 'Yes'

    pos1 = st.selectbox(formation_positions[formation][0], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][0]].pos_role.tolist()))
    pos2 = st.selectbox(formation_positions[formation][1], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][1]].pos_role.tolist()))
    pos3 = st.selectbox(formation_positions[formation][2], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][2]].pos_role.tolist()))
    pos4 = st.selectbox(formation_positions[formation][3], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][3]].pos_role.tolist()))
    pos5 = st.selectbox(formation_positions[formation][4], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][4]].pos_role.tolist()))
    pos6 = st.selectbox(formation_positions[formation][5], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][5]].pos_role.tolist()))
    pos7 = st.selectbox(formation_positions[formation][6], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][6]].pos_role.tolist()))
    pos8 = st.selectbox(formation_positions[formation][7], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][7]].pos_role.tolist()))
    pos9 = st.selectbox(formation_positions[formation][8], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][8]].pos_role.tolist()))
    pos10 = st.selectbox(formation_positions[formation][9], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][9]].pos_role.tolist()))
    pos11 = st.selectbox(formation_positions[formation][10], (role_position_lookup[role_position_lookup.form_pos == formation_positions[formation][10]].pos_role.tolist()))

chosen_roles = [pos1,pos2,pos3,pos4,pos5,pos6,pos7,pos8,pos9,pos10,pos11]
role_position_df = pd.DataFrame()
for i in range(0,11):
    role_position_df = pd.concat([role_position_df,role_position_lookup[(role_position_lookup.pos_role == chosen_roles[i]) & (role_position_lookup.form_pos == formation_positions[formation][i])]], ignore_index=True)
role_position_df['formation'] = formation
# role_position_df

clean_df = load_league_data(df)
rank_list = make_rankings(formation, mins/100, clean_df, role_position_df, [lg])
rank_list
