"""Build goal-based study plans from the catalog prerequisite graph."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

from ds60sqlpy.catalog import Catalog, Lesson


@dataclass(frozen=True, slots=True)
class LearningPath:
    """A goal and its terminal lessons, with no second lesson inventory."""

    title: str
    description: str
    targets: tuple[str, ...]


LEARNING_PATHS = {
    "python-foundations": LearningPath(
        "Python foundations",
        "Start gently and finish an independent command-line project.",
        ("python-15",),
    ),
    "sql-foundations": LearningPath(
        "SQL foundations",
        "Read tiny tables, construct queries, and produce a checked report.",
        ("sql-15",),
    ),
    "data-analysis": LearningPath(
        "Data analysis",
        "Clean and investigate records, then reconcile an analytical query.",
        ("python-30", "python-data-02", "sql-30"),
    ),
    "machine-learning": LearningPath(
        "Machine learning",
        "Build baseline models and evaluate groups and time without leakage.",
        ("python-45", "python-stats-01", "python-ml-02"),
    ),
    "database-engineering": LearningPath(
        "Database engineering",
        "Prove query correctness, batch safely, and reason about concurrent writes.",
        ("sql-60", "sql-quality-01", "sql-scale-01", "sql-concurrency-01"),
    ),
    "application-engineering": LearningPath(
        "Application engineering",
        "Integrate Python and PostgreSQL and manage safe migration and release changes.",
        ("bridge-08", "python-pro-01", "bridge-ops-01"),
    ),
    "data-product": LearningPath(
        "Data product capstone",
        "Ship a reviewed local data product with correction and incident evidence.",
        ("bridge-capstone-01",),
    ),
}


def learning_paths(catalog: Catalog) -> dict[str, LearningPath]:
    """Merge validated extension goals with the original curated routes."""
    result = dict(LEARNING_PATHS)
    for key, definition in catalog.learning_paths.items():
        if key in result:
            raise ValueError(f"Extensions must not replace an existing learning path: {key}")
        targets = tuple(definition["targets"])
        for target in targets:
            catalog.get(target)
        result[key] = LearningPath(definition["title"], definition["description"], targets)
    return result


@dataclass(frozen=True, slots=True)
class StudyPlan:
    """A topological lesson sequence and a transparent time estimate."""

    targets: tuple[str, ...]
    lessons: tuple[Lesson, ...]
    completed: tuple[str, ...]
    ready: tuple[str, ...]
    estimated_minutes: int
    weekly_hours: float

    @property
    def estimated_weeks(self) -> int:
        """Return a rounded-up estimate, excluding review and repeated attempts."""

        return math.ceil(self.estimated_minutes / (self.weekly_hours * 60))


def build_study_plan(
    catalog: Catalog,
    targets: Iterable[str],
    *,
    completed: Iterable[str] = (),
    weekly_hours: float = 5,
) -> StudyPlan:
    """Expand prerequisites, reject invalid graphs, and retain stable catalog order.

    Completion records mean the learner supplies that prerequisite evidence.
    They do not imply that all of its own prerequisites were completed. The
    traversal still validates the entire requested graph before omitting saved
    completions, so bad metadata cannot hide behind a progress checkbox.
    """

    if not math.isfinite(weekly_hours) or weekly_hours <= 0:
        raise ValueError("Weekly hours must be a positive, finite number.")
    target_ids = tuple(dict.fromkeys(targets))
    if not target_ids:
        raise ValueError("Choose at least one target lesson or a named path.")
    completed_ids = set(completed)
    for lesson_id in (*target_ids, *sorted(completed_ids)):
        catalog.get(lesson_id)

    ordered: list[Lesson] = []
    visited: set[str] = set()
    visiting: list[str] = []

    def visit(lesson_id: str) -> None:
        if lesson_id in visiting:
            cycle = " -> ".join((*visiting[visiting.index(lesson_id) :], lesson_id))
            raise ValueError(f"Prerequisite cycle: {cycle}")
        if lesson_id in visited:
            return
        lesson = catalog.get(lesson_id)
        visiting.append(lesson_id)
        for prerequisite in lesson.prerequisites:
            visit(prerequisite)
        visiting.pop()
        visited.add(lesson_id)
        ordered.append(lesson)

    # Visiting in catalog order gives one predictable plan for the same goal
    # set regardless of the order in which targets were entered.
    for lesson in catalog:
        if lesson.id in target_ids:
            visit(lesson.id)
    pending = tuple(lesson for lesson in ordered if lesson.id not in completed_ids)
    ready = tuple(lesson.id for lesson in pending if set(lesson.prerequisites) <= completed_ids)
    return StudyPlan(
        targets=target_ids,
        lessons=pending,
        completed=tuple(lesson.id for lesson in ordered if lesson.id in completed_ids),
        ready=ready,
        estimated_minutes=sum(lesson.estimated_minutes for lesson in pending),
        weekly_hours=weekly_hours,
    )
