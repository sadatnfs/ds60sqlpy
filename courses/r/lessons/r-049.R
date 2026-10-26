# r-049: independent practice
# Supplied input fixture only; fill results and add independent assertions.

y <- ts(c(2, 1.2, 0.8, 0.1, -0.2, 0.3, 0.1, 0.4))
results <- vector("list", 6L)

# Exercise 1: Derive three forecasts for a zero-mean AR(1) with phi 0.5 and latest value 0.4.
# TODO: Apply the coefficient once per horizon.
# Exercise 2: Explain why an ARIMA order(1,0,0) differs from(0,1,0).
# TODO: Identify the modeled level versus differenced quantity.
# Exercise 3: Construct rolling-origin naive predictions for origins 4 through 7 of 1:8.
# TODO: Slice the training prefix at each origin.
# Exercise 4: Diagnose using mean(y) from all eight values at the first origin.
# TODO: Identify which future values enter the fitted summary.
# Exercise 5: Difference the sequence 1:6 and retain the changed length and meaning.
# TODO: One adjacent difference uses two level observations.
# Exercise 6: Interpret forecast SEs without claiming all sources of future error are covered.
# TODO: List model and selection assumptions.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
