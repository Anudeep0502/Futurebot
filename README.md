# Futurebot
Cryptocurrency Trading Signal Generator:
This is a Python script for a trading bot that retrieves market data from the KuCoin API, performs technical analysis on the data to generate trading signals, and sends email notifications to the user when a signal is triggered. 

The script is defined in a class called FutureBot which has the following methods:

__init__(self): Initializes the class with various parameters including the API URL, symbol, time interval, start time, API key, API secret, and present signal.

core_logic(self): Implements the core logic of the trading bot, which retrieves market data from the KuCoin API, processes the data to calculate technical indicators, generates trading signals based on the indicators, and sends email notifications to the user when a signal is triggered.

send_notification(self, signal, price): Sends an email notification to the user with the trading signal and the current price.

The core_logic() method uses the requests library to make an API call to KuCoin with the required parameters such as symbol, time interval, and start time. The API call is authenticated with the API key and secret by generating a signature using the hmac library. The API response is then processed using the pandas library to convert the JSON data into a pandas dataframe, which is then used to calculate technical indicators such as the exponential moving averages (EMA) for 5 and 10 periods. The trading signal is then generated based on the difference between the EMAs, and if the signal changes from the previous signal, an email notification is sent to the user with the new signal and the current price.
