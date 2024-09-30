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
    def __init__(self, TOKEN, QUERYID,file):
        self.FLEX_URL = "https://gdcdyn.interactivebrokers.com/Universal/servlet/"
        self.REQUEST_URL = FLEX_URL + "FlexStatementService.SendRequest"
        self.STMT_URL = FLEX_URL + "FlexStatementService.GetStatement"
        self.TOKEN = TOKEN
        self.QUERYID = QUERYID
        self.file =file

    def submit_request(self, url: str, token: str, query: str) -> requests.Response:
        """Post a query to the API access point, along with an authentication token.
        Retry with a progressive timeout window.
        """
        MAX_REQUESTS = 3
        TIMEOUT_INCREMENT = 5
        response = None
        req_count = 1
        if self.file:
            return self.file
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
        if self.file:
            tree = ET.parse(self.file)
            root = tree.getroot()
            self.root = root
            return 
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
                self.remove_empty_nested_dict(v)
                if not bool(v):
                    del d[k]
            elif v == "" or v == "0.0" or v == "0.0 ()":
                del d[k]

    def parse_data(self):
        elements = [i for i in self.root.iter()]
        initial_dict={elements[i].tag:elements[i].attrib for i in range(len(elements))}
        self.remove_empty_nested_dict(initial_dict)
        self.data=initial_dict
        print(set(list(initial_dict.keys() )))
        nonempty = []
        for i in elements:
            if len(i.attrib) != 0:
                nonempty.append(i)
        self.data = nonempty

    def get_bytag(self, tag):
        """The tag can be
        'AssetSummary',
        'CashTransaction',
        'ChangeInDividendAccrual',
        'ChangeInNAV',
        'ChangeInPositionValue',
        'CorporateAction',
        'EquitySummaryByReportDateInBase',
        'FIFOPerformanceSummaryUnderlying',
        'FlexQueryResponse',
        'FlexStatement',
        'FlexStatements',
        'InterestAccrualsCurrency',
        'Lot',
        'OpenDividendAccrual',
        'OpenPosition',
        'Order',
        'PriorPeriodPosition',
        'SecurityInfo',
        'StatementOfFundsLine',
        'SymbolSummary',
        'TierInterestDetail',
        'Trade',
        'UnbundledCommissionDetail'
        """
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
        frame = pd.DataFrame.from_dict(dividends)[wanted_fields]
        self.remove_rows_with_negative_values(frame, "amount")
        frame.drop_duplicates(inplace=True)
        frame["per_share"] = frame["description"].apply(self.get_shares)
        frame["shares"] = (
            (frame["amount"] / frame["per_share"])
            .replace(np.inf, 0)
            .replace(np.NaN, 0)
            .round()
            .astype(int)
        )
        frame["usd_div"] = frame["amount"] * frame["fxRateToBase"].astype(float)
        self.dividends = frame

    def get_current_porfolio(self):
        frame = self.get_bytag("OpenPosition")
        frame.replace("", np.nan, inplace=True)
        frame.dropna(how="all", axis=1, inplace=True)
        frame = frame[frame.assetCategory != "OPT"]
        self.portfolio = frame.drop(
            [
                "accountId",
                "acctAlias",
                "assetCategory",
                "conid",
                "securityIDType",
                "cusip",
                "isin",
                "multiplier",
                "fineness",
                "weight",
                "side",
                "levelOfDetail",
                "securityID",
            ],
            axis=1,
        )
        tickers = list(self.portfolio.symbol)
        tickerss = Ticker(tickers)
        data = tickerss.asset_profile
        data = pd.DataFrame(data).transpose()
        portfolio = self.portfolio.reset_index()
        portfolio["sector"] = data.reset_index()["sector"]
        self.portfolio = portfolio
