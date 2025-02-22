import streamlit as st

st.set_page_config(
    page_title="KIF Analysis Apps",
    page_icon="⚽",
)

st.write("# Kolding IF Data Apps")

st.sidebar.success("Click on an app above ☝️")

st.markdown(
    """
    ### 🌍 KIF Scouting
    An all-in-one scouting tool to get player radars, search for players meeting data criteria, analyze similar players, plot scatter plots, rank players in pre-made or custom position-roles, and more
    ### 🧑‍💻 Opta Event Chalkboard
    Visualize Opta events for a team in a single game, a player in a single game, or a player for a full season
    ### 📊 Team Playstyle Profiles
    Analyze teams' playstyles in 9 different metrics for a single season, see their development across multiple seasons, see what other teams had the most similar style, and use filters to find teams meeting custom criteria
"""
)
