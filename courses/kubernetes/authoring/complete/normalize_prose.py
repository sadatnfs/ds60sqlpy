from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[2]


def prose(text):
    protected = re.compile(r"(`[^`]*`|\[[^\]]*\]\([^)]*\)|https?://\S+)")

    def clean(part):
        # Only separate punctuation from a following word; digit groups such as
        # 67,108,864 and host:port forms must survive unchanged.
        part = re.sub(r"([,;])(?=[A-Za-z])", r"\1 ", part)
        part = re.sub(
            r"\b(all|All|through|replicas|minimum|maximum|integer|string|generation|Generation|observedGeneration|schema|fixture|contract|second|at|target|current|observed|usage|requests|Start|start|finish|source|Source|after|before|count|healthy|window|the)(?=\d)",
            r"\1 ",
            part,
        )
        part = re.sub(
            r"(?<=\d)(seconds|milliseconds|percent|words|lessons|cases|tests|rows)\b", r" \1", part
        )
        return part

    lines = []
    fenced = False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            lines.append(line)
            continue
        if fenced:
            lines.append(line)
            continue
        chunks = protected.split(line)
        lines.append("".join(piece if i % 2 else clean(piece) for i, piece in enumerate(chunks)))
    return "".join(lines)


for folder in ("guides", "solutions", "lessons"):
    for path in (BASE / folder).glob("*.md"):
        if not any(
            path.name.startswith(key) for key in ("k8s-001", "k8s-002", "k8s-003", "k8s-008")
        ):
            path.write_text(prose(path.read_text()))
for name in ("README.md", "host-labs.md"):
    path = BASE / name
    path.write_text(prose(path.read_text()))
