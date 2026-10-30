import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--markdown-only", action="store_true")
arguments = parser.parse_args()

from plan import append_plan

if not arguments.markdown_only:
    append_plan()
import specs
from render import write_all

write_all(markdown_only=arguments.markdown_only)

from readme import write_readme

if not arguments.markdown_only:
    write_readme()

from apply_textbook import apply

apply({f"llm-{number:03}" for number in range(43, 49)}, canonical_code=True)
