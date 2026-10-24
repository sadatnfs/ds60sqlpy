"""Reapply only the15 reviewed guide prose sections; leave programs and metadata alone."""

from pathlib import Path

from depth_reviews_foundations_expert import REVIEWS, enrich_guide, polish_document_prose


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    for number in REVIEWS:
        identity = f"llm-{number:03d}"
        path = base / "guides" / f"{identity}.md"
        source = path.read_text(encoding="utf-8")
        path.write_text(enrich_guide(identity, source), encoding="utf-8")
        explanation = base / "solutions" / f"{identity}_solutions.md"
        if explanation.exists():
            text = explanation.read_text(encoding="utf-8")
            explanation.write_text(polish_document_prose(text), encoding="utf-8")


if __name__ == "__main__":
    main()
