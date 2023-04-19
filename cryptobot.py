import requests
import json
import hashlib
import hmac
import time
import pandas as pd
from datetime import datetime, timezone, timedelta
import numpy as np
import smtplib
from email.message import EmailMessage
import ssl


class FutureBot:

    def __init__(self):
        self.url = "https://api.kucoin.com/api/v1/market/candles"
        self.symbol = "BTC-USDT"
        self.type = "30min"
        self.startAt = 1667221200
        # self.endAt = 1669813200
        self.nonce = str(int(time.time() * 1000))
        self.api_key = "YOUR_API_KEY"
        self.api_secret = b"YOUR_API_SECRET"
        self.present_signal = ""

    def core_logic(self):
        headers = {
            "KC-API-KEY": self.api_key,
            "KC-API-NONCE": self.nonce,
            "KC-API-SIGNATURE": "",
            "Content-Type": "application/json"
        }

        payload = {
            "symbol": self.symbol,
            "type": self.type,
            "startAt": self.startAt
            # "endAt": self.endAt
        }
        payload_json = json.dumps(payload)
        payload_bytes = payload_json.encode('utf-8')
        signature = hmac.new(self.api_secret, payload_bytes, hashlib.sha256).hexdigest()
        headers["KC-API-SIGNATURE"] = signature

        response = requests.get(self.url, headers=headers, params=payload)
        print(response.json())
        if response.status_code != 200:
            print("Error: HTTP status code", response.status_code)
            time.sleep(120)
            self.core_logic()

        try:
            data = list(response.json()['data'])
            print(data)
            if not isinstance(data, list) or len(data) < 60:
                print("Error: unexpected data format")
                exit()
        except (json.JSONDecodeError, KeyError):
            print("Error: unable to parse response")
            exit()

        df = pd.DataFrame(data, columns=['timestamp', 'open', 'close', 'high', 'low', 'volume', 'turnover'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

        sydney_tz = timezone(timedelta(hours=11))
        df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(sydney_tz)
        df.set_index('timestamp', inplace=True)
        df = df.iloc[::-1]
        # df['MA5'] = df['close'].rolling(window=5).mean()
        # df['MA10'] = df['close'].rolling(window=10).mean()

        df['MA5'] = df['close'].ewm(span=5, adjust=False).mean()
        df['MA10'] = df['close'].ewm(span=10, adjust=False).mean()

        # df['Signal'] = np.where(df['MA5'] > df['MA10'], 'buy', 'sell')
        df['Signal'] = np.where(df['MA5'] - df['MA10'] >= 2, 'buy', 'sell')
        print(df)
        if df['Signal'].iloc[-1] != self.present_signal and self.present_signal!="":
            print ("trigger signal", self.present_signal)
            self.present_signal = df['Signal'].iloc[-1]
            self.send_notification(self.present_signal, df['close'].iloc[-1])
        else:
            print ("no change")
            self.present_signal = df['Signal'].iloc[-1]
        return df

    def send_notification(self, signal, price):
        email_sender = "anudeepbalagam@gmail.com"
        pwd = "*************"
        receiver = 'anudeepbalagam@gmail.com'
        subject = str(signal) + " Bot Notification"
        body = str(signal) + " for price" + str(price)
        em = EmailMessage()
        em["From"] = email_sender
        em["To"] = receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, pwd)
            smtp.sendmail(email_sender, receiver, em.as_string())


