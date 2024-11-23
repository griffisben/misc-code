import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib
from matplotlib.colors import to_rgba
from matplotlib import colors
from matplotlib.colors import Normalize
import matplotlib.patheffects as path_effects
from adjustText import adjust_text
from scipy import stats
plt.rcParams['figure.dpi'] = 300

def rank_column(df, column_name):
    return stats.rankdata(df[column_name], "average") / len(df[column_name])
def rank_column_inverse(df, column_name):
    return 1-stats.rankdata(df[column_name], "average") / len(df[column_name])
def style_rows(row):
    pc=row['VAEP/90 Pctile']
    if 1-pc <= 0.1:
        color = ('#01349b', '#d9e3f6')  # Elite
    elif 0.1 < 1-pc <= 0.35:
        color = ('#007f35', '#d9f0e3')  # Above Avg
    elif 0.35 < 1-pc <= 0.66:
        color = ('#9b6700', '#fff2d9')  # Avg
    else:
        color = ('#b60918', '#fddbde')  # Below Avg
    return [f'background-color: {color[1]}'] * len(row)
def style_rows_group_avg(row):
    pc=row['VAEP/90 vs Group Avg Percentile']
    if 1-pc <= 0.1:
        color = ('#01349b', '#d9e3f6')  # Elite
    elif 0.1 < 1-pc <= 0.35:
        color = ('#007f35', '#d9f0e3')  # Above Avg
    elif 0.35 < 1-pc <= 0.66:
        color = ('#9b6700', '#fff2d9')  # Avg
    else:
        color = ('#b60918', '#fddbde')  # Below Avg
    return [f'background-color: {color[1]}'] * len(row)



with st.expander('Information about Roles & Action Values'):
    st.write("""
    Role Clusters determined by an Algorithm trained on heatmaps of all UEFA T5 league players, over 2.9 million events.  \n
    Players are assigned a cluster based on the areas they operate in. Clusters are subjectively named by me.  \n
    This aims to describe the areas of the pitch a player operates in, instead of 'playmaker', 'false 9', etc.  \n
      \n
    Action Value is similar to StatsBomb's On-Ball Value (OBV) or American Soccer Analysis's Goals Added (g+).  \n
    This metric values each action in terms of the change in probability of scoring & conceding (proxied by xG instead of actual goals).  \n
    The model looks at the action type, where it took place, and context variables such as phase of play & other actions in the possession.  \n
    It excludes all penalties, totals each player's attacking & defensive value, calculates value/90', and then finally  \n
    compares this per 90 number to their position's average score. Their position is determined by the Clustering model.  \n
    The positions are shows under the player names, before the clustering role. So, a CM with a positive value may be better than the average CM
    """)

lg_lookup = pd.read_csv("https://raw.githubusercontent.com/griffisben/misc-code/main/VAEP/VAEP_app_leagues.csv")
league_list = lg_lookup.League.unique().tolist()

with st.sidebar:
    lg = st.selectbox('League', league_list)
    season = st.selectbox('Season', (sorted(lg_lookup[lg_lookup.League == lg].Season.unique().tolist(),reverse=True)))
    max_mins = st.slider('+/- Vs. Position Avg', min_value=0.1, max_value=1.0, value=0.35, step=0.05)

data_date = lg_lookup[(lg_lookup.League==lg) & (lg_lookup.Season==season)].sub_title.values[0]
sub_title = f"{lg} {data_date}"
minimum_minutes = lg_lookup[(lg_lookup.League==lg) & (lg_lookup.Season==season)].minimum_minutes.values[0]
min_mins = -max_mins

clusters = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/misc-code/main/VAEP/{sub_title.replace(' ','%20')}%20VAEP%20Data.csv")
team_list = sorted(clusters.Team.unique().tolist())
min_mins_sample = lg_lookup[(lg_lookup.League==lg) & (lg_lookup.Season==season)].minimum_minutes.values[0]
max_mins_75_sample = int(clusters.Minutes.max()*.75)

with st.sidebar:
    team = st.selectbox('Team', team_list)
    minimum_minutes = st.slider('Minimum Minutes Played', min_value=min_mins_sample, max_value=max_mins_75_sample, value=min_mins_sample)

adj_clusters = clusters[clusters.Minutes>=minimum_minutes]
position_avg = adj_clusters.groupby('Group')['VAEP/90'].mean().rename('Group_Avg')
adj_clusters = adj_clusters.merge(position_avg, on='Group')
adj_clusters['VAEP/90 vs Group Avg'] = adj_clusters['VAEP/90'] - adj_clusters['Group_Avg']
adj_clusters = adj_clusters.sort_values(by=['VAEP/90 vs Group Avg'],ascending=False).reset_index(drop=True)
adj_clusters['P_goal_diff/90'] = adj_clusters['P_goal_diff']/(adj_clusters['Minutes']/90)
adj_clusters['P_concede_diff/90'] = adj_clusters['P_concede_diff']/(adj_clusters['Minutes']/90)
adj_clusters['VAEP/90 vs Group Avg Percentile'] = adj_clusters.groupby('Group')['VAEP/90 vs Group Avg'].transform(
    lambda x: stats.rankdata(x, method='average') / len(x)
)

#################################################################################################################
def VAEP_team_img(team,clusters,min_mins,max_mins,minimum_minutes,sub_title):    
    pitch = Pitch(pitch_type='opta', pitch_color='#fbf9f4', line_color='#4A2E19', line_zorder=2,half=False)
    fig, axs = pitch.grid(endnote_height=0.045, endnote_space=0, figheight=12,
                          title_height=0.045, title_space=0,
                          axis=False,
                          grid_height=0.86)
    fig.set_facecolor('#fbf9f4')
    
    my_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#ee5454','#fbf9f4','#4c94f6'])
    
    df = clusters[(clusters.Team==team) & (clusters.Minutes>=minimum_minutes)].sort_values(by=['Minutes'],ascending=False).reset_index(drop=True)
    
    
    norm = Normalize(vmin=min_mins, vmax=max_mins)
    
    hm = pitch.scatter(x=df.x, y=df.y, ax=axs['pitch'],
                  color=my_cmap(norm(df['VAEP/90 vs Group Avg'])), edgecolor='#4a2e19',
                  lw=.75,
                       # s=df['Minutes'],
                       s=600,
                       zorder=2, cmap=my_cmap,
                       vmin=min_mins, vmax=max_mins
                 )
    
    path_eff = [path_effects.Stroke(linewidth=.66, foreground='k'), path_effects.Normal()]
    
    texts = [axs['pitch'].text(x=df.x[i], y=df.y[i], s=f"{df.playerName[i]}\n{df.Group[i]}: {df.Desc[i]}",ha='center', va='center',size=15, color=colors.to_rgba(my_cmap(norm(df['VAEP/90 vs Group Avg']))[i])[:-1]+(0.5,), path_effects=path_eff) for i in range(len(df))]
    texts = adjust_text(texts, only_move=dict(text='y'), ax=axs['pitch'])
    
    
    axs['title'].text(.5, 1, f"{team} Avg Locations, Role Clusters, & Action Value", ha='center', va='center', size=25, color='#4a2e19')
    axs['title'].text(.5, .0, f"Players with at least {minimum_minutes} minutes | {sub_title}", ha='center', va='center', size=18, color='#4a2e19')
    
    axs['endnote'].text(0, 0.5, "Data via Opta", ha='left', va='center', size=17, color='#4a2e19')
    axs['endnote'].text(1, 0.5, "@BeGriffis", ha='right', va='center', size=17, color='#4a2e19')
    # axs['endnote'].text(0.5, 1, f"Role Clusters determined by an Algorithm trained on heatmaps of all UEFA T5 league players, over 2.9 million events.\nPlayers are assigned a cluster based on the areas they operate in. Clusters are subjectively named by me.\nThis aims to describe the areas of the pitch a player operates in, instead of 'playmaker', 'false 9', etc.\n\nAction Value is similar to StatsBomb's On-Ball Value (OBV) or American Soccer Analysis's Goals Added (g+).\nThis metric values each action in terms of the change in probability of scoring & conceding (proxied by xG instead of actual goals).\nThe model looks at the action type, where it took place, and context variables such as phase of play & other actions in the possession.\nIt excludes all penalties, totals each player's attacking & defensive value, calculates value/90', and then finally\ncompares this per 90 number to their position's average score. Their position is determined by the Clustering model.\nThe positions are shows under the player names, before the clustering role. So, a CM with a positive value may be better than the average CM",
    #                     ha='center', va='top', size=13, color='#4a2e19')
    # axs['endnote'].text(0.5, 1, ending_note,
    #                     ha='center', va='top', size=13, color='#4a2e19')
    
    ##############################
    axs['pitch'].text(105, 99.75, 'AV/90\nvs Pos. Avg', ha='center', va='bottom', size=15, color='#4a2e19', weight='bold')
    
    ###
    ticks = [min_mins, min_mins+((max_mins-min_mins)*(1/7)), min_mins+((max_mins-min_mins)*(2/7)), min_mins+((max_mins-min_mins)*(3/7)), min_mins+((max_mins-min_mins)*(4/7)), min_mins+((max_mins-min_mins)*(5/7)), min_mins+((max_mins-min_mins)*(6/7)), min_mins+((max_mins-min_mins)*(7/7))]
    ys = [1.833333333,15.5952381,29.35714286,43.11904762,56.88095238,70.64285714,84.4047619,98.16666667]
    xgs = [0,0.142857143,0.285714286,0.428571429,0.571428571,0.714285714,0.857142857,1]
    path_eff = [path_effects.Stroke(linewidth=.5, foreground='k'), path_effects.Normal()]
    
    for i in range(len(ys)):
        if xgs[i] < 1:
            pitch.arrows(101.5, ys[i]+2, 101.5, ys[i+1]-2, ax=axs['pitch'],color=my_cmap(xgs[i+1]))
        elif xgs[i] == 1:
            pitch.arrows(101.5, ys[i-1]+2, 101.5, ys[i]-2, ax=axs['pitch'],color=my_cmap(xgs[i]-.0001))
            
        pitch.scatter(101.5, ys[i],
                      # s=(xgs[i]*400)+30,
                      s=400,
                      c=xgs[i], cmap=my_cmap, vmin=0,vmax=1, ec='#4a2e19', zorder=2, ax=axs['pitch'])
    
        axs['pitch'].text(103, ys[i], round(ticks[i],2), color=my_cmap(norm(ticks[i])), path_effects=path_eff, size=14, ha='left', va='center')

    return fig

team_tab, player_tab, all_player_tab = st.tabs([f'{team} Players', 'Player Research', 'All Players'])

with team_tab:
    vaep_img = VAEP_team_img(team,adj_clusters,min_mins,max_mins,minimum_minutes,sub_title)
    vaep_img

    team_vaep_players = adj_clusters[adj_clusters.Team==team][['playerName','Team','Minutes','Desc','VAEP/90','VAEP/90 vs Group Avg','P_goal_diff/90','P_concede_diff/90','VAEP/90 vs Group Avg Percentile']].rename(columns={
        'playerName':'Player','Desc':'Role','P_goal_diff/90':'Attack Value (+)/90','P_concede_diff/90':'Defense Value (-)/90','VAEP_value':'VAEP'
    })
    st.dataframe(team_vaep_players.style.apply(style_rows_group_avg, axis=1))

with player_tab:
    foc_pos = st.selectbox('Position', ('ST','Winger','AM','CM','DM','FB','CB','GK'))
    player_vaep_df = adj_clusters[adj_clusters.Group==foc_pos][['playerName','Team','Minutes','Desc','VAEP/90','VAEP/90 vs Group Avg','P_goal_diff/90','P_concede_diff/90']].rename(columns={
        'playerName':'Player','Desc':'Role','P_goal_diff/90':'Attack Value (+)/90','P_concede_diff/90':'Defense Value (-)/90','VAEP_value':'VAEP'
    })
    player_vaep_df['VAEP/90 Pctile'] = rank_column(player_vaep_df, 'VAEP/90')
    st.dataframe(player_vaep_df.style.apply(style_rows, axis=1))

with all_player_tab:
    all_player_vaep_df = adj_clusters[['playerName','Team','Minutes','Group','Desc','VAEP/90','VAEP/90 vs Group Avg','P_goal_diff/90','P_concede_diff/90','VAEP/90 vs Group Avg Percentile']].rename(columns={
        'playerName':'Player','Desc':'Role','P_goal_diff/90':'Attack Value (+)/90','P_concede_diff/90':'Defense Value (-)/90','VAEP_value':'VAEP'
    })
    st.dataframe(all_player_vaep_df.style.apply(style_rows_group_avg, axis=1))
