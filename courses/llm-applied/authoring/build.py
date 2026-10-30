"""Regenerate the course, or only its guides while preserving frozen artifacts."""

import argparse
import render
from plan import write_plan

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("--guides-only", action="store_true")
group.add_argument("--markdown-only", action="store_true")
arguments = parser.parse_args()
render.GUIDES_ONLY = arguments.guides_only or arguments.markdown_only
if not render.GUIDES_ONLY:
    write_plan()
import specs

render.write_all(guides_only=arguments.guides_only, markdown_only=arguments.markdown_only)
