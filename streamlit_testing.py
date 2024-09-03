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
import urllib.request
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
import plotly.express as px
import plotly.figure_factory as ff
from plotly.graph_objects import Layout
from highlight_text import fig_text

colorscales = px.colors.named_colorscales()
colorscales2 = [f"{cc}_r" for cc in colorscales]
colorscales += colorscales2

#from st_paywall import add_auth
#add_auth(required=True)


@st.cache_data(ttl=60*15)

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


def read_csv(link):
    return pd.read_csv(link)
def _update_slider(value):
    for i in range(1, 34):
        st.session_state[f"slider{i}"] = value

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
def filter_by_position_long(df, position):
    fw = ["CF", "RW", "LW", "AMF"]
    if position == "Forwards (AM, W, CF)":
        return df[df['Main Position'].str.contains('|'.join(fw), na=False)]
    
    stw = ["CF", "RW", "LW", "LAMF", "RAMF"]
    if position == "Strikers and Wingers":
        return df[df['Main Position'].str.contains('|'.join(stw), na=False)]
    
    fwns = ["RW", "LW", "AMF"]
    if position == "Forwards no ST (AM, W)":
        return df[df['Main Position'].str.contains('|'.join(fwns), na=False)]
    
    wing = ["RW", "LW", "WF", "LAMF", "RAMF"]
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
    df['Pct of passes being lateral'] = df['Lateral passes per 90'] / df['Passes per 90'] * 100
    df['Goals prevented %'] = (df['xG against per 90'] - df['Conceded goals per 90']) / df['xG against per 90'] * 100

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

def scout_report(data_frame, gender, league, season, xtra, template, pos, player_pos, mins, minplay, compares, name, ws_name, team, age, sig, extra_text, custom_radar, dist_labels, logo_dict, metric_selections=None):
    plt.clf()
    df = data_frame
    df = df[df['League']==full_league_name].reset_index(drop=True)

    # Filter data
    dfProspect = df[(df['Minutes played'] >= mins)].copy()
    dfProspect = filter_by_position(dfProspect, pos)
    raw_valsdf = dfProspect[(dfProspect['Player']==ws_name) & (dfProspect['Team within selected timeframe']==team) & (dfProspect['Age']==age)]
    raw_valsdf_full = dfProspect.copy()
    
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
    gk1 = "Conceded goals per 90" #a2
    gk2 = "Prevented goals per 90" #a4
    gk3 = "Shots against per 90" #a1
    gk4 = "Save rate, %" #a3
    gk5 = "Clean sheets, %"
    gk6 = "Exits per 90" #a5
    gk7 = "Aerial duels per 90"
    gk8 = "Passes per 90" #b2
    gk9 = "Accurate long passes, %" #b5
    gk10 = "Average long pass length, m"
    gk11 = 'Pct of passes being short' #b3
    gk12 = "Pct of passes being lateral" #b4
    gk13 = "Received passes per 90" #b1
    gk14 = "Goals prevented %" #a4
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
        'gkpct2', 'gkpct4', 'gkpct5', 'gkpct6', 'gkpct7',
        'gkpct8', 'gkpct9', 'gkpct10', 'gkpct11', 'gkpct12', 'gkpct13', 'gkpct14',
        'defpct1','defpct2','defpct3','defpct6','defpct7','defpct8','defpct9','defpct10','defpct11','defpct12',
        'extrapct','extrapct2','extrapct3','extrapct4','extrapct5','extrapct6','extrapct7','extrapct8','extrapct9','extrapct10',
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
            },
            'gk': {
                'gkpct3': 'Shots\nAgainst',
                'gkpct1': "Goals\nConceded",
                'gkpct4': "Save %",
                'gkpct14': "Goals\nPrevented %",
                'gkpct2': 'Prevented\nGoals',
                'gkpct6': "Coming Off\nLine",
                'gkpct13': 'Received\nPasses',
                'gkpct8': "Passes",
                'gkpct11': "% of Passes\nBeing Short",
                'gkpct12': "% of Passes\nBeing Lateral",
                'gkpct9': "Long Pass\nCmp %",
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
            raw_vals_full = raw_valsdf_full[["Player",
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
            raw_vals_full = raw_valsdf_full[["Player",
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
            raw_vals_full = raw_valsdf_full[["Player",
                               def1, def2, def3, def6,def7,extra7,def8,
                               def9, def10, def11,def12,fwd5,extra6,mid5,
                               def4,def5,extra8,
                              ]]
        if template == 'gk':
            raw_vals = raw_valsdf[["Player",
                               gk3, gk1, gk4, gk14, gk2, gk6,
                               gk13, gk8, gk11, gk12, gk9
                              ]]
            raw_vals_full = raw_valsdf_full[["Player",
                               gk3, gk1, gk4, gk14, gk2, gk6,
                               gk13, gk8, gk11, gk12, gk9
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
                    
        if template == 'gk':
            for i in range(len(df1)):
                if df1['Group'][i] <= 6:
                    df1['Group'][i] = 'Defending'
                elif df1['Group'][i] <= 11:
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
            'attacking': [4, 6, 6, 4, 3],
            'defensive': [7, 9, 3],
            'cb': [7, 7, 3],
            'gk': [6, 5]
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
    plt.annotate(f"Bars are percentiles | Values shown are {callout_text} values\nAll values are per 90 minutes | %s\nCompared to %s %s, %i+ mins\nData: Wyscout | %s\nSample Size: %i players{dist_text}" %(extra_text, league, compares, mins, sig, len(dfProspect)),
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
        0.88, 0.055, "Created by Ben Griffis\n(@BeGriffis on Twitter)\n\n<Elite (Top 10%)>\n<Above Average (11-35%)>\n<Average (36-66%)>\n<Below Average (Bottom 35%)>", color="#4A2E19",
        highlight_textprops=[{"color": '#01349b'},
                             {'color' : '#007f35'},
                             {"color" : '#9b6700'},
                             {'color' : '#b60918'},
                            ],
        size=10, fig=fig, ha='right',va='center'
    )



    return fig

def create_player_research_table(df_basic, mins, full_league_name, pos, min_age, max_age):
    dfProspect = df_basic[(df_basic['Minutes played'] >= mins) & (df_basic['League'] == full_league_name)].copy()
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
    
    ranked_columns = [
        'midpct1', 'midpct2', 'midpct3', 'midpct4', 'midpct5', 'midpct6', 'midpct7',
        'midpct8', 'midpct9', 'midpct10', 'midpct11', 'midpct12',
        'fwdpct1', 'fwdpct2', 'fwdpct3', 'fwdpct4', 'fwdpct5', 'fwdpct6', 'fwdpct7',
        'fwdpct8', 'fwdpct9', 'fwdpct10', 'fwdpct11', 'fwdpct12',
        'gkpct2', 'gkpct4', 'gkpct5', 'gkpct6', 'gkpct7',
        'gkpct8', 'gkpct9', 'gkpct10', 'gkpct11', 'gkpct12', 'gkpct13', 'gkpct14',
        'defpct1','defpct2','defpct3','defpct6','defpct7','defpct8','defpct9','defpct10','defpct11','defpct12',
        'extrapct','extrapct2','extrapct3','extrapct4','extrapct5','extrapct6','extrapct7','extrapct8','extrapct9','extrapct10',
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
    
    
    final = dfProspect[['Player','Age','League','Position','Team within selected timeframe','Birth country',
    'fwdpct1','fwdpct2','fwdpct5','fwdpct6','fwdpct11','midpct1','midpct3','midpct4','midpct5','midpct6','midpct7','midpct8','midpct9','midpct10','midpct11','midpct12','defpct1','defpct2','defpct3','defpct4','defpct5','defpct6','defpct7','defpct8','defpct9','defpct10',
                        'gkpct1','gkpct2','gkpct3','gkpct4','gkpct6','gkpct8','gkpct9', 'gkpct11', 'gkpct12', 'gkpct13', 'gkpct14',
                        'extrapct','extrapct2','extrapct3','extrapct4','extrapct5','extrapct6','extrapct7','extrapct8','extrapct9','extrapct10',
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
    'gkpct3': 'Shots\nAgainst',
    'gkpct1': "Goals\nConceded",
    'gkpct4': "Save %",
    'gkpct14': "Goals\nPrevented %",
    'gkpct2': 'Prevented\nGoals',
    'gkpct6': "Coming Off\nLine",
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

st.subheader("All data from Wyscout. Created by Ben Griffis (@BeGriffis on Twitter)")
st.subheader("You are allowed to use any of the images you create here in your own work, but you may not alter the images.")
with st.expander('App Details & Instructions'):
    st.write('''
    This app helps you find players that meet specific criteria.
    1) First, choose a league & minimum minutes threshold. This initializes the sample used to generate percentile rankings.
    2) Then, use the metric filters on the "Player Search, Filters" tab to pass a minimum percentile ranking thresholds & an age range.
    3) Players not meeting ALL of these criteria will be filtered out.
    4) Type or copy+paste any of the player names into the textbox on the "Player Radar Generation" tab to generate their radar chart.  \n  \n
    5) On the "Player Radar Generation" tab, select the Bar color Scheme (bars colored by percentile rank or metric group), Data Labels On Bars (per 90 values or percentile ranks in the bubbles calling out data), and if you want Distribution Label Lines on each bar, calling out both the average and +/- 1 standard deviation of the metric  \n
    NOTE: the player you want a radar for doesn't need to be in the table (as in, maybe they don't hit the metric filters you've set or are above the age limit), but they do need to meet the sample criteria of gender, league, & minimum minutes played.  \n  \n
    Finally, you can use the Scatter Plots tab to plot players with an X and Y variable, as well as coloring each point by a third variable.
    ''')


logo_dict_df = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Wyscout_Logo_Dict.csv')
logo_dict = pd.Series(logo_dict_df['Team logo'].values,index=logo_dict_df['Team']).to_dict()

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
    with st.form('Options Select'):
        st.header('Choose Basic Options')    
        season = st.selectbox('Season', (sorted(lg_lookup[lg_lookup.League == lg].Season.unique().tolist(),reverse=True)))
        mins = st.number_input('Minimum Minutes Played', 300, 2000, 900)
        submitted = st.form_submit_button("Submit Options")


full_league_name = f"{lg} {season}"
update_date = lg_lookup[(lg_lookup.League==lg) & (lg_lookup.Season==season)].Date.values[0]

    
if gender == 'Men':
    df = pd.read_csv(f'https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Main%20App/{full_league_name.replace(" ","%20").replace("ü","u").replace("ó","o").replace("ö","o").replace("ã","a")}.csv')
elif gender == 'Women':
    df = pd.read_csv(f'https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Main%20App/Women/{full_league_name.replace(" ","%20").replace("ü","u").replace("ó","o").replace("ö","o").replace("ã","a")}.csv')
df['League'] = full_league_name
df = df.dropna(subset=['Position','Team within selected timeframe', 'Age']).reset_index(drop=True)


clean_df = load_league_data(df, full_league_name)
df_basic = clean_df.copy()


radar_tab, filter_tab, filter_table_tab, scatter_tab = st.tabs(['Player Radar Generation', 'Player Search, Filters', 'Player Search, Results', 'Scatter Plots'])


with radar_tab:
    with st.form('Player Radar Options'):
        custom_radar_q='n'
        bar_colors = st.selectbox('Bar Color Scheme', ('Benchmarking Percentiles', 'Metric Groups'))
        callout = st.selectbox('Data Labels on Bars', ('Per 90', 'Percentile'))
        dist_labels = st.selectbox('Distribution Label Lines on Bars?', ('Yes', 'No'))
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
                custom_radar='n',
                dist_labels=dist_labels,
                logo_dict=logo_dict,
            )
            st.pyplot(radar_img.figure)
        except:
            st.text("Please enter a valid name & age.  \nPlease check spelling as well.")
        
with filter_tab:
    st.button("Reset Sliders", on_click=_update_slider, kwargs={"value": 0.0})
    with st.form('Minimum Percentile Filters'):
        submitted = st.form_submit_button("Submit Filters")
        pos_select = st.selectbox('Positions', ('Strikers', 'Strikers and Wingers', 'Forwards (AM, W, CF)',
                                'Forwards no ST (AM, W)', 'Wingers', 'Central Midfielders (DM, CM, CAM)',
                                'Central Midfielders no CAM (DM, CM)', 'Central Midfielders no DM (CM, CAM)', 'Fullbacks (FBs/WBs)',
                                'Defenders (CB, FB/WB, DM)', 'Centre-Backs', 'CBs & DMs','Goalkeepers'))
        ages = st.slider('Age Range (only for filter tab, not radar)', 0, 45, (0, 45))
            
        if ['slider1','slider2','slider3','slider4','slider5','slider6','slider7','slider8','slider9','slider10','slider11','slider12','slider13','slider14','slider15','slider16','slider17','slider18','slider19','slider20','slider21','slider22','slider23','slider24','slider25','slider26','slider27','slider28','slider29','slider30','slider31','slider32','slider33'] not in st.session_state:
            pass
        
        short = st.slider('Short & Medium Pass Cmp %', 0.0, 1.0, 0.0, key='slider1')
        long = st.slider('Long Pass Cmp %', 0.0, 1.0, 0.0, key='slider2')
        passestot = st.slider('Passes per 90', 0.0, 1.0, 0.0, key='slider3')
        smart = st.slider('Smart Passes per 90', 0.0, 1.0, 0.0, key='slider4')
        crosspct = st.slider('Cross Cmp %', 0.0, 1.0, 0.0, key='slider5')
        crosses = st.slider('Crosses per 90', 0.0, 1.0, 0.0, key='slider6')
        shotassist = st.slider('Shot Assists per 90', 0.0, 1.0, 0.0, key='slider7')
        xa = st.slider('xA per 90', 0.0, 1.0, 0.0, key='slider8')
        xasa = st.slider('xA per Shot Assist', 0.0, 1.0, 0.0, key='slider9')
        ast = st.slider('Assists per 90', 0.0, 1.0, 0.0, key='slider10')
        ast2 = st.slider('Second Assists per 90', 0.0, 1.0, 0.0, key='slider11')
        ast123 = st.slider('1st, 2nd, & 3rd Assists', 0.0, 1.0, 0.0, key='slider12')
        npxg = st.slider('npxG per 90', 0.0, 1.0, 0.0, key='slider13')
        npg = st.slider('Non-Pen Goals per 90', 0.0, 1.0, 0.0, key='slider14')
        gc = st.slider('Goals per Shot on Target', 0.0, 1.0, 0.0, key='slider15')
        npxgshot = st.slider('npxG per shot', 0.0, 1.0, 0.0, key='slider16')
        shots = st.slider('Shots per 90', 0.0, 1.0, 0.0, key='slider17')
        boxtouches = st.slider('Touches in Penalty Box per 90', 0.0, 1.0, 0.0, key='slider18')
        drib = st.slider('Dribble Success %', 0.0, 1.0, 0.0, key='slider19')
        accel = st.slider('Accelerations per 90', 0.0, 1.0, 0.0, key='slider20')
        progcarry = st.slider('Progressive Carries per 90', 0.0, 1.0, 0.0, key='slider21')
        progpass = st.slider('Progressive Passes per 90', 0.0, 1.0, 0.0, key='slider22')
        aerial = st.slider('Aerial Win %', 0.0, 1.0, 0.0, key='slider23')
        aerialswon = st.slider('Aerials Won per 90', 0.0, 1.0, 0.0, key='slider24')
        defduels = st.slider('Defensive Duels Success %', 0.0, 1.0, 0.0, key='slider25')
        defend = st.slider('Successful Defensive Actions per 90', 0.0, 1.0, 0.0, key='slider26')
        tklint = st.slider('Tackles & Interceptions per 90', 0.0, 1.0, 0.0, key='slider27')
        tkl = st.slider('Sliding Tackles per 90', 0.0, 1.0, 0.0, key='slider28')
        intercept = st.slider('Interceptions per 90', 0.0, 1.0, 0.0, key='slider29')
        shotblock = st.slider('Shots Blocked per 90', 0.0, 1.0, 0.0, key='slider30')
        foul = st.slider('Fouls Committed per 90', 0.0, 1.0, 0.0, key='slider31')
        fouldraw = st.slider('Fouls Drawn per 90', 0.0, 1.0, 0.0, key='slider32')
        cards = st.slider('Cards per 90', 0.0, 1.0, 0.0, key='slider33')
            

with filter_table_tab:
    final = create_player_research_table(df_basic, mins, full_league_name, pos_select, ages[0], ages[1])
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
        cscale = st.selectbox('Point Colorscale', colorscales, index=colorscales.index("rdylgn_r"))

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
        title = '%s %s, %s & %s <br><sup>%s%s min. %i minutes played | %s</sup><br><sup>Created by @BeGriffis, made on best-11-scouting.streamlit.app</sup>' %(season,lg,xx,yy,age_text_scatter,pos_select_scatter,mins,update_date),
        width=900,
        height=700)
    fig_scatter.update_traces(textposition='top right', marker=dict(size=10, line=dict(width=1, color='black')))
    
    fig_scatter.add_hline(y=dfProspect_scatter[yy].median(), name='Median', line_width=0.5)
    fig_scatter.add_vline(x=dfProspect_scatter[xx].median(), name='Median', line_width=0.5)
    
    st.plotly_chart(fig_scatter, theme=None, use_container_width=False)

with st.expander('Metric Glossary'):
    st.write('''
    For a more comprehensive list of definitions, please see: https://dataglossary.wyscout.com/  \n
    Short & Medium Pass = Passes shorter than 40 meters.  \n
    Long Pass = Passes longer than 40 meters.  \n
    Smart Pass = A creative and penetrative pass that attempts to break the opposition's defensive lines to gain a significant advantage in attack.  \n
    Cross = Pass from the offensive flanks aimed towards a teammate in the area in front of the opponent’s goal.  \n
    Shot Assist = A pass where the receiver's next action is a shot.  \n
    Expected Assists (xA) = The expected goal (xG) value of shots assisted by a pass. xA only exists on passes that are Shot Assists.  \n
    xA per Shot Assist = The average xA of a player's shot assists.  \n
    Second Assist = The last action of a player from the goalscoring team, prior to an Assist by a teammate.  \n
    Third Assist = The penultimate action of a player from the goalscoring team, prior to an Assist by a teammate.  \n
    Expected Goals (xG) = The likelihood a shot becomes a goal, based on many factors (player position, body part of shot, location of assist, etc.).  \n
    Non-Penalty xG (npxG) = xG from non-penalty shots only.  \n
    npxG per Shot = The average npxG of a player's (non-penalty) shots.  \n
    Acceleration = A run with the ball with a significant speed up.  \n
    Progressive Carry = A continuous ball control by one player attempting to draw the team significantly closer to the opponent goal. (see Wyscout's glossary for more info)  \n
    Progressive Pass = A forward pass that attempts to advance a team significantly closer to the opponent’s goal.  \n
    Defensive Duel = When a player attempts to dispossess an opposition player to stop an attack progressing.  \n
    ''')


