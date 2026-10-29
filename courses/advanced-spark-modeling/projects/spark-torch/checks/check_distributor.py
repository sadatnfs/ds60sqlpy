"""Preserved workshop entrypoint backed by the installed standalone package."""

import argparse

from ds60_spark_likelihood.integrations.training import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=("torch-distributor", "lightning-ddp"))
    run(parser.parse_args().case)
