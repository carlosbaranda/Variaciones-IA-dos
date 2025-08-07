
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
import datetime
import json

with open("company_names.json", "r", encoding="utf-8") as f:
    COMPANY_NAMES = json.load(f)

def generate_pdf_report(rankings, filename="informe_ranking_diario.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Informe Diario - Ranking Acciones", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    for market, df in rankings.items():
        elements.append(Paragraph(market, styles["Heading2"]))
        elements.append(Spacer(1, 6))

        df["Nombre"] = df["Ticker"].map(COMPANY_NAMES)
        data = [["Ticker", "Nombre", "Periodo", "Variación %", "Precio", "Volumen"]]
        for _, row in df.iterrows():
            data.append([
                row["Ticker"],
                row["Nombre"],
                row["Periodo"],
                f'{row["Variación %"]:.2f}%',
                f'{row["Precio"]:.2f}',
                int(row["Volumen"])
            ])
        table = Table(data, hAlign="LEFT")
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d3d3d3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

    
    # Añadir gráfico de los top 5 del día
    top_5_tickers = []
    for df in rankings.values():
        day_df = df[df["Periodo"] == "Día"]
        top_5_tickers.extend(day_df.sort_values("Variación %", ascending=False)["Ticker"].head(1).tolist())
    top_5_tickers = list(set(top_5_tickers))[:5]

    chart_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
    plot_top_5_chart(top_5_tickers, filename=chart_file)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Comparativa de los 5 valores más destacados del día", styles["Heading2"]))
    elements.append(Image(chart_file, width=480, height=280))


    # Añadir gráfico IA
    ia_tickers = list(set(TICKERS_BY_MARKET["NASDAQ"] + TICKERS_BY_MARKET["NYSE"]))
    ia_top = []
    for market, df in rankings.items():
        if market not in ["NASDAQ", "NYSE"]:
            continue
        day_df = df[(df["Periodo"] == "Día") & (df["Ticker"].isin(ia_tickers))]
        ia_top.extend(day_df.sort_values("Variación %", ascending=False)["Ticker"].head(2).tolist())
    ia_top = list(set(ia_top))[:5]

    chart_file_ia = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
    plot_top_ia_chart(ia_top, filename=chart_file_ia)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Comparativa de acciones IA más destacadas del día", styles["Heading2"]))
    elements.append(Image(chart_file_ia, width=480, height=280))

doc.build(elements)
    return filename


import matplotlib.pyplot as plt
from reportlab.platypus import Image
import tempfile
import yfinance as yf

def plot_top_5_chart(tickers, filename="top5_chart.png"):
    plt.figure(figsize=(10, 5))
    for ticker in tickers:
        df = yf.Ticker(ticker).history(period="1mo")["Close"]
        if not df.empty:
            normalized = df / df.iloc[0] * 100
            plt.plot(normalized, label=ticker)
    plt.title("Evolución últimos 30 días - Top 5 del día (normalizado)")
    plt.ylabel("Índice base 100")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def plot_top_ia_chart(tickers, filename="top_ia_chart.png"):
    plt.figure(figsize=(10, 5))
    for ticker in tickers:
        df = yf.Ticker(ticker).history(period="1mo")["Close"]
        if not df.empty:
            normalized = df / df.iloc[0] * 100
            plt.plot(normalized, label=ticker)
    plt.title("Evolución últimos 30 días - IA destacadas (normalizado)")
    plt.ylabel("Índice base 100")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
