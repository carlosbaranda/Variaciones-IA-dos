
import pandas as pd
from tickers import TICKERS_BY_MARKET
from data_loader import load_data_for_market
from utils import get_top_movers
from generate_pdf import generate_pdf_report
from email_alert import send_email
from datetime import datetime
import json

with open("company_names.json", "r", encoding="utf-8") as f:
    COMPANY_NAMES = json.load(f)

# 1. Generar rankings por mercado y por período
rankings = {}
periodos = ["Día", "Mes", "Año"]
resumen_html = {}

for market, tickers in TICKERS_BY_MARKET.items():
    df_market = load_data_for_market(tickers)
    if df_market.empty:
        continue
    tabla_completa = []

    resumen_html[market] = []

    for periodo in periodos:
        top = get_top_movers(df_market, periodo)
        top["Precio"] = df_market.groupby("Ticker").last()["Close"]
        top["Volumen"] = df_market.groupby("Ticker").last()["Volume"]
        top["Nombre"] = top["Ticker"].map(COMPANY_NAMES)
        top["Yahoo Finance"] = top["Ticker"].apply(lambda x: f"https://finance.yahoo.com/quote/{x}")
        top["Periodo"] = periodo
        tabla_completa.append(top)

        if not top.empty:
            resumen_html[market].append(
                f"{periodo}: {top.iloc[0]['Ticker']} - {top.iloc[0]['Nombre']} ({top.iloc[0]['Variación %']:.2f}%)"
            )

    if tabla_completa:
        df_final = pd.concat(tabla_completa)
        rankings[market] = df_final[["Ticker", "Nombre", "Periodo", "Variación %", "Precio", "Volumen", "Yahoo Finance"]]

# 2. Crear PDF
fecha = datetime.now().strftime("%Y-%m-%d")
pdf_filename = f"ranking_{fecha}.pdf"
generate_pdf_report(rankings, pdf_filename)

# 3. Preparar cuerpo del email (HTML)
html_body = f"""
<h3>Ranking diario - {fecha}</h3>
<p>A continuación los valores con mayor variación por mercado y período:</p>
<ul>
"""
for market, resumenes in resumen_html.items():
    html_body += f"<li><strong>{market}</strong>:<ul>"
    for linea in resumenes:
        html_body += f"<li>{linea}</li>"
    html_body += "</ul></li>"
html_body += "</ul><p>Se adjunta el informe en PDF.<br>Consulta los gráficos en Yahoo Finance desde los enlaces del PDF.</p>"

# 4. Enviar email
send_email(subject=f"Ranking diario acciones - {fecha}", body=html_body, pdf_path=pdf_filename)
