"""Keyboard and focus checks for the desktop classroom (UX-02).

Pure helpers are cut out of the shell and guide scripts by their markers and
evaluated alone in a Node vm, the same pattern as test_learning_editor.py.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import pytest

from scripts.check_classroom_browser import contrast_ratio

ASSETS = Path(__file__).parents[1] / "src/ds60sqlpy/assets"
SHELL = ASSETS / "classroom-shell.js"
GUIDE = ASSETS / "classroom-guide.js"
HTML = ASSETS / "classroom.html"
CSS = ASSETS / "classroom.css"
NODE = shutil.which("node")
needs_node = pytest.mark.skipif(NODE is None, reason="Node is an optional developer UI check")


def marked_block(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8")
    begin, end = f"// BEGIN {name}", f"// END {name}"
    assert text.count(begin) == 1 and text.count(end) == 1, name
    return text.split(begin, 1)[1].split(end, 1)[0]


def evaluate(source: str, expression: str) -> object:
    assert NODE is not None
    program = (
        "const vm = require('node:vm');\n"
        'let input = "";\n'
        "process.stdin.setEncoding('utf8');\n"
        "process.stdin.on('data', chunk => input += chunk);\n"
        "process.stdin.on('end', () => {\n"
        "const value = JSON.parse(input);\n"
        "const sandbox = {}; vm.createContext(sandbox);\n"
        "vm.runInContext(value.source, sandbox);\n"
        "console.log(JSON.stringify(vm.runInContext(value.expression, sandbox)));\n"
        "});\n"
    )
    result = subprocess.run(
        [str(NODE), "-e", program],
        input=json.dumps({"source": source, "expression": expression}),
        text=True,
        capture_output=True,
        timeout=5,
        check=True,
    )
    return json.loads(result.stdout)


EDITOR = "{closest: (s) => s === '.cm-editor' ? {} : null}"
PAGE = "{closest: () => null}"
SHORTCUT_CASES = [
    ("{key: 'k', metaKey: true, target: " + PAGE + "}", True, True),
    ("{key: 'k', ctrlKey: true, target: " + PAGE + "}", True, False),
    ("{key: 'k', ctrlKey: true, target: " + PAGE + "}", False, True),
    ("{key: 'k', metaKey: true, target: " + PAGE + "}", False, False),
    ("{key: 'k', metaKey: true, shiftKey: true, target: " + PAGE + "}", True, False),
    ("{key: 'k', ctrlKey: true, altKey: true, target: " + PAGE + "}", False, False),
    ("{key: 'K', metaKey: true, target: " + PAGE + "}", True, True),
    ("{key: 'K', ctrlKey: true, target: " + PAGE + "}", False, True),
    ("{key: 'k', metaKey: true, target: " + EDITOR + "}", True, False),
    ("{key: 'k', ctrlKey: true, target: " + EDITOR + "}", True, False),
    ("{key: 'k', ctrlKey: true, target: " + EDITOR + "}", False, False),
    ("{key: 'k', ctrlKey: true, metaKey: true, target: " + PAGE + "}", False, False),
    ("{key: 'k', ctrlKey: true, target: {}}", False, True),
    ("{key: 'k', metaKey: true}", True, True),
    ("{key: 'j', ctrlKey: true, target: " + PAGE + "}", False, False),
]


@needs_node
def test_palette_shortcut_follows_platform_and_spares_the_editor() -> None:
    source = marked_block(SHELL, "SHELL KEY HELPERS")
    calls = ", ".join(
        f"paletteShortcut({event}, {'true' if mac else 'false'})"
        for event, mac, _ in SHORTCUT_CASES
    )
    assert evaluate(source, f"[{calls}]") == [want for _, _, want in SHORTCUT_CASES]


def test_shell_keydown_uses_the_shortcut_helper() -> None:
    text = SHELL.read_text(encoding="utf-8")
    assert text.count("paletteShortcut(event, isMac)") == 1
    assert 'event.key.toLowerCase() === "k"' not in text


@needs_node
def test_inert_background_marks_only_new_siblings_and_restores_them() -> None:
    source = marked_block(GUIDE, "TOUR INERT HELPER")
    expression = (
        "(() => {"
        "const a = {inert: false}, keep = {inert: false}, b = {inert: true};"
        "const doc = {body: {children: [a, keep, b]}};"
        "const restore = inertBackground(doc, keep);"
        "const during = [a.inert, keep.inert, b.inert];"
        "restore();"
        "return {during, after: [a.inert, keep.inert, b.inert]};"
        "})()"
    )
    assert evaluate(source, expression) == {
        "during": [True, False, True],
        "after": [False, False, True],
    }


def test_tour_wires_and_releases_the_inert_background() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    assert text.count("inertBackground(document, layer)") == 1
    end_tour = text.split("function endTour()", 1)[1].split("function placeTour()", 1)[0]
    assert end_tour.index("restoreInert?.()") < end_tour.index("layer.remove()")


class Elements(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.by_id: dict[str, list[dict[str, str | None]]] = {}
        self.text: dict[str, str] = {}
        self._open: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        found = dict(attrs)
        ident = found.get("id")
        if ident:
            self.by_id.setdefault(ident, []).append(found)
            self._open = ident
            self.text[ident] = ""

    def handle_endtag(self, tag: str) -> None:
        self._open = None

    def handle_data(self, data: str) -> None:
        if self._open:
            self.text[self._open] += data


@pytest.fixture(scope="module")
def page() -> Elements:
    parser = Elements()
    parser.feed(HTML.read_text(encoding="utf-8"))
    return parser


def test_skip_to_result_link_and_focus_targets(page: Elements) -> None:
    assert len(page.by_id["skip-result"]) == 1
    link = page.by_id["skip-result"][0]
    assert link["href"] == "#runtime-results"
    assert page.text["skip-result"].strip() == "Skip to result"
    assert len(page.by_id["run"]) == 1
    assert page.by_id["run"][0]["aria-describedby"] == "capability"
    assert page.by_id["capability"][0]["tabindex"] == "-1"
    assert page.by_id["results-title"][0]["tabindex"] == "-1"
    assert len(page.by_id["runtime-results"]) == 1


def test_shell_moves_focus_for_skip_to_result() -> None:
    text = SHELL.read_text(encoding="utf-8")
    handler = text.split('byId("skip-result")', 1)[1].split("// Home quick starts", 1)[0]
    assert "preventDefault()" in handler
    assert 'byId("results-title")' in handler and 'byId("capability")' in handler


def css_rule(selector: str) -> str:
    text = CSS.read_text(encoding="utf-8")
    matches = re.findall(re.escape(selector) + r"\s*\{([^}]*)\}", text)
    assert len(matches) == 1, selector
    return matches[0]


def test_palette_and_manual_focus_cues_use_the_accent() -> None:
    assert "box-shadow: inset 0 -2px 0 var(--accent)" in css_rule(".palette-search:focus-within")
    assert "box-shadow: inset 3px 0 0 var(--accent)" in css_rule(".manual-parts li:focus")


def theme_tokens(block_selector: str) -> dict[str, str]:
    text = CSS.read_text(encoding="utf-8")
    body = re.search(re.escape(block_selector) + r"\s*\{([^}]*)\}", text)
    assert body is not None, block_selector
    return dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{6})\s*;", body.group(1)))


def rgb(hex_value: str) -> str:
    red, green, blue = (int(hex_value[i : i + 2], 16) for i in (1, 3, 5))
    return f"rgb({red}, {green}, {blue})"


@pytest.mark.parametrize("block", [":root", 'body[data-mode="dark"]'])
def test_focus_cue_accent_reaches_three_to_one(block: str) -> None:
    tokens = theme_tokens(block)
    for background in ("--surface", "--tint"):
        ratio = contrast_ratio(rgb(tokens["--accent"]), rgb(tokens[background]))
        assert ratio >= 3.0, (block, background, ratio)


def test_manual_documents_the_real_shortcuts() -> None:
    text = HTML.read_text(encoding="utf-8")
    keys = text.split('id="manual-keys"', 1)[1].split("</section>", 1)[0]
    assert "<kbd>Cmd K</kbd> on a Mac" in keys
    assert "except inside the" in keys
    assert "<kbd>Ctrl M</kbd> (<kbd>Shift Alt M</kbd> on a Mac)" in keys
    assert "Skip to result" in keys
    # The CodeMirror bundle binds tab focus mode to these exact keys.
    vendor = (ASSETS / "vendor/codemirror.v6.min.js").read_text(encoding="utf-8")
    assert '{key:"Ctrl-m",mac:"Shift-Alt-m"' in vendor


@pytest.mark.parametrize("path", [HTML, CSS, SHELL, GUIDE])
def test_no_en_or_em_dashes(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert "\u2013" not in text and "\u2014" not in text
