"""Reapply only the15 reviewed guide prose sections; leave programs and metadata alone."""

from pathlib import Path
import argparse
import sys

from depth_reviews_foundations_expert import REVIEWS, enrich_guide, polish_document_prose


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-code", action="store_true")
    arguments = parser.parse_args()
    base = Path(__file__).resolve().parents[1]
    source_root = base.parent.parent

    def canonical(text, path):
        if not arguments.canonical_code:
            return text
        if str(source_root) not in sys.path:
            sys.path.insert(0, str(source_root))
        from scripts.format_inline_code import canonical_markdown, ownership
        from scripts.format_repo import load_policy

        relative = path.relative_to(source_root).as_posix()
        generated, protected = ownership(relative, load_policy(source_root))
        if protected:
            raise ValueError("Protected Markdown output must remain unchanged: " + relative)
        if generated:
            return canonical_markdown(text, root=source_root, path=relative)
        print("Direct source layout remains owned by format-repo:", relative)
        return text

    for number in REVIEWS:
        identity = f"llm-{number:03d}"
        path = base / "guides" / f"{identity}.md"
        source = path.read_text(encoding="utf-8")
        path.write_text(canonical(enrich_guide(identity, source), path), encoding="utf-8")
        explanation = base / "solutions" / f"{identity}_solutions.md"
        if explanation.exists():
            text = explanation.read_text(encoding="utf-8")
            explanation.write_text(
                canonical(polish_document_prose(text), explanation), encoding="utf-8"
            )


if __name__ == "__main__":
    main()
