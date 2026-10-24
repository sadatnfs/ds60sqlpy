"""Regenerate the course, or only its guides while preserving frozen artifacts."""

import argparse
import render
from plan import write_plan

parser = argparse.ArgumentParser()
parser.add_argument("--guides-only", action="store_true")
arguments = parser.parse_args()
render.GUIDES_ONLY = arguments.guides_only
if not arguments.guides_only:
    write_plan()
import specs

render.write_all(guides_only=arguments.guides_only)
