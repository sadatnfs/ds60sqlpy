threads <- c(1, 2, 4);illustrative_seconds <- c(1, .62, .48)
print(data.frame(kind = "hypothetical arithmetic", threads = threads, seconds = illustrative_seconds, speedup = illustrative_seconds[1] / illustrative_seconds, efficiency = illustrative_seconds[1] / (threads * illustrative_seconds)))
serial_fraction <- .25
print(data.frame(threads = threads, ideal_amdahl_speedup = 1 / (serial_fraction + (1 - serial_fraction) / threads)))
stopifnot(1 / serial_fraction == 4)
