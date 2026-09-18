import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import AverageTrueRange

st.set_page_config(page_title="Stock AI Agent", page_icon="📈", layout="wide")

@st.cache_data(ttl=300)
def get_data(symbol, period):
    ticker = symbol.strip().upper()
    if not ticker.endswith(".NS"):
        ticker += ".NS"
    df = yf.download(ticker, period=period, interval="1d",
                     auto_adjust=False, progress=False)
    if df.empty:
        raise ValueError("Data नहीं मिला. NSE symbol check करें.")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [x[0] for x in df.columns]
    cols = ["Open","High","Low","Close","Volume"]
    df = df[cols].apply(pd.to_numeric, errors="coerce").dropna()
    df["EMA20"] = EMAIndicator(df["Close"], 20).ema_indicator()
    df["EMA50"] = EMAIndicator(df["Close"], 50).ema_indicator()
    df["EMA200"] = EMAIndicator(df["Close"], 200).ema_indicator()
    df["RSI"] = RSIIndicator(df["Close"], 14).rsi()
    macd = MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_SIGNAL"] = macd.macd_signal()
    df["ATR"] = AverageTrueRange(df["High"], df["Low"], df["Close"], 14).average_true_range()
    df["VOL20"] = df["Volume"].rolling(20).mean()
    return df.dropna()

def analyze(df):
    r = df.iloc[-1]
    score = 0
    reasons = []
    for condition, plus, minus in [
        (r.Close > r.EMA20, "Price above EMA20", "Price below EMA20"),
        (r.EMA20 > r.EMA50, "EMA20 above EMA50", "EMA20 below EMA50"),
        (r.EMA50 > r.EMA200, "EMA50 above EMA200", "EMA50 below EMA200"),
        (r.MACD > r.MACD_SIGNAL, "MACD positive", "MACD negative"),
    ]:
        score += 1 if condition else -1
        reasons.append(plus if condition else minus)
    if r.RSI >= 55:
        score += 1; reasons.append("RSI momentum positive")
    elif r.RSI <= 45:
        score -= 1; reasons.append("RSI momentum weak")
    else:
        reasons.append("RSI neutral")
    trend = "Bullish" if score >= 3 else "Bearish" if score <= -3 else "Neutral"
    return r, score, trend, reasons

st.title("📈 Stock AI Agent")
st.caption("Indian NSE technical-analysis research dashboard")

with st.sidebar:
    symbol = st.text_input("NSE Symbol", "RELIANCE")
    period = st.selectbox("History", ["6mo","1y","2y","5y"], index=1)
    run = st.button("Analyze", type="primary", use_container_width=True)

if run:
    try:
        df = get_data(symbol, period)
        r, score, trend, reasons = analyze(df)

        a,b,c,d = st.columns(4)
        a.metric("Last Price", f"₹{r.Close:,.2f}")
        b.metric("Trend", trend)
        c.metric("RSI", f"{r.RSI:.1f}")
        d.metric("Volume / 20D", f"{r.Volume/r.VOL20:.2f}x")

        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High,
                                     low=df.Low, close=df.Close, name="Price"))
        for col in ["EMA20","EMA50","EMA200"]:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col))
        fig.update_layout(height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        l, rr = st.columns(2)
        with l:
            st.subheader("Technical Inputs")
            for x in reasons: st.write("•", x)
            st.write(f"MACD: {r.MACD:.3f}")
            st.write(f"ATR14: ₹{r.ATR:.2f}")
        with rr:
            st.subheader("20-Day Levels")
            st.write(f"Support: ₹{df.Low.tail(20).min():,.2f}")
            st.write(f"Resistance: ₹{df.High.tail(20).max():,.2f}")
            st.write(f"EMA20: ₹{r.EMA20:,.2f}")
            st.write(f"EMA50: ₹{r.EMA50:,.2f}")

        st.subheader("RSI")
        st.line_chart(df[["RSI"]])

        st.info("यह V1 technical research engine है। Live data की freshness/provider limitations को ध्यान में रखें; यह personalized financial advice नहीं है.")
    except Exception as e:
        st.error(str(e))
else:
    st.info("ऊपर stock symbol डालकर Analyze दबाएँ। उदाहरण: RELIANCE, TCS, INFY, HDFCBANK")
