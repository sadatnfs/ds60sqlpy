"""Authenticated application actions for authored module pilots."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.lesson_reader import reference_relative_path, render_artifact, rendered_targets
from ds60sqlpy.module_jobs import SERVICES, ModuleJobs, profile_readiness
from ds60sqlpy.modules import ModuleCatalog, ModuleState
from ds60sqlpy.worker_operations import PROFILES

RUNTIME_GUIDANCE = {
    "k8s-kind": (
        "This pad submits only the supported curated manifests to your explicitly "
        "prepared owned kind namespace. It checks real Kubernetes state and removes "
        "only the attempt's owned objects. Cluster-wide and other unsupported labs "
        "use the separate scoped host instructions in their guide. See the optional "
        "Kubernetes overlay in the Docker classroom guide."
    ),
    "cpp20": (
        "The pad is saved as main.cpp in a fresh job folder. The worker "
        "compiles with g++ -std=c++20 -pthread -O0 -g -Wall -Wextra "
        "-Wconversion -Wpedantic main.cpp -o program, then runs ./program. A "
        "failed compile stops before execution. Multi-file CMake projects "
        "use the separate Docker instructions in the guide."
    ),
    "java21": (
        "Use public class Main with public static void main(String[] args), "
        "without a package declaration. The worker saves Main.java, runs "
        "javac --release 21 -encoding UTF-8 -Xlint:all -cp "
        "/opt/course-libs/h2-2.5.252.jar -d classes Main.java, then java -ea "
        "-Xmx512m -cp classes:/opt/course-libs/h2-2.5.252.jar Main inside Linux Docker. "
        "Extra helper classes may share this source file. Java assertions are "
        "enabled. The fixed H2 jar supports offline embedded JDBC lessons."
    ),
    "javascript-node": (
        "The pad is main.mjs, an ES module executed by Node 24. Built-in "
        "node: modules are available offline. Browser document and window "
        "APIs are not part of Node. Use the browser-specific examples and "
        "instructions where those APIs are taught."
    ),
    "typescript-node": (
        "The pad is main.mts. TypeScript checks strict types with NodeNext "
        "module resolution before emitting compiled/main.mjs for Node 24. A "
        "type error prevents execution. The fixed compiler and Node types "
        "are included in the image; no npm install runs when you run a "
        "lesson. Runtime JavaScript line numbers may differ from TypeScript "
        "source lines."
    ),
}


def runtime_guidance(profile: str, verification_id: str | None) -> str:
    """Describe the actual execution path selected for this lesson."""
    if profile == "reading":
        return (
            "This lesson uses reading, written reasoning and saved notes. "
            "There is no code execution for this worksheet. Follow any separate "
            "browser or teacher-led activity described in its guide."
        )
    if profile == "cpp20" and verification_id == "cpp-ownership-v1":
        return (
            "The pad is saved as main.cpp. GCC compiles it as C++20 with "
            "-Dmain=ds60_learner_main into learner.o, then links it with the "
            "fixed ownership verifier in verifier.o. The verifier's main "
            "calls your required functions and reports its checks; your "
            "main is not the executed entry point. A compile or link error "
            "stops before execution. Ordinary C++ lessons run your main directly."
        )
    return RUNTIME_GUIDANCE.get(
        profile,
        "Run a complete example in a fresh job folder. Save your draft to "
        "retain it; temporary runtime files are discarded after execution.",
    )


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
            # Shared guide paths prefer the canonical lesson; unique variant source
            # paths still return directly to their own saved workspace.
            lesson_links: dict[str, str] = {}
            for lesson in sorted(
                self.catalog.lessons.values(), key=lambda item: ("@" in item.id, item.id)
            ):
                for path in (lesson.guide_path, lesson.source_path):
                    lesson_links.setdefault("/" + reference_relative_path(path), lesson.id)
                    lesson_links.setdefault("/" + path, lesson.id)
            return {
                **self.catalog.index(),
                "lesson_links": lesson_links,
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
                "setup_commands": (
                    [f"./classroom --profile {lesson.runtime_profile}"]
                    if lesson.runtime_profile in SERVICES and lesson.runtime_profile != "k8s-kind"
                    else []
                ),
                "runtime_guidance": runtime_guidance(
                    lesson.runtime_profile, lesson.verification_id
                ),
                "runtime_profile": lesson.runtime_profile,
                "verification_id": lesson.verification_id,
                "guide_html": render_artifact(
                    self.catalog.content_path(lesson.guide_path),
                    repo_root=self.catalog.root,
                    targets=self.targets,
                    id_prefix="module-guide--",
                    output_path="classroom",
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
                        output_path="classroom",
                    ),
                }
                for i, path in enumerate(lesson.solution_paths)
            ]
            return {"documents": documents}
        raise ValueError("Unknown module action.")

    def close(self) -> None:
        self.jobs.close()
