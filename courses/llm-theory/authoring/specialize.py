"""Rewrite shared boilerplate paragraphs with each lesson's own fixtures and names.

Runs after every generator that writes llm-theory guides or explanations
(apply_textbook.apply and review_guides). It replaces whole paragraphs that
open with a known shared phrase, repairs prose spacing outside code and math,
and never edits fenced blocks. A second pass is a no-op.
"""

from __future__ import annotations

import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

SPACE_WORDS = {
    "are",
    "is",
    "to",
    "and",
    "of",
    "then",
    "therefore",
    "into",
    "about",
    "approximately",
    "become",
    "becomes",
    "receives",
    "receive",
    "returns",
    "remains",
    "remain",
    "produces",
    "producing",
    "predicts",
    "means",
    "mean",
    "were",
    "leaves",
    "only",
    "each",
    "averages",
    "gradient",
    "plus",
    "minus",
    "in",
    "differences",
    "families",
    "labels",
    "was",
    "gives",
    "with",
    "from",
    "at",
    "as",
    "be",
    "by",
}

PROTECT = re.compile(
    r"`[^`\n]*`|\\\(.*?\\\)|\\\[.*?\\\]|\$[^$\n]+\$|\]\([^)\s]*\)|<[^>\n]*>",
    re.S,
)

EXPLICIT = {
    "llm-020": [("100, 000, 000", "100,000,000"), ("10, 000", "10,000")],
    "llm-021": [(re.compile(r"(?<![`\w])a2(?![`\w])"), "`a2`")],
    "llm-025": [("2, 048", "2,048"), ("4, 096", "4,096"), ("8, 192", "8,192")],
    "llm-026": [("sum is-3", "sum is -3")],
    "llm-029": [("A,B,k,alpha,beta", "A, B, k, alpha and beta")],
    "llm-034": [
        ("rounding:0.5 goes", "rounding: 0.5 goes"),
        ("integer array [[32, -76], [16, 127]]", "integer array `[[32, -76], [16, 127]]`"),
    ],
    "llm-036": [("is{red,square}", "is {red, square}")],
    "llm-040": [
        (
            "differences[-1,-1,1] with families[A,A,B]",
            "differences [-1, -1, 1] with families [A, A, B]",
        ),
        ("is(-1-1+1)/3=-1/3", "is (-1-1+1)/3 = -1/3"),
        ("mean is-1 and", "mean is -1 and"),
        ("produces(-1+1)/2=0", "produces (-1+1)/2 = 0"),
        ("are[-1,1]", "are [-1, 1]"),
        ("are-1,0,0,1", "are -1, 0, 0 and 1"),
        ("at-1,", "at -1,"),
    ],
    "llm-041": [
        (
            "allowed rows 100, 110, 111; forbidden rows 011, 001, 000",
            "allowed rows `100`, `110`, `111`; forbidden rows `011`, `001`, `000`",
        )
    ],
    "llm-042": [
        (
            "q1,q2,q3, with families shape,color,astronomy",
            "q1, q2 and q3, with families shape, color and astronomy",
        )
    ],
    "llm-046": [
        ("bytes 320, 160, 80;", "bytes \\(320, 160, 80\\);"),
        ("weights 256, 192, 160 for", "weights \\(256, 192, 160\\) for"),
        ("scores 1000, 999, 998 and", "scores \\(1000, 999, 998\\) and"),
        (
            "bytes are 320, 160 and 80 and projection weights 256, 192 and 160",
            "bytes are `[320, 160, 80]` and projection weights `[256, 192, 160]`",
        ),
        (
            "Use scores[0,\\(\\log(2)\\),\\(\\log(4)\\)] and",
            "Use scores \\([0, \\log(2), \\log(4)]\\) and",
        ),
        (
            "masses are [1,2,4], so the output is(1+6+20)/7=27/7",
            "masses are [1, 2, 4], so the output is (1+6+20)/7 = 27/7",
        ),
    ],
    "llm-048": [
        ("draw in[0, 1)", "draw in \\([0, 1)\\)"),
        ("draw in[0,1)", "draw in \\([0, 1)\\)"),
        ("mass is[.2,.3,.2]", "mass is [0.2, 0.3, 0.2]"),
        ("Rejection mass is.3", "Rejection mass is 0.3"),
        ("threshold is.3/.5=.6", "threshold is 0.3/0.5 = 0.6"),
        ("it is.2/.3=2/3", "it is 0.2/0.3 = 2/3"),
    ],
}


def lc(text: str) -> str:
    if len(text) > 1 and text[1].isupper():
        return text
    return text[:1].lower() + text[1:]


def clip(text: str) -> str:
    return text.strip().rstrip(".")


def sentence(text: str) -> str:
    text = text.strip()
    text = text[:1].upper() + text[1:]
    return text if text.endswith((".", "?", "!")) else text + "."


def join(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def em(text: str) -> str:
    return f"*{text}*"


def paragraphs(text: str) -> list[tuple[bool, str]]:
    """Split into (is_fence, chunk) parts; prose chunks keep their blank-line separators."""
    parts: list[tuple[bool, str]] = []
    pos = 0
    for match in re.finditer(r"^(```|~~~)[^\n]*\n.*?^\1[ \t]*$", text, re.M | re.S):
        parts.append((False, text[pos : match.start()]))
        parts.append((True, match.group(0)))
        pos = match.end()
    parts.append((False, text[pos:]))
    return parts


def section(text: str, heading: str) -> str:
    match = re.search(rf"^## {heading}[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return match.group(1) if match else ""


def flat(text: str) -> str:
    return " ".join(text.split())


def facts(identity: str, guide: str) -> dict:
    prose = "".join(chunk for fence, chunk in paragraphs(guide) if not fence)
    title = re.search(r"^# llm-\d{3}: (.+)$", guide, re.M).group(1).strip()
    examples = []
    for match in re.finditer(r"^### Example ([A-C]): (.+)$", guide, re.M):
        rest = guide[match.end() :]
        stop = re.search(r"^#{2,3} ", rest, re.M)
        body = rest[: stop.start()] if stop else rest
        expected = re.search(r"\*\*Expected:\*\* (.+?)(?:\n\s*\n|\Z)", body, re.S)
        examples.append(
            {
                "title": match.group(2).strip(),
                "expected": flat(expected.group(1)) if expected else "",
            }
        )
    exercises = []
    for item in re.split(r"\n\s*\n", section(guide, "Exercises")):
        j = flat(item)
        match = re.match(
            r"(\d)\. \*\*(.+?)\*\* (.*?) \*\*Expected:\*\* (.*?) \*\*Verify:\*\* (.*)$", j
        )
        if match:
            exercises.append(
                {
                    "title": match.group(2).rstrip(".?"),
                    "prompt": match.group(3),
                    "expected": match.group(4),
                }
            )
    terms = re.findall(r"^\*\*([^*]+?):\*\*", section(guide, "Vocabulary"), re.M)
    code = "\n".join(
        chunk for fence, chunk in paragraphs(guide) if fence and chunk.startswith("```python")
    )
    if "torch" in code:
        stack, modules = "PyTorch", "PyTorch"
    elif "numpy" in code or "np." in code:
        stack, modules = "NumPy", "NumPy"
    else:
        stack, modules = "the Python standard library", "the standard library"
    profile = re.search(r"its `([a-z0-9-]+)` worker", prose)
    number = int(identity[-3:])
    following = f"llm-{number + 1:03d}"
    next_path = BASE / "guides" / f"{following}.md"
    next_title = None
    if number < 48 and next_path.exists():
        head = re.search(r"^# llm-\d{3}: (.+)$", next_path.read_text(encoding="utf-8"), re.M)
        next_title = head.group(1).strip() if head else None
    bad = next(
        (
            e
            for e in exercises[3:]
            if re.search(r"rais|reject|refus|invalid|Error", e["prompt"] + " " + e["expected"])
        ),
        exercises[4] if len(exercises) > 4 else None,
    )
    return {
        "id": identity,
        "title": title,
        "topic": lc(title),
        "examples": examples,
        "exercises": exercises,
        "terms": terms or [title],
        "stack": stack,
        "modules": modules,
        "profile": profile.group(1) if profile else "python-core",
        "next": following if next_title else None,
        "next_title": next_title,
        "bad": bad,
        "diag": ex4
        if (ex4 := exercises[3] if len(exercises) > 3 else None) is not bad
        else exercises[2],
        "verb": "running" if "```python" in guide else "reading",
    }


def titles(f: dict) -> str:
    return join([em(e["title"]) for e in f["examples"]])


def guide_rewrite(j: str, f: dict) -> str | None:
    ex, eg, t = f["exercises"], f["examples"], f["terms"]
    if len(ex) < 6 or len(eg) < 2:
        return None
    a, b = eg[0], eg[1]
    t1 = t[1] if len(t) > 1 else t[0]
    ident, topic, stack = f["id"], f["topic"], f["stack"]
    later = f"`{f['next']}` ({f['next_title']})" if f["next"] else "the applied LLM route"
    level = re.match(
        r"(Beginner|Intermediate|Advanced)(?: within this subject)?; (?:estimated time: |approximately )(\d+) minutes\. (.*)",
        j,
    )
    if level:
        prereqs = re.findall(r"`([a-z]+-\d{2,3})`", level.group(3).split(".")[0])
        named = []
        for p in prereqs:
            path = BASE / "guides" / f"{p}.md"
            head = (
                re.search(r"^# [^:]+: (.+)$", path.read_text(encoding="utf-8"), re.M)
                if path.exists()
                else None
            )
            named.append(f"`{p}` ({head.group(1).strip()})" if head else f"`{p}`")
        lead = f"{level.group(1)}; approximately {level.group(2)} minutes. "
        if not named:
            return lead + f"No prerequisite lesson; {lc(t[0])} and {lc(t1)} are defined below."
        label = "prerequisites" if len(named) > 1 else "prerequisite"
        tail = (
            f" This lesson defines {lc(t[0])}, {lc(t1)} and the other terms below; it needs no service account, model weights, GPU or database."
            if "within this subject" in j
            else f" Revisit {named[0].split(' ')[0]} if {lc(t[0])} or {lc(t1)} feels unfamiliar here."
        )
        return lead + f"Direct {label}: {join(named)}." + tail
    if "By the end, you can produce the exact observations below" in j:
        first = j.split(" By the end,")[0]
        return (
            f"{first} By the end, you can reproduce {em(a['title'])} and {em(b['title'])}, explain why "
            f"{em(f['bad']['title'])} must not pass silently, and carry {lc(t[0])} to {em(ex[5]['title'])} "
            f"without copying a solution. Keep each first prediction about {topic} beside the observed evidence."
        )
    if j.startswith("Start or resume the Docker classroom"):
        uv = f" (the general uv environment lacks {stack})" if stack == "PyTorch" else ""
        return (
            f"Open `./classroom` (WSL 2 on Windows), pick `{ident}`, {em(f['title'])}, and wait for "
            f"`{f['profile']}` before **Run**. That worker supplies {stack} for {titles(f)}; if `{f['profile']}` "
            f"is missing, see the [classroom instructions](../../../docs/one-command-classroom.md). Paste {em(a['title'])} "
            f"first and {em(b['title'])} after it in one saved program, so {em(b['title'])} can reuse anything it defines. "
            f"Contributors can instead copy `courses/llm-theory/lessons/{ident}.py` to `.learning/expansion/{ident}/` "
            f"and run it with {f['modules']}{uv}; {topic} needs no download or online call."
        )
    if j.startswith("Start or resume with `./classroom`"):
        return (
            f"After starting `./classroom` (WSL 2 on Windows), pick `{ident}`, {em(f['title'])}, under the LLM "
            f"theory subject on the [classroom home](../../../docs/one-command-classroom.md). `{f['profile']}` "
            f"provides {stack}, so {em(a['title'])} and {em(b['title'])} share one saved pad and the host stays "
            f"clean. Contributors studying {topic} can use any Linux, macOS or WSL 2 interpreter with {f['modules']}."
        )
    if j.startswith("Open [the learner source]("):
        return (
            f"Copy [the learner source](../lessons/{ident}.py) to `.learning/expansion/{ident}/practice.py` "
            f"before editing {em(a['title'])}, and run it from the repository root once `{f['profile']}` reports "
            f"{stack} ready. For {topic}, the evidence is the assertions and named failures of "
            f"{em(f['bad']['title'])}, not any exact printed string."
        )
    if j.startswith("If the selected contributor interpreter cannot import"):
        return (
            f"If {f['modules']} will not import for `{ident}`, record that error and repair the interpreter "
            f"outside {topic}; never pip install from the lesson. Inputs from {em(a['title'])} to "
            f"{em(ex[5]['title'])} are small literals, so Docker stays the default route."
        )
    if j.startswith("Use the reading worksheet."):
        return (
            f"Use the reading worksheet for {topic}: write a reasoned response to {titles(f)} and to each "
            f"of the six cases, ending with {em(ex[5]['title'])}. No execution or model download is required."
        )
    if j.startswith(
        (
            "Start by reading Example A",
            "Run the three worked blocks",
            "Run Examples A and B in order",
        )
    ):
        later_examples = eg[1:]
        changed = " ".join(
            f"{em(e['title'])} changes an assumption and should give: {sentence(e['expected'])}"
            for e in later_examples
        )
        order = ""
        if len(eg) == 3 or j.startswith("Run Examples A and B"):
            order = (
                f"Run {titles(f)} in order in one scratch file; {em(b['title'])} reuses the helper and fixture state "
                f"from {em(a['title'])}, so a later block alone is not a standalone program. "
            )
        if j.startswith("Run Examples A and B"):
            return order + "Run that complete file in a fresh process."
        exact = (
            " These are exact CPU-fixture mechanisms, not evidence about model quality or hardware performance."
            if j.startswith("Run the three")
            else ""
        )
        return (
            order
            + f"Before running {em(a['title'])}, write its intermediate quantities on paper and predict: "
            f"{sentence(a['expected'])} Then run it in a fresh process. {changed} Compare both with exercise 4, "
            f"{em(ex[3]['title'])}.{exact} In {topic}, a failed {stack} assertion calls for inspecting an "
            "assumption, not widening a tolerance (1e-12 for float64 and 1e-6 for float32 unless stated; counts "
            "and decisions are exact)."
        )
    if re.match(r"Read (both|two|three|\w+) worked reasoning cases", j):
        return (
            f"Read {titles(f)} and derive their intermediate quantities and units on paper; {em(a['title'])} should "
            f"conclude: {sentence(a['expected'])} Then compare the assumptions and conclusions of {em(b['title'])}. "
            f"These text blocks about {topic} are evidence tables or arguments, not programs. Keep unknown evidence "
            "distinct from a failed condition, and name the observation that would settle it."
        )
    practice = re.match(r"Exercises (?:(1-3|1 and 2) )?repeat the worked examples", j)
    if practice:
        n = 2 if practice.group(1) == "1 and 2" else 3 if practice.group(1) == "1-3" else len(eg)
        guided = join([em(e["title"]) for e in ex[:n]])
        return (
            f"Exercises {'1 and 2' if n == 2 else f'1-{n}'}, {guided}, repeat the worked examples as guided "
            f"reconstructions; rebuild each from memory, then compare. From {em(ex[n]['title'])} to "
            f"{em(ex[5]['title'])}, exercises {n + 1}-6 change the fixture or expose a failure in {topic}."
        )
    if j.startswith("For the supplied fixture, name the input unit"):
        cond = re.search(
            r"acceptance condition in your own words: (.*?) Preserve the prediction", j
        )
        middle = (
            f" In particular, explain this lesson's acceptance condition in your own words: {cond.group(1)}"
            if cond
            else ""
        )
        return (
            f"Before {f['verb']} {em(b['title'])}, predict its outcome from the prompt alone, then predict how "
            f"{em(ex[5]['title'])} ends.{middle} Keep both guesses about {topic} beside the later observations; "
            "a copied expected value is not a derivation."
        )
    if j.startswith("Before executing or calculating"):
        return (
            f"Before {f['verb']} {em(a['title'])}, write the result you expect from its fixture and the changed condition "
            f"in {em(b['title'])} that would invalidate it. Afterward, name the first observation in {topic} that "
            "supported or contradicted the prediction instead of rewriting it to match the reference."
        )
    if j.startswith("First draw the state described in the vocabulary section"):
        return (
            f"Sketch {lc(t[0])} for {em(a['title'])}, then {lc(t1)} for {em(b['title'])}, and look for the smallest "
            f"input on which they disagree. Exercise 4, {em(ex[3]['title'])}, should give: {sentence(ex[3]['expected'])} "
            f"When stuck on {topic}, ask which step of {em(f['diag']['title'])} first goes wrong rather than for code, "
            f"and save that case as a regression test for {later}."
        )
    if j.startswith(("Close both worked examples.", "Close all three worked examples.")):
        return (
            f"Close {titles(f)}. Explain {join([lc(x) for x in t[:3]])} using the fixture of {em(a['title'])}, and "
            f"reconstruct its result from the inputs ({clip(a['expected'])}). Then change one input in "
            f"{em(b['title'])} and predict whether its stated result ({clip(b['expected'])}) still holds. Say which part "
            f"of {topic} the code guarantees and which part would need new observations; a tiny deterministic fixture "
            "is not evidence about an unseen population or a production model."
        )
    source = re.match(r"API and mechanism reference: (.+?), reviewed (\d{4}-\d{2}-\d{2})\.", j)
    if source:
        return (
            f"Reference for {lc(t[0])}: {source.group(1)}, reviewed {source.group(2)}. {titles(f)} and the failure "
            f"case {em(f['bad']['title'])} are original {topic} fixtures; [validation](../../../docs/validation.md) "
            f"lists the {stack} gates, and CI artifacts for `{ident}` show which ran."
        )
    if j.startswith("Use a 0, 1 or 2 score for each of five dimensions"):
        return (
            f"Score `{ident}` from 0 to 2 on five dimensions: the data contract in {em(a['title'])}, a correct "
            f"derivation of {em(b['title'])}, diagnosis of the changed fixture in {em(f['diag']['title'])}, explicit "
            f"handling of the invalid case in {em(f['bad']['title'])}, and a fresh explanation of what {topic} can and "
            "cannot show. Normally seek \\(\\frac{8}{10}\\) with no zero for the contract or claim boundary, then require "
            f"the transfer in {em(ex[5]['title'])}. This is a human learning rubric, not a certification awarded by one "
            "successful Run."
        )
    return None


def solution_rewrite(j: str, f: dict) -> str | None:
    ex, eg, t = f["exercises"], f["examples"], f["terms"]
    if len(ex) < 6 or len(eg) < 2:
        return None
    ident, topic, stack = f["id"], f["topic"], f["stack"]
    first, last, bad = em(ex[0]["title"]), em(ex[5]["title"]), em(f["bad"]["title"])
    if j.startswith("Compare these answers only after"):
        return (
            f"Read these {topic} answers after attempting {first} through {last}, or after asking for a reveal. "
            f"They reuse the guide's literals, so a mismatch in {em(ex[2]['title'])} points to one step. "
            f"`{ident}_solution.py` holds the assertions; this page explains how they test {lc(t[0])}. Then try "
            f"{last} on a fresh input you chose before looking."
        )
    if j.startswith("Repeat one case with a changed fixture"):
        return (
            f"Change one input to {em(ex[3]['title'])} and predict the result first; keep {bad} failing beside "
            f"the repair. Log a missing {stack} separately from a wrong {lc(t[0])} value in `{ident}`."
        )
    if j.startswith("Open this reference after an attempt"):
        return (
            f"Use this {topic} reference after your own attempt. The [learner guide](../guides/{ident}.md) keeps "
            f"the fixture and Expected/Verify contracts for {first} to {last}, six separate actions; any "
            f"implementation is acceptable if {bad} still fails on that input."
        )
    if j.startswith(f"The [executable reference]({ident}_solution.py) exposes"):
        reading = (
            " The reading worksheet remains a reading exercise, regardless of the optional arithmetic checker."
            if "reading worksheet remains" in j
            else ""
        )
        return (
            f"`verify()` in the [executable reference]({ident}_solution.py) uses {stack} and literals only; on "
            f"failure, keep the {bad} input. A pass says nothing beyond these {topic} fixtures, so next explain "
            f"{lc(t[0])} from memory on a changed fixture." + reading
        )
    if j.startswith("The core functions below make the input and reduction policies explicit"):
        return (
            f"{em(eg[0]['title'])} validates and reduces its input in the functions below; the executable file "
            f"covers all six {topic} exercises. Keep the {bad} assertion and its invalid-input case; never replace "
            "them with a default."
        )
    if j.startswith("After revealing this file"):
        return (
            f"Next, pick a fixture unlike {em(eg[0]['title'])} to test independent recall, and explain why "
            f"{bad} rejects its case rather than naming the exception. Any notation works if {lc(t[0])} and its "
            f"denominator stay explicit; these {topic} checks say nothing about unseen model quality or safety."
        )
    return None


BRACKET = re.compile(
    r"(?<![\w.`])([A-Za-z_][A-Za-z0-9_.]*)((?:\[[^\[\]\n]*(?:\[[^\[\]\n]*\][^\[\]\n]*)*\])+)"
)
CALL = re.compile(r"(?<![\w.`])([a-z_][a-z0-9_]*)\(([a-z_]+(?:,[a-z_]+)+)\)")


def fix_plain(text: str, identity: str) -> str:
    text = re.sub(r"\bshape\(", "shape (", text)
    text = CALL.sub(lambda m: f"`{m.group(1)}({m.group(2).replace(',', ', ')})`", text)

    def bracket(match: re.Match) -> str:
        word, rest = match.group(1), match.group(2)
        if not re.match(r"\[[-\d.]", rest) or len(re.sub(r"[^A-Za-z]", "", word)) < 2:
            return match.group(0)
        if word.lower() in SPACE_WORDS:
            return f"{word} {rest}"
        if re.match(r",\[", match.string[match.end() :]):
            return f"{word} {rest}"
        return f"`{word}{rest}`"

    text = BRACKET.sub(bracket, text)

    def numeric_list(match: re.Match) -> str:
        body = match.group(0)
        if re.search(r",\d{3}(?!\d)", body):
            return body
        return re.sub(r",(?=\S)", ", ", body)

    text = re.sub(r"(?<![\w`])\[[-\d./]+(?:,\s?[-\d./]+)+\]", numeric_list, text)
    text = re.sub(r"(\[[-\d./, ]+\]),(?=\[)", r"\1, ", text)
    text = re.sub(r"\b(is|are|and)\((?=[A-Za-z0-9+\-/, ]+\))", r"\1 (", text)
    text = re.sub(r"\),\((?=[A-Za-z0-9, ]+\))", "), (", text)
    text = re.sub(r"\b(is|are|at)\.(\d)", r"\1 0.\2", text)
    text = re.sub(r"\b(is|are)-(\d)", r"\1 -\2", text)
    text = re.sub(r"(?<=[a-z]{3}),(?=[a-z]{3})", ", ", text)
    return text


def protected_map(text: str, func) -> str:
    out, pos = [], 0
    for match in PROTECT.finditer(text):
        out.append(func(text[pos : match.start()]))
        out.append(match.group(0))
        pos = match.end()
    out.append(func(text[pos:]))
    return "".join(out)


def fix_spacing(chunk: str, identity: str) -> str:
    for old, new in EXPLICIT.get(identity, []):
        if isinstance(old, re.Pattern):
            chunk = protected_map(chunk, lambda s, o=old, n=new: o.sub(n, s))
        else:
            chunk = chunk.replace(old, new)
    return protected_map(chunk, lambda s: fix_plain(s, identity))


def verify_prefix(block: str, heading: str | None = None) -> str:
    title = re.match(r"\d\. \*\*(.+?)\*\*", block)
    if not title and not heading:
        return block
    name = title.group(1).rstrip(".?") if title else heading
    return re.sub(
        r"\*\*Verify:\*\* In a fresh process, the exercise checks confirm",
        f"**Verify:** For *{name}*, a fresh-process check confirms",
        block,
    )


def specialize(identity: str, text: str, f: dict, rewrite) -> str:
    out = []
    heading = None
    for fence, chunk in paragraphs(text):
        if fence:
            out.append(chunk)
            continue
        pieces = re.split(r"(\n[ \t]*\n)", chunk)
        for index, piece in enumerate(pieces):
            if index % 2 or not piece.strip():
                continue
            lead = piece[: len(piece) - len(piece.lstrip())]
            trail = piece[len(piece.rstrip()) :]
            body = piece.strip()
            new = (
                rewrite(flat(body), f)
                if not body.startswith(("#", "<!--", "|", "-", ">"))
                else None
            )
            if new is not None:
                body = new
            exercise = re.match(r"## Exercise \d+: (.+)$", body)
            if exercise:
                heading = exercise.group(1).strip().rstrip(".?")
            body = verify_prefix(body, heading)
            pieces[index] = lead + fix_spacing(body, identity) + trail
        out.append("".join(pieces))
    return "".join(out)


def run(identity: str, base: Path = BASE) -> None:
    guide_path = base / "guides" / f"{identity}.md"
    guide = guide_path.read_text(encoding="utf-8")
    f = facts(identity, guide)
    new = specialize(identity, guide, f, guide_rewrite)
    if new != guide:
        guide_path.write_text(new, encoding="utf-8")
    path = base / "solutions" / f"{identity}_solutions.md"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        new = specialize(identity, text, f, solution_rewrite)
        if new != text:
            path.write_text(new, encoding="utf-8")


if __name__ == "__main__":
    import sys

    for name in sys.argv[1:] or [f"llm-{n:03d}" for n in range(1, 49)]:
        run(name)
