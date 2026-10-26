# r-001: complete reference for the declared synthetic inputs.
stopifnot(4 * 7 == 28)
quantity <- 5
unit_price <- 6
total <- quantity * unit_price
stopifnot(total == 30)
subtotal <- 20
fee <- 3
stopifnot(subtotal + fee == 23)
quantity <- 8
stopifnot(total == 30, quantity * unit_price == 48)
quantity <- 0
stopifnot(quantity * unit_price == 0)
print(c(total_from_prior_calculation = total, current_total = quantity * unit_price))
cat("r-001 reference checks passed\n")
