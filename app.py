import streamlit as st
import websocket
import json
import threading
import pandas as pd
import plotly.graph_objects as go
import time

st.set_page_config(layout="wide")

st.title("₿ Hedge Fund Order Flow Dashboard")


# -------------------
# STATE INIT
# -------------------

if "data" not in st.session_state:

    st.session_state.data = {

        "buy": 0.0,
        "sell": 0.0,
        "cvd": 0.0,
        "price": 0.0,
        "trades": [],
        "whales": [],
        "started": False

    }


# -------------------
# BINANCE WS
# -------------------

def start_ws():

    def binance():

        def on_msg(ws, msg):

            d = json.loads(msg)

            price = float(d['p'])
            qty = float(d['q'])

            st.session_state.data["price"] = price

            if d['m']:

                st.session_state.data["sell"] += qty
                st.session_state.data["cvd"] -= qty
                side = "SELL"

            else:

                st.session_state.data["buy"] += qty
                st.session_state.data["cvd"] += qty
                side = "BUY"

            trade = ["Binance", price, qty, side]

            st.session_state.data["trades"].append(trade)

            if qty > 1:

                st.session_state.data["whales"].append(trade)


        ws = websocket.WebSocketApp(

            "wss://stream.binance.com:9443/ws/btcusdt@trade",
            on_message=on_msg

        )

        ws.run_forever()


    thread = threading.Thread(target=binance)

    thread.daemon = True

    thread.start()


# start only once

if not st.session_state.data["started"]:

    start_ws()

    st.session_state.data["started"] = True


# -------------------
# CALCULATIONS
# -------------------

buy = st.session_state.data["buy"]

sell = st.session_state.data["sell"]

total = buy + sell

buy_per = (buy/total*100) if total > 0 else 0


# -------------------
# METRICS
# -------------------

c1,c2,c3,c4 = st.columns(4)

c1.metric("BTC Price", st.session_state.data["price"])

c2.metric("Buy %", round(buy_per,2))

c3.metric("Sell %", round(100-buy_per,2))

c4.metric("CVD", round(st.session_state.data["cvd"],2))


# -------------------
# GAUGE
# -------------------

fig = go.Figure(go.Indicator(

mode="gauge+number",

value=buy_per,

title={'text': "Buy Pressure"},

gauge={'axis': {'range': [0,100]}}

))

st.plotly_chart(fig, use_container_width=True)


# -------------------
# TRADES
# -------------------

st.subheader("Trade Tape")

df = pd.DataFrame(

st.session_state.data["trades"][-50:],

columns=["Exchange","Price","Qty","Side"]

)

st.dataframe(df)


# -------------------
# WHALES
# -------------------

st.subheader("Whale Alerts")

wf = pd.DataFrame(

st.session_state.data["whales"][-20:],

columns=["Exchange","Price","Qty","Side"]

)

st.dataframe(wf)


# -------------------
# AUTO REFRESH
# -------------------

time.sleep(2)

st.rerun()
