import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time
from datetime import datetime

st.set_page_config(layout="wide")

# ---------------- THEME ----------------

theme = st.sidebar.selectbox("Theme", ["Dark","Light"])

bg = "#0e1117" if theme=="Dark" else "white"
text = "white" if theme=="Dark" else "black"

st.markdown(f"""
<style>
.stApp {{
background-color:{bg};
color:{text};
}}
</style>
""", unsafe_allow_html=True)


st.title("ULTIMATE Institutional BTC Dashboard")


# ---------------- SAFE REQUEST ----------------

def safe_get(url):

    try:

        r=requests.get(url, timeout=10)

        if r.status_code==200:

            return r.json()

        else:

            return None

    except:

        return None


# ---------------- PRICE ----------------

@st.cache_data(ttl=2)

def get_price():

    data=safe_get(

    "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

    )

    if data and "price" in data:

        return float(data["price"])

    return 0


# ---------------- TRADES ----------------

@st.cache_data(ttl=2)

def get_trades():

    data=safe_get(

    "https://api.binance.com/api/v3/trades?symbol=BTCUSDT&limit=100"

    )

    if not data:

        return pd.DataFrame()


    df=pd.DataFrame(data)

    df["price"]=df["price"].astype(float)

    df["qty"]=df["qty"].astype(float)

    df["time"]=pd.to_datetime(df["time"], unit="ms")

    df["side"]=df["isBuyerMaker"].apply(

        lambda x:"SELL" if x else "BUY"

    )

    return df


# ---------------- DEPTH ----------------

@st.cache_data(ttl=2)

def get_depth():

    data=safe_get(

    "https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=10"

    )

    if not data:

        return pd.DataFrame(), pd.DataFrame()


    bids=pd.DataFrame(data["bids"], columns=["price","qty"]).astype(float)

    asks=pd.DataFrame(data["asks"], columns=["price","qty"]).astype(float)

    return bids, asks


# ---------------- FETCH ----------------

price=get_price()

trades=get_trades()

bids, asks=get_depth()


# ---------------- CALC ----------------

buy=trades[trades.side=="BUY"].qty.sum() if not trades.empty else 0

sell=trades[trades.side=="SELL"].qty.sum() if not trades.empty else 0

total=buy+sell

buy_per=(buy/total*100) if total>0 else 0

cvd=buy-sell


# ---------------- METRICS ----------------

c1,c2,c3,c4=st.columns(4)

c1.metric("Price", price)

c2.metric("Buy %", round(buy_per,2))

c3.metric("Sell %", round(100-buy_per,2))

c4.metric("CVD", round(cvd,2))


# ---------------- HEATMAP ----------------

st.subheader("Liquidity Heatmap")

fig=go.Figure()

if not bids.empty:

    fig.add_bar(x=bids.price, y=bids.qty, name="Bids")

if not asks.empty:

    fig.add_bar(x=asks.price, y=asks.qty, name="Asks")

st.plotly_chart(fig, use_container_width=True)


# ---------------- TRADES ----------------

st.subheader("Trades")

st.dataframe(trades)


# ---------------- EXPORT ----------------

csv=trades.to_csv(index=False).encode()

st.download_button(

"Export CSV",

csv,

"btc_trades.csv",

"text/csv"

)


# ---------------- AUTO REFRESH ----------------

time.sleep(3)

st.rerun()
