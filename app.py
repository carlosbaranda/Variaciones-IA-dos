
import streamlit as st
import pandas as pd
import json
from data_loader import load_data_for_market
from utils import get_top_movers, plot_multiple_stocks
from tickers import TICKERS_BY_MARKET

with open("company_names.json", "r", encoding="utf-8") as f:
    COMPANY_NAMES = json.load(f)

st.set_page_config(layout="wide")
st.title("📊 Seguimiento de acciones con mayor variación")

menu = st.sidebar.radio("Navegación", ["Mercados", "Ranking IA", "Comparar acciones"])

def format_label(ticker):
    return f"{ticker} - {COMPANY_NAMES.get(ticker, ticker)}"

if menu == "Mercados":
    market = st.selectbox("Selecciona el mercado", list(TICKERS_BY_MARKET.keys()))
    period = st.selectbox("Selecciona el período", ["Día", "Mes", "Año"])

    tickers = TICKERS_BY_MARKET[market]
    df_all = load_data_for_market(tickers)

    top_movers = get_top_movers(df_all, period)
    top_movers["Nombre"] = top_movers["Ticker"].map(COMPANY_NAMES)

    st.subheader(f"Top variaciones ({period.lower()}) - {market}")
    st.dataframe(top_movers[["Ticker", "Nombre", "Variación %"]], use_container_width=True)

    ticker_options = {format_label(t): t for t in top_movers["Ticker"]}
    selected_label = st.selectbox("Selecciona un valor para ver su evolución", list(ticker_options.keys()))
    selected_ticker = ticker_options[selected_label]

    st.markdown("### Selecciona el rango de fechas para el gráfico")
    start_date = st.date_input("Desde", pd.to_datetime("2023-08-01"))
    end_date = st.date_input("Hasta", pd.to_datetime("today"))

    from utils import plot_price_with_moving_averages
    plot_price_with_moving_averages(selected_ticker, start=start_date, end=end_date)

elif menu == "Ranking IA":
    st.subheader("🔍 Acciones relacionadas con IA")
    ai_tickers = list(set(TICKERS_BY_MARKET["NASDAQ"] + TICKERS_BY_MARKET["NYSE"]))
    df_ai = load_data_for_market(ai_tickers)

    period = st.selectbox("Selecciona el período", ["Día", "Mes", "Año"], key="ai_period")
    top_ai = get_top_movers(df_ai, period)
    top_ai["Nombre"] = top_ai["Ticker"].map(COMPANY_NAMES)

    st.dataframe(top_ai[["Ticker", "Nombre", "Variación %"]], use_container_width=True)

    ticker_options = {format_label(t): t for t in top_ai["Ticker"]}
    selected_label = st.selectbox("Selecciona una acción de IA para ver su evolución", list(ticker_options.keys()), key="ai_chart")
    selected_ticker = ticker_options[selected_label]

    st.markdown("### Selecciona el rango de fechas para el gráfico")
    start_date_ai = st.date_input("Desde", pd.to_datetime("2023-08-01"), key="ai_start")
    end_date_ai = st.date_input("Hasta", pd.to_datetime("today"), key="ai_end")

    from utils import plot_price_with_moving_averages
    plot_price_with_moving_averages(selected_ticker, start=start_date_ai, end=end_date_ai)

elif menu == "Comparar acciones":
    st.subheader("📉 Comparador de acciones")
    all_tickers = list(set(t for tickers in TICKERS_BY_MARKET.values() for t in tickers))
    all_ticker_labels = [f"{t} - {COMPANY_NAMES.get(t, t)}" for t in all_tickers]
    selected_labels = st.multiselect("Selecciona varias acciones para comparar", all_ticker_labels)

    selected_tickers = [label.split(" - ")[0] for label in selected_labels]

    st.markdown("### Selecciona el rango de fechas para el gráfico comparativo")
    start_compare = st.date_input("Desde", pd.to_datetime("2023-08-01"), key="multi_start")
    end_compare = st.date_input("Hasta", pd.to_datetime("today"), key="multi_end")

    if selected_tickers:
        plot_multiple_stocks(selected_tickers, start=start_compare, end=end_compare)
