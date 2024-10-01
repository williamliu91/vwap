import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

@st.cache_data
def get_top_50_sp500():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        sp500 = tables[0]
        return sp500['Symbol'].head(50).tolist()
    except Exception as e:
        st.error(f"Error fetching S&P 500 data: {e}")
        return []

def calculate_vroc(data, period=5):
    data['VROC'] = data['Volume'].pct_change(periods=period) * 100
    return data

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

def get_yesterday_data(ticker):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=1)
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval="5m")
        if data.empty:
            start_date = start_date - timedelta(days=1)
            data = yf.download(ticker, start=start_date, end=end_date, interval="5m")
        data = calculate_vroc(data)
        data = calculate_rsi(data)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

st.set_page_config(layout="wide")

st.title('VROC and RSI Day Trading Dashboard - Top 50 S&P 500 Stocks')

# Get top 50 S&P 500 stocks
top_50_stocks = get_top_50_sp500()

if not top_50_stocks:
    st.error("Unable to fetch stock data. Please try again later.")
    st.stop()

# Sidebar for stock selection
selected_stock = st.sidebar.selectbox('Select a stock', top_50_stocks)

# Fetch yesterday's data for the selected stock
data = get_yesterday_data(selected_stock)

if data.empty:
    st.error(f"No data available for {selected_stock}. Please select another stock.")
    st.stop()

# Display basic info
st.header(f"Analysis for {selected_stock}")
st.subheader(f"Date: {data.index[0].date()}")


# VROC and RSI trading signals
st.sidebar.subheader('Trading Signal Parameters')
vroc_buy_threshold = st.sidebar.slider('VROC Buy Threshold', 0, 100, 20)
vroc_sell_threshold = st.sidebar.slider('VROC Sell Threshold', -100, 0, -20)
rsi_buy_threshold = st.sidebar.slider('RSI Buy Threshold', 0, 40, 30)
rsi_sell_threshold = st.sidebar.slider('RSI Sell Threshold', 60, 100, 70)

signals = data[['Close', 'VROC', 'RSI']].copy()
signals['Signal'] = 0
signals.loc[(signals['VROC'] > vroc_buy_threshold) & (signals['RSI'] < rsi_buy_threshold), 'Signal'] = 1
signals.loc[(signals['VROC'] < vroc_sell_threshold) & (signals['RSI'] > rsi_sell_threshold), 'Signal'] = -1

# Plot price, VROC, RSI, and signals with adjusted height to match sidebar
fig = plt.figure(figsize=(5, 5))  # Adjusted figure size to reduce height
gs = fig.add_gridspec(6, 1, hspace=1.2)  # Adjusted number of rows and hspace for more space

# Assign ax1 to 2 rows, ax2 and ax3 to 2 rows each
ax1 = fig.add_subplot(gs[:2, 0])  # Price chart takes up 2 rows
ax2 = fig.add_subplot(gs[2:4, 0], sharex=ax1)  # VROC chart takes up 2 rows
ax3 = fig.add_subplot(gs[4:, 0], sharex=ax1)  # RSI chart takes up 2 rows

# Plot price and signals
ax1.plot(data.index, data['Close'], label='Close Price', linewidth=0.8)
ax1.scatter(signals.index[signals['Signal'] == 1], 
            signals.loc[signals['Signal'] == 1, 'Close'], 
            color='green', label='Buy Signal', marker='^', s=20)  # Reduced marker size
ax1.scatter(signals.index[signals['Signal'] == -1], 
            signals.loc[signals['Signal'] == -1, 'Close'], 
            color='red', label='Sell Signal', marker='v', s=20)  # Reduced marker size
ax1.set_title(f'{selected_stock} Price with VROC and RSI Signals', fontsize=6)
ax1.set_ylabel('Price', fontsize=5)
ax1.legend(fontsize=4, loc='upper left', bbox_to_anchor=(1, 1))  # Smaller legend, moved outside the plot

# Plot VROC
ax2.plot(data.index, data['VROC'], label='VROC', linewidth=0.8)
ax2.axhline(y=vroc_buy_threshold, color='g', linestyle='--', label=f'Buy Threshold ({vroc_buy_threshold})', linewidth=0.8)
ax2.axhline(y=vroc_sell_threshold, color='r', linestyle='--', label=f'Sell Threshold ({vroc_sell_threshold})', linewidth=0.8)
ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.8)
ax2.set_title('Volume Rate of Change (VROC)', fontsize=6)
ax2.set_ylabel('VROC (%)', fontsize=5)
ax2.legend(fontsize=4, loc='upper left', bbox_to_anchor=(1, 1))  # Smaller legend, moved outside the plot

# Plot RSI
ax3.plot(data.index, data['RSI'], label='RSI', linewidth=0.8)
ax3.axhline(y=rsi_buy_threshold, color='g', linestyle='--', label=f'Buy Threshold ({rsi_buy_threshold})', linewidth=0.8)
ax3.axhline(y=rsi_sell_threshold, color='r', linestyle='--', label=f'Sell Threshold ({rsi_sell_threshold})', linewidth=0.8)
ax3.axhline(y=50, color='k', linestyle='-', linewidth=0.8)
ax3.set_title('Relative Strength Index (RSI)', fontsize=6)
ax3.set_ylabel('RSI', fontsize=5)
ax3.set_ylim(0, 100)
ax3.legend(fontsize=4, loc='upper left', bbox_to_anchor=(1, 1))  # Smaller legend, moved outside the plot

# X-axis label and tick font sizes, with 0-degree rotation
plt.xlabel('Time', fontsize=5)
plt.xticks(rotation=0, fontsize=5)  # Smaller x-axis labels and no rotation

# Adjust y-tick font sizes for all subplots
ax1.tick_params(axis='y', labelsize=5)
ax2.tick_params(axis='y', labelsize=5)
ax3.tick_params(axis='y', labelsize=5)

# Adjust x-tick font sizes and rotation for each subplot
ax1.tick_params(axis='x', labelsize=5, rotation=0)
ax2.tick_params(axis='x', labelsize=5, rotation=0)
ax3.tick_params(axis='x', labelsize=5, rotation=0)

# Adjust layout to avoid overlapping
plt.tight_layout()

# Display the plot
st.pyplot(fig)





# Calculate potential returns
signals['Returns'] = signals['Close'].pct_change()
signals['Strategy_Returns'] = signals['Signal'].shift(1) * signals['Returns']

total_return = (1 + signals['Strategy_Returns']).prod() - 1
sharpe_ratio = signals['Strategy_Returns'].mean() / signals['Strategy_Returns'].std() * (252 ** 0.5)

st.subheader('Strategy Performance')
st.write(f"Total Return: {total_return:.2%}")
st.write(f"Sharpe Ratio: {sharpe_ratio:.2f}")

st.warning("Note: This is a simplified simulation and should not be used for actual trading without further refinement and risk management.")