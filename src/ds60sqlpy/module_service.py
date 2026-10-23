"""Authenticated application actions for authored module pilots."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.lesson_reader import render_artifact, rendered_targets
from ds60sqlpy.module_jobs import ModuleJobs, profile_readiness
from ds60sqlpy.modules import ModuleCatalog, ModuleState
from ds60sqlpy.worker_operations import PROFILES

RUNTIME_GUIDANCE = {
    ("cpp20"): (
        "The pad is saved as main.cpp in a fresh job folder. The worker "
        "compiles with g++ -std=c++20 -pthread -O0 -g -Wall -Wextra "
        "-Wconversion -Wpedantic main.cpp -o program, then runs ./program. A "
        "failed compile stops before execution. Multi-file CMake projects "
        "use the separate Docker instructions in the guide."
    ),
    ("java21"): (
        "Use public class Main with public static void main(String[] args), "
        "without a package declaration. The worker saves Main.java, runs "
        "javac --release 21 -encoding UTF-8 -Xlint:all -d classes Main.java, "
        "then java -ea -Xmx512m -cp classes Main. Extra helper classes may "
        "share this source file. Java assertions are enabled."
    ),
    ("javascript-node"): (
        "The pad is main.mjs, an ES module executed by Node 24. Built-in "
        "node: modules are available offline. Browser document and window "
        "APIs are not part of Node. Use the browser-specific examples and "
        "instructions where those APIs are taught."
    ),
    ("typescript-node"): (
        "The pad is main.mts. TypeScript checks strict types with NodeNext "
        "module resolution before emitting compiled/main.mjs for Node 24. A "
        "type error prevents execution. The fixed compiler and Node types "
        "are included in the image; no npm install runs when you run a "
        "lesson. Runtime JavaScript line numbers may differ from TypeScript "
        "source lines."
    ),
}


class ModuleService:
    def __init__(self, catalog: Catalog, state_directory: Path | None = None) -> None:
        self.catalog = ModuleCatalog(catalog.repo_root)
        self.state = ModuleState(self.catalog, state_directory)
        self.jobs = ModuleJobs(self.catalog, self.state)
        self.targets = rendered_targets(catalog)

    def action(self, payload: dict[str, Any]) -> dict[str, Any]:
        action = payload.get("action")
        if action == "module-index":
            with self.jobs.lock:
                active = self.jobs.active
            return {
                **self.catalog.index(),
                "active_job": self.jobs.get(active) if active is not None else None,
            }
        if action == "module-readiness":
            profiles = {lesson.runtime_profile for lesson in self.catalog.lessons.values()}
            return {"profiles": profile_readiness(self.jobs.client, profiles)}
        if action == "module-job":
            return self.jobs.get(payload.get("job_id"))
        if action == "module-cancel":
            return self.jobs.cancel(payload.get("job_id"))
        if action == "module-recover":
            return self.jobs.recover(payload.get("job_id"), payload.get("confirmation"))
        lesson = self.catalog.get(payload.get("lesson_id"))
        if action == "module-lesson":
            planned = self.catalog.planned[lesson.id]
            session = self.state.read(lesson.id)
            return {
                **planned,
                "status": "authored",
                "language": lesson.language,
                "learning_mode": lesson.learning_mode,
                "source_filename": PROFILES[lesson.runtime_profile].filename
                if lesson.runtime_profile in PROFILES
                else "notes.md",
                "runtime_guidance": RUNTIME_GUIDANCE.get(
                    lesson.runtime_profile,
                    (
                        "Run a complete example in a fresh job folder. Save your draft to "
                        "retain it; temporary runtime files are discarded after execution."
                    ),
                ),
                "runtime_profile": lesson.runtime_profile,
                "verification_id": lesson.verification_id,
                "guide_html": render_artifact(
                    self.catalog.content_path(lesson.guide_path),
                    repo_root=self.catalog.root,
                    targets=self.targets,
                    id_prefix="module-guide--",
                    output_path="journeys",
                ),
                "source": session["source"] if "source" in session else self.catalog.source(lesson),
                "session": session,
                "history": self.jobs.history(lesson.id),
                "capability": self.jobs.client.readiness(lesson.runtime_profile),
            }
        if action == "module-save":
            return {"session": self.state.save(lesson.id, payload.get("fields"))}
        if action == "module-run":
            return self.jobs.start(
                lesson.id,
                payload.get("source"),
                payload.get("timeout_seconds", 60),
                payload.get("request_id"),
            )
        if action == "module-solutions":
            if payload.get("reveal") is not True:
                raise ValueError("Explicitly reveal a solution after attempting the exercises.")
            documents = [
                {
                    "path": path,
                    "html": render_artifact(
                        self.catalog.content_path(path),
                        repo_root=self.catalog.root,
                        targets=self.targets,
                        id_prefix=f"module-solution-{i}--",
                        output_path="journeys",
                    ),
                }
                for i, path in enumerate(lesson.solution_paths)
            ]
            return {"documents": documents}
        raise ValueError("Unknown module action.")

    def close(self) -> None:
        self.jobs.close()
