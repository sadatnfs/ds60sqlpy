from pathlib import Path

from ds60sqlpy.lesson_reader import LinkResolver, render_markdown


def test_method_label_is_readable_and_keeps_coverage_anchor(tmp_path: Path) -> None:
    resolver = LinkResolver(
        repo_root=tmp_path,
        source_path=tmp_path / "book.md",
        targets={},
        fragment_prefix="module-guide--",
    )
    rendered = render_markdown(
        "### stat-01-01\n\n**Descriptive analysis**\n\nExplain the denominator.\n",
        resolver=resolver,
        id_prefix="module-guide--",
    )
    assert '<h5 id="module-guide--stat-01-01">Descriptive analysis' in rendered
    assert rendered.count("Descriptive analysis") == 1
    assert 'href="#module-guide--stat-01-01"' in rendered
    assert "Explain the denominator." in rendered


def test_method_label_is_escaped_and_normal_heading_does_not_consume_body(tmp_path: Path) -> None:
    resolver = LinkResolver(repo_root=tmp_path, source_path=tmp_path / "book.md", targets={})
    rendered = render_markdown("### stat-01-02\n\n**A < B & C**\n\nText\n", resolver=resolver)
    assert "A &lt; B &amp; C" in rendered
    ordinary = render_markdown("### Ordinary\n\n**Keep this paragraph**\n", resolver=resolver)
    assert "<p><strong>Keep this paragraph</strong></p>" in ordinary
