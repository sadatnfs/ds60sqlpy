"""Authored HTML gets an escaped reader; generated pages keep their navigation."""

from pathlib import Path

from ds60sqlpy.lesson_reader import LinkResolver, ReaderTarget, _linked_reference_sources


def test_html_source_discovery_does_not_turn_the_course_home_into_a_code_dump(
    tmp_path: Path,
) -> None:
    names = [
        "START_HERE.html",
        "lesson-pages/python-001.html",
        "reference-pages/existing.md.html",
        "src/ds60sqlpy/assets/journey_preview.html",
        "courses/web-development/lessons/web-001.html",
    ]
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("<!doctype html><title>Example</title><p>Read me</p>", encoding="utf-8")
    links = "\n".join(f"[Page {n}]({name})" for n, name in enumerate(names))
    targets = list(_linked_reference_sources(tmp_path / "README.md", links, repo_root=tmp_path))
    assert targets == [tmp_path / names[-1]]
    resolver = LinkResolver(
        repo_root=tmp_path,
        source_path=tmp_path / "README.md",
        targets={targets[0]: ReaderTarget("reference-pages/" + names[-1] + ".html", "")},
    )
    assert resolver.href("START_HERE.html#catalog") == "../START_HERE.html#catalog"
    assert resolver.href(names[-1]) == "../reference-pages/" + names[-1] + ".html"
