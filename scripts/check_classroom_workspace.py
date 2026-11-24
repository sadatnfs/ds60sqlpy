"""Phase 6 desktop workspace flows for the real Chromium classroom gate.

`scripts/check_classroom_browser.py` calls these checks against a disposable
stack. They cover the per-mode workspace strip, a keyboard-only flow, a focus
visibility walk, an optional axe-core scan, draft preservation, the draft
conflict panel, an authored module walkthrough and the restart stages. The
pure helpers at the top run offline in tests/test_classroom_browser_probe.py.
No third-party module is imported here; Playwright objects arrive as arguments.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

AXE_VERSION = "4.14.1"
AXE_TARGET_LIMIT = 5
AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]
BLOCKING_IMPACTS = frozenset({"serious", "critical"})
EXECUTION_ACTIONS = frozenset({"run", "step-through"})
MODE_KEYS = (
    "legacy-python",
    "sql-snippet",
    "sql-lesson",
    "module-ready",
    "module-not-ready",
    "module-reading",
    "dax-offline",
    "browser-preview",
)
BROWSER_PROFILES = frozenset({"html-browser", "javascript-browser"})
# The disposable stack starts only the Python Core worker.
READY_PROFILES = frozenset({"python-core"})
SAVED = "Saved in your local learning workspace."
CONFLICT_TEXT = (
    "A browser copy of this lesson from an earlier visit differs from your saved draft. "
    "Your saved draft is in the editor and nothing was replaced."
)
KEEP_TEXT = (
    "Kept your saved draft. The browser copy is offered again the next time you open this lesson."
)
SOURCE_EDITOR = "#source-editor .cm-content"


# Pure helpers ---------------------------------------------------------------


def classify_axe(result: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split axe violations into blocking (serious, critical) and recorded findings."""
    blocking: list[dict[str, Any]] = []
    recorded: list[dict[str, Any]] = []
    for violation in result.get("violations", []):
        nodes = violation.get("nodes") or []
        finding = {
            "id": violation.get("id"),
            "impact": violation.get("impact"),
            "nodes": len(nodes),
            "targets": [
                " ".join(str(part) for part in node.get("target") or [])
                for node in nodes[:AXE_TARGET_LIMIT]
            ],
        }
        (blocking if finding["impact"] in BLOCKING_IMPACTS else recorded).append(finding)
    return blocking, recorded


def lesson_mode_keys(lesson: dict[str, Any], ready_profiles: frozenset[str]) -> list[str]:
    """Name the workspace modes one published lesson row can demonstrate."""
    if lesson.get("status") != "authored":
        return []
    profile = lesson.get("runtime_profile")
    if lesson.get("engine") == "legacy":
        if profile == "python":
            return ["legacy-python"]
        if profile == "sql":
            return ["sql-snippet", "sql-lesson"]
        return []
    if profile == "reading":
        return ["module-reading"]
    if profile == "dax-offline":
        return ["dax-offline"]
    if profile in BROWSER_PROFILES:
        return ["browser-preview"]
    if not isinstance(profile, str) or not profile:
        return []
    return ["module-ready" if profile in ready_profiles else "module-not-ready"]


def choose_mode_samples(
    index: dict[str, Any], ready_profiles: frozenset[str] = READY_PROFILES
) -> dict[str, str]:
    """Pick the first lesson ID by sort for every workspace mode present in the index."""
    found: dict[str, list[str]] = {}
    for track in index.get("tracks", []):
        for lesson in track.get("lessons", []):
            for key in lesson_mode_keys(lesson, ready_profiles):
                found.setdefault(key, []).append(str(lesson["id"]))
    return {key: sorted(found[key])[0] for key in MODE_KEYS if key in found}


def track_of(index: dict[str, Any], lesson_id: str) -> str:
    for track in index.get("tracks", []):
        if any(lesson.get("id") == lesson_id for lesson in track.get("lessons", [])):
            return str(track["id"])
    raise KeyError(lesson_id)


def lesson_row(index: dict[str, Any], lesson_id: str) -> dict[str, Any]:
    for track in index.get("tracks", []):
        for lesson in track.get("lessons", []):
            if lesson.get("id") == lesson_id:
                return dict(lesson)
    raise KeyError(lesson_id)


def expected_strip(mode: str, profile: str) -> dict[str, Any]:
    """The 06-01 strip copy, Run label and Result visibility for one sampled mode."""
    if mode == "module-reading":
        return {
            "label": "Reading lesson",
            "run": "Reading and reasoning",
            "runs_in": "No code runs in this lesson.",
            "results_visible": False,
        }
    if mode == "dax-offline":
        return {
            "label": "Offline draft",
            "run": None,
            "runs_in": "Nothing runs. You save, compare and export this draft.",
            "results_visible": False,
        }
    if mode == "browser-preview":
        return {
            "label": "Browser preview",
            "run": "Run browser preview",
            "runs_in": "The isolated preview in this browser tab",
            "results_visible": True,
        }
    runs_in = {
        "legacy-python": "The Python runner in your local classroom",
        "sql-snippet": "PostgreSQL in your local classroom",
        "sql-lesson": "PostgreSQL in your local classroom",
    }.get(mode, "The " + profile + " worker container on this computer")
    return {
        "label": "Code practice",
        "run": "Run code",
        "runs_in": runs_in,
        "results_visible": True,
    }


def focus_cue_ok(style: dict[str, Any]) -> bool:
    """A focus cue is a solid-ish outline at least 2px wide or any box shadow."""
    outline = str(style.get("outlineStyle") or "none")
    match = re.match(r"^\s*([0-9.]+)px", str(style.get("outlineWidth") or ""))
    width = float(match.group(1)) if match else 0.0
    if outline not in {"none", "hidden"} and width >= 2:
        return True
    shadow = str(style.get("boxShadow") or "none").strip()
    return shadow not in {"", "none"}


def normalized_action(path: str, action: str) -> str:
    """Map API actions onto the names assert_no_execution_requests understands."""
    if path == "/api/modules" and action.startswith("module-"):
        return action.removeprefix("module-")
    if path == "/api/classroom":
        return "classroom:" + action
    return action


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Browser helpers -------------------------------------------------------------


def _gate() -> Any:
    # Imported lazily: the gate imports this module at load time.
    from scripts import check_classroom_browser

    return check_classroom_browser


class RequestLog:
    """Record classroom API actions so checks can prove nothing executed."""

    def __init__(self, page: Any) -> None:
        self.actions: list[str] = []
        page.on("request", self._record)

    def _record(self, request: Any) -> None:
        if request.method != "POST":
            return
        path = urlsplit(request.url).path
        if path not in {"/api/lab", "/api/modules", "/api/classroom"}:
            return
        try:
            payload = request.post_data_json
        except ValueError:
            return
        if isinstance(payload, dict) and isinstance(payload.get("action"), str):
            self.actions.append(normalized_action(path, payload["action"]))

    def mark(self) -> int:
        return len(self.actions)

    def since(self, start: int) -> list[str]:
        return self.actions[start:]


@contextmanager
def fresh_page(browser: Any, origin: str, audit: Any) -> Iterator[Any]:
    context = audit.context(browser, origin)
    try:
        yield context.new_page()
    finally:
        context.close()


def load_home(page: Any, origin: str, expect: Any) -> None:
    page.goto(origin + "/classroom")
    expect(page.locator("#subject-cards .subject-card").first).to_be_visible(timeout=90_000)
    page.wait_for_function("() => typeof index === 'object' && index && index.tracks")


def page_index(page: Any) -> dict[str, Any]:
    data: dict[str, Any] = page.evaluate("() => index")
    return data


def wait_loaded(page: Any, lesson_id: str, expect: Any) -> None:
    expect(page).to_have_url(
        re.compile(r"[#&]lesson=" + re.escape(quote(lesson_id, safe="")) + r"(?:&|$)")
    )
    expect(page.locator('#lessons button[aria-current="page"] small')).to_contain_text(lesson_id)
    expect(page.locator("#save-state")).to_contain_text(re.compile(r"Loaded|Recovered|Saved|Kept"))
    expect(page.locator("#workspace-mode")).to_be_visible()


def show_practice(page: Any, expect: Any) -> None:
    """Leave reading focus so the code pane and Result panel are on screen.

    Tutorial lessons open in reading focus by design, and the choice is kept per track,
    so a mode check must switch to the practice view the way a learner would.
    """
    toggle = page.locator("#reading-toggle")
    if toggle.is_visible() and toggle.get_attribute("aria-pressed") == "true":
        toggle.click()
        expect(toggle).to_have_attribute("aria-pressed", "false")


def open_lesson(page: Any, lesson_id: str, expect: Any) -> None:
    """Open a lesson through the same function the palette and lesson list call."""
    page.evaluate("id => openLesson(id)", lesson_id)
    wait_loaded(page, lesson_id, expect)
    show_practice(page, expect)


def goto_lesson(page: Any, origin: str, lesson_id: str, expect: Any) -> None:
    page.goto(origin + "/classroom#lesson=" + quote(lesson_id, safe=""))
    wait_loaded(page, lesson_id, expect)
    show_practice(page, expect)


def set_pad_mode(page: Any, mode: str, expect: Any) -> None:
    if page.locator("#pad-mode").input_value() != mode:
        page.locator("#pad-mode").select_option(mode)
    expect(page).to_have_url(re.compile(r"[#&]mode=" + mode + r"(?:&|$)"))
    expect(page.locator("#pad-mode")).to_have_value(mode)
    expect(page.locator("#save-state")).to_contain_text("Loaded")


def conflict_shown(page: Any) -> bool:
    return bool(
        page.locator("#draft-conflict").count() and page.locator("#draft-conflict").is_visible()
    )


def keep_saved_draft_if_offered(page: Any, expect: Any) -> bool:
    """Tolerate a draft conflict prompt: keep the saved draft and report it was shown."""
    if not conflict_shown(page):
        return False
    page.locator("#draft-conflict").get_by_role("button", name="Keep saved draft").click()
    expect(page.locator("#draft-conflict")).to_have_count(0)
    return True


def strip_values(page: Any) -> list[str]:
    values: list[str] = page.locator("#workspace-mode").evaluate(
        "node => [...node.children].map(child => child.textContent.trim())"
    )
    return values


def active_info(page: Any) -> dict[str, Any]:
    info: dict[str, Any] = page.evaluate(
        """() => {
          const active = document.activeElement;
          if (!active || active === document.body || active === document.documentElement)
            return { none: true };
          const editor = active.closest('.code-editor');
          const target = editor || active;
          const style = getComputedStyle(target);
          const classes = [...active.classList].slice(0, 2).map(name => '.' + name).join('');
          return {
            none: false,
            selector: active.tagName.toLowerCase() + (active.id ? '#' + active.id : '') + classes,
            id: active.id || '',
            inEditor: Boolean(active.closest('.cm-editor')),
            viaEditor: Boolean(editor),
            outlineStyle: style.outlineStyle,
            outlineWidth: style.outlineWidth,
            boxShadow: style.boxShadow
          };
        }"""
    )
    return info


def tab(page: Any, *, back: bool = False) -> None:
    """Press Tab, first releasing the CodeMirror Tab trap the way a learner would."""
    if page.evaluate("() => Boolean(document.activeElement?.closest('.cm-editor'))"):
        page.keyboard.press("Escape")
    page.keyboard.press("Shift+Tab" if back else "Tab")


def tab_until(page: Any, predicate: str, limit: int, what: str) -> None:
    """Press Tab until a JavaScript predicate on document.activeElement holds."""
    script = "() => { const el = document.activeElement; return Boolean(" + predicate + "); }"
    for _ in range(limit):
        if page.evaluate(script):
            return
        tab(page)
    if not page.evaluate(script):
        raise AssertionError(f"Keyboard focus never reached {what} within {limit} Tab presses.")


def module_snapshot(page: Any, lesson_id: str) -> dict[str, Any]:
    """learner_snapshot reads legacy pads; this is the module equivalent with the same keys."""
    snapshot: dict[str, Any] = page.evaluate(
        """async lessonId => {
          const lesson = await api('module-lesson', { lesson_id: lessonId });
          return {
            route: location.pathname + location.hash,
            selectedLesson:
              document.querySelector('#lessons button[aria-current="page"] small')
                ?.textContent.trim() || null,
            source: document.getElementById('source').value,
            explanation: document.getElementById('explanation').value,
            session: lesson.session,
            exerciseProgress: exerciseProgress(),
            pad: { code: lesson.session.source ?? lesson.source },
            history: (lesson.history || []).map(job => job.id || job.job_id || job.receipt_id)
          };
        }""",
        lesson_id,
    )
    return snapshot


def assert_module_state_unchanged(
    page: Any, lesson_id: str, before: dict[str, Any], action: str, audit: Any
) -> None:
    after = module_snapshot(page, lesson_id)
    changed = [key for key in before if before[key] != after[key]]
    assert not changed, f"{action} changed learner state: {changed}"
    audit.preserved(action, before, after)


def record_preservation(audit: Any, inspection: str, lesson: str, before: str, after: str) -> None:
    audit.preservation.append(
        {
            "inspection": inspection,
            "lesson_before": lesson,
            "lesson_after": lesson,
            "draft_sha256_before": sha256(before),
            "draft_sha256_after": sha256(after),
        }
    )


# Flows -----------------------------------------------------------------------


def mode_sample_checks(
    page: Any, samples: dict[str, str], index: dict[str, Any], expect: Any
) -> dict[str, Any]:
    """UX-01: each sampled lesson shows the strip, Run label and Result visibility for its mode."""
    receipt: dict[str, Any] = {}
    for mode, lesson_id in samples.items():
        open_lesson(page, lesson_id, expect)
        if mode == "sql-snippet":
            set_pad_mode(page, "snippet", expect)
        elif mode == "sql-lesson":
            set_pad_mode(page, "lesson", expect)
        keep_saved_draft_if_offered(page, expect)
        cap: dict[str, Any] = page.evaluate("() => current.capability || {}")
        profile = str(cap.get("profile") or lesson_row(index, lesson_id).get("runtime_profile"))
        want = expected_strip(mode, profile)
        strip = strip_values(page)
        assert len(strip) == 6, f"{lesson_id}: the mode strip has {len(strip)} cells."
        assert strip[1] == want["label"], f"{lesson_id} ({mode}): lesson type {strip[1]!r}"
        assert strip[3] == want["runs_in"], f"{lesson_id} ({mode}): code runs in {strip[3]!r}"
        results = page.locator("#runtime-results")
        if want["results_visible"]:
            expect(results).to_be_visible()
        else:
            expect(results).to_be_hidden()
            assert results.get_attribute("hidden") is not None, (
                f"{lesson_id}: the Result panel is hidden only by CSS."
            )
        run = page.locator("#run")
        if want["run"] is None:
            expect(run).to_be_hidden()
        else:
            expect(run).to_have_text(want["run"])
        text = page.locator("#workspace-view").inner_text()
        if not want["results_visible"]:
            assert "Press Run code" not in text, f"{lesson_id}: a {mode} lesson promises a run."
        capability = page.locator("#capability")
        if mode == "module-not-ready":
            assert cap.get("ready") is False, f"{lesson_id}: {profile} unexpectedly ready."
            expect(capability).to_have_text(
                "The " + profile + " runtime is not ready. " + str(cap.get("detail") or "")
            )
            expect(capability).to_have_class("notice warn")
            expect(run).to_be_disabled()
        elif mode in {"legacy-python", "sql-snippet", "sql-lesson", "module-ready"}:
            assert cap.get("ready") is True, f"{lesson_id}: the {mode} runtime is not ready."
            expect(capability).to_contain_text("Ready to run in your local classroom.")
            expect(run).to_be_enabled()
        elif mode == "module-reading":
            expect(run).to_be_disabled()
        receipt[mode] = {
            "id": lesson_id,
            "strip": strip,
            "results_visible": results.is_visible(),
            "run_label": None if want["run"] is None else run.inner_text(),
        }
    return receipt


def authored_walkthrough_check(
    browser: Any, origin: str, audit: Any, expect: Any, track: str = "go"
) -> dict[str, Any]:
    """QUAL-02: open the first validated authored walkthrough, step it and leave no trace."""
    document = json.loads((ROOT / "courses" / track / "walkthroughs.json").read_text())
    entry = document["walkthroughs"][0]
    lesson_id = str(entry["lesson_id"])
    steps = entry["steps"]
    assert len(steps) >= 2, f"{lesson_id}: an authored walkthrough needs at least two steps."
    gate = _gate()
    with fresh_page(browser, origin, audit) as page:
        log = RequestLog(page)
        goto_lesson(page, origin, lesson_id, expect)
        keep_saved_draft_if_offered(page, expect)
        assert page.evaluate("() => current.walkthrough_available") is True, (
            f"{lesson_id}: the server did not offer its authored walkthrough."
        )
        button = page.locator("#walk-reference")
        expect(button).to_be_visible()
        before = module_snapshot(page, lesson_id)
        start = log.mark()
        button.focus()
        page.keyboard.press("Enter")
        panel = page.locator("#step-panel")
        expect(panel).to_be_visible()
        expect(panel).to_have_attribute("data-kind", "authored")
        expect(page.locator("#step-badge")).to_be_visible()
        expect(page.locator("#step-badge")).to_have_text("Authored steps, not a live trace")
        expect(page.locator("#step-count")).to_have_text(f"Step 1 of {len(steps)}")
        narration = page.locator("#step-narration")
        expect(narration).to_have_text(
            "Step 1: " + steps[0]["title"] + ". " + steps[0]["explanation"]
        )
        expect(narration).to_be_visible()
        page.keyboard.press("ArrowRight")
        expect(page.locator("#step-count")).to_have_text(f"Step 2 of {len(steps)}")
        expect(narration).to_contain_text("Step 2: " + steps[1]["title"] + ".")
        page.keyboard.press("ArrowLeft")
        expect(page.locator("#step-count")).to_have_text(f"Step 1 of {len(steps)}")
        expect(narration).to_contain_text("Step 1: " + steps[0]["title"] + ".")
        page.keyboard.press("Escape")
        expect(panel).to_be_hidden()
        actions = log.since(start)
        gate.assert_no_execution_requests(log.actions, start, "The authored walkthrough")
        assert actions.count("walkthrough") == 1, actions
        assert not {"save", "save-pad"} & set(actions), f"The walkthrough saved: {actions}"
        assert_module_state_unchanged(page, lesson_id, before, "The authored walkthrough", audit)
    audit.passed(f"The {lesson_id} authored walkthrough opens, steps and closes without a run")
    return {
        "track": track,
        "lesson_id": lesson_id,
        "steps": len(steps),
        "first_step": steps[0]["title"],
        "keyboard_step": True,
        "requests": actions,
        "stale_hidden": "server-validated",
    }


def keyboard_flow(
    browser: Any, origin: str, audit: Any, expect: Any, lesson_id: str, title: str
) -> dict[str, bool]:
    """UX-02: the desktop flow with page.keyboard only (Chromium on Linux uses Control)."""
    gate = _gate()
    steps: dict[str, bool] = {}
    marker = "KEYBOARD_" + uuid.uuid4().hex
    with fresh_page(browser, origin, audit) as page:
        log = RequestLog(page)
        load_home(page, origin, expect)
        tab_until(page, "el && el.matches('a.skip[href=\"#main\"]')", 5, "the skip link")
        page.keyboard.press("Enter")
        assert page.evaluate("() => Boolean(document.activeElement?.closest('#main'))"), (
            "Skip to learning content did not move focus into main."
        )
        steps["skip_to_content"] = True

        page.keyboard.press("Control+k")
        expect(page.locator("#palette")).to_have_attribute("open", "")
        page.keyboard.type(lesson_id)
        page.keyboard.press("Enter")
        wait_loaded(page, lesson_id, expect)
        expect(page.locator("#title")).to_be_visible()
        expect(page.locator("#title")).to_contain_text(title)
        steps["palette_opens_lesson"] = True

        tab_until(page, "el && el.closest('.cm-content')", 400, "the code editor")
        page.keyboard.press("Control+k")
        page.wait_for_timeout(200)
        assert page.locator("#palette").get_attribute("open") is None, (
            "Control+K inside the editor opened the palette."
        )
        steps["palette_ignored_in_editor"] = True

        # Replace the draft: starters may end in raise SystemExit(main()), so an
        # appended line would never run.
        page.keyboard.press("Control+a")
        page.keyboard.type(f"print({marker!r})")
        page.keyboard.press("Control+s")
        expect(page.locator("#save-state")).to_have_text(SAVED)
        steps["save_shortcut"] = True
        page.keyboard.press("Escape")
        page.keyboard.press("Tab")
        assert not page.evaluate("() => Boolean(document.activeElement?.closest('.cm-editor'))"), (
            "Escape then Tab did not leave the editor."
        )
        steps["leave_editor"] = True

        page.keyboard.press("Control+Enter")
        expect(page.locator("#output")).to_contain_text(marker, timeout=90_000)
        expect(page.locator("#job-status")).to_contain_text("Finished", timeout=90_000)
        steps["run_shortcut"] = True

        page.reload()
        wait_loaded(page, lesson_id, expect)
        keep_saved_draft_if_offered(page, expect)
        # After a reload the lesson load moves focus into the page, so start from the
        # first skip link; Skip to result must be the very next Tab stop.
        page.locator('a.skip[href="#main"]').focus()
        tab_until(page, "el && el.id === 'skip-result'", 2, "Skip to result")
        page.keyboard.press("Enter")
        expect(page.locator("#results-title")).to_be_focused()
        steps["skip_to_result"] = True

        tab_until(page, "el && el.matches('#job-history > summary')", 60, "Saved runs")
        page.keyboard.press("Enter")
        expect(page.locator("#job-history")).to_have_attribute("open", "")
        expect(page.locator("#history button").first).to_be_visible()
        before = gate.learner_snapshot(page, lesson_id)
        start = log.mark()
        tab_until(
            page,
            "el && el === [...document.querySelectorAll('#history button')].at(-1)",
            60,
            "the oldest saved run",
        )
        page.keyboard.press("Enter")
        expect(page.locator("#run-storage-status")).to_contain_text("Saved run")
        gate.assert_no_execution_requests(log.actions, start, "Opening an old run by keyboard")
        gate.assert_learning_state_unchanged(
            page, lesson_id, before, "Opening an old run by keyboard", audit
        )
        steps["open_old_run"] = True

        page.reload()
        wait_loaded(page, lesson_id, expect)
        keep_saved_draft_if_offered(page, expect)
        tab_until(page, "el && el.id === 'tour-start'", 200, "Tour this page")
        page.keyboard.press("Enter")
        expect(page.locator(".tour-card")).to_be_visible()
        assert page.evaluate(
            """() => [...document.body.children]
                .filter(node => !node.classList.contains('tour-layer'))
                .every(node => node.inert || ['SCRIPT', 'TEMPLATE'].includes(node.tagName))"""
        ), "The page behind the tour is not inert."
        for _ in range(10):
            page.keyboard.press("Tab")
            assert page.evaluate("() => Boolean(document.activeElement?.closest('.tour-layer'))"), (
                "Tab left the open tour."
            )
        page.keyboard.press("Escape")
        expect(page.locator(".tour-card")).to_have_count(0)
        assert page.evaluate("() => ![...document.body.children].some(node => node.inert)"), (
            "Closing the tour left the page inert."
        )
        steps["tour_traps_focus"] = True
    assert all(steps.values())
    audit.passed("A keyboard-only learner can skip, search, save, run, jump to results and review")
    return steps


def focus_walk(
    browser: Any, origin: str, audit: Any, expect: Any, lessons: list[str], stops: int = 80
) -> dict[str, Any]:
    """UX-02: every Tab stop shows a visible cue; CodeMirror is judged by .code-editor."""
    checked = 0
    failures: list[dict[str, Any]] = []
    with fresh_page(browser, origin, audit) as page:
        for lesson_id in lessons:
            goto_lesson(page, origin, lesson_id, expect)
            keep_saved_draft_if_offered(page, expect)
            page.evaluate("() => document.activeElement?.blur()")
            for _ in range(stops):
                tab(page)
                info = active_info(page)
                if info["none"]:
                    continue
                checked += 1
                if not focus_cue_ok(info):
                    failures.append(
                        {
                            "lesson": lesson_id,
                            "selector": info["selector"],
                            "outline": f"{info['outlineStyle']} {info['outlineWidth']}",
                            "box_shadow": info["boxShadow"],
                        }
                    )
    receipt = {
        "lessons": lessons,
        "stops": checked,
        "allowlist": [".cm-content via .code-editor:focus-within"],
        "failures": failures,
    }
    assert not failures, "Focus stops without a visible cue: " + json.dumps(failures[:20])
    audit.passed(f"{checked} keyboard focus stops show a visible cue")
    return receipt


def axe_scan(
    browser: Any,
    origin: str,
    audit: Any,
    expect: Any,
    axe_script: Path,
    samples: dict[str, str],
) -> dict[str, Any]:
    """D-01: no serious or critical axe-core findings in light and dark themes."""
    if not axe_script.is_file():
        raise AssertionError(f"--axe-script {axe_script} does not exist.")
    pages: list[tuple[str, str | None]] = [("home", None)]
    for mode in (
        "legacy-python",
        "sql-snippet",
        "module-reading",
        "dax-offline",
        "module-not-ready",
        "browser-preview",
    ):
        if mode in samples:
            pages.append((mode, samples[mode]))
    pages.append(("palette", None))
    blocking: list[dict[str, Any]] = []
    recorded: list[dict[str, Any]] = []
    scanned: list[str] = []
    version = None
    with fresh_page(browser, origin, audit) as page:
        for name, lesson_id in pages:
            if lesson_id is None:
                load_home(page, origin, expect)
            else:
                goto_lesson(page, origin, lesson_id, expect)
                if name == "sql-snippet":
                    set_pad_mode(page, "snippet", expect)
                keep_saved_draft_if_offered(page, expect)
            page.add_script_tag(path=str(axe_script))
            version = page.evaluate("() => axe.version")
            assert version == AXE_VERSION, f"axe-core {version} is not the pinned {AXE_VERSION}."
            for theme in ("light", "dark"):
                if page.locator("body").get_attribute("data-mode") != theme:
                    page.locator("#theme-toggle").click()
                expect(page.locator("body")).to_have_attribute("data-mode", theme)
                if name == "palette":
                    page.keyboard.press("Control+k")
                    expect(page.locator("#palette")).to_have_attribute("open", "")
                # Saved figure and preview frames are separate documents without axe.
                result = page.evaluate(
                    """tags => axe.run(document, {
                        runOnly: { type: 'tag', values: tags },
                        iframes: false
                    })""",
                    AXE_TAGS,
                )
                if name == "palette":
                    page.keyboard.press("Escape")
                found, advisory = classify_axe(result)
                for finding in found:
                    blocking.append({**finding, "page": name, "theme": theme})
                for finding in advisory:
                    recorded.append({**finding, "page": name, "theme": theme})
                scanned.append(f"{name}:{theme}")
    receipt = {
        "version": version,
        "tags": AXE_TAGS,
        "pages": scanned,
        "blocking": blocking,
        "recorded": recorded,
    }
    # The gate calls assert_axe_clean after its remaining checks, so one run keeps
    # both this evidence and the later results.
    return receipt


def assert_axe_clean(audit: Any) -> None:
    """D-01: fail the gate on any serious or critical axe-core finding that was recorded."""
    receipt = audit.workspace.get("axe")
    if not receipt or "skipped" in receipt:
        return
    blocking = receipt["blocking"]
    assert not blocking, "axe-core serious or critical findings: " + json.dumps(blocking)
    audit.passed(
        f"axe-core {AXE_VERSION}: no serious or critical findings on {len(receipt['pages'])} scans"
    )


def draft_conflict_check(page: Any, lesson_id: str, source: str, audit: Any, expect: Any) -> None:
    """STATE-01: a stale browser copy is offered, never forced, and never saved over a draft."""
    gate = _gate()
    log = RequestLog(page)
    before = gate.learner_snapshot(page, lesson_id)
    key = page.evaluate("() => workspaceKey()")
    stale = "CONFLICT_" + uuid.uuid4().hex
    page.evaluate(
        """([key, source]) => localStorage.setItem(
            'ds60.classroom.unsaved.' + key,
            JSON.stringify({ source, prediction: '', explanation: '' }))""",
        [key, f"print({stale!r})\n"],
    )
    start = log.mark()
    page.reload()
    wait_loaded(page, lesson_id, expect)
    panel = page.locator("#draft-conflict")
    expect(panel).to_be_visible()
    expect(page.locator("#draft-conflict-text")).to_have_text(CONFLICT_TEXT)
    expect(panel.locator("button")).to_have_text(
        ["Use browser copy", "Keep saved draft", "Discard browser copy"]
    )
    expect(page.locator("#source")).to_have_value(source)
    stored = page.evaluate(
        "key => [localStorage.getItem('ds60.classroom.unsaved.' + key), "
        "localStorage.getItem('ds60.classroom.conflict.' + key)]",
        key,
    )
    assert stored[0] is None and stored[1] and stale in stored[1], stored
    page.wait_for_timeout(1500)
    assert not {"save", "save-pad"} & set(log.since(start)), log.since(start)
    gate.assert_learning_state_unchanged(page, lesson_id, before, "Offering a browser copy", audit)
    panel.get_by_role("button", name="Keep saved draft").click()
    expect(panel).to_have_count(0)
    expect(page.locator("#save-state")).to_have_text(KEEP_TEXT)
    page.reload()
    wait_loaded(page, lesson_id, expect)
    expect(page.locator("#draft-conflict")).to_be_visible()
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("#draft-conflict").get_by_role("button", name="Discard browser copy").click()
    expect(page.locator("#draft-conflict")).to_have_count(0)
    assert (
        page.evaluate("key => localStorage.getItem('ds60.classroom.conflict.' + key)", key) is None
    )
    expect(page.locator("#source")).to_have_value(source)
    gate.assert_no_execution_requests(log.actions, start, "The draft conflict panel")
    gate.assert_learning_state_unchanged(
        page, lesson_id, before, "Keeping and discarding a browser copy", audit
    )
    audit.passed("A stale browser copy is offered, kept and discarded without replacing the draft")


def preservation_checks(
    browser: Any, origin: str, audit: Any, expect: Any, samples: dict[str, str]
) -> None:
    """STATE-01: drafts survive reload and lesson switching; reset and history never execute."""
    gate = _gate()
    marker = "PRESERVE_" + uuid.uuid4().hex
    legacy_id = samples["legacy-python"]
    module_id = samples["module-ready"]
    other_id = samples.get("sql-snippet") or samples["module-reading"]
    legacy_source = f"print({marker + '_LEGACY'!r})\n"
    module_source = f"print({marker + '_MODULE'!r})\n"
    with fresh_page(browser, origin, audit) as page:
        log = RequestLog(page)
        goto_lesson(page, origin, legacy_id, expect)
        keep_saved_draft_if_offered(page, expect)
        gate.show_code_and_notes(page, expect)
        page.locator(SOURCE_EDITOR).fill(legacy_source)
        gate.save(page, expect)
        page.reload()
        wait_loaded(page, legacy_id, expect)
        expect(page.locator("#source")).to_have_value(legacy_source)
        record_preservation(
            audit,
            "Reload keeps the legacy draft",
            legacy_id,
            legacy_source,
            page.locator("#source").input_value(),
        )
        open_lesson(page, other_id, expect)
        open_lesson(page, legacy_id, expect)
        expect(page.locator("#source")).to_have_value(legacy_source)
        record_preservation(
            audit,
            "Lesson switch keeps the legacy draft",
            legacy_id,
            legacy_source,
            page.locator("#source").input_value(),
        )
        draft_conflict_check(page, legacy_id, legacy_source, audit, expect)

        sql_id = samples.get("sql-snippet")
        if sql_id is not None:
            open_lesson(page, sql_id, expect)
            set_pad_mode(page, "snippet", expect)
            reset = page.locator("#sql-ready-reset")
            prepare = page.locator("#sql-ready-action")
            if not reset.is_visible() and prepare.is_visible():
                prepare.click()
            expect(reset).to_be_visible(timeout=90_000)
            expect(reset).to_be_enabled(timeout=90_000)
            before = gate.learner_snapshot(page, sql_id)
            start = log.mark()
            page.once("dialog", lambda dialog: dialog.accept())
            reset.click()
            expect(page.locator("#status")).to_have_text(
                "The training tables were reset to the original course data.", timeout=90_000
            )
            gate.assert_no_execution_requests(log.actions, start, "Resetting SQL practice data")
            gate.assert_learning_state_unchanged(
                page, sql_id, before, "Resetting SQL practice data", audit
            )

        open_lesson(page, module_id, expect)
        keep_saved_draft_if_offered(page, expect)
        gate.show_code_and_notes(page, expect)
        page.locator(SOURCE_EDITOR).fill(module_source)
        gate.save(page, expect)
        page.reload()
        wait_loaded(page, module_id, expect)
        keep_saved_draft_if_offered(page, expect)
        expect(page.locator("#source")).to_have_value(module_source)
        record_preservation(
            audit,
            "Reload keeps the module draft",
            module_id,
            module_source,
            page.locator("#source").input_value(),
        )
        open_lesson(page, legacy_id, expect)
        open_lesson(page, module_id, expect)
        expect(page.locator("#source")).to_have_value(module_source)
        record_preservation(
            audit,
            "Lesson switch keeps the module draft",
            module_id,
            module_source,
            page.locator("#source").input_value(),
        )
        expect(page.locator("#run")).to_be_enabled()
        page.locator("#run").click()
        expect(page.locator("#output")).to_contain_text(marker + "_MODULE", timeout=150_000)
        expect(page.locator("#job-status")).to_contain_text("succeeded", timeout=150_000)
        page.reload()
        wait_loaded(page, module_id, expect)
        keep_saved_draft_if_offered(page, expect)
        page.locator("#job-history > summary").click()
        history = page.locator("#history button")
        expect(history.first).to_be_visible()
        before = module_snapshot(page, module_id)
        start = log.mark()
        history.last.click()
        expect(page.locator("#run-storage-status")).to_contain_text("Saved run")
        page.wait_for_timeout(500)
        gate.assert_no_execution_requests(log.actions, start, "Opening module history")
        assert not {"save", "save-pad"} & set(log.since(start)), log.since(start)
        assert_module_state_unchanged(page, module_id, before, "Opening module history", audit)
        expect(page.locator("#source")).to_have_value(module_source)
    audit.passed(
        "Drafts survive reload and lesson switches; SQL reset and history never run or save"
    )


def workspace_checks(
    browser: Any, origin: str, audit: Any, expect: Any, axe_script: Path | None
) -> None:
    """Phase 6 desktop flows. Results land in audit.workspace for the gate receipt."""
    with fresh_page(browser, origin, audit) as page:
        load_home(page, origin, expect)
        index = page_index(page)
        samples = choose_mode_samples(index)
        assert len(samples) >= 5, f"Only {len(samples)} workspace modes were found: {samples}"
        audit.workspace["mode_samples"] = mode_sample_checks(page, samples, index, expect)
    audit.passed(f"Workspace strip, Run label and Result panel match {len(samples)} lesson modes")

    audit.workspace["authored_walkthrough"] = authored_walkthrough_check(
        browser, origin, audit, expect
    )
    python_id = samples["legacy-python"]
    audit.workspace["keyboard"] = keyboard_flow(
        browser, origin, audit, expect, python_id, str(lesson_row(index, python_id)["title"])
    )
    walk = [python_id] + ([samples["module-reading"]] if "module-reading" in samples else [])
    audit.workspace["focus_walk"] = focus_walk(browser, origin, audit, expect, walk)
    preservation_checks(browser, origin, audit, expect, samples)
    if axe_script is None:
        audit.workspace["axe"] = {"skipped": "no --axe-script"}
    else:
        audit.workspace["axe"] = axe_scan(browser, origin, audit, expect, axe_script, samples)


def restart_stage(
    browser: Any, origin: str, audit: Any, expect: Any, stage: str, marker: Path
) -> None:
    """Write drafts before a classroom container restart, or verify them afterwards."""
    gate = _gate()
    if stage not in {"write", "verify"}:
        raise ValueError("The restart stage is write or verify.")
    with fresh_page(browser, origin, audit) as page:
        if stage == "write":
            load_home(page, origin, expect)
            samples = choose_mode_samples(page_index(page))
            token = "RESTART_" + uuid.uuid4().hex
            lessons = []
            for mode in ("legacy-python", "module-ready"):
                lesson_id = samples[mode]
                source = f"print({token + '_' + mode.split('-')[0].upper()!r})\n"
                goto_lesson(page, origin, lesson_id, expect)
                keep_saved_draft_if_offered(page, expect)
                gate.show_code_and_notes(page, expect)
                page.locator(SOURCE_EDITOR).fill(source)
                gate.save(page, expect)
                lessons.append({"id": lesson_id, "mode": mode, "source": source})
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text(
                json.dumps({"schema_version": 1, "token": token, "lessons": lessons}, indent=2)
                + "\n",
                encoding="utf-8",
            )
            audit.workspace["restart"] = {"stage": "write", "lessons": lessons, "written": True}
            audit.passed("Restart marker drafts saved before the container restart")
            return
        data = json.loads(marker.read_text(encoding="utf-8"))
        # A just-restarted classroom rebuilds its library index; wait for it like a
        # learner who opens the home page first, not inside the 5 second lesson wait.
        load_home(page, origin, expect)
        for lesson in data["lessons"]:
            goto_lesson(page, origin, lesson["id"], expect)
            conflict = keep_saved_draft_if_offered(page, expect)
            expect(page.locator("#source")).to_have_value(lesson["source"])
            lesson["conflict_prompt"] = conflict
            record_preservation(
                audit,
                "Container restart keeps the draft",
                lesson["id"],
                lesson["source"],
                page.locator("#source").input_value(),
            )
        audit.workspace["restart"] = {
            "stage": "verify",
            "token": data["token"],
            "lessons": data["lessons"],
            "verified": True,
        }
        audit.passed("Drafts saved before the classroom restart are intact afterwards")


__all__ = [
    "assert_axe_clean",
    "classify_axe",
    "choose_mode_samples",
    "expected_strip",
    "focus_cue_ok",
    "normalized_action",
    "restart_stage",
    "workspace_checks",
]
