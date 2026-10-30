"""Generate the deployment tutorial from its maintained chapters and unit metadata."""

import argparse
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def outputs():
    units = json.loads((BASE / "authoring/units.json").read_text())
    if [row["id"] for row in units] != [f"spark-deploy-{i:03d}" for i in range(1, 19)]:
        raise ValueError("Preserve the eighteen stable deployment lesson identities")
    result = {}
    plan = []
    admitted = []
    for number, unit in enumerate(units, 1):
        body = (BASE / "authoring/chapters" / f"{number:02d}.md").read_text().strip()
        if len(body.split()) < 350 or body.count("## Worked case") != 2 or "\u2014" in body:
            raise ValueError(
                f"{unit['id']} requires substantial original prose and two worked cases"
            )
        header = (
            f"# {unit['id']}: {unit['title']}\n\n"
            f"Tutorial mode. Stage: {unit['level']}. Direct prerequisites: "
            + ", ".join(f"`{key}`" for key in unit["prerequisites"])
            + ".\n\n"
            + "Read this tutorial in the classroom. Its commands run only in the separately "
            "prepared [owned workshop](../projects/cluster-lab/README.md); "
            "there is no pad Run action. "
            "Examples describe expected observations. Check the workshop qualification ledger "
            "for actual execution evidence.\n\n"
        )
        guide = header + body + "\n"
        result[BASE / "guides" / (unit["id"] + ".md")] = guide
        result[BASE / "lessons" / (unit["id"] + ".md")] = guide
        plan.append(
            unit
            | {
                "runtime": "reading",
                "lab": unit["outcome"],
                "verification": (
                    "Compare the two worked cases and retain source-bound observations; "
                    "configuration alone is not runtime evidence."
                ),
            }
        )
        admitted.append(
            {
                "id": unit["id"],
                "status": "authored",
                "language": "markdown",
                "runtime_profile": "reading",
                "guide_path": f"courses/spark-deployment/guides/{unit['id']}.md",
                "source_path": f"courses/spark-deployment/lessons/{unit['id']}.md",
                "solution_paths": [],
                "verification_id": None,
            }
        )
    result[BASE / "track.json"] = (
        json.dumps(
            {
                "schema_version": 1,
                "id": "spark-deployment",
                "title": "Spark deployment: Compose, notebooks and Kubernetes",
                "summary": (
                    "An eighteen-unit tutorial connecting driver placement, isolated Compose, "
                    "Jupyter, images, networking, live/history UIs, storage, security, resource "
                    "budgets and portable Kubernetes submission."
                ),
                "learning_mode": "tutorial",
                "lessons": plan,
            },
            indent=2,
        )
        + "\n"
    )
    result[BASE / "lessons.json"] = (
        json.dumps(
            {"schema_version": 1, "track_id": "spark-deployment", "lessons": admitted}, indent=2
        )
        + "\n"
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = []
    for path, expected in outputs().items():
        if not path.exists() or path.read_text() != expected:
            changed.append(str(path.relative_to(BASE)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(expected)
    if args.check and changed:
        raise SystemExit("Deployment source drift: " + ", ".join(changed))
    print(f"Checked {len(outputs())} deployment artifacts; drift={len(changed)}")


if __name__ == "__main__":
    main()
