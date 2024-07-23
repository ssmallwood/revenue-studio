import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_projections(years, scenario, products, staffing, partnerships, other_costs):
    data = []
    for year in range(years):
        year_data = {"Year": 2025 + year}
        
        # Apply scenario adjustments
        scenario_multiplier = {"Optimistic": 1.2, "Most Likely": 1.0, "Pessimistic": 0.8}[scenario]
        
        # Calculate revenue for each product
        for product in products:
            revenue = product['initial_revenue'] * (1 + product['growth_rate'] * scenario_multiplier / 100) ** year
            year_data[f"{product['name']} Revenue"] = revenue
        
        # Calculate staffing costs
        staffing_cost = staffing['num_employees'] * staffing['avg_salary'] * (1 + staffing['cost_growth'] / 100) ** year
        year_data["Staffing Costs"] = staffing_cost
        
        # Calculate other costs
        year_data["Other Costs"] = other_costs['initial'] * (1 + other_costs['growth_rate'] / 100) ** year
        
        # Calculate total revenue and costs
        total_revenue = sum([year_data[f"{p['name']} Revenue"] for p in products])
        total_costs = staffing_cost + year_data["Other Costs"]
        year_data["Total Revenue"] = total_revenue
        year_data["Total Costs"] = total_costs
        
        # Calculate margin and subsidy
        margin = total_revenue - total_costs
        subsidy = max(0, margin * 0.5)  # Assuming 50% of margin goes to subsidy
        year_data["Margin"] = margin
        year_data["Total Subsidy"] = subsidy
        
        # Calculate average subsidy per partner
        year_data["Avg Subsidy per Partner"] = subsidy / partnerships['num_partners'] if partnerships['num_partners'] > 0 else 0
        
        data.append(year_data)
    
    return pd.DataFrame(data)

st.set_page_config(page_title="Advanced Earned Revenue Product Studio Projections", layout="wide")

st.title("Advanced Earned Revenue Product Studio Projections")
st.write("Visualize revenue, costs, and impact projections over five years (2025-2030)")

# Sidebar for inputs
st.sidebar.header("Adjust Parameters")

# Scenario selection
scenario = st.sidebar.selectbox("Choose Scenario", ["Optimistic", "Most Likely", "Pessimistic"])

# Product Mix
st.sidebar.subheader("Product Mix")
products = [
    {"name": "B2B Research", "initial_revenue": st.sidebar.number_input("Initial B2B Research Revenue", value=200000, step=10000), 
     "growth_rate": st.sidebar.slider("B2B Research Growth Rate (%)", 0, 100, 20)},
    {"name": "Events", "initial_revenue": st.sidebar.number_input("Initial Events Revenue", value=150000, step=10000), 
     "growth_rate": st.sidebar.slider("Events Growth Rate (%)", 0, 100, 15)},
    {"name": "B2C Products", "initial_revenue": st.sidebar.number_input("Initial B2C Products Revenue", value=100000, step=10000), 
     "growth_rate": st.sidebar.slider("B2C Products Growth Rate (%)", 0, 100, 25)}
]

# Staffing Model
st.sidebar.subheader("Staffing")
staffing = {
    "num_employees": st.sidebar.slider("Number of Employees", 1, 20, 5),
    "avg_salary": st.sidebar.number_input("Average Salary", value=80000, step=5000),
    "cost_growth": st.sidebar.slider("Annual Cost Growth (%)", 0, 10, 3)
}

# Other Costs
st.sidebar.subheader("Other Costs")
other_costs = {
    "initial": st.sidebar.number_input("Initial Other Costs", value=100000, step=10000),
    "growth_rate": st.sidebar.slider("Other Costs Growth Rate (%)", 0, 20, 5)
}

# Partnerships
st.sidebar.subheader("Partnerships")
partnerships = {
    "num_partners": st.sidebar.slider("Number of Partners", 1, 20, 5)
}

# Calculate projections
df = calculate_projections(6, scenario, products, staffing, partnerships, other_costs)

# Visualization
fig = make_subplots(rows=2, cols=2, subplot_titles=("Revenue Breakdown", "Costs vs Revenue", "Margin and Subsidy", "Avg Subsidy per Partner"))

# Revenue Breakdown
for product in products:
    fig.add_trace(go.Scatter(x=df["Year"], y=df[f"{product['name']} Revenue"], name=f"{product['name']} Revenue", stackgroup='revenue'), row=1, col=1)

# Costs vs Revenue
fig.add_trace(go.Scatter(x=df["Year"], y=df["Total Revenue"], name="Total Revenue"), row=1, col=2)
fig.add_trace(go.Scatter(x=df["Year"], y=df["Total Costs"], name="Total Costs"), row=1, col=2)

# Margin and Subsidy
fig.add_trace(go.Scatter(x=df["Year"], y=df["Margin"], name="Margin"), row=2, col=1)
fig.add_trace(go.Scatter(x=df["Year"], y=df["Total Subsidy"], name="Total Subsidy"), row=2, col=1)

# Avg Subsidy per Partner
fig.add_trace(go.Scatter(x=df["Year"], y=df["Avg Subsidy per Partner"], name="Avg Subsidy per Partner"), row=2, col=2)

fig.update_layout(height=800, title_text=f"Earned Revenue Product Studio Projections ({scenario} Scenario)")
fig.update_xaxes(title_text="Year")
fig.update_yaxes(title_text="Amount ($)")

st.plotly_chart(fig, use_container_width=True)

# Key Metrics
st.subheader("Key Metrics for 2030")
final_year = df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${final_year['Total Revenue']:,.0f}")
col2.metric("Total Costs", f"${final_year['Total Costs']:,.0f}")
col3.metric("Total Subsidy", f"${final_year['Total Subsidy']:,.0f}")
col4.metric("Avg Subsidy per Partner", f"${final_year['Avg Subsidy per Partner']:,.0f}")

# Break-even Analysis
break_even_year = df[df["Total Revenue"] >= df["Total Costs"]]["Year"].min()
st.subheader("Break-even Analysis")
st.write(f"Projected break-even year: {break_even_year}")

# Display the data table
st.subheader("Projection Data")
st.dataframe(df.style.format({col: "${:,.0f}" for col in df.columns if col != "Year"}))

st.info("Note: This model assumes that 50% of the margin goes towards the subsidy for partner newsrooms. The scenario selection affects the growth rates of revenue streams. Adjust the parameters to see how different scenarios affect the projections.")