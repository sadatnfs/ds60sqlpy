"""Inspect actual DistributedSampler membership without launching a trainer."""

import json

from .distributed_cases import sampler_audit

if __name__ == "__main__":
    print(json.dumps(sampler_audit(), sort_keys=True))
