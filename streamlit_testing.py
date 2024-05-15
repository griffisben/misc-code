import streamlit as st

tab1, tab2 = st.tabs(['Tab 1', 'Tab 2'])

with tab1:
    with st.sidebar:
        one_team_choice = st.selectbox('One Team Depth Chart?', (['No','Yes']))

with tab2:
    with st.sidebar:
        ages = st.slider('Age Range', 0, 45, (0, 45))
