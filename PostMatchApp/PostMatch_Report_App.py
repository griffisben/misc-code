import pandas as pd
import streamlit as st
from PIL import Image
import requests
import io
import altair as alt

#########################
def ben_theme():
    return {
        'config': {
            'background': '#fbf9f4',
            # 'text': '#4a2e19',
            'mark': {
                'color': '#4c94f6',
            },
            'axis': {
                'titleColor': '#4a2e19',
                'labelColor': '#4a2e19',
            },
            'text': {
                'fill': '#4a2e19'
            },
            'title': {
                'color': '#4a2e19',
                'subtitleColor': '#4a2e19'
            }
        }
    }

# register the custom theme under a chosen name
alt.themes.register('ben_theme', ben_theme)

# enable the newly registered theme
alt.themes.enable('ben_theme')
################################

lg_lookup = pd.read_csv("https://raw.githubusercontent.com/griffisben/misc-code/main/PostMatchApp/PostMatchLeagues.csv")
league_list = lg_lookup.League.tolist()

with st.sidebar:
    league = st.selectbox('What League Do You Want Reports For?', league_list)
    update_date = lg_lookup[lg_lookup.League==league].Update.values[0]
    
st.title(f"{league} Post-Match Reports")
st.subheader(f"Last Updated: {update_date}\n")
st.subheader('All data via Opta')

df = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/misc-code/main/PostMatchApp/League_Files/{league.replace(' ','%20')}%20Full%20Match%20List.csv")
df['Match_Name'] = df['Match'] + ' ' + df['Date']

with st.sidebar:
    team_list = sorted(list(set(df.Home.unique().tolist() + df.Away.unique().tolist())))
    team = st.selectbox('What team do you want reports & data for?', team_list)

    specific = st.selectbox('Specific Match or Most Recent Matches?', ('Specific Match','Recent Matches'))
    if specific == 'Specific Match':
        match_list = df[(df.Home == team) | (df.Away == team)].copy()
        match_choice = st.selectbox('Match', match_list.Match_Name.tolist())
        render_matches = [match_choice]
    if specific == 'Recent Matches':
        match_list = df[(df.Home == team) | (df.Away == team)].copy()
        num_matches = st.slider('Number of Recent Matches', min_value=1, max_value=5, value=3)
        render_matches = match_list.head(num_matches).Match_Name.tolist()

report_tab, data_tab, graph_tab = st.tabs(['Match Report', 'Data by Match - Table', 'Data by Match - Graph'])

for i in range(len(render_matches)):
    match_string = render_matches[i].replace(' ','%20')
    url = f"https://raw.githubusercontent.com/griffisben/misc-code/main/PostMatchApp/Image_Files/{league.replace(' ','%20')}/{match_string}.png"
    response = requests.get(url)
    game_image = Image.open(io.BytesIO(response.content))
    report_tab.image(game_image)

team_data = pd.read_csv(f"https://raw.githubusercontent.com/griffisben/misc-code/main/PostMatchApp/Stat_Files/{league.replace(' ','%20')}.csv")
league_data = team_data.copy().reset_index(drop=True)
team_data = team_data[team_data.Team==team].reset_index(drop=True)
team_data['Shots per 1.0 xT'] = team_data['Shots per 1.0 xT'].astype(float)
team_data.rename(columns={'Shots per 1.0 xT':'Shots per 1 xT'},inplace=True)

league_data['Shots per 1.0 xT'] = league_data['Shots per 1.0 xT'].astype(float)
league_data.rename(columns={'Shots per 1.0 xT':'Shots per 1 xT'},inplace=True)


team_data['xG per 1 xT'] = team_data['xG']/team_data['xT']
league_data['xG per 1 xT'] = league_data['xG']/league_data['xT']

team_data['xGA per 1 xT Against'] = team_data['xGA']/team_data['xT Against']
league_data['xGA per 1 xT Against'] = league_data['xGA']/team_data['xT Against']

available_vars = ['Possession','xG','xGA','xGD','Goals','Goals Conceded','GD','GD-xGD','Shots','Shots Faced','Field Tilt','Passes in Opposition Half','Passes into Box','xT','xT Against','Shots per 1 xT','xG per 1 xT','xGA per 1 xT Against','PPDA','High Recoveries','Crosses','Corners','Fouls']

team_data[available_vars] = team_data[available_vars].astype(float)
league_data[available_vars] = league_data[available_vars].astype(float)


data_tab.write(team_data)
with graph_tab:
    var = st.selectbox('Metric to Plot', available_vars)
    
    lg_avg_var = league_data[var].mean()
    team_avg_var = team_data[var].mean()
    
    c = (
       alt.Chart(team_data[::-1], title=alt.Title(
       f"{team} {var}, {league}",
       subtitle=[f"Data via Opta | Data as of {update_date}"]
   ))
       .mark_line(point=True)
       .encode(x=alt.X('Date', sort=None), y=var, tooltip=['Match','Date',var,'Possession','xGD','GD'])
    )

    lg_avg_line = alt.Chart(pd.DataFrame({'y': [lg_avg_var]})).mark_rule().encode(y='y')
    
    lg_avg_label = lg_avg_line.mark_text(
        x="width",
        dx=-2,
        align="right",
        baseline="bottom",
        text="League Avg"
    )

    team_avg_line = alt.Chart(pd.DataFrame({'y': [team_avg_var]})).mark_rule(color='red').encode(y='y')
    
    team_avg_label = team_avg_line.mark_text(
        x="width",
        dx=-2,
        align="right",
        baseline="bottom",
        text="Team Avg",
        color='red'
    )


    chart = (c + lg_avg_line + lg_avg_label + team_avg_line + team_avg_label)
    st.altair_chart(chart, use_container_width=True)
