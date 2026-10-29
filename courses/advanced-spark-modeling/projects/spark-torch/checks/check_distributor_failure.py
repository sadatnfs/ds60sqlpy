"""Preserved failure-check entrypoint backed by the installed standalone package."""

from ds60_spark_likelihood.integrations.failure_check import run

if __name__ == "__main__":
    run()
