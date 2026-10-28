"""Build original synthetic teaching tables without a network or private input."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / "python/fixtures"


def csv_text(fields: list[str], rows: list[dict[str, object]]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def restaurant() -> str:
    rng = random.Random(20261028)
    rows: list[dict[str, object]] = []
    for index in range(240):
        size = 1 + rng.randrange(6)
        bill_cents = 700 + 350 * size + rng.randrange(4000)
        tip_cents = bill_cents * (8 + rng.randrange(18)) // 100
        rows.append(
            {
                "total_bill": f"{bill_cents / 100:.2f}",
                "tip": f"{tip_cents / 100:.2f}",
                "sex": ("Female", "Male")[index % 2],
                "smoker": ("No", "Yes")[rng.randrange(2)],
                "day": ("Thur", "Fri", "Sat", "Sun")[index % 4],
                "time": ("Lunch", "Dinner")[(index // 4) % 2],
                "size": size,
            }
        )
    return csv_text(["total_bill", "tip", "sex", "smoker", "day", "time", "size"], rows)


def passengers() -> str:
    rng = random.Random(20261029)
    rows: list[dict[str, object]] = []
    for index in range(360):
        pclass = index % 3 + 1
        female = index % 2 == 0
        age = 1 + rng.randrange(80)
        sibsp, parch = rng.randrange(4), rng.randrange(3)
        probability = min(95, max(5, 15 + 45 * female + 20 * (pclass == 1) + 15 * (age < 16)))
        survived = int(rng.randrange(100) < probability)
        embarked = ("S", "C", "Q")[rng.randrange(3)]
        fare_cents = 900 + (4 - pclass) * 1000 + rng.randrange(9000)
        rows.append(
            {
                "survived": survived,
                "pclass": pclass,
                "sex": "female" if female else "male",
                "age": "" if index % 13 == 0 else f"{age:.1f}",
                "sibsp": sibsp,
                "parch": parch,
                "fare": "" if index % 31 == 0 else f"{fare_cents / 100:.2f}",
                "embarked": "" if index % 37 == 0 else embarked,
                "class": {1: "First", 2: "Second", 3: "Third"}[pclass],
                "who": "child" if age < 16 else ("woman" if female else "man"),
                "adult_male": not female and age >= 16,
                "deck": "ABCDEFG"[index % 7] if index % 4 == 0 else "",
                "embark_town": ""
                if index % 37 == 0
                else {"S": "Southampton", "C": "Cherbourg", "Q": "Queenstown"}[embarked],
                "alive": "yes" if survived else "no",
                "alone": sibsp + parch == 0,
            }
        )
    return csv_text(
        [
            "survived",
            "pclass",
            "sex",
            "age",
            "sibsp",
            "parch",
            "fare",
            "embarked",
            "class",
            "who",
            "adult_male",
            "deck",
            "embark_town",
            "alive",
            "alone",
        ],
        rows,
    )


def birds() -> str:
    rng = random.Random(20261030)
    rows: list[dict[str, object]] = []
    for index in range(180):
        species = index % 3
        rows.append(
            {
                "species": ("Adelie", "Chinstrap", "Gentoo")[species],
                "island": ("Biscoe", "Dream", "Torgersen")[(index // 3) % 3],
                "bill_length_mm": ""
                if index % 17 == 0
                else f"{(380 + 45 * species + rng.randrange(65)) / 10:.1f}",
                "bill_depth_mm": f"{(165 - 10 * species + rng.randrange(30)) / 10:.1f}",
                "flipper_length_mm": 180 + 17 * species + rng.randrange(20),
                "body_mass_g": 3000 + 650 * species + 25 * rng.randrange(32),
                "sex": "" if index % 29 == 0 else ("Male", "Female")[index % 2],
            }
        )
    return csv_text(
        [
            "species",
            "island",
            "bill_length_mm",
            "bill_depth_mm",
            "flipper_length_mm",
            "body_mass_g",
            "sex",
        ],
        rows,
    )


def outputs() -> dict[str, str]:
    tables = {
        "restaurant-bills": restaurant(),
        "passenger-outcomes": passengers(),
        "bird-measurements": birds(),
    }
    manifest = {
        "schema_version": 1,
        "datasets": {
            key: {
                "kind": "synthetic",
                "rows": len(text.splitlines()) - 1,
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
            for key, text in tables.items()
        },
    }
    return {
        **{key + ".csv": value for key, value in tables.items()},
        "manifest.json": json.dumps(manifest, indent=2) + "\n",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    drift = []
    for name, text in outputs().items():
        content = text.encode("utf-8")
        path = DESTINATION / name
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                drift.append(name)
        else:
            DESTINATION.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    if drift:
        print("Teaching fixture drift: " + ", ".join(drift))
        return 1
    print(
        "Three original synthetic teaching datasets checked"
        if args.check
        else "Three original synthetic teaching datasets written"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
