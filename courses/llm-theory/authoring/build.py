from plan import append_plan

append_plan()
import specs
from render import write_all

write_all()

from readme import write_readme

write_readme()

from apply_textbook import apply

apply({f"llm-{number:03}" for number in range(43, 49)})
