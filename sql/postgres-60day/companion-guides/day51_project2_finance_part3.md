# Day 51 — Project 2: Finance (Part 3) — Reconciliation and Data Hygiene (Companion Guide)

Objectives
- Reconcile trades vs positions vs cash; detect breaks
- Handle corporate actions (splits/dividends) at a basic level
- Build daily sanity checks and exception reports

Reconciliation queries
- Position continuity: position_t = position_{t-1} + signed_trades_t + splits_t
- Cash: cash_t = cash_{t-1} − buys + sells + dividends − fees
- Breaks: LEFT JOIN expected vs actual; flag absolute/relative differences

Corporate actions (simplified)
- Splits: adjust positions and cost basis by split ratio; join corporate_actions table
- Dividends: cash inflow on ex‑date; reinvest if dividend_reinvest flag

Exception framework
- exceptions(type, key, dt, expected, actual, diff, severity)
- Populate from reconciliation queries; drive alerts downstream

Pitfalls
- Time zone/date alignment across providers
- Late trades and restatements; design reruns idempotently

Deliverables
- Daily exception report with counts and top breaks

Stretch goals
- FIFO lot‑level realized P&L and wash sale handling
- Corporate action backfilling and adjustment audit table
