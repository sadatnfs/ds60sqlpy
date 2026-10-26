# r-048: complete reference for the declared synthetic inputs.
d <- data.frame(time = c(1, 2, 3, 4), event = c(1, 0, 1, 1))
validate_event <- function(event) {
  if (anyNA(event) || !all(event %in% c(0, 1))) stop("event must use 0/1 coding")
}
validate_event(d$event)
km <- survival::survfit(survival::Surv(time, event) ~ 1, data = d)
stopifnot(max(abs(summary(km, times = 1:4)$surv - c(0.75, 0.75, 0.375, 0))) < 1e-12)
changed <- d; changed$event[2] <- 1
wrong <- survival::survfit(survival::Surv(time, event) ~ 1, data = changed)
stopifnot(abs(summary(wrong, times = 2)$surv - 0.5) < 1e-12)
stopifnot(inherits(try(validate_event(c(0, 2)), silent = TRUE), "try-error"))
c <- data.frame(time = 1:12, event = c(1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0), group = c(0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1))
fit <- survival::coxph(survival::Surv(time, event) ~ group, data = c, x = TRUE)
stopifnot(all(is.finite(coef(fit))), all(exp(coef(fit)) > 0))
diagnostic <- survival::cox.zph(fit)
stopifnot(all(is.finite(diagnostic$table)), "GLOBAL" %in% rownames(diagnostic$table))
stopifnot(sum(d$event) == 3, nrow(d) == 4)
cat("r-048 reference checks passed\n")
