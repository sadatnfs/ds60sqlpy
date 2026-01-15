# Day 49 — Project 2: Finance (Part 1) — Trades → Positions → P&L (Companion Guide)

Objectives
- Transform trades into daily positions via fills and corporate actions
- Compute end‑of‑day valuation and daily P&L (realized/unrealized)
- Handle weekends/holidays with a trading calendar

Data assumptions
- trades(security_id, trade_dt, qty, price, side)
- prices(security_id, dt, close)
- calendar(dt, is_trading_day)

Pipeline
1) signed_trades: qty_signed = CASE side WHEN 'BUY' THEN qty ELSE -qty END
2) position_days: expand each security across all trading days from first trade to last price via a calendar join
3) positions: cumulative SUM(qty_signed) OVER (PARTITION BY security ORDER BY dt)
4) valuation: position * close; daily unrealized_pnl = position * (close − LAG(close))
5) realized_pnl (simplified): when qty_signed decreases position, use average cost; else 0

Techniques
- Window cumulative sums and LAG for price deltas
- Calendar join to fill gaps (generate_series or calendar table)
- LEFT JOINs with COALESCE for missing prices

Pitfalls
- Corporate actions (splits/dividends) not modeled — note assumptions
- Look‑ahead bias: never use future prices
- Performance on large calendars; pre‑restrict to securities with activity

Deliverables
- positions_pnl(security_id, dt, position, close, unrealized_pnl, realized_pnl)

Stretch goals
- VWAP cost basis; FIFO lots via windowed allocation (advanced)
- Portfolio aggregation and benchmark relative returns
