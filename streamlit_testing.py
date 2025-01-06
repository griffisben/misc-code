import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Historic average points needed for positions
avg_points_premier_league = [
    87.8, 79, 72, 68, 65, 62, 59, 56, 54, 52,
    50, 48, 46, 44, 42, 40, 38, 36, 34, 32
]

avg_points_league_one = [
    91, 88, 83, 81, 78, 76, 73, 70, 67, 65,
    63, 61, 59, 57, 55, 53, 51, 49, 47, 45,
    43, 41, 39, 37
]

# Streamlit app
st.title("Expected Points and Position Calculator")
st.write("Calculate expected points and table position based on average xG and xGA.")

# Input fields
avg_xg = st.number_input("Average xG per game", min_value=0.0, value=1.5, step=0.1)
avg_xga = st.number_input("Average xGA per game", min_value=0.0, value=1.2, step=0.1)
games_in_season = st.number_input("Number of games in the season", min_value=1, value=38, step=1)

# Dropdown to select league
league = st.selectbox("Select League", ["Premier League", "League One"])

# Constants
c = 1.535706245

# Calculate expected points
def calculate_expected_points(xg, xga, games, c):
    win_prob = (xg ** c) / ((xg ** c) + (xga ** c))
    expected_points = win_prob * 3 * games
    return expected_points

expected_points = calculate_expected_points(avg_xg, avg_xga, games_in_season, c)
st.write(f"### Expected Points for the Season: {expected_points:.2f}")

# Determine expected position based on selected league
if league == "Premier League":
    avg_points = avg_points_premier_league
else:
    avg_points = avg_points_league_one

expected_position = sum(expected_points < p for p in avg_points) + 1
st.write(f"### Expected Table Position: {expected_position}")

# Sensitivity analysis
sensitivity_xg = calculate_expected_points(avg_xg + 0.5, avg_xga, games_in_season, c) - expected_points
sensitivity_xga = expected_points - calculate_expected_points(avg_xg, avg_xga + 0.5, games_in_season, c)

with st.expander("Sensitivity Analysis"):
    st.markdown(f"If **Average xG** increases by 0.5, expected points increase by **{sensitivity_xg:.2f}** points.")
    st.markdown(f"If **Average xGA** decreases by 0.5, expected points increase by **{sensitivity_xga:.2f}** points.")

# Plotting
xg_values = np.linspace(0.5, 3.0, 50)
xga_values = np.linspace(0.5, 3.0, 50)
points_grid = np.array([calculate_expected_points(xg, xga, games_in_season, c) for xg, xga in zip(xg_values, xga_values)])

fig, ax = plt.subplots()
ax.plot(xg_values, points_grid, label="Expected Points", color="blue")
ax.axhline(y=expected_points, color='gray', linestyle='--', label=f"Your Expected Points ({expected_points:.2f})")
ax.set_xlabel("Average xG per game")
ax.set_ylabel("Expected Points")
ax.legend()

st.pyplot(fig)
