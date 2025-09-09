import streamlit as st

st.set_page_config(
    page_title="Best XI",
    page_icon="⚽",
)

st.write("# Best XI Scouting")

st.sidebar.success("Choose the Men's or Women's app above ☝️")

st.markdown(
    """
    ## Best XI Men's
    An all-in-one scouting tool to find & analyze players from around the world. Rank players in specific role-positions, get player radars, search for players meeting data criteria, and plot scatter plots.
    ## Best XI Women's
    All of the features from the men's app, plus the ability to generate player similarities and create your own custom roles!
    #### All data from Wyscout, created by Ben Griffis
"""
)
