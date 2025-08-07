
import pandas as pd
import streamlit as st
import yfinance as yf

def get_top_movers(df, period):
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Ticker", "Date"])
    latest = df.groupby("Ticker").last()["Close"]

    if period == "Día":
        prev = df.groupby("Ticker").nth(-2)["Close"]
    elif period == "Mes":
        cutoff = df["Date"].max() - pd.DateOffset(months=1)
        prev = df[df["Date"] <= cutoff].groupby("Ticker").last()["Close"]
    elif period == "Año":
        cutoff = df["Date"].max() - pd.DateOffset(years=1)
        prev = df[df["Date"] <= cutoff].groupby("Ticker").last()["Close"]
    else:
        return pd.DataFrame()

    variation = ((latest - prev) / prev * 100).sort_values(ascending=False)
    return variation.reset_index().rename(columns={0: "Variación %"}).head(15)

def plot_price_with_moving_averages(ticker, start=None, end=None):
    df = yf.Ticker(ticker).history(period="1y")
    df.index = pd.to_datetime(df.index)
    if start and end:
        df = df[(df.index >= pd.to_datetime(start)) & (df.index <= pd.to_datetime(end))]
    df["MA60"] = df["Close"].rolling(window=60).mean()
    df["MA200"] = df["Close"].rolling(window=200).mean()
    st.line_chart(df[["Close", "MA60", "MA200"]])


def plot_multiple_stocks(tickers, start=None, end=None):
    df_all = pd.DataFrame()
    for ticker in tickers:
        df = yf.Ticker(ticker).history(period="1y")
        df.index = pd.to_datetime(df.index)
        df = df["Close"]
        if start and end:
            df = df[(df.index >= pd.to_datetime(start)) & (df.index <= pd.to_datetime(end))]
        if not df.empty:
            normalized = df / df.iloc[0] * 100  # normalización: 100 en el primer día
            df_all[ticker] = normalized
    if not df_all.empty:
        st.line_chart(df_all.rename(columns=lambda x: f"{x} (100%)"))
