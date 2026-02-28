import streamlit as st
import websocket
import json
import threading
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")

st.title("⚡ Realtime BTC Liquidation Dashboard (FREE)")

# -----------------------
# SESSION STATE INIT
# -----------------------

if "liquidations" not in st.session_state:
    st.session_state.liquidations = []

if "trades" not in st.session_state:
    st.session_state.trades = []

if "bids" not in st.session_state:
    st.session_state.bids = []

if "asks" not in st.session_state:
    st.session_state.asks = []

if "oi" not in st.session_state:
    st.session_state.oi = 0


# -----------------------
# LIQUIDATION STREAM
# -----------------------

def liquidation_ws():

    def on_message(ws, message):

        data = json.loads(message)

        if "o" in data:

            o = data["o"]

            price = float(o["p"])
            qty = float(o["q"])
            side = o["S"]

            st.session_state.liquidations.append({

                "time": datetime.now(),
                "price": price,
                "qty": qty,
                "side": side

            })

    ws = websocket.WebSocketApp(

        "wss://fstream.binance.com/ws/!forceOrder@arr",

        on_message=on_message

    )

    ws.run_forever()


# -----------------------
# TRADE STREAM
# -----------------------

def trade_ws():

    def on_message(ws, message):

        data = json.loads(message)

        price = float(data["p"])
        qty = float(data["q"])

        st.session_state.trades.append({

            "time": datetime.now(),
            "price": price,
            "qty": qty

        })

    ws = websocket.WebSocketApp(

        "wss://fstream.binance.com/ws/btcusdt@aggTrade",

        on_message=on_message

    )

    ws.run_forever()


# -----------------------
# DEPTH STREAM
# -----------------------

def depth_ws():

    def on_message(ws, message):

        data = json.loads(message)

        st.session_state.bids = data["b"]
        st.session_state.asks = data["a"]

    ws = websocket.WebSocketApp(

        "wss://fstream.binance.com/ws/btcusdt@depth20@100ms",

        on_message=on_message

    )

    ws.run_forever()


# -----------------------
# OPEN INTEREST STREAM
# -----------------------

def oi_ws():

    def on_message(ws, message):

        data = json.loads(message)

        st.session_state.oi = float(data["o"])

    ws = websocket.WebSocketApp(

        "wss://fstream.binance.com/ws/btcusdt@openInterest",

        on_message=on_message

    )

    ws.run_forever()


# -----------------------
# START THREADS
# -----------------------

threading.Thread(target=liquidation_ws, daemon=True).start()
threading.Thread(target=trade_ws, daemon=True).start()
threading.Thread(target=depth_ws, daemon=True).start()
threading.Thread(target=oi_ws, daemon=True).start()


# -----------------------
# DISPLAY METRICS
# -----------------------

st.metric("Open Interest", st.session_state.oi)


# -----------------------
# LIQUIDATION HEATMAP
# -----------------------

st.subheader("🔥 Liquidations")

liq_df = pd.DataFrame(st.session_state.liquidations[-100:])

st.dataframe(liq_df)


# -----------------------
# WHALE DETECTION
# -----------------------

st.subheader("🐋 Whale Trades")

trade_df = pd.DataFrame(st.session_state.trades[-200:])

if not trade_df.empty:

    whale_df = trade_df[trade_df.qty > 5]

    st.dataframe(whale_df)


# -----------------------
# LIQUIDITY HEATMAP
# -----------------------

st.subheader("📚 Liquidity Heatmap")

if st.session_state.bids:

    bids = pd.DataFrame(st.session_state.bids, columns=["price","qty"]).astype(float)

    asks = pd.DataFrame(st.session_state.asks, columns=["price","qty"]).astype(float)

    fig = go.Figure()

    fig.add_bar(x=bids.price, y=bids.qty, name="Bids")

    fig.add_bar(x=asks.price, y=asks.qty, name="Asks")

    st.plotly_chart(fig, use_container_width=True)


# -----------------------
# EXPORT
# -----------------------

if not liq_df.empty:

    csv = liq_df.to_csv(index=False).encode()

    st.download_button(

        "Download Liquidations CSV",

        csv,

        "liquidations.csv"

    )


# -----------------------
# AUTO REFRESH
# -----------------------

st.experimental_rerun()
