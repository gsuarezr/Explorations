import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_insider_data(ticker):
    url = f"https://openinsider.com/screener?s={ticker}&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&xp=1&vl=&vh=&ocl=&och=&sicMin=&sicMax=&sortcol=0&cnt=50&page=1"
    headers = {'User-Agent': 'Mozilla/5.0'}

    response = requests.get(url, headers=headers)
    if not response.ok:
        return pd.DataFrame(), f"Failed to fetch data for {ticker}"

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find("table", class_="tinytable")

    if table is None:
        return pd.DataFrame(), f"No data available for {ticker}"

    df = pd.read_html(str(table))[0]
    
    # Filter only Buy transactions
    df = df[df['Trade Type'].str.contains('P', na=False)]

    return df, None

def main():
    st.title("📈 Insider Buying Tracker")

    # Example ticker list (you can also use st.text_input or file upload here)
    tickers = st.text_input("Enter comma-separated tickers (e.g. AAPL,TSLA,NVDA):", "AAPL,TSLA")
    tickers = [ticker.strip().upper() for ticker in tickers.split(',') if ticker.strip()]

    if tickers:
        for ticker in tickers:
            st.subheader(f"🕵️ Insider Purchases for {ticker}")
            df, error = get_insider_data(ticker)

            if error:
                st.warning(error)
            elif df.empty:
                st.info(f"No recent purchases found for {ticker}.")
            else:
                st.dataframe(df)

if __name__ == "__main__":
    main()
