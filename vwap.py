
# Step 2: Import necessary libraries
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_ta as ta  # For technical analysis indicators like EMA and RSI
import streamlit as st

# Step 3: Function to fetch data and calculate indicators
def fetch_stock_data(stock_symbol, period):
    # Fetch stock data from Yahoo Finance
    stock_data = yf.download(stock_symbol, period=period, interval='1d')
    
    # Ensure no NaN values in 'Close' column by dropping rows
    stock_data = stock_data.dropna(subset=['Close'])
    
    # Calculate VWAP
    stock_data['Typical_Price'] = (stock_data['High'] + stock_data['Low'] + stock_data['Close']) / 3
    stock_data['Cumulative_Volume'] = stock_data['Volume'].cumsum()
    stock_data['Cumulative_TPV'] = (stock_data['Typical_Price'] * stock_data['Volume']).cumsum()
    stock_data['VWAP'] = stock_data['Cumulative_TPV'] / stock_data['Cumulative_Volume']

    # Calculate EMA 50
    stock_data['EMA_50'] = ta.ema(stock_data['Close'], length=50)

    # Calculate RSI
    stock_data['RSI'] = ta.rsi(stock_data['Close'], length=14)

    # Ensure no NaN values in calculated columns
    stock_data = stock_data.dropna(subset=['VWAP', 'EMA_50', 'RSI'])

    # Generate Buy/Sell Signals
    stock_data['Signal'] = 0  # Default no signal

    # Buy when price is above VWAP, between VWAP and EMA 50, and RSI is below 40
    stock_data.loc[(stock_data['Close'] > stock_data['VWAP']) & 
                   (stock_data['Close'] < stock_data['EMA_50']) & 
                   (stock_data['RSI'] < 40), 'Signal'] = 1  # Buy Signal

    # Sell when price is below VWAP, between VWAP and EMA 50, and RSI is above 60
    stock_data.loc[(stock_data['Close'] < stock_data['VWAP']) & 
                   (stock_data['Close'] > stock_data['EMA_50']) & 
                   (stock_data['RSI'] > 60), 'Signal'] = -1  # Sell Signal
    
    return stock_data

# Step 4: Streamlit application
def main():
    st.title('Stock Analysis with VWAP, EMA, and RSI')

    # Dropdown for stock selection (Top 50 Stocks)
    stocks = {
        'Apple Inc. (AAPL)': 'AAPL',
        'Microsoft Corp (MSFT)': 'MSFT',
        'Alphabet Inc. (GOOGL)': 'GOOGL',
        'Amazon.com Inc. (AMZN)': 'AMZN',
        'Tesla Inc. (TSLA)': 'TSLA',
        'Meta Platforms Inc. (META)': 'META',
        'NVIDIA Corp (NVDA)': 'NVDA',
        'Berkshire Hathaway Inc. (BRK.B)': 'BRK-B',
        'Johnson & Johnson (JNJ)': 'JNJ',
        'Visa Inc. (V)': 'V',
        'Walmart Inc. (WMT)': 'WMT',
        'UnitedHealth Group (UNH)': 'UNH',
        'Procter & Gamble Co. (PG)': 'PG',
        'Mastercard Inc. (MA)': 'MA',
        'Exxon Mobil Corp (XOM)': 'XOM',
        'Coca-Cola Co. (KO)': 'KO',
        'PepsiCo Inc. (PEP)': 'PEP',
        'AbbVie Inc. (ABBV)': 'ABBV',
        'Pfizer Inc. (PFE)': 'PFE',
        'Walt Disney Co. (DIS)': 'DIS',
        'Cisco Systems Inc. (CSCO)': 'CSCO',
        'Intel Corp (INTC)': 'INTC',
        'IBM (IBM)': 'IBM',
        'Salesforce.com Inc. (CRM)': 'CRM',
        'AT&T Inc. (T)': 'T',
        'Netflix Inc. (NFLX)': 'NFLX',
        'Adobe Inc. (ADBE)': 'ADBE',
        'Abbott Laboratories (ABT)': 'ABT',
        'Medtronic plc (MDT)': 'MDT',
        'Amgen Inc. (AMGN)': 'AMGN',
        'Booking Holdings Inc. (BKNG)': 'BKNG',
        'Costco Wholesale Corp. (COST)': 'COST',
        'Broadcom Inc. (AVGO)': 'AVGO',
        'Chevron Corp (CVX)': 'CVX',
        'T-Mobile US Inc. (TMUS)': 'TMUS',
        'Qualcomm Inc. (QCOM)': 'QCOM',
        '3M Company (MMM)': 'MMM',
        'Honeywell International Inc. (HON)': 'HON',
        'PayPal Holdings Inc. (PYPL)': 'PYPL',
        'Texas Instruments Inc. (TXN)': 'TXN',
        'Union Pacific Corp (UNP)': 'UNP',
        'Bristol-Myers Squibb Co. (BMY)': 'BMY',
        'S&P Global Inc. (SPGI)': 'SPGI',
        'Lilly (Eli) and Co. (LLY)': 'LLY',
        'General Electric Co. (GE)': 'GE',
        'Goldman Sachs Group Inc. (GS)': 'GS',
        'American Express Co. (AXP)': 'AXP',
        'Morgan Stanley (MS)': 'MS',
        'NextEra Energy Inc. (NEE)': 'NEE',
        'Chubb Limited (CB)': 'CB',
        'CVS Health Corp (CVS)': 'CVS'
    }
    
    # Keep only 1y period
    period = '1y'
    selected_stock = st.selectbox('Select Stock', list(stocks.keys()))
    stock_symbol = stocks[selected_stock]

    # Fetch and process data automatically after selection
    stock_data = fetch_stock_data(stock_symbol, period)

    # Plotting the Stock Prices, VWAP, EMA 50, and Buy/Sell Signals
    plt.figure(figsize=(14, 10))

    # Price Plot
    plt.subplot(2, 1, 1)  # First subplot for price
    plt.plot(stock_data.index, stock_data['Close'], label=f'{selected_stock} Price', color='blue')
    plt.plot(stock_data.index, stock_data['VWAP'], label='VWAP', color='orange', linestyle='--')
    plt.plot(stock_data.index, stock_data['EMA_50'], label='EMA 50', color='purple', linestyle='-.')

    # Plot Buy Signals
    plt.plot(stock_data[stock_data['Signal'] == 1].index, 
             stock_data['Close'][stock_data['Signal'] == 1], '^', markersize=10, color='g', lw=0, label='Buy Signal')

    # Plot Sell Signals
    plt.plot(stock_data[stock_data['Signal'] == -1].index, 
             stock_data['Close'][stock_data['Signal'] == -1], 'v', markersize=10, color='r', lw=0, label='Sell Signal')

    # Add title and labels for price plot
    plt.title(f'{selected_stock} Prices with VWAP, EMA 50, and Buy/Sell Signals (1 Year)')
    plt.xlabel('Date')
    plt.ylabel('Price in USD')
    plt.legend()
    plt.grid(True)

    # RSI Plot
    plt.subplot(2, 1, 2)  # Second subplot for RSI
    plt.plot(stock_data.index, stock_data['RSI'], label='RSI', color='purple')
    plt.axhline(60, linestyle='--', alpha=0.5, color='red')  # Overbought line
    plt.axhline(40, linestyle='--', alpha=0.5, color='green')  # Oversold line
    plt.title('Relative Strength Index (RSI)')
    plt.xlabel('Date')
    plt.ylabel('RSI Value')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    st.pyplot(plt)

# Run the Streamlit app
if __name__ == "__main__":
    main()
