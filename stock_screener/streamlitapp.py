import streamlit as st
import pandas as pd
import numpy as np
import glob
import plotly.express as px
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from ibkr import TOKEN, QUERYID, IBKR

pd.options.plotting.backend = "plotly"


@st.cache_data
def fetchdata():
    ibkr = IBKR(TOKEN, QUERYID)
    ibkr.get_data()
    ibkr.get_trades()
    ibkr.get_dividends()
    div = ibkr.dividends
    ibkr.get_current_porfolio()
    data = ibkr.portfolio
    return div, data, ibkr


div, data, ibkr = fetchdata()

st.sidebar.image("logo.png")


st.title("Gerardo's Retirement Savings")

st.sidebar.title("Portfolio Tracking and Modeling")
panel = st.sidebar.selectbox(
    "What aspect of your finances do you want to see?",
    ("Porfolio Summary", "Dividends", "Investor metrics", "Valuations", "Watch List"),
)


st.sidebar.markdown(
    "###### made by [Gerardo Suarez](https://mcditoos.github.io), You can find me on Github as [@mcditoos](https://github.com/mcditoos)"
)


if panel == "Porfolio Summary":
    st.subheader("Basic Summary")
    st.caption(f"I have been investing in stocks since {ibkr.trades.tradeDate.min()}")

    mask = div.symbol == ""
# The code snippet `currentcash =
# round(float(ibkr.get_bytag("EquitySummaryByReportDateInBase")[["reportDate",
# "cash"]].sort_values(by="reportDate").iloc[-1].cash), 2)` is calculating the
# current cash balance in the portfolio. Here's a breakdown of what each part of
# the code is doing:
    currentcash = round(
        float(
            ibkr.get_bytag("EquitySummaryByReportDateInBase")[["reportDate", "cash"]]
            .sort_values(by="reportDate")
            .iloc[-1]
            .cash
        ),
        2,
    )
    initial = div[mask].usd_div.sum().round(2)
    stockstotal = data.positionValueInBase.astype(float).sum().round(2)
    st.caption(
        "There is a little discrepancy in stock prices between the yahoo API and IBKR, so perhaps I should change APIs. For now I think the difference is ok, though it is about 15$ I'm guessing due to the MXN positions"
    )
    st.caption(f"Number of Stocks in Portfolio: {len(data)}")
    st.caption(f"Current Value of Stocks: {stockstotal}")
    st.caption(f"IDLE Cash: {currentcash}")
    st.caption(f"Current Value of portfolio: {currentcash+stockstotal}")
    st.caption(f"Initial investment: {initial} This is broken I definetely invested more there should be around a 2000 difference only")
    st.caption(f"Current PnL: {currentcash+stockstotal-initial}")
    st.caption(
        f"Current PnL: {np.round((currentcash+stockstotal-initial)/initial *100,2)} %"
    )
    st.caption(f"Earned from dividends: {div[~mask].usd_div.sum().round(2)}")

    ## Plot for positions and percentages
    fig = px.pie(
        data,
        values="positionValueInBase",
        names="symbol",
        hole=0.4,
        width=700,
        height=700,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label+value",
        textfont_color="#0d0c0c",
        marker=dict(line=dict(color="#000000", width=2)),
    )
    fig.update_layout(font={"size": 18})
    st.plotly_chart(fig)

    ## Plot By Holding number in Sector
    st.title("By Holding number in Sector")
    frame = data["sector"].value_counts().to_frame().reset_index()
    fig2 = px.pie(
        frame, values="count", names="sector", hole=0.4, width=700, height=700
    )
    fig2.update_traces(
        textposition="inside",
        textinfo="percent+label+value",
        textfont_color="#0d0c0c",
        marker=dict(line=dict(color="#000000", width=2)),
    )
    fig2.update_layout(font={"size": 18})
    st.plotly_chart(fig2)

    ## Plot By Holding number in Sector
    st.title("By Money in Sector")
    data["positionValueInBase"] = data["positionValueInBase"].astype(float)
    frame = (
        data[["positionValueInBase", "sector"]].groupby(by="sector").sum().reset_index()
    )
    fig3 = px.pie(
        frame,
        values="positionValueInBase",
        names="sector",
        hole=0.4,
        width=700,
        height=700,
    )
    fig3.update_traces(
        textposition="inside",
        textinfo="percent+label+value",
        textfont_color="#0d0c0c",
        marker=dict(line=dict(color="#000000", width=2)),
    )
    fig3.update_layout(font={"size": 18})
    st.plotly_chart(fig3)


if panel == "Dividends":
    st.header("Dividend information by source")

    dividendstocks = set(div.symbol)  #
    dividendstocks.remove("")
    dd = div[div.symbol != ""]
    dd["InPortfolio"] = [i in set(data.symbol) for i in dd.symbol]
    fig = px.bar(
        dd,
        y="symbol",
        x="usd_div",
        color="InPortfolio",
        title="Dividends Received (Historical)",
        labels={
            "usd_div": "Amount (USD)",
            "symbol": "Stock",
            "InPortfolio": "Currently Owned",
        },
        orientation="h",
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending", "automargin": False}, height=600
    )  # add only this line
    st.plotly_chart(fig, theme=None)
    st.header("Dividend information by Month")
    dd["month"] = pd.to_datetime(dd.settleDate).dt.month
    dd["year"] = pd.to_datetime(dd.settleDate).dt.year
    fd = dd[["month", "year", "usd_div"]].groupby(["month", "year"]).sum().reset_index()
    fig = go.Figure()
    for i in set(fd.year):
        fig.add_trace(
            go.Bar(
                x=fd[fd.year == i]["month"],
                y=fd["usd_div"],
                name=f"{i}",
            )
        )

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        barmode="group",
        xaxis_tickangle=-45,
        xaxis=dict(
            tickvals=list(range(1, 13)),
            ticktext=[
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ],
        ),
        title="Dividends By Month and Year",
    )
    st.plotly_chart(fig)

    st.header("Are Dividends Received Growing?")
    owned = set(dd[dd.InPortfolio == True].symbol)
    option = st.selectbox(
        "How would you like to be contacted?",
        owned,
        placeholder="Select stock to check...",
    )

    st.write("You selected:", option)
    if option is not None:
        fig = px.line(
            dd[dd.symbol == option],
            x="settleDate",
            y="per_share",
            title=f"Dividends of {option} in Time",
            labels={"per_share": "Amount per share(USD)", "settleDate": "Date"},
        )
        st.plotly_chart(fig)
        fig = px.line(
            dd[dd.symbol == option],
            x="settleDate",
            y="shares",
            title=f"Shares of {option} in Time",
            labels={"shares": "Shares", "settleDate": "Date"},
        )
        st.plotly_chart(fig)

if panel == "Watch List":
    df = pd.read_csv("watchlist.csv")
    edited_df = st.data_editor(df)


if panel == "Investor metrics":
    st.header("Sharpe Ratio")
