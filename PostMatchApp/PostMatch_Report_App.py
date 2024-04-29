import pandas as pd
import streamlit as st
from PIL import Image
import warnings
warnings.filterwarnings('ignore')
@st.cache_data(ttl=6*60*60)
def read_csv(link):
    return pd.read_csv(link)

df = read_csv('https://raw.githubusercontent.com/griffisben/misc-code/main/PostMatchApp/USL%20Championship%20Full%20Match%20List.csv')
df['Match_Name'] = df['Match'] + ' ' + df['Date']
team_list = sorted(list(set(df.Home.unique().tolist() + df.Away.unique().tolist())))


st.title('Post-Match Reports, 2024 USL Championship')

with st.sidebar:
    # st.header('What Team Do You Want Reports For?')
    team = st.selectbox('What Team Do You Want Reports For?', team_list, index=team_list.index('Loudoun United'))

    # st.header('Specific Match or Most Recent Matches?')
    specific = st.selectbox('Specific Match or Most Recent Matches?', ('Specific Match','Recent Matches'))
    if specific == 'Specific Match':
        match_list = df[(df.Home == team) | (df.Away == team)].copy()
        match_choice = st.selectbox('Match', match_list.Match_Name.tolist())
        render_matches = [match_choice]
    if specific == 'Recent Matches':
        match_list = df[(df.Home == team) | (df.Away == team)].copy()
        num_matches = st.slider('Number of Recent Matches', min_value=1, max_value=5, value=3)
        render_matches = match_list.head(num_matches).Match.tolist()

for i in range(len(render_matches)):
    game_image = Image.open(f"/PostMatchApp/USLC_2024/{render_matches[i]}.png")
    st.image(game_image)



