import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Fixed constant
C = 1.535706245

# Historical average points by position (20-team Premier League)
avg_points_by_position = [
    87.8, 79, 72, 68, 65, 62, 59, 56, 54, 52,
    50, 48, 46, 44, 42, 40, 38, 36, 34, 32
]

def pythagorean_expectation(xg, xga, c):
    """Calculate the win probability using the Pythagorean expectation formula."""
    win_prob = (xg ** c) / (xg ** c + xga ** c)
    return win_prob

def sensitivity_analysis(xg, xga, c, games):
    """Calculate the sensitivity of expected points to changes in xG and xGA."""
    d_win_dxg = (c * (xg ** (c - 1)) * (xga ** c)) / ((xg ** c + xga ** c) ** 2)
    d_win_dxga = -(c * (xga ** (c - 1)) * (xg ** c)) / ((xg ** c + xga ** c) ** 2)
    
    # Sensitivity with 0.5 unit change instead of 1.0
    sensitivity_xg = 0.5 * d_win_dxg * games  # Adjusted for 0.5 unit change in xG
    sensitivity_xga = -0.5 * d_win_dxga * games  # Negative because reducing xGA increases points
    return sensitivity_xg, sensitivity_xga

def get_expected_position(points):
    """Get the expected league position based on historical averages."""
    for i, avg_points in enumerate(avg_points_by_position, start=1):
        if points >= avg_points:
            return i
    return 20  # Last position if points are very low

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
expected_position = get_expected_position(expected_points_season)
sensitivity_xg, sensitivity_xga = sensitivity_analysis(avg_xg, avg_xga, C, games)

# Display results
st.subheader("Results")
st.write(f"**Expected Points Per Game:** {expected_points_per_game:.2f}")
st.write(f"**Expected Points for the Season:** {expected_points_season:.2f}")
st.write(f"**Expected Table Position:** {expected_position}")
st.write(f"**Sensitivity to xG:** {sensitivity_xg:.2f} expected points per season (for a 0.5 unit change)")
st.write(f"**Sensitivity to xGA:** {sensitivity_xga:.2f} expected points per season (for a 0.5 unit change)")

# Highlight which adjustment is better
if sensitivity_xg > sensitivity_xga:
    st.write("💡 Increasing **xG** would lead to more expected points per season.")
else:
    st.write("💡 Decreasing **xGA** would lead to more expected points per season.")

# Add an intuitive explanation for sensitivity
st.markdown("""
### What Does Sensitivity to xG and xGA Mean?

- **Sensitivity to xG:** This value indicates how much **expected points** would change for every **0.5-unit increase in xG per game**, while keeping **xGA constant**. 
- For example, if the sensitivity to xG is 23.32, this means that for every **0.5-unit increase in xG per game**, the team would expect an additional **23.32 points** over the course of the season. 
- A higher sensitivity to xG means **improving attacking performance** will have a **large impact** on expected points.

- **Sensitivity to xGA:** This value shows how much **expected points** would change for every **0.5-unit decrease in xGA per game**, while keeping **xG constant**. 
- For example, if the sensitivity to xGA is -18.75, this means that for every **0.5-unit decrease in xGA per game**, the team would expect an additional **18.75 points** over the course of the season. 
- A higher sensitivity to xGA means **improving defensive performance** (lowering xGA) will have a **large impact** on expected points.

### Which Should You Focus On?
- If the sensitivity to **xG** is higher, then improving your team's attacking performance is the best way to increase expected points.
- If the sensitivity to **xGA** is higher, then focusing on improving your defense will yield a better return in terms of points.
""")

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
fig, ax = plt.subplots(figsize=(10, 6))
X, Y = np.meshgrid(xg_values, xga_values)
cp = ax.contourf(X, Y, expected_points.T, cmap="coolwarm", levels=20)
colorbar = fig.colorbar(cp, label="Expected Points for the Season")
ax.set_title("Impact of Average xG and xGA on Expected Points for a Season")
ax.set_xlabel("Average xG per Game")
ax.set_ylabel("Average xGA per Game")

# Highlight user-provided values with rounded xG and xGA
rounded_xg = round(avg_xg, 2)
rounded_xga = round(avg_xga, 2)
ax.axvline(x=avg_xg, color="#4a2e19", linestyle="--", label=f"Avg xG = {rounded_xg}")
ax.axhline(y=avg_xga, color="#4a2e19", linestyle="--", label=f"Avg xGA = {rounded_xga}")

# Add the legend
ax.legend()

# Adjust layout to reduce white space above the graph
plt.tight_layout()

# Display the plot in Streamlit
st.pyplot(fig)
