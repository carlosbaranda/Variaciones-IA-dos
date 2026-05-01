import streamlit as st
import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime

# ============================================================
# CONFIGURACIÓN STREAMLIT
# ============================================================

st.set_page_config(page_title="Variaciones IA - Bolsa", layout="wide")
st.title("📊 Variaciones IA - Bolsa")
st.caption("Modelo robusto sin dependencia obligatoria de company_names.json")

# ============================================================
# CARGA SEGURA DE NOMBRES DE COMPAÑÍAS
# ============================================================

@st.cache_data(ttl=3600)
def cargar_company_names():
    """
    Carga company_names.json solo si existe.
    Si no existe, devuelve un diccionario vacío y la app sigue funcionando.
    """
    posibles_rutas = [
        "company_names.json",
        "./company_names.json",
        "data/company_names.json"
    ]

    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}

    return {}


company_names = cargar_company_names()


def obtener_nombre_compania(ticker, info=None):
    """
    Prioridad:
    1. Nombre en company_names.json, si existe.
    2. shortName de yfinance.
    3. longName de yfinance.
    4. El propio ticker.
    """
    if ticker in company_names:
        return company_names[ticker]

    if info:
        return (
            info.get("shortName")
            or info.get("longName")
            or ticker
        )

    return ticker


# ============================================================
# LISTA DE TICKERS
# Puedes ampliar esta lista con tus valores IA / tecnología
# ============================================================

tickers = [
    "NVDA", "MSFT", "GOOGL", "META", "AMZN", "TSLA", "AAPL", "AMD", "AVGO",
    "CRM", "ORCL", "ADBE", "PLTR", "SMCI", "ARM", "TSM", "ASML", "INTC",
    "QCOM", "MU", "SNOW", "NOW", "PANW", "CRWD", "NET", "DDOG", "MDB"
]

# ============================================================
# FUNCIONES
# ============================================================

def calcular_variacion(actual, anterior):
    try:
        if anterior == 0 or pd.isna(anterior):
            return 0
        return ((actual - anterior) / anterior) * 100
    except Exception:
        return 0


@st.cache_data(ttl=3600, show_spinner=False)
def obtener_datos(lista_tickers):
    registros = []
    errores = []
    inicio_ano = f"{datetime.now().year}-01-01"

    for ticker in lista_tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="370d", auto_adjust=False)

            if hist.empty or len(hist) < 30:
                errores.append(ticker)
                continue

            try:
                info = stock.info or {}
            except Exception:
                info = {}

            cierre_actual = float(hist["Close"].iloc[-1])
            apertura_actual = float(hist["Open"].iloc[-1])
            cierre_semana = float(hist["Close"].iloc[-6]) if len(hist) >= 6 else float(hist["Close"].iloc[0])
            cierre_mes = float(hist["Close"].iloc[-22]) if len(hist) >= 22 else float(hist["Close"].iloc[0])
            cierre_12m = float(hist["Close"].iloc[-252]) if len(hist) >= 252 else float(hist["Close"].iloc[0])

            hist_ytd = hist[hist.index >= inicio_ano]
            cierre_inicio_ano = float(hist_ytd["Close"].iloc[0]) if not hist_ytd.empty else float(hist["Close"].iloc[0])

            volumen_diario = float(hist["Volume"].iloc[-1])
            volumen_medio_50 = float(hist["Volume"].tail(50).mean()) if len(hist) >= 50 else float(hist["Volume"].mean())

            registros.append({
                "Ticker": ticker,
                "Nombre": obtener_nombre_compania(ticker, info),
                "Sector": info.get("sector", "N/D"),
                "Industria": info.get("industry", "N/D"),
                "Último Precio": round(cierre_actual, 2),
                "Cambio Día (%)": round(calcular_variacion(cierre_actual, apertura_actual), 2),
                "Cambio Semana (%)": round(calcular_variacion(cierre_actual, cierre_semana), 2),
                "Cambio Mes (%)": round(calcular_variacion(cierre_actual, cierre_mes), 2),
                "YTD (%)": round(calcular_variacion(cierre_actual, cierre_inicio_ano), 2),
                "Cambio 12M (%)": round(calcular_variacion(cierre_actual, cierre_12m), 2),
                "Volumen Diario": int(volumen_diario),
                "Volumen Medio 50": int(volumen_medio_50),
                "Diferencia Volumen (%)": round(calcular_variacion(volumen_diario, volumen_medio_50), 2),
                "PER": round(info.get("trailingPE"), 2) if isinstance(info.get("trailingPE"), (int, float)) else None,
                "Market Cap": info.get("marketCap", None)
            })

        except Exception:
            errores.append(ticker)
            continue

    return pd.DataFrame(registros), errores


def resaltar_variaciones(val):
    try:
        num = float(val)
        if num > 3:
            return "color: green; font-weight: bold"
        elif num < -3:
            return "color: red; font-weight: bold"
    except Exception:
        return ""
    return ""


# ============================================================
# EJECUCIÓN
# ============================================================

with st.spinner("Cargando datos..."):
    df, errores = obtener_datos(tickers)

if df.empty:
    st.error("No se han podido obtener datos. Revisa conexión, tickers o disponibilidad de yfinance.")
    st.stop()

st.sidebar.header("Filtros")

busqueda = st.sidebar.text_input("Buscar ticker o compañía")

df_filtrado = df.copy()

if busqueda:
    texto = busqueda.lower().strip()
    df_filtrado = df_filtrado[
        df_filtrado["Ticker"].str.lower().str.contains(texto, na=False) |
        df_filtrado["Nombre"].str.lower().str.contains(texto, na=False)
    ]

sector_sel = st.sidebar.selectbox(
    "Sector",
    ["Todos"] + sorted(df_filtrado["Sector"].dropna().unique())
)

if sector_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Sector"] == sector_sel]

ordenar_por = st.sidebar.selectbox(
    "Ordenar por",
    [
        "Cambio Día (%)",
        "Cambio Semana (%)",
        "Cambio Mes (%)",
        "YTD (%)",
        "Cambio 12M (%)",
        "Diferencia Volumen (%)",
        "Market Cap",
        "PER"
    ]
)

ascendente = st.sidebar.checkbox("Orden ascendente", value=False)

df_filtrado = df_filtrado.sort_values(ordenar_por, ascending=ascendente, na_position="last")

# ============================================================
# ALERTA SOBRE JSON
# ============================================================

if not company_names:
    st.info("No se ha encontrado company_names.json. La app está usando nombres automáticos de yfinance o el ticker como alternativa.")

if errores:
    with st.expander("Tickers sin datos o con error"):
        st.write(", ".join(errores))

# ============================================================
# MÉTRICAS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Valores analizados", len(df_filtrado))

mejor_dia = df_filtrado.sort_values("Cambio Día (%)", ascending=False).iloc[0]
col2.metric("Mejor día", mejor_dia["Ticker"], f'{mejor_dia["Cambio Día (%)"]:.2f}%')

mejor_ytd = df_filtrado.sort_values("YTD (%)", ascending=False).iloc[0]
col3.metric("Mejor YTD", mejor_ytd["Ticker"], f'{mejor_ytd["YTD (%)"]:.2f}%')

mayor_vol = df_filtrado.sort_values("Diferencia Volumen (%)", ascending=False).iloc[0]
col4.metric("Mayor volumen relativo", mayor_vol["Ticker"], f'{mayor_vol["Diferencia Volumen (%)"]:.2f}%')

# ============================================================
# TABLA PRINCIPAL
# ============================================================

st.subheader("📋 Tabla principal")

columnas_variacion = [
    "Cambio Día (%)",
    "Cambio Semana (%)",
    "Cambio Mes (%)",
    "YTD (%)",
    "Cambio 12M (%)",
    "Diferencia Volumen (%)"
]

st.dataframe(
    df_filtrado.style.map(resaltar_variaciones, subset=columnas_variacion),
    use_container_width=True,
    height=550
)

# ============================================================
# RANKINGS
# ============================================================

st.subheader("🏆 Rankings")

tab1, tab2, tab3 = st.tabs(["Día", "YTD", "Volumen"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🟢 Top subidas día")
        st.dataframe(df_filtrado.sort_values("Cambio Día (%)", ascending=False).head(15)[
            ["Ticker", "Nombre", "Cambio Día (%)"]
        ], use_container_width=True)
    with c2:
        st.markdown("### 🔴 Top caídas día")
        st.dataframe(df_filtrado.sort_values("Cambio Día (%)", ascending=True).head(15)[
            ["Ticker", "Nombre", "Cambio Día (%)"]
        ], use_container_width=True)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🟢 Top ganadores YTD")
        st.dataframe(df_filtrado.sort_values("YTD (%)", ascending=False).head(15)[
            ["Ticker", "Nombre", "YTD (%)"]
        ], use_container_width=True)
    with c2:
        st.markdown("### 🔴 Top perdedores YTD")
        st.dataframe(df_filtrado.sort_values("YTD (%)", ascending=True).head(15)[
            ["Ticker", "Nombre", "YTD (%)"]
        ], use_container_width=True)

with tab3:
    st.markdown("### 🔊 Mayor incremento de volumen relativo")
    st.dataframe(df_filtrado.sort_values("Diferencia Volumen (%)", ascending=False).head(20)[
        ["Ticker", "Nombre", "Volumen Diario", "Volumen Medio 50", "Diferencia Volumen (%)"]
    ], use_container_width=True)

# ============================================================
# DESCARGA CSV
# ============================================================

csv = df_filtrado.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "📥 Descargar CSV",
    data=csv,
    file_name=f"variaciones_ia_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

st.caption("Datos vía yfinance. Los nombres se cargan desde company_names.json si existe; si no, se usa yfinance o el ticker.")
