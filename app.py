import streamlit as st
import websocket
import json
import threading
import pandas as pd
import plotly.graph_objects as go
import time

# ------------------------
# CONFIG
# ------------------------

st.set_page_config(layout="wide")

st.title("₿ Hedge Fund Order Flow Dashboard")


# ------------------------
# STATE
# ------------------------

if "buy" not in st.session_state:

    st.session_state.buy = 0.0

if "sell" not in st.session_state:

    st.session_state.sell = 0.0

if "cvd" not in st.session_state:

    st.session_state.cvd = 0.0

if "price" not in st.session_state:

    st.session_state.price = 0.0

if "trades" not in st.session_state:

    st.session_state.trades = []

if "whales" not in st.session_state:

    st.session_state.whales = []


# ------------------------
# BINANCE
# ------------------------

def binance():

    def on_msg(ws, msg):

        data = json.loads(msg)

        price = float(data['p'])
        qty = float(data['q'])

        st.session_state.price = price

        if data['m']:

            st.session_state.sell += qty

            st.session_state.cvd -= qty

            side = "SELL"

        else:

            st.session_state.buy += qty

            st.session_state.cvd += qty

            side = "BUY"


        trade = ["Binance", price, qty, side]

        st.session_state.trades.append(trade)


        if qty > 5:

            st.session_state.whales.append(trade)


    ws = websocket.WebSocketApp(

        "wss://stream.binance.com:9443/ws/btcusdt@trade",

        on_message=on_msg

    )

    ws.run_forever()


# ------------------------
# COINBASE
# ------------------------

def coinbase():

    def on_open(ws):

        ws.send(json.dumps({

            "type": "subscribe",

            "channels": [{"name": "matches",

            "product_ids": ["BTC-USD"]}]

        }))


    def on_msg(ws, msg):

        data = json.loads(msg)

        if data.get("type") == "match":

            price = float(data["price"])

            qty = float(data["size"])


            if data["side"] == "sell":

                st.session_state.sell += qty

                st.session_state.cvd -= qty

                side = "SELL"

            else:

                st.session_state.buy += qty

                st.session_state.cvd += qty

                side = "BUY"


            trade = ["Coinbase", price, qty, side]

            st.session_state.trades.append(trade)


            if qty > 5:

                st.session_state.whales.append(trade)


    ws = websocket.WebSocketApp(

        "wss://ws-feed.exchange.coinbase.com",

        on_open=on_open,

        on_message=on_msg

    )

    ws.run_forever()


threading.Thread(target=binance, daemon=True).start()

threading.Thread(target=coinbase, daemon=True).start()


# ------------------------
# CALCULATIONS
# ------------------------

buy = st.session_state.buy

sell = st.session_state.sell

total = buy + sell


if total > 0:

    buy_per = buy / total * 100

else:

    buy_per = 0


# ------------------------
# TOP METRICS
# ------------------------

c1,c2,c3,c4 = st.columns(4)

c1.metric("BTC Price", f"${st.session_state.price}")

c2.metric("Buy %", round(buy_per,2))

c3.metric("Sell %", round(100-buy_per,2))

c4.metric("CVD", round(st.session_state.cvd,2))


# ------------------------
# GAUGE
# ------------------------

fig = go.Figure(go.Indicator(

mode="gauge+number",

value=buy_per,

title={'text': "Buy Pressure"},

gauge={'axis': {'range': [0,100]}}

))

st.plotly_chart(fig, use_container_width=True)


# ------------------------
# CVD CHART
# ------------------------

cvd_df = pd.DataFrame({

"CVD":[st.session_state.cvd]

})

cvd_fig = go.Figure()

cvd_fig.add_trace(go.Scatter(

y=cvd_df["CVD"],

mode='lines',

name='CVD'

))

st.plotly_chart(cvd_fig, use_container_width=True)


# ------------------------
# TRADES
# ------------------------

st.subheader("Trade Tape")

df = pd.DataFrame(

st.session_state.trades[-50:],

columns=["Exchange","Price","Qty","Side"]

)

st.dataframe(df)


# ------------------------
# WHALES
# ------------------------

st.subheader("Whale Alerts (>5 BTC)")

whale_df = pd.DataFrame(

st.session_state.whales[-20:],

columns=["Exchange","Price","Qty","Side"]

)

st.dataframe(whale_df)


time.sleep(1)

st.rerun()
