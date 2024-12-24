import streamlit as st

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
