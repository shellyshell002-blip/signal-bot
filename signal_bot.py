import os
import time
import logging
from datetime import datetime

import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException

from telegram import Bot


# =========================
# CONFIGURATION
# =========================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")


SYMBOL = "BTCUSDT"
INTERVAL = "5m"

PAPER_MODE = True   # Change to False after testing


# =========================
# CONNECTIONS
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


client = Client(
    BINANCE_API_KEY,
    BINANCE_SECRET_KEY
)


telegram_bot = Bot(
    token=TELEGRAM_BOT_TOKEN
)


# =========================
# TELEGRAM ALERT
# =========================

def send_message(text):
    try:
        telegram_bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=text
        )
    except Exception as e:
        logging.error(e)
    # =========================
# MARKET DATA
# =========================

def get_candles():
    try:
        candles = client.get_klines(
            symbol=SYMBOL,
            interval=INTERVAL,
            limit=100
        )

        prices = []

        for candle in candles:
            prices.append(float(candle[4]))

        return prices

    except BinanceAPIException as e:
        logging.error(e)
        return []


# =========================
# STRATEGY
# =========================

def moving_average(values, period):
    if len(values) < period:
        return None

    return sum(values[-period:]) / period


def check_signal():

    prices = get_candles()

    if not prices:
        return "NO DATA"

    short_ma = moving_average(prices, 10)
    long_ma = moving_average(prices, 30)

    if short_ma is None or long_ma is None:
        return "WAIT"


    current_price = prices[-1]


    if short_ma > long_ma:
        signal = "BUY"

    elif short_ma < long_ma:
        signal = "SELL"

    else:
        signal = "HOLD"


    message = f"""
📊 Trading Signal

Symbol: {SYMBOL}
Price: {current_price}

Short MA: {round(short_ma,2)}
Long MA: {round(long_ma,2)}

Signal: {signal}

Time:
{datetime.now()}
"""


    send_message(message)

    return signal
  # =========================
# BOT RUN LOOP
# =========================

def main():

    send_message(
        f"""
🤖 Signal Bot Started

Symbol: {SYMBOL}
Mode: {"PAPER" if PAPER_MODE else "LIVE"}

Monitoring every {INTERVAL}
"""
    )


    while True:

        try:
            signal = check_signal()

            logging.info(
                f"Current signal: {signal}"
            )


            # Wait before checking again
            time.sleep(300)


        except Exception as e:

            logging.error(e)

            send_message(
                f"⚠️ Bot Error:\n{e}"
            )

            time.sleep(60)



# =========================
# START PROGRAM
# =========================

if __name__ == "__main__":
    main()
