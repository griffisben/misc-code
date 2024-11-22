import pandas as pd
# import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib
from matplotlib.colors import to_rgba
from matplotlib import colors
from matplotlib.colors import Normalize
import matplotlib.patheffects as path_effects
from adjustText import adjust_text
plt.rcParams['figure.dpi'] = 300


lg_lookup = pd.read_csv("https://raw.githubusercontent.com/griffisben/misc-code/main/VAEP/VAEP_app_leagues.csv")
league_list = lg_lookup.League.unique().tolist()

with st.sidebar:
    lg = st.selectbox('League', league_list)
    season = st.selectbox('Season', (sorted(lg_lookup[lg_lookup.League == lg].Season.unique().tolist(),reverse=True)))
    max_mins = st.slider('+/- Vs. Position Avg', min_value=0.1, max_value=1.0, value=0.4, step='float')


lg = "Danish 1. Division"
season = "24-25"

data_date = lg_lookup[(lg_lookup.League==lg) & (lg_lookup.Season==season)].sub_title.values[0]
sub_title = f"{lg} {data_date}"
minimum_minutes = lg_lookup[(lg_lookup.League==lg) & (lg_lookup.Season==season)].minimum_minutes.values[0]
min_mins = -max_mins

clusters = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/misc-code/main/VAEP/{sub_title.replace(' ','%20')}%20VAEP%20Data.csv")
team_list = sorted(clusters.Team.unique().tolist())
with st.sidebar:
    team = st.selectbox('Team', team_list)

#################################################################################################################

ending_note = f"""Role Clusters determined by an Algorithm trained on heatmaps of all UEFA T5 league players, over 2.9 million events.
Players are assigned a cluster based on the areas they operate in. Clusters are subjectively named by me.
This aims to describe the areas of the pitch a player operates in, instead of 'playmaker', 'false 9', etc.

Action Value is similar to StatsBomb's On-Ball Value (OBV) or American Soccer Analysis's Goals Added (g+).
This metric values each action in terms of the change in probability of scoring & conceding (proxied by xG instead of actual goals).
The model looks at the action type, where it took place, and context variables such as phase of play & other actions in the possession.
It excludes all penalties, totals each player's attacking & defensive value, calculates value/90', and then finally
compares this per 90 number to their position's average score. Their position is determined by the Clustering model.
The positions are shows under the player names, before the clustering role. So, a CM with a positive value may be better than the average CM"""


pitch = Pitch(pitch_type='opta', pitch_color='#fbf9f4', line_color='#4A2E19', line_zorder=2,half=False)
fig, axs = pitch.grid(endnote_height=0.045, endnote_space=0, figheight=12,
                      title_height=0.045, title_space=0,
                      axis=False,
                      grid_height=0.86)
fig.set_facecolor('#fbf9f4')

my_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#ee5454','#fbf9f4','#4c94f6'])

df = clusters[clusters.Team==team].sort_values(by=['Minutes'],ascending=False).reset_index(drop=True)


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
axs['endnote'].text(0.5, 1, ending_note,
                    ha='center', va='top', size=13, color='#4a2e19')

##############################
# cbar_bottom = axs['pitch'].get_position().y0+.045
# cbar_left = axs['pitch'].get_position().x1 + 0.01
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

st.image(fig)
