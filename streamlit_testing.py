import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from statistics import mean, harmonic_mean
from math import pi
sns.set_style("white")
import matplotlib
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
import urllib.request
from highlight_text import fig_text
import streamlit as st
import warnings
warnings.filterwarnings('ignore')
import plotly.express as px
import plotly.figure_factory as ff
from plotly.graph_objects import Layout
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import zscore
import seaborn as sns
from matplotlib.colors import Normalize, to_rgba
import altair as alt

plt.clf()
plt.style.use('default')  # Reset Matplotlib
sns.reset_defaults()  # Reset Seaborn


colorscales = px.colors.named_colorscales()
colorscales2 = [f"{cc}_r" for cc in colorscales]
colorscales += colorscales2

def make_season_metric_img(player_df, adj_80s, player, foc_var, league, season):
    
    # Adjust for 85% TOG if needed
    if adj_80s == 'Yes':
        player_df[foc_var] = (player_df[foc_var] / player_df['TOG%']) * 85
        adj_text = "Data Adjusted to 85% TOG% | 85% Time On Ground Percentage is average for starters per game | Darker bar color indicates more time on ground"
    else:
        adj_text = "Darker bar color indicates more time on ground"

    # Create a color scale based on 'TOG%'
    color_scale = alt.Scale(domain=[0, 100], range=['white', '#4c94f6'])

    # Create the bar chart
    chart = alt.Chart(player_df).mark_bar(stroke='black', strokeWidth=0.75).encode(
        x=alt.X('Opponent:N', title=None, sort=None),
        y=alt.Y(f'{foc_var}:Q', title=foc_var),
        color=alt.Color('TOG%:Q', scale=color_scale, legend=alt.Legend(title="TOG%")),
        tooltip=[alt.Tooltip('Opponent:N', title="Opponent"),
                 alt.Tooltip(foc_var, title=foc_var, format=".1f"),
                 alt.Tooltip('TOG%:Q', title="TOG%", format=".1f")]
    ).properties(
        width=1000,
        height=800
    )

    # Add text labels on bars
    text = chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-5,
        size=10,
        color='black'
    ).encode(
        text=alt.Text(foc_var, format=".1f")
    )

    # Combine bar chart and labels
    final_chart = (chart + text).properties(
        title=alt.Title(
            text=f"{player} {foc_var} By Round, {season} {league}", fontSize=18,
            subtitle=adj_text, subtitleFontSize=10, align='left', anchor='start')
    )

    return final_chart

def NormalizeData(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data)) * 100

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
def _update_slider(value):
    for i in range(1, 45):
        st.session_state[f"slider{i}"] = value

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
        
        ax.hlines(mean_percentile/100, angle - 0.055, angle + 0.055, colors='black', linestyles='dotted', linewidth=2, alpha=0.8, zorder=2)
        ax.hlines(std_dev_up_percentile/100, angle - 0.055, angle + 0.055, colors=text_col, linestyles='dotted', linewidth=2, alpha=0.8, zorder=2)
        ax.hlines(std_dev_down_percentile/100, angle - 0.055, angle + 0.055, colors=text_col, linestyles='dotted', linewidth=2, alpha=0.8, zorder=2)

def create_filter_table_df(mins, filter_pos):
    df = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/AFL-Radars/refs/heads/main/Player-Data/{league}/{season}.csv")
    df = df.dropna(subset=['player_position'])
    df.reset_index(drop=True,inplace=True)
    df['Possessions'] = df['contested_possessions']+df['uncontested_possessions']
    if league == 'AFL':
        df['Kick Efficiency'] = df['effective_kicks']/df['kicks']*100
        df['Handball Efficiency'] = (df['effective_disposals']-df['effective_kicks'])/df['handballs']*100
        df['Hitout Efficiency'] = df['hitouts_to_advantage']/df['hitouts']*100
    df['% of Possessions Contested'] = df['contested_possessions']/(df['Possessions'])*100
    df['% of Marks Contested'] = df['contested_marks']/(df['marks'])*100
    df['Points'] = (df['goals']*6)+(df['behinds'])
    df['Points per Shot'] = df['Points']/df['shots_at_goal']
    df['Points per Shot'] = [0 if df['shots_at_goal'][i]==0 else df['Points'][i]/df['shots_at_goal'][i] for i in range(len(df))]

    if filter_pos != None:
        pattern = r'(^|, )(' + '|'.join(filter_pos) + r')($|, )'
        df = df[df['player_position'].str.contains(pattern, regex=True)]

    numcols = ['kicks', 'marks', 'handballs',
       'disposals', 'effective_disposals', 'goals', 'behinds', 'hitouts',
       'tackles', 'rebounds', 'inside_fifties', 'clearances', 'clangers',
       'free_kicks_for', 'free_kicks_against',
               # 'brownlow_votes',
       'contested_possessions', 'uncontested_possessions', 'contested_marks',
       'marks_inside_fifty', 'one_percenters', 'bounces', 'goal_assists',
        'afl_fantasy_score',
               # 'supercoach_score',
               'centre_clearances',
       'stoppage_clearances', 'score_involvements', 'metres_gained',
       'turnovers', 'intercepts', 'tackles_inside_fifty', 'contest_def_losses',
       'contest_def_one_on_ones', 'contest_off_one_on_ones',
       'contest_off_wins', 'def_half_pressure_acts', 'effective_kicks',
       'f50_ground_ball_gets', 'ground_ball_gets', 'hitouts_to_advantage',
        'intercept_marks', 'marks_on_lead',
       'pressure_acts', 'rating_points', 'ruck_contests', 'score_launches',
       'shots_at_goal', 'spoils', '80sr',
              'Possessions','Kick Efficiency', 'Handball Efficiency','% of Possessions Contested',
              '% of Marks Contested','Hitout Efficiency','Points per Shot','Points']
    revcols = ['clangers', 'turnovers', 'free_kicks_against']
    if league == 'AFLW':
        trouble_cols = [
            'contest_def_one_on_ones', 'def_half_pressure_acts', 'intercept_marks', 'hitout_win_percentage', 'contest_off_wins', 'pressure_acts', 'score_launches', 'effective_kicks', 'contest_off_one_on_ones', 'marks_on_lead', 'spoils', 'ground_ball_gets', 'hitouts_to_advantage', 'ruck_contests', 'contest_def_losses', 'f50_ground_ball_gets', 'effective_disposals',
            'Kick Efficiency','Handball Efficiency','Hitout Efficiency']
        numcols = [x for x in numcols if x not in trouble_cols]

    dfProspect = df[df['PctOfSeason']>=mins/100]
    dfProspect['PctOfSeason'] = round(dfProspect['PctOfSeason']*100,2)
    dfProspect['80s'] = round(dfProspect['80s'],2)
    
    for i in range(len(numcols)):
        dfProspect[numcols[i]] = stats.rankdata(dfProspect[numcols[i]], "average")/len(dfProspect[numcols[i]])
        dfProspect[numcols[i]] = round(dfProspect[numcols[i]],2)
    for i in range(len(revcols)):
        dfProspect[revcols[i]] = 1-stats.rankdata(dfProspect[revcols[i]], "average")/len(dfProspect[revcols[i]])
        dfProspect[revcols[i]] = round(dfProspect[revcols[i]],2)
        
    dfProspect.fillna(0,inplace=True)

    return dfProspect.reset_index(drop=True)

def scout_report(league, season, pos, mins, name,callout, bar_colors, dist_labels, sig, extra_text):
    plt.clf()
    plt.style.use('default')  # Reset Matplotlib
    sns.reset_defaults()  # Reset Seaborn
    if league == 'AFLW':
        logo_df = pd.DataFrame({'team':['Adelaide Crows','Brisbane Lions','Carlton','Collingwood','Essendon','Fremantle','Geelong Cats','Gold Coast SUNS','GWS GIANTS','Hawthorn','Melbourne','Kangaroos','Port Adelaide','Richmond','St Kilda','Sydney Swans','West Coast Eagles','Western Bulldogs'],
                       'logo_url':['https://upload.wikimedia.org/wikipedia/en/thumb/0/07/Adelaide_Crows_Logo_2024.svg/1024px-Adelaide_Crows_Logo_2024.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/c/c7/Brisbane_Lions_logo_2010.svg/1024px-Brisbane_Lions_logo_2010.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/5/58/Carlton_FC_Logo_2020.svg/1024px-Carlton_FC_Logo_2020.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/a/a6/Collingwood_Football_Club_Logo_%282017%E2%80%93present%29.svg/1024px-Collingwood_Football_Club_Logo_%282017%E2%80%93present%29.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/8/8b/Essendon_FC_logo.svg/1920px-Essendon_FC_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/c/ca/Fremantle_FC_logo.svg/1280px-Fremantle_FC_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/5/5f/Geelong_Cats_logo.svg/1024px-Geelong_Cats_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/7/73/Gold_Coast_Suns_logo_%28introduced_late_2024%29.svg/1280px-Gold_Coast_Suns_logo_%28introduced_late_2024%29.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/0/07/GWS_Giants_logo.svg/1280px-GWS_Giants_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/6/62/Hawthorn-football-club-brand.svg/1280px-Hawthorn-football-club-brand.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/4/4e/Melbournefc.svg/1024px-Melbournefc.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/f/fc/North_Melbourne_FC_logo.svg/1024px-North_Melbourne_FC_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/3/36/Port_Adelaide_Football_Club_logo.svg/800px-Port_Adelaide_Football_Club_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/3/35/Richmond_Tigers_logo.svg/800px-Richmond_Tigers_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/0/06/St_Kilda_Football_Club_logo_2024.svg/1024px-St_Kilda_Football_Club_logo_2024.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/a/af/Sydney_Swans_Logo_2020.svg/1024px-Sydney_Swans_Logo_2020.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/b/b5/West_Coast_Eagles_logo_2017.svg/1280px-West_Coast_Eagles_logo_2017.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/0/09/Western_Bulldogs_logo.svg/1024px-Western_Bulldogs_logo.svg.png']})
        game_length = 17*4
        trouble_cols = [
            'contest_def_one_on_ones', 'def_half_pressure_acts', 'intercept_marks', 'hitout_win_percentage', 'contest_off_wins', 'pressure_acts', 'score_launches', 'effective_kicks', 'contest_off_one_on_ones', 'marks_on_lead', 'spoils', 'ground_ball_gets', 'hitouts_to_advantage', 'ruck_contests', 'contest_def_losses', 'f50_ground_ball_gets', 'effective_disposals',
        'kick_efficiency','handball_efficiency','hitout_efficiency']
    if league == 'AFL':
        logo_df = pd.DataFrame({'team':['Adelaide Crows','Brisbane Lions','Carlton','Collingwood','Essendon','Fremantle','Geelong Cats','Gold Coast SUNS','GWS GIANTS','Hawthorn','Melbourne','North Melbourne','Port Adelaide','Richmond','St Kilda','Sydney Swans','West Coast Eagles','Western Bulldogs'],
                       'logo_url':['https://upload.wikimedia.org/wikipedia/en/thumb/0/07/Adelaide_Crows_Logo_2024.svg/1024px-Adelaide_Crows_Logo_2024.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/c/c7/Brisbane_Lions_logo_2010.svg/1024px-Brisbane_Lions_logo_2010.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/5/58/Carlton_FC_Logo_2020.svg/1024px-Carlton_FC_Logo_2020.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/a/a6/Collingwood_Football_Club_Logo_%282017%E2%80%93present%29.svg/1024px-Collingwood_Football_Club_Logo_%282017%E2%80%93present%29.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/8/8b/Essendon_FC_logo.svg/1920px-Essendon_FC_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/c/ca/Fremantle_FC_logo.svg/1280px-Fremantle_FC_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/5/5f/Geelong_Cats_logo.svg/1024px-Geelong_Cats_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/7/73/Gold_Coast_Suns_logo_%28introduced_late_2024%29.svg/1280px-Gold_Coast_Suns_logo_%28introduced_late_2024%29.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/0/07/GWS_Giants_logo.svg/1280px-GWS_Giants_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/6/62/Hawthorn-football-club-brand.svg/1280px-Hawthorn-football-club-brand.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/4/4e/Melbournefc.svg/1024px-Melbournefc.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/f/fc/North_Melbourne_FC_logo.svg/1024px-North_Melbourne_FC_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/3/36/Port_Adelaide_Football_Club_logo.svg/800px-Port_Adelaide_Football_Club_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/3/35/Richmond_Tigers_logo.svg/800px-Richmond_Tigers_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/0/06/St_Kilda_Football_Club_logo_2024.svg/1024px-St_Kilda_Football_Club_logo_2024.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/a/af/Sydney_Swans_Logo_2020.svg/1024px-Sydney_Swans_Logo_2020.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/b/b5/West_Coast_Eagles_logo_2017.svg/1280px-West_Coast_Eagles_logo_2017.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/0/09/Western_Bulldogs_logo.svg/1024px-Western_Bulldogs_logo.svg.png']})
        game_length = 20*4
        
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

    
    #####################################################################################
    # Filter data
    dfProspect = df[df['PctOfSeason']>=mins/100]
    fallback_raw_valsdf = dfProspect[(dfProspect['player_name']==name)]
    team = fallback_raw_valsdf.player_team.values[0]

    if pos == None:
        compares = 'All Players'
    else:
        pattern = r'(^|, )(' + '|'.join(pos) + r')($|, )'
        dfProspect = dfProspect[dfProspect['player_position'].str.contains(pattern, regex=True)]
        if len(pos) > 2:
            compares = f"{', '.join(pos[:-1])}, and {pos[-1]}"
        elif len(pos) == 2:
            compares = f"{pos[0]} and {pos[1]}"
        elif len(pos) == 1:
            compares = f"{pos[0]}"
        else:
            compares = f"{pos}s"
            
    raw_valsdf = dfProspect[(dfProspect['player_name']==name)]
    if len(raw_valsdf)==0:
        dfProspect = pd.concat([dfProspect,fallback_raw_valsdf],ignore_index=True)
        raw_valsdf = dfProspect[(dfProspect['player_name']==name)]
    raw_valsdf_full = dfProspect.copy()

    numcols = ['kicks', 'marks', 'handballs',
       'disposals', 'effective_disposals', 'goals', 'behinds', 'hitouts',
       'tackles', 'rebounds', 'inside_fifties', 'clearances', 'clangers',
       'free_kicks_for', 'free_kicks_against',
               # 'brownlow_votes',
       'contested_possessions', 'uncontested_possessions', 'contested_marks',
       'marks_inside_fifty', 'one_percenters', 'bounces', 'goal_assists',
        'afl_fantasy_score',
               # 'supercoach_score',
               'centre_clearances',
       'stoppage_clearances', 'score_involvements', 'metres_gained',
       'turnovers', 'intercepts', 'tackles_inside_fifty', 'contest_def_losses',
       'contest_def_one_on_ones', 'contest_off_one_on_ones',
       'contest_off_wins', 'def_half_pressure_acts', 'effective_kicks',
       'f50_ground_ball_gets', 'ground_ball_gets', 'hitouts_to_advantage',
        'intercept_marks', 'marks_on_lead',
       'pressure_acts', 'rating_points', 'ruck_contests', 'score_launches',
       'shots_at_goal', 'spoils', '80sr',
              'possessions','kick_efficiency', 'handball_efficiency','pct_contested_poss',
              'pct_marks_contested','hitout_efficiency','points_per_shot',]
    revcols = ['clangers', 'turnovers', 'free_kicks_against']
    if league == 'AFLW':
        numcols = [x for x in numcols if x not in trouble_cols]
    
    for i in range(len(numcols)):
        dfProspect['%s_pct' %numcols[i]] = stats.rankdata(dfProspect[numcols[i]], "average")/len(dfProspect[numcols[i]])
    
    for i in range(len(revcols)):
        dfProspect['%s_pct' %revcols[i]] = 1-stats.rankdata(dfProspect[revcols[i]], "average")/len(dfProspect[revcols[i]])
        
    dfProspect.fillna(0,inplace=True)
    df_pros = dfProspect
#     ######################################################################
    
    dfRadarMF = dfProspect[(dfProspect['player_name']==name)].reset_index(drop=True)
    pos_callout = dfRadarMF.player_position.values[0]
    pct_played = dfRadarMF.PctOfSeason.values[0]
    gms_played = dfRadarMF['80s'].values[0]
    pic = dfRadarMF.picture.values[0]
    pic = pic.replace(" ","%20")
    team_pic = logo_df[logo_df['team']==team].logo_url.values[0]

    if league == 'AFL':
        dfRadarMF = dfRadarMF[["player_name",
                               'goals_pct','behinds_pct','shots_at_goal_pct','points_per_shot_pct','goal_assists_pct','score_involvements_pct',
                               'kicks_pct','handballs_pct','kick_efficiency_pct','handball_efficiency_pct','rebounds_pct','inside_fifties_pct','possessions_pct','pct_contested_poss_pct','metres_gained_pct',
                               'marks_pct','pct_marks_contested_pct','marks_inside_fifty_pct','intercept_marks_pct','marks_on_lead_pct','free_kicks_for_pct',
                               'spoils_pct','tackles_pct','tackles_inside_fifty_pct','ground_ball_gets_pct','intercepts_pct','clearances_pct','pressure_acts_pct','score_launches_pct','one_percenters_pct',
                               'clangers_pct','turnovers_pct','free_kicks_against_pct',
                               ]]
        raw_vals = raw_valsdf[["player_name",
                               'goals','behinds','shots_at_goal','points_per_shot','goal_assists','score_involvements',
                               'kicks','handballs','kick_efficiency','handball_efficiency','rebounds','inside_fifties','possessions','pct_contested_poss','metres_gained',
                               'marks','pct_marks_contested','marks_inside_fifty','intercept_marks','marks_on_lead','free_kicks_for',
                               'spoils','tackles','tackles_inside_fifty','ground_ball_gets','intercepts','clearances','pressure_acts','score_launches','one_percenters',
                               'clangers','turnovers','free_kicks_against',
                               ]]
        raw_vals_full = raw_valsdf_full[["player_name",
                               'goals','behinds','shots_at_goal','points_per_shot','goal_assists','score_involvements',
                               'kicks','handballs','kick_efficiency','handball_efficiency','rebounds','inside_fifties','possessions','pct_contested_poss','metres_gained',
                               'marks','pct_marks_contested','marks_inside_fifty','intercept_marks','marks_on_lead','free_kicks_for',
                               'spoils','tackles','tackles_inside_fifty','ground_ball_gets','intercepts','clearances','pressure_acts','score_launches','one_percenters',
                               'clangers','turnovers','free_kicks_against',
                               ]]
    if league != 'AFL':
        dfRadarMF = dfRadarMF[["player_name",
                               'goals_pct','behinds_pct','shots_at_goal_pct','points_per_shot_pct','goal_assists_pct','score_involvements_pct',
                               'kicks_pct','handballs_pct','rebounds_pct','inside_fifties_pct','possessions_pct','pct_contested_poss_pct','metres_gained_pct',
                               'marks_pct','pct_marks_contested_pct','marks_inside_fifty_pct','free_kicks_for_pct',
                               'tackles_pct','tackles_inside_fifty_pct','intercepts_pct','clearances_pct','one_percenters_pct',
                               'clangers_pct','turnovers_pct','free_kicks_against_pct',
                               ]]
        raw_vals = raw_valsdf[["player_name",
                               'goals','behinds','shots_at_goal','points_per_shot','goal_assists','score_involvements',
                               'kicks','handballs','rebounds','inside_fifties','possessions','pct_contested_poss','metres_gained',
                               'marks','pct_marks_contested','marks_inside_fifty','free_kicks_for',
                               'tackles','tackles_inside_fifty','intercepts','clearances','one_percenters',
                               'clangers','turnovers','free_kicks_against',
                               ]]
        raw_vals_full = raw_valsdf_full[["player_name",
                               'goals','behinds','shots_at_goal','points_per_shot','goal_assists','score_involvements',
                               'kicks','handballs','rebounds','inside_fifties','possessions','pct_contested_poss','metres_gained',
                               'marks','pct_marks_contested','marks_inside_fifty','free_kicks_for',
                               'tackles','tackles_inside_fifty','intercepts','clearances','one_percenters',
                               'clangers','turnovers','free_kicks_against',
                               ]]
    dfRadarMF.rename(columns={'goals_pct':'Goals',
                            'behinds_pct':'Behinds',
                              'shots_at_goal_pct':'Shots',
                              'points_per_shot_pct':'Points/\nShot',
                            'goal_assists_pct':'Goal\nAssists',
                            'score_involvements_pct':'Score\nInvolves',
                            'kicks_pct':'Kicks',
                            'handballs_pct':'Handballs',
                            'kick_efficiency_pct':'Kick\nEff %',
                            'handball_efficiency_pct':'Handball\nEff %',
                            'rebounds_pct':'Rebound\n50s',
                            'inside_fifties_pct':'Inside\n50s',
                            'possessions_pct':'Poss.',
                            'pct_contested_poss_pct':'% Poss.\nContested',
                            'metres_gained_pct':'Meters\nGained',
                            'marks_pct':'Marks',
                            'pct_marks_contested_pct':'% of Mks\nContested',
                            'marks_inside_fifty_pct':'Marks\nIn 50',
                            'intercept_marks_pct':'Intercept\nMarks',
                            'marks_on_lead_pct':'Lead\nMarks',
                            'free_kicks_for_pct':'Frees\nFor',
                              'spoils_pct':'Spoils',
                            'tackles_pct':'Tackles',
                            'tackles_inside_fifty_pct':'Tackles\nIn 50',
                            'ground_ball_gets_pct':'Ground\nBall Gets',
                            'intercepts_pct':'Inter-\n-cepts',
                            'clearances_pct':'Clears',
                            'pressure_acts_pct':'Pressure\nActs',
                            'score_launches_pct':'Score\nLaunches',
                            'one_percenters_pct':'1%er',
                            'clangers_pct':'Clangers',
                            'turnovers_pct':'Turn-\novers',
                            'free_kicks_against_pct':'Frees\nAgainst',
                             }, inplace=True)

    print('Number of players comparing to:',len(dfProspect))
    
#     ###########################################################################

    df1 = dfRadarMF.T.reset_index()

    df1.columns = df1.iloc[0] 

    df1 = df1[1:]
    df1 = df1.reset_index()
    df1 = df1.rename(columns={'player_name': 'Metric',
                        name: 'Value',
                             'index': 'Group'})
    if league == 'AFL':
        for i in range(len(df1)):
            if df1['Group'][i] <= 6:
                df1['Group'][i] = 'Scoring'
            elif df1['Group'][i] <= 15:
                df1['Group'][i] = 'Possession'
            elif df1['Group'][i] <= 21:
                df1['Group'][i] = 'Marks'
            elif df1['Group'][i] <= 30:
                df1['Group'][i] = 'Defense'
            elif df1['Group'][i] <= 33:
                df1['Group'][i] = 'Bad'
    if league != 'AFL':
        for i in range(len(df1)):
            if df1['Group'][i] <= 6:
                df1['Group'][i] = 'Scoring'
            elif df1['Group'][i] <= 13:
                df1['Group'][i] = 'Possession'
            elif df1['Group'][i] <= 17:
                df1['Group'][i] = 'Marks'
            elif df1['Group'][i] <= 22:
                df1['Group'][i] = 'Defense'
            elif df1['Group'][i] <= 25:
                df1['Group'][i] = 'Bad'

    #####################################################################
    
    ### This link below is where I base a lot of my radar code off of
    ### https://www.python-graph-gallery.com/circular-barplot-with-groups


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

    if league == 'AFL':
        GROUPS_SIZE = [6,9,6,9,3]  # Attacker template
    if league != 'AFL':
        GROUPS_SIZE = [6,7,4,5,3]  # Attacker template
        
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
    for group, size in zip(GROUPS_SIZE, GROUPS_SIZE): #replace first GROUPS SIZE with ['Passing', 'Creativity'] etc if needed
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

    
    if callout == 'Per Game':
        callout_text = " | Values shown are per game"
        callout_title = ' & Per Game Values'
    elif callout == 'Percentile':
        callout_text = ' | Values shown are percentiles'
        callout_title = ''

    for i, bar in enumerate(ax.patches):
        if bar_colors == 'Metric Groups':
            if callout == 'Per Game':
                value_format = f'{round(raw_vals.iloc[0][i+1], 2)}'
            else:
                value_format = format(bar.get_height() * 100, '.0f')
            color = 'black'
            face = 'white'
        elif bar_colors == 'Benchmarking Percentiles':
            if callout == 'Per Game':
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



    if dist_labels == 'Yes':
        add_labels_dist(ANGLES[IDXS], VALUES, LABELS, OFFSET, ax, text_cs, raw_vals_full)
    if dist_labels == 'No':
        add_labels(ANGLES[IDXS], VALUES, LABELS, OFFSET, ax, text_cs)


    PAD = 0.02
    ax.text(0.125, 0 + PAD, "0", size=10, color='#4A2E19')
    ax.text(0.125, 0.2 + PAD, "20", size=10, color='#4A2E19')
    ax.text(0.125, 0.4 + PAD, "40", size=10, color='#4A2E19')
    ax.text(0.125, 0.6 + PAD, "60", size=10, color='#4A2E19')
    ax.text(0.125, 0.8 + PAD, "80", size=10, color='#4A2E19')
    ax.text(0.125, 1 + PAD, "100", size=10, color='#4A2E19')
    

    if dist_labels == 'Yes':
        dist_text = "Black dot line = metric mean\nColored dot line = +/- 0.5 std. deviations\n"
    if dist_labels == 'No':
        dist_text = ""

    plt.suptitle('%s (%s, %.1f%s TOG)\n%s %s Percentile Rankings%s'
                 %(name, pos_callout, pct_played*100, '%', season,league,callout_title),
                 fontsize=15.5,
                 fontfamily="DejaVu Sans",
                color="#4A2E19", #4A2E19
                 fontweight="bold", fontname="DejaVu Sans",
                x=0.5,
                y=.97)

    plt.annotate(f"'Per Game' means per {game_length} minutes\nBars are percentiles%s\nAll values are per game%s\nCompared to %s\nOnly includes players with at least %.0f%s time on ground\nData: AFL | %s\nSample Size: %i players" %(callout_text,extra_text, compares, mins, '%', sig, len(dfProspect)),
                 xy = (-.05, -.05), xycoords='axes fraction',
                ha='left', va='center',
                fontsize=9, fontfamily="DejaVu Sans",
                color="#4A2E19", fontweight="regular", fontname="DejaVu Sans",
                ) 
    plt.annotate(f"{dist_text}Clangers, Turnovers, & Frees Against\nare all reverse-coded so that a higher percentile\nis acheived by having a lower value.",
                 xy = (1.05, -.05), xycoords='axes fraction',
                ha='right', va='center',
                fontsize=9, fontfamily="DejaVu Sans",
                color="#4A2E19", fontweight="regular", fontname="DejaVu Sans",
                )


    ######## Club Image ########
    from PIL import Image
    urllib.request.urlretrieve(pic,"player_pic.png")
    image = Image.open('player_pic.png')
    newax = fig.add_axes([.42,.43,0.18,0.18], anchor='C', zorder=1)
    newax.imshow(image)
    newax.axis('off')
    
    urllib.request.urlretrieve(team_pic,"team_pic.png")
    image = Image.open('team_pic.png')
    newax = fig.add_axes([.15,.82,0.1,0.1], anchor='C', zorder=1)
    newax.imshow(image)
    newax.axis('off')

    ######## League Logo Image ########
    if league == 'AFL':
        urllib.request.urlretrieve("https://upload.wikimedia.org/wikipedia/en/thumb/e/e4/Australian_Football_League.svg/1920px-Australian_Football_League.svg.png","afl_logo.png")
    if league == 'AFLW':
        urllib.request.urlretrieve("https://upload.wikimedia.org/wikipedia/en/thumb/b/b1/AFL_Women%27s_logo.svg/1280px-AFL_Women%27s_logo.svg.png","afl_logo.png")
    if league == 'VFL':
        urllib.request.urlretrieve("https://upload.wikimedia.org/wikipedia/en/thumb/3/34/VFL_Football_Logo.svg/1024px-VFL_Football_Logo.svg.png","afl_logo.png")
    l_image = Image.open('afl_logo.png')
    newax = fig.add_axes([.76,.82,0.1,0.1], anchor='C', zorder=1)
    newax.imshow(l_image)
    newax.axis('off')

    ax.set_facecolor('#fbf9f4')
    fig = plt.gcf()
    fig.patch.set_facecolor('#fbf9f4')
#     ax.set_facecolor('#fbf9f4')
    fig.set_size_inches(12, (12*.9)) #length, height
#     fig.set_size_inches(9.416,10.304)
    
    fig_text(
    0.13, 0.165, "<Elite>\n<Above Average>\n<Average>\n<Below Average>", color="#4A2E19",
    highlight_textprops=[{"color": '#01349b'},
                         {'color' : '#007f35'},
                         {"color" : '#9b6700'},
                         {'color' : '#b60918'},
#                          {'color' : 'cornflowerblue'}
                        ],
    size=12, fig=fig, ha='left',va='center'
    )


    fig_show = plt.gcf()
    plt.style.use('default')  # Reset Matplotlib
    sns.reset_defaults()  # Reset Seaborn
    return fig_show

########################################################################
########################################################################
########################################################################
########################################################################
########################################################################
########################################################################

st.title("Footy Radars :rugby_football:")
st.caption("All data via AFL")

with st.expander('Instructions'): 
    st.write("""
    _Welcome to Footy Radars! This app allows you to generate statistical performance images for AFL players, benchmarked against the rest of the competition_  \n  \n
    **Sidebar:**  \n
    1) Choose the league (AFL only for now, but I'm working on adding AFLW & VFL)  \n
    2) Select your desired season  \n
    3) Set the minimum time on ground % for players to have played to be included  \n  \n
    **Player Radar Tab:**  \n
    1) Choose the positions to benchmark against (leave blank for all players, or choose 1 or more positions to _only_ include those position - no matter what position(s) you choose, the player you select will be included)  \n
    2) Decide if you want the data labels to be per game (per 80 minutes) numbers for each metric, or the player's percentile rank  \n
    3) Choose whether you want the distribution lines (mean & standard deviation) for each metric to be added to each bar. Note: this can be helpful, but be aware that not all metrics will have a normal distribution  \n
    4) Click the radar generation button to create your player's visual. You can right-click & save the image to use it for personal use (just make sure not to edit the picture to remove my signature, and please link people to this app!)  \n  \n
    **All Players List Tab**  \n
    This tab simply has the list of every player from the league & season you've selected. You can use this to find the specific player's name you want to generate a radar for, and also double check their time on ground %  \n
    **Scatter Plots Tab**  \n
    1) First choose the positions you want to plot. Leave blank to plot all positions  \n
    2) Choose your desired X, Y, and Color variables  \n
    3) Select the colorscale to use (I've loaded all sequential & diverging (and reversed ending in _r) colorscales from this page: https://matplotlib.org/stable/gallery/color/colormap_reference.html)  \n
    4) Submit your scatter plot options and the chart will generate. Hover over points to see the player, team, & position. You can also save the plot by hovering over it and clicking the Camera button that appears. The plot is also interactive & zoomable  \n
    **Player Search Tabs**  \n
    The 'Search' allows you to set minimum percentile filters for players to meet in order to show up in the 'Results' tab. The percentiles are all based off of the position(s) you select, and of course, leave the position fiilter blank to include all players  \n
    **Weighted Metric Ranking Tab**  \n
    1) Choose the position(s) you want to include, leaving this blank if you want to include all players  \n
    2) Select any number of metrics you want to use for ranking players  \n
    3) Submit these options, and sliders will appear below for you to set your weightings  \n
    4) Set weights for your metrics. These are used to create weighted, normalized z-scores using all of the included metrics. In the table, the metrics will be 0 to 100, with the player recording the lowest value receiving 0, and the highest value 100. These normalized z-scores are thus easy to interpret across metrics while retaining the distribution of the raw scores  \n
    5) Submit these weightings and a table will appear showing the final, normalized weighted z-score ranking of players for your specified model. The 'Score' column will always be between 0 and 100: the player with 100 is the player with the largest weighted score, and the player with 0 is the one with the lowest. Again, the use of z-scores allows us to retain the distribution of weighted scores  \n
    6) We can interpret a player scoring 100 as the best player (in the given position(s) if applicable) that year in your specified model. And a player with a score of 73 could theoretically be 73% as good as that best player 
""")

avail_data = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/AFL-Radars/refs/heads/main/AvailableData.csv")

with st.sidebar:
    league = st.selectbox('League', avail_data.Competition.unique().tolist())
    season = st.selectbox('Season', sorted(avail_data[avail_data.Competition==league].Season.tolist(),reverse=True))
    mins = st.number_input('Minimum Time On Ground %', 0, 100, 60, 1)

extra_text = avail_data[(avail_data.Competition==league) & (avail_data.Season==season)].DataTime.values[0]

radar_tab, all_players_tab, scatter_tab, filter_tab, filter_table_tab, ranking_tab, metric_trend_tab = st.tabs(['Player Radar', 'All Players List', 'Scatter Plots', 'Player Search, Filters', 'Player Search, Results', 'Weighted Metric Ranking', 'Game-By-Game Metrics'])

with radar_tab:
    with st.form('Radar Options'):
        pos = st.multiselect('Positions to Include (leave blank for all)', ['Full-Forward','Forward Pocket','Centre Half-Forward','Half-Forward','Wing','Centre','Ruck-Rover','Rover','Ruck','Half-Back','Centre Half-Back','Back-Pocket','Full-Back'])
        if pos == []:
            pos = None
        callout = st.selectbox('Data Labels: Per Game or Percentiles?', ['Per Game','Percentile'])
        dist_labels = st.selectbox('Distribution Labels on Bars?', ['Yes','No'])
        name = st.text_input("Player", "")
        submitted = st.form_submit_button("Generate Radar!")
        
        try:
            radar_img = scout_report(league = league,
                         season = season,
                         pos = pos, #### make multiselect('Full-Forward','Forward Pocket','Centre Half-Forward','Half-Forward','Wing','Centre','Ruck-Rover','Rover','Ruck','Half-Back','Centre Half-Back','Back-Pocket','Full-Back',)
                         mins = mins,     # time on ground (50% = 50% of season)
                         name = name,
                         sig = 'Created by Ben Griffis (@BeGriffis)',
                         callout = callout, # Percentile | Per Game
                         bar_colors = 'Benchmarking Percentiles',  ## Benchmarking Percentiles | Metric Groups
                         dist_labels = dist_labels,
                         extra_text = f' | {extra_text}',
                        )
            st.pyplot(radar_img.figure)
        except:
            st.text("Please enter a valid player name. Refer to the All Players List tab if needed.  \nEnsure your player meets the minimum TOG% threshold.")

with all_players_tab:
    df = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/AFL-Radars/refs/heads/main/Player-Data/{league}/{season}.csv")
    df = df[['player_name','player_team','player_position','games_played','PctOfSeason','afl_fantasy_score']].rename(columns={'player_name':'Player','player_team':'Team','player_position':'Position(s)','games_played':'Games','PctOfSeason':'TOG%','afl_fantasy_score':'AFL Fantasy Score per game'})
    df

with scatter_tab:
    df = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/AFL-Radars/refs/heads/main/Player-Data/{league}/{season}.csv")
    df['Possessions'] = df['contested_possessions']+df['uncontested_possessions']
    if league == 'AFL':
        df['Kick Efficiency'] = df['effective_kicks']/df['kicks']*100
        df['Handball Efficiency'] = (df['effective_disposals']-df['effective_kicks'])/df['handballs']*100
        df['Hitout Efficiency'] = df['hitouts_to_advantage']/df['hitouts']*100
    df['% of Possessions Contested'] = df['contested_possessions']/(df['Possessions'])*100
    df['% of Marks Contested'] = df['contested_marks']/(df['marks'])*100
    df['Points'] = (df['goals']*6)+(df['behinds'])
    df['Points per Shot'] = df['Points']/df['shots_at_goal']
    df['Points per Shot'] = [0 if df['shots_at_goal'][i]==0 else df['Points'][i]/df['shots_at_goal'][i] for i in range(len(df))]
    scatter_df = df
    scatter_df.rename(columns={'player_name':'Player','player_team':'Team','player_position':'Position(s)','PctOfSeason':'TOG%','games_played':'Games Played','kicks':'Kicks','marks':'Marks','handballs':'Handballs','disposals':'Disposals','effective_disposals':'Effective Disposals','goals':'Goals','behinds':'Behinds','hitouts':'Hitouts','tackles':'Tackles','rebounds':'Rebound 50s','inside_fifties':'Inside 50s','clearances':'Clearances','clangers':'Clangers','free_kicks_for':'Free Kicks For','free_kicks_against':'Free Kicks Against','contested_possessions':'Contested Possessions','uncontested_possessions':'Uncontested Possessions','contested_marks':'Contested Marks','marks_inside_fifty':'Marks Inside Fifty','one_percenters':'One Percenters','bounces':'Bounces','goal_assists':'Goal Assists','afl_fantasy_score':'Afl Fantasy Score','centre_clearances':'Centre Clearances','stoppage_clearances':'Stoppage Clearances','score_involvements':'Score Involvements','metres_gained':'Metres Gained','turnovers':'Turnovers','intercepts':'Intercepts','tackles_inside_fifty':'Tackles Inside Fifty','contest_def_losses':'Contest Def Losses','contest_def_one_on_ones':'Contest Def One On Ones','contest_off_one_on_ones':'Contest Off One On Ones','contest_off_wins':'Contest Off Wins','def_half_pressure_acts':'Def Half Pressure Acts','effective_kicks':'Effective Kicks','f50_ground_ball_gets':'Forward 50 Ground Ball Gets','ground_ball_gets':'Ground Ball Gets','hitouts_to_advantage':'Hitouts To Advantage','intercept_marks':'Intercept Marks','marks_on_lead':'Marks On Lead','pressure_acts':'Pressure Acts','rating_points':'Rating Points','ruck_contests':'Ruck Contests','score_launches':'Score Launches','shots_at_goal':'Shots At Goal','spoils':'Spoils'},
                      inplace=True)
    scatter_df = scatter_df[scatter_df['TOG%']>=mins/100]

    vars = scatter_df.columns[6:].tolist()
    vars.remove('80sr')
    
    with st.form("Scatter Options"):
        submitted = st.form_submit_button("Submit Options")

        scatter_pos = st.multiselect('Positions to Include (leave blank for all)', ['Full-Forward','Forward Pocket','Centre Half-Forward','Half-Forward','Wing','Centre','Ruck-Rover','Rover','Ruck','Half-Back','Centre Half-Back','Back-Pocket','Full-Back'])
        xx = st.selectbox('X-Axis Variable', vars, index=0)
        yy = st.selectbox('Y-Axis Variable', vars, index=25)
        cc = st.selectbox('Point Color Variable', vars, index=0)
        cscale = st.selectbox('Point Colorscale', colorscales, index=78)

    if scatter_pos == []:
        scatter_pos = None
    if scatter_pos == None:
        compares = 'All Players'
    else:
        pattern = r'(^|, )(' + '|'.join(scatter_pos) + r')($|, )'
        scatter_df = scatter_df[scatter_df['Position(s)'].str.contains(pattern, regex=True)]
        if len(scatter_pos) > 2:
            compares = f"{', '.join(scatter_pos[:-1])}, and {scatter_pos[-1]}"
        elif len(scatter_pos) == 2:
            compares = f"{scatter_pos[0]} and {scatter_pos[1]}"
        elif len(scatter_pos) == 1:
            compares = f"{scatter_pos[0]}"
        else:
            compares = f"{scatter_pos}s"

    fig_scatter = px.scatter(
        scatter_df,
        x = xx,
        y = yy,
        color = cc,
        color_continuous_scale = cscale,
        text = 'Player',
        hover_data=['Team', 'Position(s)', 'TOG%'],
        hover_name = 'Player',
        title = f'{season} {league}, {xx} & {yy}<br><sup>{compares}, minimum {mins}% Time On Ground<br>Values are per 80 minutes played | {extra_text} | Created on footy-radars.streamlit.app</sup>',
        width=900,
        height=700)
    fig_scatter.update_traces(textposition='top right', marker=dict(size=10, line=dict(width=1, color='black')))
    
    fig_scatter.add_hline(y=scatter_df[yy].median(), name='Median', line_width=0.5)
    fig_scatter.add_vline(x=scatter_df[xx].median(), name='Median', line_width=0.5)
    
    st.plotly_chart(fig_scatter, theme=None, use_container_width=False)

with filter_tab:
    st.button("Reset Sliders", on_click=_update_slider, kwargs={"value": 0.0})
    with st.form('Minimum Percentile Filters'):
        submitted = st.form_submit_button("Submit Filters")
        filter_pos = st.multiselect('Positions to Include (leave blank for all)', ['Full-Forward','Forward Pocket','Centre Half-Forward','Half-Forward','Wing','Centre','Ruck-Rover','Rover','Ruck','Half-Back','Centre Half-Back','Back-Pocket','Full-Back'])
            
        if ['slider1','slider2','slider3','slider4','slider5','slider6','slider7','slider8','slider9','slider10','slider11','slider12','slider13','slider14','slider15','slider16','slider17','slider18','slider19','slider20','slider21','slider22','slider23','slider24','slider25','slider26','slider27','slider28','slider29','slider30','slider31','slider32','slider33','slider34','slider35','slider36','slider37','slider38','slider39','slider40','slider41','slider42','slider43','slider44','slider45'] not in st.session_state:
            pass

        filter_v1 = st.slider('Metres Gained', 0.0, 1.0, 0.0, key='slider1')
        filter_v2 = st.slider('Disposals', 0.0, 1.0, 0.0, key='slider2')
        if league == 'AFL':
            filter_v3 = st.slider('Effective Disposals', 0.0, 1.0, 0.0, key='slider3')
        filter_v4 = st.slider('Handballs', 0.0, 1.0, 0.0, key='slider4')
        if league == 'AFL':
            filter_v5 = st.slider('Handball Efficiency', 0.0, 1.0, 0.0, key='slider5')
        filter_v6 = st.slider('Kicks', 0.0, 1.0, 0.0, key='slider6')
        if league == 'AFL':
            filter_v7 = st.slider('Kick Efficiency', 0.0, 1.0, 0.0, key='slider7')
        filter_v8 = st.slider('Shots At Goal', 0.0, 1.0, 0.0, key='slider8')
        filter_v9 = st.slider('Goals', 0.0, 1.0, 0.0, key='slider9')
        filter_v10 = st.slider('Behinds', 0.0, 1.0, 0.0, key='slider10')
        filter_v11 = st.slider('Points', 0.0, 1.0, 0.0, key='slider11')
        filter_v12 = st.slider('Points per Shot', 0.0, 1.0, 0.0, key='slider12')
        filter_v13 = st.slider('Goal Assists', 0.0, 1.0, 0.0, key='slider13')
        filter_v14 = st.slider('Score Involvements', 0.0, 1.0, 0.0, key='slider14')
        filter_v15 = st.slider('Marks', 0.0, 1.0, 0.0, key='slider15')
        filter_v16 = st.slider('Marks Inside 50', 0.0, 1.0, 0.0, key='slider16')
        filter_v17 = st.slider('Contested Marks', 0.0, 1.0, 0.0, key='slider17')
        filter_v18 = st.slider('Inside 50s', 0.0, 1.0, 0.0, key='slider18')
        filter_v19 = st.slider('Rebound 50s', 0.0, 1.0, 0.0, key='slider19')
        if league == 'AFL':
            filter_v20 = st.slider('Marks On Lead', 0.0, 1.0, 0.0, key='slider20')
            filter_v21 = st.slider('Intercept Marks', 0.0, 1.0, 0.0, key='slider21')
        filter_v22 = st.slider('% of Possessions Contested', 0.0, 1.0, 0.0, key='slider22')
        filter_v23 = st.slider('% of Marks Contested', 0.0, 1.0, 0.0, key='slider23')
        filter_v24 = st.slider('One Percenters', 0.0, 1.0, 0.0, key='slider24')
        filter_v25 = st.slider('Tackles', 0.0, 1.0, 0.0, key='slider25')
        filter_v26 = st.slider('Tackles Inside 50', 0.0, 1.0, 0.0, key='slider26')
        filter_v27 = st.slider('Clearances', 0.0, 1.0, 0.0, key='slider27')
        filter_v28 = st.slider('Turnovers', 0.0, 1.0, 0.0, key='slider28')
        filter_v29 = st.slider('Intercepts', 0.0, 1.0, 0.0, key='slider29')
        if league == 'AFL':
            filter_v30 = st.slider('Pressure Acts', 0.0, 1.0, 0.0, key='slider30')
            filter_v31 = st.slider('Def Half Pressure Acts', 0.0, 1.0, 0.0, key='slider31')
            filter_v32 = st.slider('Forward 50 Ground Ball Gets', 0.0, 1.0, 0.0, key='slider32')
            filter_v33 = st.slider('Ground Ball Gets', 0.0, 1.0, 0.0, key='slider33')
            filter_v34 = st.slider('Ruck Contests', 0.0, 1.0, 0.0, key='slider34')
        filter_v35 = st.slider('Hitouts', 0.0, 1.0, 0.0, key='slider35')
        if league == 'AFL':
            filter_v36 = st.slider('Hitout Efficiency', 0.0, 1.0, 0.0, key='slider36')
            filter_v37 = st.slider('Hitouts To Advantage', 0.0, 1.0, 0.0, key='slider37')
        filter_v38 = st.slider('Centre Clearances', 0.0, 1.0, 0.0, key='slider38')
        filter_v39 = st.slider('Stoppage Clearances', 0.0, 1.0, 0.0, key='slider39')
        if league == 'AFL':
            filter_v40 = st.slider('Score Launches', 0.0, 1.0, 0.0, key='slider40')
            filter_v41 = st.slider('Spoils', 0.0, 1.0, 0.0, key='slider41')
        filter_v42 = st.slider('Free Kicks For', 0.0, 1.0, 0.0, key='slider42')
        filter_v43 = st.slider('Free Kicks Against', 0.0, 1.0, 0.0, key='slider43')
        filter_v44 = st.slider('Clangers', 0.0, 1.0, 0.0, key='slider44')
        filter_v45 = st.slider('Afl Fantasy Score', 0.0, 1.0, 0.0, key='slider45')

with filter_table_tab:
    if filter_pos == []:
        filter_pos = None
    df = create_filter_table_df(mins, filter_pos)

    if league == 'AFL':
        player_research_table = df[
        (df['metres_gained']>=filter_v1) &
        (df['disposals']>=filter_v2) &
        (df['effective_disposals']>=filter_v3) &
        (df['handballs']>=filter_v4) &
        (df['Handball Efficiency']>=filter_v5) &
        (df['kicks']>=filter_v6) &
        (df['Kick Efficiency']>=filter_v7) &
        (df['shots_at_goal']>=filter_v8) &
        (df['goals']>=filter_v9) &
        (df['behinds']>=filter_v10) &
        (df['Points']>=filter_v11) &
        (df['Points per Shot']>=filter_v12) &
        (df['goal_assists']>=filter_v13) &
        (df['score_involvements']>=filter_v14) &
        (df['marks']>=filter_v15) &
        (df['marks_inside_fifty']>=filter_v16) &
        (df['contested_marks']>=filter_v17) &
        (df['inside_fifties']>=filter_v18) &
        (df['rebounds']>=filter_v19) &
        (df['marks_on_lead']>=filter_v20) &
        (df['intercept_marks']>=filter_v21) &
        (df['% of Possessions Contested']>=filter_v22) &
        (df['% of Marks Contested']>=filter_v23) &
        (df['one_percenters']>=filter_v24) &
        (df['tackles']>=filter_v25) &
        (df['tackles_inside_fifty']>=filter_v26) &
        (df['clearances']>=filter_v27) &
        (df['turnovers']>=filter_v28) &
        (df['intercepts']>=filter_v29) &
        (df['pressure_acts']>=filter_v30) &
        (df['def_half_pressure_acts']>=filter_v31) &
        (df['f50_ground_ball_gets']>=filter_v32) &
        (df['ground_ball_gets']>=filter_v33) &
        (df['ruck_contests']>=filter_v34) &
        (df['hitouts']>=filter_v35) &
        (df['Hitout Efficiency']>=filter_v36) &
        (df['hitouts_to_advantage']>=filter_v37) &
        (df['centre_clearances']>=filter_v38) &
        (df['stoppage_clearances']>=filter_v39) &
        (df['score_launches']>=filter_v40) &
        (df['spoils']>=filter_v41) &
        (df['free_kicks_for']>=filter_v42) &
        (df['free_kicks_against']>=filter_v43) &
        (df['clangers']>=filter_v44) &
        (df['afl_fantasy_score']>=filter_v45)
        ].reset_index(drop=True)
    if league == 'AFLW':
        player_research_table = df[
        (df['metres_gained']>=filter_v1) &
        (df['disposals']>=filter_v2) &
        # (df['effective_disposals']>=filter_v3) &
        (df['handballs']>=filter_v4) &
        # (df['Handball Efficiency']>=filter_v5) &
        (df['kicks']>=filter_v6) &
        # (df['Kick Efficiency']>=filter_v7) &
        (df['shots_at_goal']>=filter_v8) &
        (df['goals']>=filter_v9) &
        (df['behinds']>=filter_v10) &
        (df['Points']>=filter_v11) &
        (df['Points per Shot']>=filter_v12) &
        (df['goal_assists']>=filter_v13) &
        (df['score_involvements']>=filter_v14) &
        (df['marks']>=filter_v15) &
        (df['marks_inside_fifty']>=filter_v16) &
        (df['contested_marks']>=filter_v17) &
        (df['inside_fifties']>=filter_v18) &
        (df['rebounds']>=filter_v19) &
        # (df['marks_on_lead']>=filter_v20) &
        # (df['intercept_marks']>=filter_v21) &
        (df['% of Possessions Contested']>=filter_v22) &
        (df['% of Marks Contested']>=filter_v23) &
        (df['one_percenters']>=filter_v24) &
        (df['tackles']>=filter_v25) &
        (df['tackles_inside_fifty']>=filter_v26) &
        (df['clearances']>=filter_v27) &
        (df['turnovers']>=filter_v28) &
        (df['intercepts']>=filter_v29) &
        # (df['pressure_acts']>=filter_v30) &
        # (df['def_half_pressure_acts']>=filter_v31) &
        # (df['f50_ground_ball_gets']>=filter_v32) &
        # (df['ground_ball_gets']>=filter_v33) &
        # (df['ruck_contests']>=filter_v34) &
        (df['hitouts']>=filter_v35) &
        # (df['Hitout Efficiency']>=filter_v36) &
        # (df['hitouts_to_advantage']>=filter_v37) &
        (df['centre_clearances']>=filter_v38) &
        (df['stoppage_clearances']>=filter_v39) &
        # (df['score_launches']>=filter_v40) &
        # (df['spoils']>=filter_v41) &
        (df['free_kicks_for']>=filter_v42) &
        (df['free_kicks_against']>=filter_v43) &
        (df['clangers']>=filter_v44) &
        (df['afl_fantasy_score']>=filter_v45)
        ].reset_index(drop=True)

    if league == 'AFL':
        cols_to_show = ['player_name','player_team','player_position','PctOfSeason','80s','metres_gained','disposals','effective_disposals','handballs','Handball Efficiency','kicks','Kick Efficiency','shots_at_goal','goals','behinds','Points','Points per Shot','goal_assists','score_involvements','marks','marks_inside_fifty','contested_marks','inside_fifties','rebounds','marks_on_lead','intercept_marks','% of Possessions Contested','% of Marks Contested','one_percenters','tackles','tackles_inside_fifty','clearances','turnovers','intercepts','pressure_acts','def_half_pressure_acts','f50_ground_ball_gets','ground_ball_gets','ruck_contests','hitouts','Hitout Efficiency','hitouts_to_advantage','centre_clearances','stoppage_clearances','score_launches','spoils','free_kicks_for','free_kicks_against','clangers','afl_fantasy_score',]
        player_research_table = player_research_table[cols_to_show].rename(columns={'player_name':'Player','player_team':'Team','player_position':'Position(s)','PctOfSeason':'TOG%', 'metres_gained':'Metres Gained','disposals':'Disposals','effective_disposals':'Effective Disposals','handballs':'Handballs','Handball Efficiency':'Handball Efficiency','kicks':'Kicks','Kick Efficiency':'Kick Efficiency','shots_at_goal':'Shots At Goal','goals':'Goals','behinds':'Behinds','Points':'Points','Points per Shot':'Points per Shot','goal_assists':'Goal Assists','score_involvements':'Score Involvements','marks':'Marks','marks_inside_fifty':'Marks Inside 50','contested_marks':'Contested Marks','inside_fifties':'Inside 50s','rebounds':'Rebound 50s','marks_on_lead':'Marks On Lead','intercept_marks':'Intercept Marks','% of Possessions Contested':'% of Possessions Contested','% of Marks Contested':'% of Marks Contested','one_percenters':'One Percenters','tackles':'Tackles','tackles_inside_fifty':'Tackles Inside 50','clearances':'Clearances','turnovers':'Turnovers','intercepts':'Intercepts','pressure_acts':'Pressure Acts','def_half_pressure_acts':'Def Half Pressure Acts','f50_ground_ball_gets':'Forward 50 Ground Ball Gets','ground_ball_gets':'Ground Ball Gets','ruck_contests':'Ruck Contests','hitouts':'Hitouts','Hitout Efficiency':'Hitout Efficiency','hitouts_to_advantage':'Hitouts To Advantage','centre_clearances':'Centre Clearances','stoppage_clearances':'Stoppage Clearances','score_launches':'Score Launches','spoils':'Spoils','free_kicks_for':'Free Kicks For','free_kicks_against':'Free Kicks Against','clangers':'Clangers','afl_fantasy_score':'Afl Fantasy Score',})
    if league == 'AFLW':
        cols_to_show = ['player_name','player_team','player_position','PctOfSeason','80s','metres_gained','disposals','effective_disposals','handballs','Handball Efficiency','kicks','Kick Efficiency','shots_at_goal','goals','behinds','Points','Points per Shot','goal_assists','score_involvements','marks','marks_inside_fifty','contested_marks','inside_fifties','rebounds','marks_on_lead','intercept_marks','% of Possessions Contested','% of Marks Contested','one_percenters','tackles','tackles_inside_fifty','clearances','turnovers','intercepts','pressure_acts','def_half_pressure_acts','f50_ground_ball_gets','ground_ball_gets','ruck_contests','hitouts','Hitout Efficiency','hitouts_to_advantage','centre_clearances','stoppage_clearances','score_launches','spoils','free_kicks_for','free_kicks_against','clangers','afl_fantasy_score',]
        trouble_cols = [
            'contest_def_one_on_ones', 'def_half_pressure_acts', 'intercept_marks', 'hitout_win_percentage', 'contest_off_wins', 'pressure_acts', 'score_launches', 'effective_kicks', 'contest_off_one_on_ones', 'marks_on_lead', 'spoils', 'ground_ball_gets', 'hitouts_to_advantage', 'ruck_contests', 'contest_def_losses', 'f50_ground_ball_gets', 'effective_disposals',
            'Kick Efficiency','Handball Efficiency','Hitout Efficiency']
        cols_to_show = [x for x in cols_to_show if x not in trouble_cols]
        player_research_table = player_research_table[cols_to_show].rename(columns={'player_name':'Player','player_team':'Team','player_position':'Position(s)','PctOfSeason':'TOG%','80s':'68s','metres_gained':'Metres Gained','disposals':'Disposals','effective_disposals':'Effective Disposals','handballs':'Handballs','Handball Efficiency':'Handball Efficiency','kicks':'Kicks','Kick Efficiency':'Kick Efficiency','shots_at_goal':'Shots At Goal','goals':'Goals','behinds':'Behinds','Points':'Points','Points per Shot':'Points per Shot','goal_assists':'Goal Assists','score_involvements':'Score Involvements','marks':'Marks','marks_inside_fifty':'Marks Inside 50','contested_marks':'Contested Marks','inside_fifties':'Inside 50s','rebounds':'Rebound 50s','marks_on_lead':'Marks On Lead','intercept_marks':'Intercept Marks','% of Possessions Contested':'% of Possessions Contested','% of Marks Contested':'% of Marks Contested','one_percenters':'One Percenters','tackles':'Tackles','tackles_inside_fifty':'Tackles Inside 50','clearances':'Clearances','turnovers':'Turnovers','intercepts':'Intercepts','pressure_acts':'Pressure Acts','def_half_pressure_acts':'Def Half Pressure Acts','f50_ground_ball_gets':'Forward 50 Ground Ball Gets','ground_ball_gets':'Ground Ball Gets','ruck_contests':'Ruck Contests','hitouts':'Hitouts','Hitout Efficiency':'Hitout Efficiency','hitouts_to_advantage':'Hitouts To Advantage','centre_clearances':'Centre Clearances','stoppage_clearances':'Stoppage Clearances','score_launches':'Score Launches','spoils':'Spoils','free_kicks_for':'Free Kicks For','free_kicks_against':'Free Kicks Against','clangers':'Clangers','afl_fantasy_score':'Afl Fantasy Score',})
    
    st.write("Colored numbers shown are percentile ranks")
    
    st.dataframe(player_research_table.style.applymap(color_percentile, subset=player_research_table.columns[5:]))


with ranking_tab:
    df = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/AFL-Radars/refs/heads/main/Player-Data/{league}/{season}.csv")
    df['Possessions'] = df['contested_possessions']+df['uncontested_possessions']
    if league == 'AFL':
        df['Kick Efficiency'] = df['effective_kicks']/df['kicks']*100
        df['Handball Efficiency'] = (df['effective_disposals']-df['effective_kicks'])/df['handballs']*100
        df['Hitout Efficiency'] = df['hitouts_to_advantage']/df['hitouts']*100
    df['% of Possessions Contested'] = df['contested_possessions']/(df['Possessions'])*100
    df['% of Marks Contested'] = df['contested_marks']/(df['marks'])*100
    df['Points'] = (df['goals']*6)+(df['behinds'])
    df['Points per Shot'] = df['Points']/df['shots_at_goal']
    df['Points per Shot'] = [0 if df['shots_at_goal'][i]==0 else df['Points'][i]/df['shots_at_goal'][i] for i in range(len(df))]
    df.rename(columns={'player_name':'Player','player_team':'Team','player_position':'Position(s)','PctOfSeason':'TOG%','games_played':'Games Played','kicks':'Kicks','marks':'Marks','handballs':'Handballs','disposals':'Disposals','effective_disposals':'Effective Disposals','goals':'Goals','behinds':'Behinds','hitouts':'Hitouts','tackles':'Tackles','rebounds':'Rebound 50s','inside_fifties':'Inside 50s','clearances':'Clearances','clangers':'Clangers','free_kicks_for':'Free Kicks For','free_kicks_against':'Free Kicks Against','contested_possessions':'Contested Possessions','uncontested_possessions':'Uncontested Possessions','contested_marks':'Contested Marks','marks_inside_fifty':'Marks Inside Fifty','one_percenters':'One Percenters','bounces':'Bounces','goal_assists':'Goal Assists','afl_fantasy_score':'Afl Fantasy Score','centre_clearances':'Centre Clearances','stoppage_clearances':'Stoppage Clearances','score_involvements':'Score Involvements','metres_gained':'Metres Gained','turnovers':'Turnovers','intercepts':'Intercepts','tackles_inside_fifty':'Tackles Inside Fifty','contest_def_losses':'Contest Def Losses','contest_def_one_on_ones':'Contest Def One On Ones','contest_off_one_on_ones':'Contest Off One On Ones','contest_off_wins':'Contest Off Wins','def_half_pressure_acts':'Def Half Pressure Acts','effective_kicks':'Effective Kicks','f50_ground_ball_gets':'Forward 50 Ground Ball Gets','ground_ball_gets':'Ground Ball Gets','hitouts_to_advantage':'Hitouts To Advantage','intercept_marks':'Intercept Marks','marks_on_lead':'Marks On Lead','pressure_acts':'Pressure Acts','rating_points':'Rating Points','ruck_contests':'Ruck Contests','score_launches':'Score Launches','shots_at_goal':'Shots At Goal','spoils':'Spoils'},
                      inplace=True)
    df = df[df['TOG%']>=mins/100]
    df['TOG%'] = 100*df['TOG%']

    with st.form('Position & Metric Rankings'):
        submitted = st.form_submit_button("Submit Positions & Metrics")
        rank_pos = st.multiselect('Positions to Include (leave blank for all)', ['Full-Forward','Forward Pocket','Centre Half-Forward','Half-Forward','Wing','Centre','Ruck-Rover','Rover','Ruck','Half-Back','Centre Half-Back','Back-Pocket','Full-Back'])
        vars = df.columns[9:].tolist()
        vars.remove('80sr')
        metrics = st.multiselect("Choose metrics to include:", vars)

    if rank_pos != []:
        pattern = r'(^|, )(' + '|'.join(rank_pos) + r')($|, )'
        df = df[df['Position(s)'].str.contains(pattern, regex=True)]

    if metrics:
        # User assigns weights
        with st.form('Metric Weightings'):
            submitted = st.form_submit_button("Submit Metric Weightings")
            weights = {}
            for metric in metrics:
                weights[metric] = st.slider(f"Weight for {metric}", 0.0, 1.0, 0.5, 0.05)
        
        # Normalize data using z-score
        df_filtered = df.copy()
        df_filtered[metrics] = df_filtered[metrics].apply(zscore, nan_policy='omit')
        for metric in metrics:
            df_filtered[metric] = df_filtered[metric] + abs(df_filtered[metric].min())
            df_filtered[metric] = NormalizeData(df_filtered[metric])
            
        # Compute weighted z-score ranking
        df_filtered["Score"] = df_filtered[metrics].apply(lambda row: sum(row[metric] * weights[metric] for metric in metrics), axis=1)
        min_score = df_filtered["Score"].min()
        max_score = df_filtered["Score"].max()
        df_filtered["Score"] = (df_filtered["Score"] - min_score) / (max_score - min_score) * 100

        # Display results
        st.write("Normalized Weighted Z-Score Player Rankings")
        st.dataframe(df_filtered.sort_values("Score", ascending=False)[["Player","Team","Position(s)",'TOG%',"Score",] + metrics].style.applymap(color_percentile_100, subset=df_filtered.sort_values("Score", ascending=False)[["Player","Team","Position(s)",'TOG%',"Score",] + metrics].columns[4:]))

    else:
        st.warning("Please select at least one metric.")

with metric_trend_tab:
    df = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/AFL-Radars/refs/heads/main/Player-Data/{league}/GameByGame/{season}.csv")
    df = df.rename(columns={'player.playerId':'player_id','player.photoURL':'picture','minutes':'minutes','kicks':'kicks','marks':'marks','handballs':'handballs','disposals':'disposals','extendedStats.effectiveDisposals':'effective_disposals','goals':'goals','behinds':'behinds','hitouts':'hitouts','tackles':'tackles','rebound50s':'rebounds','inside50s':'inside_fifties','clearances.totalClearances':'clearances','clangers':'clangers','freesFor':'free_kicks_for','freesAgainst':'free_kicks_against','':'brownlow_votes','contestedPossessions':'contested_possessions','uncontestedPossessions':'uncontested_possessions','contestedMarks':'contested_marks','marksInside50':'marks_inside_fifty','onePercenters':'one_percenters','bounces':'bounces','goalAssists':'goal_assists','dreamTeamPoints':'afl_fantasy_score','':'supercoach_score','clearances.centreClearances':'centre_clearances','clearances.stoppageClearances':'stoppage_clearances','scoreInvolvements':'score_involvements','metresGained':'metres_gained','turnovers':'turnovers','intercepts':'intercepts','tacklesInside50':'tackles_inside_fifty','extendedStats.contestDefLosses':'contest_def_losses','extendedStats.contestDefOneOnOnes':'contest_def_one_on_ones','extendedStats.contestOffOneOnOnes':'contest_off_one_on_ones','extendedStats.contestOffWins':'contest_off_wins','extendedStats.defHalfPressureActs':'def_half_pressure_acts','extendedStats.effectiveKicks':'effective_kicks','extendedStats.f50GroundBallGets':'f50_ground_ball_gets','extendedStats.groundBallGets':'ground_ball_gets','extendedStats.hitoutsToAdvantage':'hitouts_to_advantage','extendedStats.hitoutWinPercentage':'hitout_win_percentage','extendedStats.interceptMarks':'intercept_marks','extendedStats.marksOnLead':'marks_on_lead','extendedStats.pressureActs':'pressure_acts','ratingPoints':'rating_points','extendedStats.ruckContests':'ruck_contests','extendedStats.scoreLaunches':'score_launches','shotsAtGoal':'shots_at_goal','extendedStats.spoils':'spoils','team.name':'player_team','player.player.position':'player_position','player.playerJumperNumber':'guernsey_number',
    })
    if league == 'AFL':
        df['minutes'] = 80*(df['timeOnGroundPercentage']/100)
    if league == 'AFLW':
        df['minutes'] = (17*4)*(df['timeOnGroundPercentage']/100)
    df['player_name'] = df['player.givenName'] + " " + df['player.surname']
    df.utcStartTime = pd.to_datetime(df.utcStartTime)
    df = df.sort_values(['utcStartTime']).reset_index(drop=True)
    df['Possessions'] = df['contested_possessions']+df['uncontested_possessions']
    if league == 'AFL':
        df['Kick Efficiency'] = df['effective_kicks']/df['kicks']*100
        df['Handball Efficiency'] = (df['effective_disposals']-df['effective_kicks'])/df['handballs']*100
        df['Hitout Efficiency'] = df['hitouts_to_advantage']/df['hitouts']*100
    df['% of Possessions Contested'] = df['contested_possessions']/(df['Possessions'])*100
    df['% of Marks Contested'] = df['contested_marks']/(df['marks'])*100
    df['Points'] = (df['goals']*6)+(df['behinds'])
    df['Points per Shot'] = df['Points']/df['shots_at_goal']
    df['Points per Shot'] = [0 if df['shots_at_goal'][i]==0 else df['Points'][i]/df['shots_at_goal'][i] for i in range(len(df))]
    df.rename(columns={'player_name':'Player','player_team':'Team','player_position':'Position(s)','timeOnGroundPercentage':'TOG%','games_played':'Games Played','kicks':'Kicks','marks':'Marks','handballs':'Handballs','disposals':'Disposals','effective_disposals':'Effective Disposals','goals':'Goals','behinds':'Behinds','hitouts':'Hitouts','tackles':'Tackles','rebounds':'Rebound 50s','inside_fifties':'Inside 50s','clearances':'Clearances','clangers':'Clangers','free_kicks_for':'Free Kicks For','free_kicks_against':'Free Kicks Against','contested_possessions':'Contested Possessions','uncontested_possessions':'Uncontested Possessions','contested_marks':'Contested Marks','marks_inside_fifty':'Marks Inside Fifty','one_percenters':'One Percenters','bounces':'Bounces','goal_assists':'Goal Assists','afl_fantasy_score':'Afl Fantasy Score','centre_clearances':'Centre Clearances','stoppage_clearances':'Stoppage Clearances','score_involvements':'Score Involvements','metres_gained':'Metres Gained','turnovers':'Turnovers','intercepts':'Intercepts','tackles_inside_fifty':'Tackles Inside Fifty','contest_def_losses':'Contest Def Losses','contest_def_one_on_ones':'Contest Def One On Ones','contest_off_one_on_ones':'Contest Off One On Ones','contest_off_wins':'Contest Off Wins','def_half_pressure_acts':'Def Half Pressure Acts','effective_kicks':'Effective Kicks','f50_ground_ball_gets':'Forward 50 Ground Ball Gets','ground_ball_gets':'Ground Ball Gets','hitouts_to_advantage':'Hitouts To Advantage','intercept_marks':'Intercept Marks','marks_on_lead':'Marks On Lead','pressure_acts':'Pressure Acts','rating_points':'Rating Points','ruck_contests':'Ruck Contests','score_launches':'Score Launches','shots_at_goal':'Shots At Goal','spoils':'Spoils'},
                      inplace=True)
    df['Opponent'] = [f"vs. {df['away.team.name'][i]} - {df['round.name'][i]}" if df['Team'][i]==df['home.team.name'][i] else f"at {df['home.team.name'][i]} - {df['round.name'][i]}" for i in range(len(df))]
   
    with st.form('Player Game-By-Game Metric Development'):
        submitted = st.form_submit_button("Submit Player & Metric")
        player = st.text_input("Player", "")
        # vars = df.columns[21:].tolist()
        # vars.remove('Opponent')
        foc_var = st.selectbox("Metric to Plot:", vars+['TOG%'])
        adj_80s = st.selectbox('Adjust Data for Time On Ground?', ['Yes','No'])
        
        player_df = df[df.Player==player].reset_index(drop=True)
        
        #############
        if len(player_df) > 0:
            season_metric_fig = make_season_metric_img(player_df, adj_80s, player, foc_var, league, season)
            st.altair_chart(season_metric_fig, use_container_width=True)
        else:
            st.write(f"Your chosen player played 0 {league} games in {season}")
