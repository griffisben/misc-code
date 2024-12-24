import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Fixed constant
C = 1.535706245

def pythagorean_expectation(xg, xga, c):
    """Calculate the win probability using the Pythagorean expectation formula."""
    win_prob = (xg ** c) / (xg ** c + xga ** c)
    return win_prob

# Streamlit app
st.title("Season-Based Pythagorean Expectation for Soccer")

# Display the formula
st.latex(r"""
\text{Win Probability} = \frac{\text{xG}^c}{\text{xG}^c + \text{xGA}^c}, \quad c = 1.535706245
""")

# User inputs
st.sidebar.header("Inputs")
avg_xg = st.sidebar.number_input("Average xG per Game", min_value=0.0, value=1.5, step=0.1)
avg_xga = st.sidebar.number_input("Average xGA per Game", min_value=0.0, value=1.2, step=0.1)
games = st.sidebar.number_input("Number of Games in Season", min_value=1, value=38, step=1)

# Calculations
win_prob = pythagorean_expectation(avg_xg, avg_xga, C)
expected_points_per_game = 3 * win_prob
expected_points_season = expected_points_per_game * games

# Display results
st.subheader("Results")
st.write(f"**Expected Points Per Game:** {expected_points_per_game:.2f}")
st.write(f"**Expected Points for the Season:** {expected_points_season:.2f}")

# Visualization
st.subheader("Visualization of Impact")
st.write("The graph below shows how varying Average xG and xGA affects expected points for a season.")

# Generate data for visualization
xg_values = np.linspace(0.5, 3.0, 50)  # Range for average xG
xga_values = np.linspace(0.5, 3.0, 50)  # Range for average xGA

# Calculate expected points for each combination of xG and xGA
expected_points = np.zeros((len(xg_values), len(xga_values)))
for i, xg_val in enumerate(xg_values):
    for j, xga_val in enumerate(xga_values):
        win_prob = pythagorean_expectation(xg_val, xga_val, C)
        expected_points[i, j] = 3 * win_prob * games

# Plotting the graph using Matplotlib
fig, ax = plt.subplots(figsize=(8, 6))
X, Y = np.meshgrid(xg_values, xga_values)
cp = ax.contourf(X, Y, expected_points.T, cmap="viridis", levels=20)
fig.colorbar(cp, label="Expected Points for the Season")
ax.set_title("Impact of Average xG and xGA on Expected Points for a Season")
ax.set_xlabel("Average xG per Game")
ax.set_ylabel("Average xGA per Game")

# Highlight user-provided values with rounded xG and xGA
rounded_xg = round(avg_xg, 2)
rounded_xga = round(avg_xga, 2)
ax.axvline(x=avg_xg, color="red", linestyle="--", label=f"Avg xG = {rounded_xg}")
ax.axhline(y=avg_xga, color="blue", linestyle="--", label=f"Avg xGA = {rounded_xga}")
ax.legend()

# Display the plot in Streamlit
st.pyplot(fig)
