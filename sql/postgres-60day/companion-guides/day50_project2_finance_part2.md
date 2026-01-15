# Day 50 — Project 2: Finance (Part 2) — Risk, Drawdowns, and Attribution (Companion Guide)

Objectives
- Compute returns, volatility, and drawdowns for securities/portfolio
- Attribute performance across sectors or strategies
- Estimate simple Value‑at‑Risk (VaR) from historical returns

Returns and risk
- Daily return r_t = close_t/close_{t-1} − 1; use LAG
- Rolling volatility: STDDEV_SAMP(r_t) OVER (ORDER BY dt ROWS BETWEEN 20 PRECEDING AND CURRENT ROW)
- Drawdown: running max of cumulative returns; DD_t = (cum_ret_t / running_max) − 1

Attribution
- Map securities to sector; aggregate returns and contributions by sector
- Contribution = weight_{t-1} × return_t; sum by sector and over time

VaR (historical)
- Compute distribution of daily P&L over a window; p1 percentile as VaR_99
- PERCENTILE_CONT(0.01) WITHIN GROUP (ORDER BY pnl)

Pitfalls
- Using arithmetic mean of returns instead of geometric for multi‑period
- Inconsistent weights timing; use t‑1 weights for t return attribution

Deliverables
- risk_metrics(security/portfolio, dt, ret, vol20, dd)
- attribution(sector, dt, contribution)

Stretch goals
- Conditional VaR (expected shortfall)
- Beta and alpha vs benchmark using rolling regression (outside SQL scope)
