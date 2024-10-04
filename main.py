import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="CO2 Trading Exchange", layout="wide")

# Set the interval for live updates (seconds)
update_interval = 3

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

# Function to simulate new OHLC price data with correct time increment
def simulate_new_price(prices):
    last_row = prices.iloc[-1]
    new_open = last_row['Close']
    new_high = new_open + random.uniform(0, 1)
    new_low = new_open - random.uniform(0, 1)
    new_close = random.uniform(new_low, new_high)
    
    # Increment the timestamp of the last row by 3 seconds
    new_time = last_row.name + pd.Timedelta(seconds=update_interval)
    
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
        background-color: #f0b90b;
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
    st.markdown("<h2 style='color:#f0b90b;'>Heikin-Ashi CO2 Candlestick Chart</h2>", unsafe_allow_html=True)
    
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
    st.markdown("<h3 style='color:#f0b90b;'>Positions & Order History</h3>", unsafe_allow_html=True)
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
    st.markdown("<h3 style='color:#f0b90b;'>Order Book</h3>", unsafe_allow_html=True)
    
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
    st.markdown("<h3 style='color:#f0b90b;'>Recent Trades</h3>", unsafe_allow_html=True)
    
    recent_trades = pd.DataFrame({
        "Time": pd.to_datetime([pd.Timestamp.now(), pd.Timestamp.now() - pd.Timedelta('1 min')]),
        "Price (USD)": [ha_prices['HA_Close'].iloc[-1], ha_prices['HA_Close'].iloc[-2]],
        "Amount (tons)": [random.randint(10, 100), random.randint(10, 100)]
    })
    
    st.table(recent_trades)

    st.markdown("<h3 style='color:#f0b90b;'>Place an Order</h3>", unsafe_allow_html=True)
    order_type = st.radio("Order Type", ["Market", "Limit"])
    amount = st.number_input("Amount to Trade (tons)", min_value=1, max_value=200, value=10)
    price = st.number_input("Price (USD per ton)", min_value=10.0, max_value=100.0, value=20.0) if order_type == "Limit" else None

    if st.button("Submit Order"):
        st.success("Order submitted successfully!")

# Rerun the app every X seconds
time.sleep(update_interval)
st.experimental_rerun()
