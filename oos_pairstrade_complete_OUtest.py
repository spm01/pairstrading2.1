#importing packages
from polars_bloomberg import BQuery
from datetime import date
import numpy as np
import polars as pl
import pandas as pd
import altair as alt
from statsmodels.tsa.stattools import coint

#setting up my env
import os
os.chdir('c:/Users/Sean/OneDrive/Desktop/Python/finance/pairstrade')

#pulling in the functions that I've made!! (first time doing this)
from pairstrade import run_strategy_deviation, run_strategy_bollinger

#importing data
df_pandas = pd.read_csv('KO_PEP_DATA_COMPLETE.csv')
df_oos = pl.from_pandas(df_pandas)

#setting the values for the test
dev_window, dev_k = 52, 1.4389999999999517
boll_window, boll_k = 90, 1.553999999999939

def add_rolling_cointegration(df, window):
    ko = df['KO US EQUITY'].to_numpy()
    pep = df['PEP US EQUITY'].to_numpy()

    p_values = np.full(len(df), np.nan)

    for i in range(window, len(df)):
        ko_slice = ko[i-window:i]
        pep_slice = pep[i-window:i]

        _, p_val, _ = coint(ko_slice, pep_slice)
        p_values[i] = p_val
    return df.with_columns(pl.Series('coint_p', p_values))

#add OU half life test
def add_rolling_halflife(df, window):
    ko = df['KO US EQUITY'].to_numpy()
    pep = df['PEP US EQUITY'].to_numpy()
    half_lives = np.full(len(df), np.nan)

    for i in range(window, len(df)):
        ko_slice = ko[i-window:i]
        pep_slice = pep[i-window:i]

        # build the spread
        spread = ko_slice - pep_slice  # or your hedge-ratio-adjusted version

        # AR(1) regression on the spread
        spread_lag = spread[:-1]
        spread_diff = np.diff(spread)
        phi = np.polyfit(spread_lag, spread_diff, 1)[0]  # slope coefficient

        # OU half-life
        phi_ar1 = 1 + phi
        if phi_ar1 > 0 and phi_ar1 < 1:  # only valid mean-reverting range
            half_lives[i] = -np.log(2) / np.log(phi_ar1)
        else:
            half_lives[i] = np.nan  # not mean-reverting, don't trade

    return df.with_columns(pl.Series('half_life', half_lives))

# run it right after cointegration
df_oos_coint = add_rolling_cointegration(df_oos, window=120)
df_oos_coint = add_rolling_halflife(df_oos_coint, window=120)

#running the OOS test
#passing in new data but with the old parameters
df_pnl_dev, sharpe_dev = run_strategy_deviation(df_oos_coint, dev_window, dev_k)
df_pnl_boll, sharpe_boll = run_strategy_bollinger(df_oos_coint, boll_window, boll_k)

df_pnl_dev = df_pnl_dev.with_columns(
    pl.when((pl.col('coint_p') > 0.05) | (pl.col('half_life') > 40))
    .then(0)
    .otherwise(pl.col("Target Position"))
    .alias("Target Position")
)

df_pnl_boll = df_pnl_boll.with_columns(
    pl.when((pl.col('coint_p') > 0.05) | (pl.col('half_life') > 40))
    .then(0)
    .otherwise(pl.col("Target Position"))
    .alias("Target Position")
)

def recalculate_metrics(df):
    df = df.with_columns([
        pl.col('Target Position').shift(1).alias("Position Held")
    ]).with_columns([
        ((pl.col("Ret_KO") - pl.col('Ret_PEP')) * pl.col('Position Held')).alias('Strategy_Daily_Return')
    ]).with_columns([
        pl.col('Strategy_Daily_Return').fill_null(0).cum_sum().alias('Cumulative_PnL')
    ])

# Simple Sharpe calculation (simplified)
    daily_ret = df['Strategy_Daily_Return']
    sharpe = (daily_ret.mean() / daily_ret.std() * (252**0.5)) if daily_ret.std() != 0 else 0
    return df, sharpe

df_pnl_dev, sharpe_dev = recalculate_metrics(df_pnl_dev)
df_pnl_boll, sharpe_boll = recalculate_metrics(df_pnl_boll)


#create a comparison table
performance_summary = pl.DataFrame({
    "Metric": ["Sharpe Ratio", "Total P&L (%)"],
    "Deviation Method": [
        str(round(sharpe_dev, 3)), 
        f"{df_pnl_dev['Cumulative_PnL'][-1] * 100:.2f}%"
    ],
    "Bollinger Method": [
        str(round(sharpe_boll, 3)), 
        f"{df_pnl_boll['Cumulative_PnL'][-1] * 100:.2f}%"
    ]
})

print(performance_summary)

#prepare data for graphing
#take the date and PnL from each function and add a label
dev_plot = df_pnl_dev.select([
    pl.col("date"), 
    pl.col("Cumulative_PnL"), 
    pl.lit("Deviation").alias("Strategy")
])

boll_plot = df_pnl_boll.select([
    pl.col("date"), 
    pl.col("Cumulative_PnL"), 
    pl.lit("Bollinger").alias("Strategy")
])

#stack them on top of each other
combined_df = pl.concat([dev_plot, boll_plot])

#create the chart
chart = alt.Chart(combined_df).mark_line().encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('Cumulative_PnL:Q', title='Cumulative Return', axis=alt.Axis(format='.1%')),
    color=alt.Color('Strategy:N', scale=alt.Scale(domain=['Deviation', 'Bollinger'], range=['#1f77b4', '#ff7f0e'])),
    tooltip=['date', 'Cumulative_PnL', 'Strategy']
).properties(
    title='Out-of-Sample Performance Comparison [Cointegrated] (2024/2025)',
    width=800,
    height=400
).interactive() 

#display the chart in browswer
chart.show()
