import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from statistics import mean, harmonic_mean
from math import pi
sns.set_style("white")
import warnings
warnings.filterwarnings('ignore')
import matplotlib
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
import urllib.request
from highlight_text import fig_text
import streamlit as st

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

def scout_report(league, season, pos, mins, name,callout, bar_colors, dist_labels, sig, extra_text):
    import matplotlib
    matplotlib.rcParams.update(matplotlib.rcParamsDefault)
    df = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/AFL-Radars/refs/heads/main/Player-Data/{league}/{season}.csv")
    df = df.dropna(subset=['player_position']).reset_index(drop=True)
    df['possessions'] = df['contested_possessions']+df['uncontested_possessions']
    df['kick_efficiency'] = df['effective_kicks']/df['kicks']*100
    df['handball_efficiency'] = (df['effective_disposals']-df['effective_kicks'])/df['handballs']*100
    df['pct_contested_poss'] = df['contested_possessions']/(df['possessions'])*100
    df['pct_marks_contested'] = df['contested_marks']/(df['marks'])*100
    df['hitout_efficiency'] = df['hitouts_to_advantage']/df['hitouts']*100
    df['points'] = (df['goals']*6)+(df['behinds'])
    df['points_per_shot'] = df['points']/df['shots_at_goal']
    df['points_per_shot'] = [0 if df['shots_at_goal'][i]==0 else df['points'][i]/df['shots_at_goal'][i] for i in range(len(df))]

    logo_df = pd.DataFrame({'team':['Adelaide Crows','Brisbane Lions','Carlton','Collingwood','Essendon','Fremantle','Geelong Cats','Gold Coast SUNS','GWS Giants','Hawthorn','Melbourne','North Melbourne','Port Adelaide','Richmond','St Kilda','Sydney Swans','West Coast Eagles','Western Bulldogs'],
                           'logo_url':['https://upload.wikimedia.org/wikipedia/en/thumb/4/49/Adelaide_Crows_logo_2010.svg/1920px-Adelaide_Crows_logo_2010.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/c/c7/Brisbane_Lions_logo_2010.svg/1024px-Brisbane_Lions_logo_2010.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/5/58/Carlton_FC_Logo_2020.svg/1024px-Carlton_FC_Logo_2020.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/a/a6/Collingwood_Football_Club_Logo_%282017%E2%80%93present%29.svg/1024px-Collingwood_Football_Club_Logo_%282017%E2%80%93present%29.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/8/8b/Essendon_FC_logo.svg/1920px-Essendon_FC_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/c/ca/Fremantle_FC_logo.svg/1280px-Fremantle_FC_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/5/5f/Geelong_Cats_logo.svg/1024px-Geelong_Cats_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/7/7d/Gold_Coast_Suns_AFL_Logo.svg/1920px-Gold_Coast_Suns_AFL_Logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/0/07/GWS_Giants_logo.svg/1280px-GWS_Giants_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/6/62/Hawthorn-football-club-brand.svg/1280px-Hawthorn-football-club-brand.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/4/4e/Melbournefc.svg/1024px-Melbournefc.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/f/fc/North_Melbourne_FC_logo.svg/1024px-North_Melbourne_FC_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/3/36/Port_Adelaide_Football_Club_logo.svg/800px-Port_Adelaide_Football_Club_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/3/35/Richmond_Tigers_logo.svg/800px-Richmond_Tigers_logo.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/0/06/St_Kilda_Football_Club_logo_2024.svg/1024px-St_Kilda_Football_Club_logo_2024.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/a/af/Sydney_Swans_Logo_2020.svg/1024px-Sydney_Swans_Logo_2020.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/b/b5/West_Coast_Eagles_logo_2017.svg/1280px-West_Coast_Eagles_logo_2017.svg.png','https://upload.wikimedia.org/wikipedia/en/thumb/0/09/Western_Bulldogs_logo.svg/1024px-Western_Bulldogs_logo.svg.png']})
    
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
              'pct_marks_contested','hitout_efficiency','points_per_shot']
    revcols = ['clangers', 'turnovers', 'free_kicks_against']
    
    
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
    dfRadarMF.rename(columns={'goals_pct':'Goals',
                            'behinds_pct':'Behinds',
                              'shots_at_goal_pct':'Shots',
                              'points_per_shot_pct':'Points/\nShot',
                            'goal_assists_pct':'Goal\nAssists',
                            'score_involvements_pct':'Score\nInvolves',
                            'kicks_pct':'Kicks',
                            'handballs_pct':'Handballs',
                            'kick_efficiency_pct':'Kick\nSucc %',
                            'handball_efficiency_pct':'Handball\nSucc %',
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

    GROUPS_SIZE = [6,9,6,9,3]  # Attacker template

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

    plt.annotate("'Per Game' means per 80 minutes\nBars are percentiles%s\nAll values are per game%s\nCompared to %s\nOnly includes players with at least %.1f games played\nData: AFL | %s\nSample Size: %i players" %(callout_text,extra_text, compares, mins, sig, len(dfProspect)),
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
    urllib.request.urlretrieve("https://upload.wikimedia.org/wikipedia/en/thumb/e/e4/Australian_Football_League.svg/1920px-Australian_Football_League.svg.png","afl_logo.png")
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
    return fig_show

########################################################################
########################################################################
########################################################################
########################################################################
########################################################################
########################################################################

avail_data = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/AFL-Radars/refs/heads/main/AvailableData.csv")

with st.sidebar():
    league = st.selectbox('League', avail_data.Competition.unique().tolist(), default='AFL')
    season = st.selectbox('Season', sorted(avail_data[avail_data.Competition==league].Season.tolist(),reverse=True))
    mins = st.number_input('Minimum Time On Ground %', 0, 100, 35, 1)

extra_text = avail_data[(avail_data.Competition==league) & (avail_data.Season==season)].DataTime.values[0]


radar_tab, all_players_tab = st.tabs(['Player Radar', 'All Players List'])

with radar_tab:
    with st.form('Radar Options'):
        pos = st.multiselect('Positions to Include (leave blank for all)', ['Full-Forward','Forward Pocket','Centre Half-Forward','Half-Forward','Wing','Centre','Ruck-Rover','Rover','Ruck','Half-Back','Centre Half-Back','Back-Pocket','Full-Back'])
        callout = st.selectbox('Data Labels: Per Game or Percentiles?', ['Per Game','Percentile'])
        bar_colors = st.selectbox('Bar Coloring Scheme: Benchmarking Percentiles or Metric Groups?', ['Benchmarking Percentiles','Metric Groups'])
        dist_labels = st.selectbox('Distribution Labels on Bars?', ['Yes','No'])
        name = st.text_input("Player to Generate Radar For", "")

        try:
            radar_img = scout_report(league = league,
                         season = season,
                         pos = pos, #### make multiselect('Full-Forward','Forward Pocket','Centre Half-Forward','Half-Forward','Wing','Centre','Ruck-Rover','Rover','Ruck','Half-Back','Centre Half-Back','Back-Pocket','Full-Back',)
                         mins = mins,     # time on ground (50% = 50% of season)
                         name = name,
                         sig = 'Created by Ben Griffis (@BeGriffis)',
                         callout = callout, # Percentile | Per Game
                         bar_colors = bar_colors,  ## Benchmarking Percentiles | Metric Groups
                         dist_labels = dist_labels,
                         extra_text = f' | {extra_text}',
                        )
            st.pyplot(radar_img.figure)
        except:
            st.text("Please enter a valid player name. Refer to the All Players List tab if needed.  \nEnsure your player meets the minimum TOG% threshold.")