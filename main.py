import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LinearRegression

# Set page configuration
st.set_page_config(page_title="CO2 Trading Exchange", layout="wide")

# Registration Page
def registration_page():
    st.markdown("<h2 style='color:#00ff00;'>User Registration</h2>", unsafe_allow_html=True)
    country = st.text_input("Country")
    company_name = st.text_input("Company Name")
    industry = st.text_input("Industry")
    carbon_credits = st.number_input("Number of Carbon Credits", min_value=1, max_value=100000, value=100)
    
    if st.button("Register"):
        if country and company_name and industry:
            st.session_state['registered'] = True
            st.success("Registration successful! You can now access the trading platform.")
        else:
            st.error("Please fill in all the required fields.")

# Dashboard Page
def dashboard_page():
    # Simulate new prices and update the price data
    st.session_state['prices'] = simulate_new_price(st.session_state['prices'])

    # Calculate Heikin-Ashi values
    ha_prices = calculate_heikin_ashi(st.session_state['prices'])

    # CSS to make the page elements match Bybit-like spacing and font size
    st.markdown("""
        <style>
        body {
            background-color: #121212;
            color: white;
        }
        .stButton>button {
            background-color: #00ff00;
            color: black;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown p {
            color: white;
        }
        .main .block-container {
            padding-top: 20px;
            padding-bottom: 0px;
            padding-left: 30px;
            padding-right: 30px;
        }
        .stTextInput input, .stNumberInput input {
            background-color: #333;
            color: white;
        }
        .stRadio label {
            font-size: 16px;
        }
        .block-container {
            padding: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

    # Layout Setup
    col1, col2, col3 = st.columns([2.5, 1, 1])

    # Column 1: Heikin-Ashi Price Chart (Using Plotly)
    with col1:
        st.markdown("<h2 style='color:#00ff00;'>Heikin-Ashi CO2 Candlestick Chart</h2>", unsafe_allow_html=True)
        
        # Create a Plotly candlestick chart with increased size
        fig = go.Figure(data=[go.Candlestick(
            x=ha_prices.index,
            open=ha_prices['HA_Open'],
            high=ha_prices['HA_High'],
            low=ha_prices['HA_Low'],
            close=ha_prices['HA_Close'],
            increasing_line_color='green',
            decreasing_line_color='red'
        )])
        
        # Set chart title and axis labels
        fig.update_layout(
            title="Heikin-Ashi CO2 Prices",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            height=500,  # Increase the height of the chart
            margin=dict(l=10, r=10, t=50, b=50)  # Reduce margins for more compact view
        )
        
        # Display the Plotly chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

        # Positions & Order History at the bottom of the page
        st.markdown("<h3 style='color:#00ff00;'>Positions & Order History</h3>", unsafe_allow_html=True)
        positions = pd.DataFrame({
            "Contract": ["CO2-DEC24"],
            "Quantity": [10],
            "Entry Price": [19.00],
            "Mark Price": [ha_prices['HA_Close'].iloc[-1]],
            "P&L": [f"${round((ha_prices['HA_Close'].iloc[-1] - 19.00) * 10, 2)}"]
        })
        st.table(positions)

    # Column 2: Order Book
    with col2:
        st.markdown("<h3 style='color:#00ff00;'>Order Book</h3>", unsafe_allow_html=True)
        
        buy_orders = pd.DataFrame({
            "Price (USD)": sorted([random.uniform(19, 20) for _ in range(5)], reverse=True),
            "Amount (tons)": [random.randint(10, 100) for _ in range(5)]
        })
        sell_orders = pd.DataFrame({
            "Price (USD)": sorted([random.uniform(20.5, 22) for _ in range(5)]),
            "Amount (tons)": [random.randint(10, 100) for _ in range(5)]
        })
        
        st.markdown("#### Buy Orders")
        st.table(buy_orders)
        
        st.markdown("#### Sell Orders")
        st.table(sell_orders)

    # Column 3: Recent Trades & Order Placement
    with col3:
        st.markdown("<h3 style='color:#00ff00;'>Recent Trades</h3>", unsafe_allow_html=True)
        
        recent_trades = pd.DataFrame({
            "Time": pd.to_datetime([pd.Timestamp.now(), pd.Timestamp.now() - pd.Timedelta('1 min')]),
            "Price (USD)": [ha_prices['HA_Close'].iloc[-1], ha_prices['HA_Close'].iloc[-2]],
            "Amount (tons)": [random.randint(10, 100), random.randint(10, 100)]
        })
        
        st.table(recent_trades)

        st.markdown("<h3 style='color:#00ff00;'>Place an Order</h3>", unsafe_allow_html=True)
        order_type = st.radio("Order Type", ["Market", "Limit"])
        amount = st.number_input("Amount to Trade (tons)", min_value=1, max_value=200, value=10)
        price = st.number_input("Price (USD per ton)", min_value=10.0, max_value=100.0, value=20.0) if order_type == "Limit" else None

        if st.button("Submit Order"):
            st.success("Order submitted successfully!")

# Analytics Page
def analytics_page():
    st.markdown("<h2 style='color:#00ff00;'>Trading Analytics & Insights</h2>", unsafe_allow_html=True)
    st.write("Explore insights from trading activity and user engagement on the platform.")

    # Summary Metrics
    st.markdown("<h3 style='color:#00ff00;'>Summary Metrics</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_price = st.session_state['prices']['Close'].mean()
        st.metric(label="Average Price (USD)", value=f"${avg_price:.2f}")
    with col2:
        total_trades = random.randint(800, 1500)
        st.metric(label="Total Trades", value=f"{total_trades}")
    with col3:
        est_annual_volume = random.randint(20000, 40000)
        st.metric(label="Est. Annual Volume (tons)", value=f"{est_annual_volume:,}")
    with col4:
        avg_order_size = random.randint(5, 50)
        st.metric(label="Avg. Order Size (tons)", value=f"{avg_order_size}")

    # Price Prediction Chart
    st.markdown("<h3 style='color:#00ff00;'>Price Prediction Using Linear Regression</h3>", unsafe_allow_html=True)
    prices_df = st.session_state['prices'].reset_index()
    prices_df['Time'] = prices_df.index.astype(float)

    X = prices_df[['Time']]
    y = prices_df['Close']

    model = LinearRegression()
    model.fit(X, y)
    future_times = np.array(range(len(prices_df), len(prices_df) + 50)).reshape(-1, 1)
    future_predictions = model.predict(future_times)

    fig_pred = px.line(x=future_times.flatten(), y=future_predictions, labels={'x': 'Future Time', 'y': 'Predicted Price'}, title='Predicted CO2 Price Trend')
    fig_pred.update_traces(line=dict(color='green'))  # Use shades of green
    st.plotly_chart(fig_pred, use_container_width=True)

    # User Activity Analytics
    st.markdown("<h3 style='color:#00ff00;'>User Activity Overview</h3>", unsafe_allow_html=True)
    total_orders = random.randint(500, 1200)
    successful_orders = total_orders * random.uniform(0.75, 0.95)
    canceled_orders = total_orders - successful_orders
    avg_order_value = random.uniform(4000, 12000)
    estimated_annual_orders = total_orders * 12
    estimated_annual_value = avg_order_value * estimated_annual_orders

    # Displaying user activity analytics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Orders", value=f"{total_orders}")
    with col2:
        st.metric(label="Successful Orders", value=f"{successful_orders:.0f}")
    with col3:
        st.metric(label="Canceled Orders", value=f"{canceled_orders:.0f}")

    # Bar chart for user activity per month
    st.markdown("<h3 style='color:#00ff00;'>Monthly User Activity</h3>", unsafe_allow_html=True)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_orders = [random.randint(100, 150) for _ in months]
    fig_activity = px.bar(x=months, y=monthly_orders, labels={'x': 'Month', 'y': 'Number of Orders'}, title='Monthly Order Activity', color_discrete_sequence=['green'])
    st.plotly_chart(fig_activity, use_container_width=True)

    # Order Success vs. Cancellations - Pie Chart
    st.markdown("<h3 style='color:#00ff00;'>Order Success vs. Cancellations</h3>", unsafe_allow_html=True)
    fig_pie = px.pie(values=[successful_orders, canceled_orders], names=['Successful Orders', 'Canceled Orders'], title='Order Success vs. Cancellations', color_discrete_sequence=['#008000', '#90EE90'])
    st.plotly_chart(fig_pie, use_container_width=True)

    # User Growth Prediction
    st.markdown("<h3 style='color:#00ff00;'>User Growth Prediction</h3>", unsafe_allow_html=True)
    months_ahead = np.arange(1, 13)
    user_growth_rate = 0.05  # Assuming a 5% growth rate each month
    current_users = 500
    predicted_users = current_users * ((1 + user_growth_rate) ** months_ahead)
    fig_growth = px.line(x=months_ahead, y=predicted_users, labels={'x': 'Months Ahead', 'y': 'Predicted Number of Users'}, title='Predicted User Growth Over the Next Year')
    fig_growth.update_traces(line=dict(color='green'))
    st.plotly_chart(fig_growth, use_container_width=True)

    # Trade Value Projections - Line Chart
    st.markdown("<h3 style='color:#00ff00;'>Trade Value Projections</h3>", unsafe_allow_html=True)
    growth_scenarios = ['Conservative', 'Moderate', 'Aggressive']
    projected_values = [estimated_annual_value * (1 + growth_rate) for growth_rate in [0.03, 0.06, 0.10]]
    projections_df = pd.DataFrame({'Scenario': growth_scenarios, 'Projected Value (USD)': projected_values})

    fig_scenarios = px.bar(projections_df, x='Scenario', y='Projected Value (USD)', title='Trade Value Projections for Different Growth Scenarios', color='Scenario', color_discrete_sequence=['#006400', '#32CD32', '#228B22'])
    st.plotly_chart(fig_scenarios, use_container_width=True)

    # Top Performing Users (Fake Data)
    st.markdown("<h3 style='color:#00ff00;'>Top Performing Users</h3>", unsafe_allow_html=True)
    top_users = pd.DataFrame({
        "Username": [f"User{i}" for i in range(1, 6)],
        "Total Trades": [random.randint(50, 150) for _ in range(5)],
        "Total Value (USD)": [f"${random.uniform(20000, 50000):,.2f}" for _ in range(5)],
        "Avg P&L (%)": [f"{random.uniform(5, 20):.2f}%" for _ in range(5)]
    })
    st.table(top_users)

    st.write("These insights are generated based on the simulated trading activity on our platform.")

# Function to simulate new OHLC price data with correct time increment
def simulate_new_price(prices):
    last_row = prices.iloc[-1]
    new_open = last_row['Close']
    new_high = new_open + random.uniform(0, 1)
    new_low = new_open - random.uniform(0, 1)
    new_close = random.uniform(new_low, new_high)
    
    # Increment the timestamp of the last row by 3 seconds
    new_time = last_row.name + pd.Timedelta(seconds=3)
    
    # Add new row with the incremented time
    new_row = pd.DataFrame({'Open': [new_open], 'High': [new_high], 'Low': [new_low], 'Close': [new_close]}, index=[new_time])
    return pd.concat([prices, new_row]).tail(50)

# Function to calculate Heikin-Ashi candlesticks
def calculate_heikin_ashi(prices):
    ha_prices = prices.copy()
    
    ha_prices['HA_Close'] = (prices['Open'] + prices['High'] + prices['Low'] + prices['Close']) / 4
    ha_prices['HA_Open'] = (ha_prices['Open'].shift(1) + ha_prices['Close'].shift(1)) / 2
    ha_prices['HA_Open'].fillna((prices['Open'] + prices['Close']) / 2, inplace=True)
    ha_prices['HA_High'] = ha_prices[['High', 'HA_Open', 'HA_Close']].max(axis=1)
    ha_prices['HA_Low'] = ha_prices[['Low', 'HA_Open', 'HA_Close']].min(axis=1)
    
    return ha_prices

# Navigation Sidebar
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Registration", "Dashboard", "Analytics"])
    
    if page == "Registration":
        registration_page()
    elif page == "Dashboard":
        if 'registered' in st.session_state:
            dashboard_page()
        else:
            st.error("Please register before accessing the dashboard.")
    elif page == "Analytics":
        if 'registered' in st.session_state:
            analytics_page()
        else:
            st.error("Please register before accessing the analytics.")

if __name__ == "__main__":
    # Initialize state for price data (Open, High, Low, Close) if not already present
    if 'prices' not in st.session_state:
        # Initialize time series with fixed time increments
        st.session_state['prices'] = pd.DataFrame({
            'Time': pd.date_range(start=pd.Timestamp.now(), periods=50, freq='S'),
            'Open': [20 + random.uniform(-0.5, 0.5) for _ in range(50)],
            'High': [20 + random.uniform(0, 1) for _ in range(50)],
            'Low': [20 + random.uniform(-1, 0) for _ in range(50)],
            'Close': [20 + random.uniform(-0.5, 0.5) for _ in range(50)]
        }).set_index('Time')
    
    main()
