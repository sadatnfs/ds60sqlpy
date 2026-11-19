import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--markdown-only", action="store_true")
# --no-plan regenerates lessons without rewriting docs/expansion/plans/llm-theory.json.
parser.add_argument("--no-plan", action="store_true")
arguments = parser.parse_args()

from plan import append_plan

if not (arguments.markdown_only or arguments.no_plan):
    append_plan()
import specs
from render import write_all

write_all(markdown_only=arguments.markdown_only, write_plan=not arguments.no_plan)

from readme import write_readme

if not arguments.markdown_only:
    write_readme()

from apply_textbook import apply

apply({f"llm-{number:03}" for number in range(43, 49)}, canonical_code=True)
