# Data for the Flex queries
TOKEN = "83191847859487227934479"
QUERYID = "766957"
# Import require libraries
import requests
import xml.etree.ElementTree as ET
import time
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import yfinance as yf
from yahooquery import Ticker

# Define URLS for enpoints
FLEX_URL = "https://gdcdyn.interactivebrokers.com/Universal/servlet/"
REQUEST_URL = FLEX_URL + "FlexStatementService.SendRequest"
STMT_URL = FLEX_URL + "FlexStatementService.GetStatement"


# The main part of this file the IBKR class to obtain my portfolio data
class IBKR:
    def __init__(self, TOKEN, QUERYID):
        self.FLEX_URL = "https://gdcdyn.interactivebrokers.com/Universal/servlet/"
        self.REQUEST_URL = FLEX_URL + "FlexStatementService.SendRequest"
        self.STMT_URL = FLEX_URL + "FlexStatementService.GetStatement"
        self.TOKEN = TOKEN
        self.QUERYID = QUERYID

    def submit_request(self, url: str, token: str, query: str) -> requests.Response:
        """Post a query to the API access point, along with an authentication token.
        Retry with a progressive timeout window.
        """
        MAX_REQUESTS = 3
        TIMEOUT_INCREMENT = 5
        response = None
        req_count = 1
        while not response:
            try:
                response = requests.get(
                    url,
                    params={"v": "3", "t": token, "q": query},
                    headers={"user-agent": "Java"},
                    timeout=req_count * TIMEOUT_INCREMENT,
                )
            except requests.exceptions.Timeout:
                if req_count >= MAX_REQUESTS:
                    raise
                else:
                    print("Request Timeout, re-sending...")
                    req_count += 1

        return response

    def get_data(self):
        """
        Gets my trading data from IBKR, first it gets the reference code to request for the data later it does
        """
        response = self.submit_request(
            url=self.REQUEST_URL, token=self.TOKEN, query=self.QUERYID
        )
        elem = ET.fromstring(response.content)
        data = {child.tag: child.text for child in elem}
        reference = data["ReferenceCode"]
        repeat = True
        while repeat:
            response2 = self.submit_request(
                url=self.STMT_URL, token=TOKEN, query=reference
            )
            elem2 = ET.fromstring(response2.content)
            self.root = ET.XML(response2.content)
            data2 = {child.tag: child.text for child in self.root}
            try:
                if data2["Status"] == "Warn":
                    time.sleep(30)
            except KeyError:
                repeat = False
                self.parse_data()

    def remove_empty_nested_dict(self, d):
        """
        Recursively remove desired elements from a nested dictionary
        """
        for k, v in list(d.items()):
            if isinstance(v, dict):
                remove_empty_nested_dict(v)
                if not bool(v):
                    del d[k]
            elif v == "" or v == "0.0" or v == "0.0 ()":
                del d[k]

    def parse_data(self):
        elements = [i for i in self.root.iter()]
        # initial_dict={elements[i].tag:elements[i].attrib for i in range(len(elements))}
        # self.remove_empty_nested_dict(initial_dict)
        # self.data=initial_dict
        # print(set(list(initial_dict.keys() )))
        nonempty = []
        for i in elements:
            if len(i.attrib) != 0:
                nonempty.append(i)
        self.data = nonempty

    def get_bytag(self, tag):
        elements = []
        for i in self.data:
            if i.tag == tag:
                elements.append(i.attrib)
        frame = pd.DataFrame.from_dict(elements)
        return frame

    def remove_rows_with_negative_values(self, df, column_name):
        """
        Removes all rows with negative values on a given column from a Pandas DataFrame.
        """
        df[column_name] = pd.to_numeric(df[column_name])
        df.drop(df[df[column_name] < 0].index, inplace=True)

    def remove_rows_with_value(self, df, column_name, value):
        """
        Removes all rows with a certain value for a given column from a Pandas DataFrame.
        """
        df.drop(df[df[column_name] == value].index, inplace=True)

    def get_trades(self):
        trades = self.get_bytag("Trade")
        wanted_fields = [
            "tradeDate",
            "currency",
            "fxRateToBase",
            "symbol",
            "description",
            "ibCommission",
            "tradePrice",
            "quantity",
            "fifoPnlRealized",
            "assetCategory",
        ]
        frame = pd.DataFrame.from_dict(trades)[wanted_fields]
        self.remove_rows_with_value(frame, "symbol", "USD.MXN")
        self.remove_rows_with_value(frame, "symbol", "EUR.USD")
        self.trades = frame

    def get_shares(self, string):
        try:
            s = string.split(" ").index("PER") - 1
            return float(string.split(" ")[s])
        except:
            return 0

    def get_dividends(self):
        dividends = self.get_bytag("CashTransaction")

        wanted_fields = [
            "symbol",
            "description",
            "currency",
            "fxRateToBase",
            "amount",
            "settleDate",
        ]
        frame = pd.DataFrame.from_dict(dividends)
        frame = frame[frame["assetCategory"] != "OPT"][wanted_fields]
        self.remove_rows_with_negative_values(frame, "amount")
        frame.drop_duplicates(inplace=True)
        frame["per_share"] = frame["description"].apply(self.get_shares)
        try:
            frame["shares"] = (
                (frame["amount"] / frame["per_share"])
                .replace(np.inf, 0)
                .round()
                .astype(int)
            )
            frame["usd_div"] = frame["amount"] * frame["fxRateToBase"].astype(float)
        except:
            pass

        self.dividends = frame

    def get_current_porfolio(self):
        self.get_trades()
        frame = self.trades
        frame = frame[frame["assetCategory"] != "OPT"]
        all_symbols = set(frame["symbol"])
        all_symbols = [i if "USD" not in i else "" for i in all_symbols]
        all_symbols = [x for x in all_symbols if x]
        portfolio_names = []

        def to_ticker(s):
            if s == "MXN":
                return ".MX"
            elif s == "EUR":
                return ".DE"
            else:
                return ""

        for i in all_symbols:
            by_sym = frame[frame["symbol"] == i]
            if by_sym["quantity"].astype(float).sum() != 0:
                portfolio_names.append(
                    {
                        "symbol": i + to_ticker(list(by_sym["currency"])[0]),
                        "shares": by_sym["quantity"].astype(float).sum(),
                        "avg_price": by_sym[by_sym["quantity"].astype(float) > 0][
                            "tradePrice"
                        ]
                        .astype(float)
                        .mean()
                        - (
                            by_sym["ibCommission"].astype(float).sum()
                            / by_sym["quantity"].astype(float).sum()
                        ),
                    }
                )
        portfolio = pd.DataFrame(portfolio_names)
        tickers = list(portfolio.symbol)
        tickerss = Ticker(tickers)
        # Retrieve each company's profile information
        data = tickerss.asset_profile
        data = pd.DataFrame(data).transpose()
        ticker = yf.Tickers(tickers)
        s = ticker.history(period="1h")["Open"].fillna(0).sum()

        def convertobase(df):
            if ".MX" in df["symbol"]:
                mxnusd = yf.Ticker("MXN=X").history("1h").Low.iloc[0]
                return df["price_pershare"] / mxnusd
            else:
                return df["price_pershare"]

        portfolio.set_index("symbol", inplace=True)
        portfolio["industry"] = data["industry"]
        portfolio["sector"] = data["sector"]
        portfolio["price_pershare"] = s
        portfolio.reset_index(inplace=True)
        portfolio["avg_usd"] = portfolio.apply(lambda x: convertobase(x), axis=1)
        portfolio["total_value"] = (portfolio["avg_usd"] * portfolio["shares"]).round(2)
        return portfolio
