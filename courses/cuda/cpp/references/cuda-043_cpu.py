"""cuda-043: CPU reference only, not CUDA execution."""

setup_us, ordinary_us, replay_us = 300, 20, 5
break_even = setup_us / (ordinary_us - replay_us)
assert break_even == 20
assert setup_us + 21 * replay_us < 21 * ordinary_us
print({"synthetic_break_even_replays": break_even})
