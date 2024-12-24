import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def pythagorean_expectation(xg, xga, c):
    # Calculate the win probability
    win_prob = (xg ** c) / (xg ** c + xga ** c)
    return win_prob

def sensitivity_analysis(xg, xga, c):
    # Partial derivative with respect to xG
    d_win_dxg = (c * (xg ** (c - 1)) * (xga ** c)) / ((xg ** c + xga ** c) ** 2)
    
    # Partial derivative with respect to xGA
    d_win_dxga = -(c * (xga ** (c - 1)) * (xg ** c)) / ((xg ** c + xga ** c) ** 2)
    
    return d_win_dxg, abs(d_win_dxga)

# Streamlit app
st.title("Pythagorean Expectation for Soccer")

# User inputs
st.sidebar.header("Inputs")
xg = st.sidebar.number_input("Expected Goals For (xG)", min_value=0.0, value=1.5, step=0.1)
xga = st.sidebar.number_input("Expected Goals Against (xGA)", min_value=0.0, value=1.2, step=0.1)
c = st.sidebar.slider("Constant (c)", min_value=1.0, max_value=2.0, value=1.5357, step=0.01)

# Calculations
win_prob = pythagorean_expectation(xg, xga, c)
d_win_dxg, d_win_dxga = sensitivity_analysis(xg, xga, c)

# Display results
st.subheader("Results")
st.write(f"**Win Probability:** {win_prob:.4f}")
st.write(f"**Sensitivity to xG:** {d_win_dxg:.4f}")
st.write(f"**Sensitivity to xGA:** {d_win_dxga:.4f}")

if d_win_dxg > d_win_dxga:
    st.write("💡 Increasing **xG** has a larger impact on win probability.")
else:
    st.write("💡 Decreasing **xGA** has a larger impact on win probability.")

# Visualization
st.subheader("Visualization of Impact")
st.write("The graph below shows how varying xG and xGA affects expected points based on the provided constant c.")

# Generate data for visualization
xg_values = np.linspace(0.5, 3.0, 50)  # Range for xG
xga_values = np.linspace(0.5, 3.0, 50)  # Range for xGA

# Calculate expected points for each combination of xG and xGA
expected_points = np.zeros((len(xg_values), len(xga_values)))
for i, xg_val in enumerate(xg_values):
    for j, xga_val in enumerate(xga_values):
        win_prob = pythagorean_expectation(xg_val, xga_val, c)
        expected_points[i, j] = 3 * win_prob

# Plotting the graph using Matplotlib
fig, ax = plt.subplots(figsize=(8, 6))
X, Y = np.meshgrid(xg_values, xga_values)
cp = ax.contourf(X, Y, expected_points.T, cmap="viridis", levels=20)
fig.colorbar(cp, label="Expected Points")
ax.set_title("Impact of xG and xGA on Expected Points")
ax.set_xlabel("Expected Goals For (xG)")
ax.set_ylabel("Expected Goals Against (xGA)")
ax.axvline(x=xg, color="red", linestyle="--", label=f"xG = {round(xg,2)}")
ax.axhline(y=xga, color="blue", linestyle="--", label=f"xGA = {round(xga,2)}")
ax.legend()

# Display the plot in Streamlit
st.pyplot(fig)
