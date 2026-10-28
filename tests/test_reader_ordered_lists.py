"""Observe rendered list numbering through HTML semantics, not source-string counts."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.lesson_reader import LinkResolver, render_markdown

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class _Item:
    ordinal: int | None
    parts: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join("".join(self.parts).split())


@dataclass
class _List:
    ordered: bool
    next_ordinal: int
    attributes: dict[str, str | None]
    items: list[_Item] = field(default_factory=list)
    current: _Item | None = None


class _NumberingOracle(HTMLParser):
    """Apply default/start/value list counters while collecting visible item text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lists: list[_List] = []
        self.stack: list[_List] = []
        self.visible: list[str] = []
        self.code_blocks: list[str] = []
        self.pre_buffers: list[list[str]] = []
        self.math_elements: Counter[str] = Counter()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag in {"ol", "ul"}:
            start = values.get("start")
            context = _List(tag == "ol", int(start) if start is not None else 1, values)
            self.lists.append(context)
            self.stack.append(context)
        elif tag == "li":
            assert self.stack, "A rendered list item must belong to a list"
            context = self.stack[-1]
            explicit = values.get("value")
            ordinal = (
                (int(explicit) if explicit is not None else context.next_ordinal)
                if context.ordered
                else None
            )
            context.current = _Item(ordinal)
            context.items.append(context.current)
            if ordinal is not None:
                context.next_ordinal = ordinal + 1
        elif tag == "pre":
            self.pre_buffers.append([])
        if tag in {"math", "mfrac", "msup"}:
            self.math_elements[tag] += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "li":
            assert self.stack
            self.stack[-1].current = None
        elif tag in {"ol", "ul"}:
            assert self.stack and self.stack[-1].ordered == (tag == "ol")
            self.stack.pop()
        elif tag == "pre":
            self.code_blocks.append("".join(self.pre_buffers.pop()))

    def handle_data(self, data: str) -> None:
        self.visible.append(data)
        for context in self.stack:
            if context.current is not None:
                context.current.parts.append(data)
        if self.pre_buffers:
            self.pre_buffers[-1].append(data)

    @property
    def ordered_items(self) -> list[tuple[int | None, str]]:
        return [
            (item.ordinal, item.text) for row in self.lists if row.ordered for item in row.items
        ]

    @property
    def unordered_items(self) -> list[str]:
        return [item.text for row in self.lists if not row.ordered for item in row.items]


def observe(source: str, source_path: Path | None = None) -> _NumberingOracle:
    resolver = LinkResolver(
        repo_root=ROOT, source_path=source_path or ROOT / "README.md", targets={}
    )
    parser = _NumberingOracle()
    parser.feed(render_markdown(source, resolver=resolver))
    parser.close()
    assert not parser.stack and not parser.pre_buffers
    return parser


def test_real_day02_notebook_steps_continue_after_commands_and_paragraphs() -> None:
    catalog = Catalog.load(ROOT)
    guide = catalog.resolve(catalog.get("python-02").guide_path)
    source = guide.read_text(encoding="utf-8")
    route = source.split("### Optional contributor notebook route", 1)[1].split("\n## ", 1)[0]

    rendered = observe(route, guide)

    assert [number for number, _ in rendered.ordered_items] == [1, 2, 3, 4]
    assert [text.split(" ", 1)[0] for _, text in rendered.ordered_items] == [
        "Check",
        "Read",
        "Restart",
        "Attempt",
    ]
    assert len(rendered.code_blocks) == 2


@pytest.mark.parametrize("delimiter", [".", ")"])
@pytest.mark.parametrize(
    "marker,start",
    [("0", 0), ("7", 7), ("000000002", 2), ("999999999", 999999999)],
)
def test_first_supported_numeric_marker_sets_the_browser_counter(
    delimiter: str, marker: str, start: int
) -> None:
    rendered = observe(f"{marker}{delimiter} first\n1{delimiter} second\n42{delimiter} third")

    assert rendered.ordered_items == [(start, "first"), (start + 1, "second"), (start + 2, "third")]
    assert len(rendered.lists) == 1
    assert rendered.lists[0].attributes["start"] == str(start)


@pytest.mark.parametrize("delimiter", [".", ")"])
@pytest.mark.parametrize("first", ["1", "000000001"])
def test_default_and_repeated_one_markers_keep_normal_markdown_sequence(
    delimiter: str, first: str
) -> None:
    rendered = observe(f"{first}{delimiter} first\n1{delimiter} second\n1{delimiter} third")

    assert rendered.ordered_items == [(1, "first"), (2, "second"), (3, "third")]
    assert len(rendered.lists) == 1 and "start" not in rendered.lists[0].attributes


def test_paragraph_and_fence_breaks_retain_explicit_following_step_numbers() -> None:
    rendered = observe(
        "1. prepare\n\nA separate explanation.\n\n"
        "2. inspect\n\n```text\na literal command\n```\n\n"
        "3. run\n4. review\n"
    )

    assert rendered.ordered_items == [(1, "prepare"), (2, "inspect"), (3, "run"), (4, "review")]
    assert len(rendered.lists) == 3
    assert "A separate explanation." in "".join(rendered.visible)


def test_unordered_lists_do_not_share_ordered_counters_or_acquire_start_values() -> None:
    rendered = observe(
        "- first bullet\n+ second bullet\n\n"
        "4. ordered first\n1. ordered next\n\n"
        "* final bullet\n\n0) zero\n1) one\n"
    )

    assert rendered.ordered_items == [
        (4, "ordered first"),
        (5, "ordered next"),
        (0, "zero"),
        (1, "one"),
    ]
    assert rendered.unordered_items == ["first bullet", "second bullet", "final bullet"]
    assert all("start" not in row.attributes for row in rendered.lists if not row.ordered)


@pytest.mark.parametrize("delimiter", [".", ")"])
@pytest.mark.parametrize(
    "marker",
    [
        pytest.param("1234567890", id="ten-ascii-digits"),
        pytest.param("9" * 5000, id="beyond-integer-conversion-limit"),
        pytest.param("٢", id="arabic-indic-digit"),
        pytest.param("２", id="fullwidth-digit"),
        pytest.param("२", id="devanagari-digit"),
        pytest.param("²", id="superscript-digit"),
    ],
)
def test_long_or_non_ascii_numeric_text_is_not_a_list_marker(marker: str, delimiter: str) -> None:
    source = f"{marker}{delimiter} ordinary text"
    rendered = observe(source)

    assert rendered.lists == []
    assert "".join(rendered.visible) == source


def test_list_numbers_do_not_reinterpret_literal_code_or_explicit_math() -> None:
    code = "0. literal list-like code\n99999999999999999999) still code\n２. unicode code"
    rendered = observe(
        "4. first with `8. inline literal`\n\n```text\n"
        + code
        + "\n```\n\n\\[\n\\frac{1}{2}\n\\]\n\n5. final with \\(R^2\\)\n"
    )

    assert [number for number, _ in rendered.ordered_items] == [4, 5]
    assert "8. inline literal" in rendered.ordered_items[0][1]
    assert [block.rstrip("\n") for block in rendered.code_blocks] == [code]
    assert rendered.math_elements == {"math": 2, "mfrac": 1, "msup": 1}
