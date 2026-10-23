"""Authenticated application actions for authored module pilots."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.lesson_reader import render_artifact, rendered_targets
from ds60sqlpy.module_jobs import ModuleJobs, profile_readiness
from ds60sqlpy.modules import ModuleCatalog, ModuleState


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
