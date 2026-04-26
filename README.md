# pairstrading2.1
Added the OU halflife test to confirm viability of trading
# pairstradingv2.0
Updated version of my pairs trading strategy that applies OU test before executing trades.
For context, the Ornstein-Uhlenbeck (OU) process half-life measures the expected time for a mean-reverting process to travel half the distance back to its long-term mean.

This is an extension of my prior work on a pairs trading implementation built around a simple mean reversion strategy and cointegration testing using **Coke (KO)** and **Pepsi (PEP)** as the test pair.  
I remain invested in whether or not there exists a higher performing methodology between the 'devation' approach v. traditional bollinger bands approach. 

---

## Overview

This project compares two mean reversion strategies across 2024 and 2025 out-of-sample data:

- **Deviation Strategy**: signals trades using the standard deviation *of* the standard deviation (volatility of volatility)
- **Bollinger Band Strategy**: the traditional approach, signaling trades when the spread exceeds `mean ± (σ × k)`

---

## Project Structure

| File | Description |
|---|---|
| `oos_pairstrade_complete_UOtest.py` | Out-of-sample test scripts with updated cointegration testing for 2024 and 2025 |
All other files remain unchanged from my prior pairstradingv1.0 and pairstradingv2.0 repositories.

---

## Strategy Functions

Two functions live in `pairstrade.py`:

**`run_strategy_deviation`**
Uses the deviation of the deviation to determine when to enter a trade. Requires an initial burn-in period to calculate the second-order deviation, which pushes the trading start date to approximately mid-year.

**`run_strategy_bollinger`**
Standard Bollinger Band implementation. Signals a trade when the spread relationship between KO and PEP exceeds a k-value multiple of the rolling standard deviation.

---
## Orenstein-Uhlenbeck Test Cointegration Testing
In brief, Ornstein-Uhlenbeck (OU) process half-life measures the expected time for a mean-reverting process to travel half the distance back to its long-term mean.

Why is that important for this exercise?  
This metric helps determine how quickly a system, such as financial spreads or physical velocities, returns to equilibrium. OU testing gives us a good window in being able to decide when/whether to execute a trade and how quickly we can expect the trade to last. 

As part of this exercise, we also need to set the window for evaluation, typically between 15-60 days. For this exercise, I picked 40 days as an even split with slight weight towards longer term trade windows. 

---
## Results
### COMPLETE  
This is an updated section to include the complete performance over 2024/2025 while accounting for a ~6month burn-in period during 2023 before strategy implementation. 
Compared to my prior v2.0 work, in v2.1, I only use 'complete' data which accountsin for the ~6month burn-in period. 

# Window: 40 Days
Given the high performance of my initial pairstradev1.0 and relative high performance of v2.0, I had high expectations for v2.1 but unfortunately, total PnL continued to meaningfully decrease. My honest assessment is that I have too many conditions the program needs to fulfill before executing a trade which in total reduces the amount of trades being made. 

In total, only 22 trades were being considered in the entire 2.5yr timeframe which is astonishingly low.

Impressively, my Deviation strategy continues to outpreform the benchmark Bollinger Bands approach here. 

**Total PnL:  
Deviation: 4.45%  
Bollinger: -1.54%**  


---

## Roadmap — Terminus

This is the final stop along the project that I've been aiming for. 

Functionally, each 'layer' of this project serves as a new condition for the stock pair to pass before a trade is executed. With each layer comes additional safety at the cost of additional PnL. 

Moving forward, if I was to implement this project on new stocks, I would use the cointegration test to determine the validity of the pair arrangement, and then execute my Deviation appraoch on the pairs.

Additionally, I wouldn't use a pure stock ratio (KO / PEP) but rather a price adjusted ratio to compensate for the intrinsic price difference between the stocks (KO / PEP*coefficient).

---

