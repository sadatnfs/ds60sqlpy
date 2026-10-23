"use strict";
// One workspace, two persistence adapters. Existing lesson IDs and saved work stay intact.
const $ = (id) => document.getElementById(id);
const phases = ["read", "predict", "attempt", "compare", "explain"];
const finished = new Set([
  "succeeded",
  "failed",
  "cancelled",
  "timed_out",
  "blocked",
]);
const themes = {
  python: ["#795405", "#fff3cd", "#f2ce79", "#3d3421", "Py"],
  sql: ["#2458a6", "#e9f0ff", "#a9caff", "#22334c", "SQL"],
  bridge: ["#006c7a", "#e1f5f8", "#89dce7", "#203b42", "↔"],
  kubernetes: ["#2854af", "#e9efff", "#aec8ff", "#25334e", "K8s"],
  cpp: ["#67429d", "#f0eaff", "#cfb6ff", "#352b48", "C++"],
  java: ["#9a3b26", "#ffede6", "#ffb39d", "#492d28", "Jv"],
  "javascript-typescript": ["#735700", "#fff4ca", "#f1d778", "#3d3522", "JS"],
  "scala-spark": ["#9a3043", "#ffeaf0", "#ffb1c0", "#482b35", "Sp"],
  "deep-learning-tensorflow": [
    "#934412",
    "#fff0df",
    "#ffc18a",
    "#433327",
    "TF",
  ],
  "deep-learning-pytorch": ["#a02d43", "#ffe9ee", "#ffafc0", "#482a34", "PT"],
  "llm-theory": ["#5542a5", "#eeeaff", "#c9bdff", "#322c4b", "Lm"],
  "llm-applied": ["#006b60", "#def6ee", "#8adfc9", "#223e38", "AI"],
  nlp: ["#923875", "#fbe8f4", "#f3b5df", "#432c3e", "Aa"],
  "statistics-ml": ["#70428b", "#f4e9fa", "#ddbcf3", "#3c2e45", "Σ"],
};
let index = null,
  trackId = null,
  lessonId = null,
  current = null;
let intentVersion = 0,
  loadSequence = 0,
  saveTimer = null,
  saveQueue = Promise.resolve(),
  pendingSaves = 0;
let activeJob = null,
  activeJobRecord = null,
  pollTimer = null,
  pollInFlight = false,
  pollAgain = false,
  monitorPaused = false;
let submitInFlight = false,
  legacyRunActive = false,
  displayedJob = null,
  readingFocused = false,
  editorEscape = false;
let visibleRoute = "/classroom",
  highlightSequence = 0,
  highlightTimer = null,
  previewVisible = false;
let resultRevision = 0,
  runHistorySequence = 0,
  receiptLoadSequence = 0;
let hintNumber = 1,
  phase = "read",
  phaseNotes = {},
  darkMode = false,
  catalogSearchTimer = null;
const draftRevisions = new Map(),
  savedRevisions = new Map();
function node(tag, text, cls) {
  const item = document.createElement(tag);
  if (text !== undefined) item.textContent = text;
  if (cls) item.className = cls;
  return item;
}
function status(text, error = false) {
  $("status").textContent = text;
  $("status").className = "status" + (error ? " error" : "");
}
function pref(key, fallback = null) {
  try {
    return (
      JSON.parse(localStorage.getItem("ds60.classroom." + key)) ?? fallback
    );
  } catch (_) {
    return fallback;
  }
}
function remember(key, value) {
  try {
    localStorage.setItem("ds60.classroom." + key, JSON.stringify(value));
  } catch (_) {}
}
function track() {
  return index?.tracks.find((item) => item.id === trackId);
}
function hasLessonId(record, id) {
  return (
    record.id === id ||
    (record.variants || []).some((variant) => variant.id === id)
  );
}
function locate(id) {
  for (const subject of index?.tracks || []) {
    const record = subject.lessons.find((item) => hasLessonId(item, id));
    if (record) return { subject, record };
  }
  return null;
}
function lesson() {
  return locate(lessonId)?.record;
}
function workspaceKey(data = current) {
  return data
    ? data.id +
        (data.engine === "legacy"
          ? ":" + data.runner.id + ":" + (data.mode || "snippet")
          : "")
    : "";
}
function contextOf(data = current) {
  return data
    ? {
        id: data.id,
        engine: data.engine,
        language: data.runner?.id || data.language,
        mode: data.mode,
        reading: data.runtime_profile === "reading",
        key: workspaceKey(data),
      }
    : null;
}
function values() {
  if (current?.engine === "legacy") phaseNotes[phase] = $("phase-note").value;
  return {
    source: $("source").value,
    prediction: $("prediction").value,
    explanation: $("explanation").value,
    ...(current?.engine === "legacy"
      ? {
          evidence: {
            ...phaseNotes,
            predict: $("prediction").value,
            explain: $("explanation").value,
          },
        }
      : {}),
    ...(current?.learning_mode === "tutorial"
      ? { review: $("read-chapter").checked ? "read" : "" }
      : {}),
  };
}
function sameFields(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}
function stashDraft(key, fields) {
  try {
    localStorage.setItem(
      "ds60.classroom.unsaved." + key,
      JSON.stringify(fields),
    );
    return true;
  } catch (_) {
    return false;
  }
}
async function request(endpoint, action, fields = {}, bounded = true) {
  const controller = new AbortController(),
    timer = bounded ? setTimeout(() => controller.abort(), 25000) : null;
  try {
    const response = await fetch("/api/" + endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-DS60-Token": SERVER_TOKEN,
      },
      body: JSON.stringify({ action, ...fields }),
      signal: controller.signal,
    });
    const data = await response.json();
    if (!response.ok)
      throw new Error(
        data.error || "The local classroom rejected this action.",
      );
    return data;
  } catch (error) {
    if (error.name === "AbortError")
      throw new Error(
        "The classroom did not respond in time. Your browser draft is retained. Reconnect before submitting another run.",
      );
    throw error;
  } finally {
    if (timer !== null) clearTimeout(timer);
  }
}
function api(action, fields = {}) {
  return request("modules", action, fields);
}
function lab(action, fields = {}, bounded = true) {
  return request("lab", action, fields, bounded);
}
function classroom(action, fields = {}) {
  return request("classroom", action, fields);
}
async function saveLesson(context, fields) {
  if (context.engine === "module")
    return api("module-save", { lesson_id: context.id, fields });
  if (!context.reading)
    await lab("save-pad", {
      lesson_id: context.id,
      language: context.language,
      ...(context.mode ? { mode: context.mode } : {}),
      code: fields.source,
    });
  for (const item of phases)
    await lab("save", {
      lesson_id: context.id,
      phase: item,
      note: fields.evidence?.[item] || "",
    });
}
function queueSave() {
  if (!current || current.id !== lessonId) return Promise.resolve();
  const context = contextOf(),
    fields = values(),
    revision = draftRevisions.get(context.key) || 0;
  pendingSaves++;
  $("save-state").textContent = "Saving to your local learning workspace...";
  const request = saveQueue
    .catch(() => {})
    .then(async () => {
      try {
        await saveLesson(context, fields);
        savedRevisions.set(context.key, revision);
        const sameView = workspaceKey() === context.key;
        const sameDraft =
          sameView &&
          (draftRevisions.get(context.key) || 0) === revision &&
          sameFields(values(), fields);
        if (sameDraft) {
          $("save-state").textContent =
            "Saved in your local learning workspace.";
          try {
            localStorage.removeItem("ds60.classroom.unsaved." + context.key);
            if (context.engine === "module")
              localStorage.removeItem("ds60.module.unsaved." + context.id);
          } catch (_) {}
        } else if (sameView) {
          $("save-state").textContent =
            "Unsaved changes. Your newer draft is waiting to save.";
          stashDraft(context.key, values());
        }
      } catch (error) {
        const latest = workspaceKey() === context.key ? values() : fields;
        const backup = stashDraft(context.key, latest);
        if (workspaceKey() === context.key)
          $("save-state").textContent =
            "Server save failed. " +
            (backup
              ? "Your browser backup is retained. Keep this page open until the save succeeds."
              : "Browser storage is unavailable. Keep this page open and copy your work.");
        status(error.message, true);
        throw error;
      } finally {
        pendingSaves--;
      }
    });
  saveQueue = request;
  return request;
}
async function flushSave() {
  clearTimeout(saveTimer);
  saveTimer = null;
  if (current && current.id === lessonId) await queueSave();
  else await saveQueue;
}
function markDirty() {
  if (!current) return;
  const key = workspaceKey();
  draftRevisions.set(key, (draftRevisions.get(key) || 0) + 1);
  const backup = stashDraft(key, values());
  $("save-state").textContent = backup
    ? "Unsaved changes. A browser backup is retained while saving."
    : "Unsaved changes. Browser storage is unavailable; keep this page open.";
  updateErrorJump();
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    saveTimer = null;
    queueSave().catch(() => {});
  }, 800);
}
function theme(subject, element = document.body) {
  const colors = themes[subject?.theme_key || subject?.id] || [
    "#4b50a1",
    "#eeedfb",
    "#c4c1ff",
    "#302e48",
    "↗",
  ];
  element.style.setProperty("--accent", colors[darkMode ? 2 : 0]);
  element.style.setProperty("--tint", colors[darkMode ? 3 : 1]);
  return colors[4];
}
function setTheme(dark) {
  darkMode = dark;
  document.body.dataset.mode = dark ? "dark" : "light";
  document.documentElement.style.colorScheme = dark ? "dark" : "light";
  $("theme-toggle").setAttribute("aria-pressed", String(dark));
  $("theme-toggle").textContent = dark ? "Light appearance" : "Dark appearance";
  theme($("home-view").hidden ? track() : null);
  if (index) renderHome();
}
function estimatedSessions(record) {
  const minutes = Number(record.estimated_minutes);
  return minutes > 0
    ? Math.max(1, Math.ceil(minutes / Number($("pace").value || 30)))
    : null;
}
function renderHome() {
  if (!index) return;
  const query = $("catalog-search").value.trim().toLowerCase(),
    terms = query.split(/\s+/).filter(Boolean),
    matches = (text) =>
      terms.every((term) => String(text).toLowerCase().includes(term));
  const cards = $("subject-cards");
  cards.replaceChildren();
  let count = 0;
  for (const subject of index.tracks) {
    if (
      query &&
      !matches(subject.title + " " + subject.description + " " + subject.id)
    )
      continue;
    count++;
    const card = node("button", undefined, "subject-card");
    card.type = "button";
    const icon = theme(subject, card);
    card.append(
      node("span", icon, "subject-icon"),
      node("span", "GO AT YOUR OWN PACE", "card-stage"),
      node("h3", subject.title),
      node(
        "p",
        subject.description ||
          "Explore clear explanations, worked examples, and a place to practice.",
      ),
    );
    const authored = subject.lessons.filter(
        (item) => item.status !== "planned",
      ).length,
      bottom = node("span", undefined, "card-bottom");
    bottom.append(
      node(
        "span",
        authored +
          (subject.id === "statistics-ml" ? " tutorial chapters" : " lessons") +
          " · Open path",
      ),
      node("span", "↗", "card-arrow"),
    );
    card.append(bottom);
    card.addEventListener("click", () =>
      switchTrack(subject.id).catch((error) => status(error.message, true)),
    );
    cards.append(card);
  }
  const results = [];
  if (query)
    for (const subject of index.tracks)
      for (const record of subject.lessons)
        if (
          matches(
            record.title +
              " " +
              record.id +
              " " +
              (record.concepts || []).join(" "),
          )
        )
          results.push({ subject, record });
  $("search-lessons").hidden = !results.length;
  $("search-lesson-list").replaceChildren();
  for (const { subject, record } of results.slice(0, 40)) {
    const button = node("button");
    const title = node("span", record.title);
    title.append(node("small", subject.title + " · " + record.id));
    button.append(title, node("small", record.level || ""));
    button.addEventListener("click", () =>
      openLesson(record.id).catch((error) => status(error.message, true)),
    );
    $("search-lesson-list").append(button);
  }
  $("search-summary").textContent = query
    ? count +
      " matching paths and " +
      results.length +
      " matching lessons" +
      (results.length > 40
        ? " (showing the first 40; refine your search)."
        : ".")
    : "";
  $("no-results").hidden = count > 0 || results.length > 0;
  const countLessons = index.tracks.reduce(
    (total, subject) =>
      total +
      subject.lessons.filter((item) => item.status !== "planned").length,
    0,
  );
  $("catalog-summary").textContent =
    countLessons +
    " lessons and chapters · " +
    index.tracks.length +
    " learning paths · One local classroom";
  const recent = pref("lastLesson") || migratedRecent(),
    resume = recent && locate(recent.id);
  $("resume").hidden = !resume;
  if (resume) {
    $("resume").textContent = "Continue: " + resume.record.title;
    $("resume").onclick = () =>
      openLesson(recent.id, true, recent.context || {}).catch((error) =>
        status(error.message, true),
      );
  }
}
function migratedRecent() {
  try {
    const old = JSON.parse(localStorage.getItem("ds60.lastLesson") || "null");
    if (old?.id && locate(old.id)) return old;
    const moduleId = localStorage.getItem("ds60.module.last-lesson");
    return moduleId && locate(moduleId) ? { id: moduleId } : null;
  } catch (_) {
    return null;
  }
}
async function showHome(historyMode = "push") {
  const version = ++intentVersion;
  await flushSave();
  if (version !== intentVersion) return;
  if (
    current &&
    (draftRevisions.get(workspaceKey()) || 0) >
      (savedRevisions.get(workspaceKey()) || 0)
  ) {
    status(
      "Your draft changed while it was saving. Save the latest version before leaving this lesson.",
    );
    return;
  }
  ++loadSequence;
  $("home-view").hidden = false;
  $("workspace-view").hidden = true;
  theme(null);
  renderHome();
  recordRoute("/classroom", historyMode);
  document.title = "DS60 Classroom · Choose your next idea";
  $("home-title").focus({ preventScroll: true });
  window.scrollTo({ top: 0 });
  status(
    activeJobRecord
      ? "A saved job for " +
          activeJobRecord.lesson_id +
          " is still being monitored. You can explore another path."
      : "Choose any subject. Your saved work stays with each lesson.",
  );
}
function renderNavigation() {
  const subject = track();
  $("subject-label").textContent = subject.title;
  $("path-title").textContent = subject.title;
  $("path-description").textContent = subject.description || "";
  $("subject-select").replaceChildren();
  for (const item of index.tracks) {
    const option = node("option", item.title);
    option.value = item.id;
    $("subject-select").append(option);
  }
  $("subject-select").value = trackId;
  renderLessons();
  renderPager();
}
function visibleLessons() {
  const terms = $("lesson-query")
    .value.toLowerCase()
    .split(/\s+/)
    .filter(Boolean);
  return (track()?.lessons || []).filter(
    (item) =>
      ($("stage").value === "all" || item.level === $("stage").value) &&
      terms.every((term) =>
        (item.title + " " + item.id + " " + (item.concepts || []).join(" "))
          .toLowerCase()
          .includes(term),
      ),
  );
}
function renderLessons() {
  const list = $("lessons");
  list.replaceChildren();
  const rows = visibleLessons();
  $("lesson-count").textContent =
    rows.length + " of " + (track()?.lessons.length || 0) + " lessons shown";
  for (const item of rows) {
    const button = node("button", item.title);
    button.type = "button";
    if (hasLessonId(item, lessonId))
      button.setAttribute("aria-current", "page");
    const sessions = estimatedSessions(item);
    button.append(
      node(
        "small",
        item.id +
          (item.completed ? " · Demonstrated" : "") +
          " · " +
          (item.level || "") +
          (sessions
            ? " · ~" + sessions + (sessions === 1 ? " session" : " sessions")
            : ""),
      ),
    );
    button.addEventListener("click", () =>
      openLesson(item.id).catch((error) => status(error.message, true)),
    );
    list.append(button);
  }
  if (!rows.length)
    list.append(
      node(
        "p",
        "No lessons match. Clear the search or choose another stage.",
        "muted",
      ),
    );
}
function renderPager() {
  const rows = track()?.lessons || [],
    position = rows.findIndex((item) => hasLessonId(item, lessonId));
  $("previous-lesson").disabled = position <= 0;
  $("next-lesson").disabled = position < 0 || position >= rows.length - 1;
  $("journey-position").textContent =
    position >= 0 ? position + 1 + " of " + rows.length : "";
  if (position > 0)
    $("previous-lesson").setAttribute(
      "aria-label",
      "Previous: " + rows[position - 1].title,
    );
  if (position >= 0 && position < rows.length - 1)
    $("next-lesson").setAttribute(
      "aria-label",
      "Next: " + rows[position + 1].title,
    );
}
async function switchTrack(id) {
  const subject = index.tracks.find((item) => item.id === id);
  if (!subject) return;
  const remembered = pref("lastTrack." + id);
  const first =
    subject.lessons.find((item) => item.status !== "planned") ||
    subject.lessons[0];
  if (!first) return;
  const target =
    remembered && subject.lessons.some((item) => hasLessonId(item, remembered))
      ? remembered
      : first.id;
  await openLesson(target);
}
async function fetchLesson(id, subject, requested = {}) {
  if (subject.engine !== "legacy")
    return {
      ...(await api("module-lesson", { lesson_id: id })),
      engine: "module",
    };
  const data = await lab("lesson", { lesson_id: id }),
    capabilities = data.capabilities;
  if (!capabilities?.runners?.length)
    throw new Error(
      "This lesson has no workspace capability. Restart the classroom with its current files.",
    );
  const selected =
    capabilities.runners.find((item) => item.id === requested.language) ||
    capabilities.runners.find(
      (item) => item.id === capabilities.default_runner,
    );
  if (!selected) throw new Error("The default lesson runner is unavailable.");
  const mode = selected.modes?.some((item) => item.id === requested.mode)
    ? requested.mode
    : selected.default_mode || null;
  const effective = {
      ...selected,
      ...(selected.modes || []).find((item) => item.id === mode),
    },
    reading = selected.kind === "reading";
  const pad = reading
    ? { code: "", saved: true }
    : await lab("read-pad", {
        lesson_id: id,
        language: selected.id,
        ...(mode ? { mode } : {}),
      });
  const source =
    pad.saved === true
      ? pad.code
      : pad.code ||
        (selected.executor === "python"
          ? 'print("Hello, classroom!")\n'
          : selected.executor === "sql"
            ? data.sql_snippet_starter || "SELECT 42 AS answer;\n"
            : "");
  return {
    ...data,
    engine: "legacy",
    runner: selected,
    effective,
    mode,
    language: selected.id,
    runtime_profile: reading ? "reading" : selected.id,
    source,
    source_filename:
      mode === "lesson"
        ? data.lesson_path.split("/").at(-1)
        : "practice" + selected.file_suffix,
    session: {
      ...data.session,
      prediction: data.session.predict || "",
      explanation: data.session.explain || "",
    },
    capability: {
      profile: selected.id,
      ready: Boolean(effective.can_run && effective.available),
      detail: effective.reason || "",
    },
    runtime_guidance: [
      effective.reason,
      selected.setup,
      effective.setup,
      selected.notebook_guidance,
      selected.verification,
    ]
      .filter(Boolean)
      .join("\n\n"),
    history: [],
    setup_commands: [],
  };
}
function renderVariants(record, id) {
  $("variant").replaceChildren();
  for (const item of record.variants || []) {
    const option = node("option", item.title);
    option.value = item.id;
    $("variant").append(option);
  }
  $("variant").value = id;
  $("variant").hidden = (record.variants || []).length < 2;
  $("variant-label").hidden = $("variant").hidden;
}
function renderLegacyControls(data) {
  const legacy = data.engine === "legacy";
  for (const id of ["legacy-workspace", "legacy-evidence", "legacy-pad-tools"])
    $(id).hidden = !legacy;
  $("job-history").hidden = false;
  $("cancel").hidden = legacy && !activeJob;
  $("source-section").hidden = legacy && data.runtime_profile === "reading";
  if (!legacy) return;
  $("runner").replaceChildren();
  for (const item of data.capabilities.runners) {
    const option = node(
      "option",
      item.title +
        (item.kind === "reading" ? "" : item.can_run ? "" : " (save only)"),
    );
    option.value = item.id;
    $("runner").append(option);
  }
  $("runner").value = data.runner.id;
  $("pad-mode").replaceChildren();
  for (const item of data.runner.modes || []) {
    const option = node("option", item.title);
    option.value = item.id;
    $("pad-mode").append(option);
  }
  $("pad-mode").value = data.mode || "";
  $("mode-control").hidden = (data.runner.modes || []).length < 2;
  $("sql-setup").hidden = data.runner.executor !== "sql";
  $("starter").disabled = data.runner.id !== data.capabilities.default_runner;
  $("coaching-prompt").textContent = data.coaching_prompt || "";
  $("confirmed").checked = false;
  $("hint").textContent = "";
  hintNumber = 1;
  phase = "read";
  phaseNotes = Object.fromEntries(
    phases.map((item) => [item, data.session[item] || ""]),
  );
  $("phase").value = phase;
  $("phase-note").value = phaseNotes[phase];
  $("phase-label").textContent = "Reading notes";
}
async function openLesson(id, save = true, requested = {}) {
  requested = {
    ...pref("context." + id, {}),
    ...Object.fromEntries(
      Object.entries(requested).filter(
        ([, value]) => value !== null && value !== undefined,
      ),
    ),
  };
  const found = locate(id);
  if (!found) {
    status("That lesson is not in this classroom library.", true);
    return;
  }
  const version = ++intentVersion;
  if (save) await flushSave();
  if (version !== intentVersion) return;
  if (
    current &&
    (draftRevisions.get(workspaceKey()) || 0) >
      (savedRevisions.get(workspaceKey()) || 0)
  ) {
    status(
      "Your draft changed while it was saving. Save the latest version before switching lessons.",
    );
    return;
  }
  const previousKey = workspaceKey(),
    previousRevision = draftRevisions.get(previousKey) || 0;
  const sequence = ++loadSequence;
  if (found.record.status === "planned") {
    current = null;
    trackId = found.subject.id;
    lessonId = id;
    theme(found.subject);
    $("home-view").hidden = true;
    $("workspace-view").hidden = false;
    renderNavigation();
    $("title").textContent = found.record.title;
    $("outcome").textContent = found.record.outcome || "";
    $("badges").replaceChildren(node("span", "Planned lesson", "badge"));
    renderPrerequisites(found.record.prerequisites || []);
    $("authored").hidden = true;
    $("planned").hidden = false;
    $("planned").replaceChildren(
      node("h2", "A future learning opportunity"),
      node("p", found.record.lab || "This lesson has not been authored yet."),
      node("p", found.record.verification || ""),
    );
    $("capability").textContent =
      "Planned content has no coding workspace or claimed runtime yet.";
    $("runtime-setup").hidden = true;
    $("llm-reading-route").hidden = true;
    recordRoute(
      "/classroom#" + new URLSearchParams({ lesson: id }),
      requested._history || "push",
    );
    status(
      "This lesson is planned. Choose an authored lesson to read and practice.",
    );
    return;
  }
  status("Opening " + found.record.title + "...");
  let data;
  try {
    data = await fetchLesson(id, found.subject, requested);
  } catch (error) {
    if (sequence === loadSequence && version === intentVersion)
      status(
        "Could not open this lesson. Your previous workspace is still here. " +
          error.message,
        true,
      );
    throw error;
  }
  if (sequence !== loadSequence || version !== intentVersion) return;
  if (
    workspaceKey() !== previousKey ||
    (draftRevisions.get(previousKey) || 0) !== previousRevision
  ) {
    status(
      "You edited the current draft while the new lesson was loading. Your workspace is preserved; choose the lesson again when ready.",
    );
    return;
  }
  current = data;
  trackId = found.subject.id;
  lessonId = id;
  theme(found.subject);
  $("home-view").hidden = true;
  $("workspace-view").hidden = false;
  $("workspace-view").dataset.navigation = "closed";
  $("lesson-menu").setAttribute("aria-expanded", "false");
  const filters = pref("filters." + trackId, {});
  $("stage").value = ["beginner", "intermediate", "advanced"].includes(
    filters.stage,
  )
    ? filters.stage
    : "all";
  $("lesson-query").value =
    typeof filters.query === "string" ? filters.query : "";
  renderNavigation();
  renderVariants(found.record, id);
  renderLegacyControls(data);
  const tutorial = data.learning_mode === "tutorial";
  setReadingView(preferredReadingView(tutorial));
  $("solution-section").hidden = tutorial;
  $("chapter-read-label").hidden = !tutorial;
  $("read-chapter").checked = data.session.review === "read";
  $("prediction-label").hidden = tutorial;
  $("prediction").hidden = tutorial;
  $("pad-title").textContent = tutorial
    ? "Worked examples and notes"
    : "Code and reflection";
  $("explanation-label").textContent = tutorial
    ? "Notes and interpretations"
    : "Explain the evidence";
  $("learning-guidance").textContent = tutorial
    ? "Read the explanations and explore the examples at your own pace. There are no exams, problem sets, or withheld solutions. The read marker is your personal bookmark."
    : "A successful run is evidence, not automatic mastery. Explain what happened, investigate a boundary case, and revisit the idea later.";
  $("title").textContent = data.title || found.record.title;
  $("outcome").textContent =
    data.outcome || found.record.outcome || (data.topics || []).join(" · ");
  $("badges").replaceChildren(
    node("span", found.subject.title, "badge subject"),
    node("span", data.level || found.record.level, "badge"),
    node("span", tutorial ? "Tutorial chapter" : "Practice lesson", "badge"),
  );
  if (data.estimated_minutes || found.record.estimated_minutes)
    $("badges").append(
      node(
        "span",
        (data.estimated_minutes || found.record.estimated_minutes) +
          " min suggested study",
        "badge",
      ),
    );
  renderPrerequisites(data.prerequisites || found.record.prerequisites || []);
  $("llm-reading-route").hidden = !["llm-theory", "llm-applied"].includes(
    trackId,
  );
  $("guide").innerHTML = data.guide_html;
  renderSections();
  $("source").value = data.source || "";
  $("prediction").value = data.session.prediction || "";
  $("explanation").value = data.session.explanation || "";
  $("solutions").replaceChildren();
  $("solutions").hidden = true;
  let recovered = false;
  const key = workspaceKey();
  try {
    const backup = JSON.parse(
      localStorage.getItem("ds60.classroom.unsaved." + key) ||
        (data.engine === "module"
          ? localStorage.getItem("ds60.module.unsaved." + id)
          : null) ||
        "null",
    );
    if (
      backup &&
      ["source", "prediction", "explanation"].every(
        (field) => typeof backup[field] === "string",
      )
    ) {
      for (const field of ["source", "prediction", "explanation"])
        $(field).value = backup[field];
      if (tutorial && typeof backup.review === "string")
        $("read-chapter").checked = backup.review === "read";
      if (data.engine === "legacy" && backup.evidence) {
        phaseNotes = Object.fromEntries(
          phases.map((item) => [
            item,
            typeof backup.evidence[item] === "string"
              ? backup.evidence[item]
              : phaseNotes[item] || "",
          ]),
        );
        $("phase-note").value = phaseNotes[phase];
      }
      recovered = true;
    }
  } catch (_) {}
  draftRevisions.set(key, (draftRevisions.get(key) || 0) + 1);
  savedRevisions.set(key, (draftRevisions.get(key) || 0) - (recovered ? 1 : 0));
  $("save-state").textContent = recovered
    ? "Recovered a browser draft. Save it to retain this version in your local learning workspace."
    : "Loaded from your local learning workspace.";
  $("language").textContent =
    data.language +
    (data.runtime_profile !== data.language
      ? " · " + data.runtime_profile
      : "");
  $("runtime-details").hidden = !data.runtime_guidance;
  $("runtime-guidance").textContent = data.runtime_guidance || "";
  $("planned").hidden = true;
  $("authored").hidden = false;
  resetResult();
  renderHistory(data.history || []);
  const resumable = (data.history || []).find(
    (job) => !finished.has(job.status),
  );
  if (!activeJob && resumable) adoptJob(resumable, false);
  if (activeJobRecord?.lesson_id === id) showJob(activeJobRecord);
  else if (data.history?.length) showJob(data.history[0]);
  updateControls();
  if (activeJob && !monitorPaused) poll();
  if (data.engine === "legacy" && legacyReceipts.has(key)) {
    const saved = legacyReceipts.get(key);
    showLegacyResult(saved.result, saved.context, saved.source);
  }
  previewVisible = pref("preview." + trackId, false);
  updatePreviewVisibility();
  if (data.engine === "legacy") {
    refreshPadHistory().catch((error) => status(error.message, true));
    const retained = legacyReceipts.get(key);
    refreshRunHistory({
      showLatest: retained?.result.receipt_saved !== false,
    }).catch((error) => status(error.message, true));
  }
  remember("lastLesson", {
    id,
    context: { language: data.runner?.id, mode: data.mode },
  });
  remember("lastTrack." + trackId, id);
  if (data.engine === "legacy")
    remember("context." + id, { language: data.runner.id, mode: data.mode });
  recordRoute(
    "/classroom#" +
      new URLSearchParams({
        lesson: id,
        ...(data.engine === "legacy"
          ? {
              language: data.runner.id,
              ...(data.mode ? { mode: data.mode } : {}),
            }
          : {}),
      }),
    requested._history || "push",
  );
  document.title = $("title").textContent + " | DS60 Classroom";
  $("title").focus({ preventScroll: true });
  $("title").scrollIntoView({ block: "start" });
  status(
    tutorial
      ? "The chapter and your saved notes are ready. Read and explore at your own pace."
      : "Your guide, code, and notes are ready. Choose a small idea to try.",
  );
}
function renderPrerequisites(ids) {
  $("prerequisites").replaceChildren();
  if (!ids.length) {
    $("prerequisites").append(
      node("span", "Start here: no earlier lesson is required."),
    );
    return;
  }
  $("prerequisites").append(
    node("span", "Helpful foundations, whenever you need them: "),
  );
  for (const id of ids) {
    const found = locate(id);
    if (!found) {
      $("prerequisites").append(node("span", id + " "));
      continue;
    }
    const button = node("button", id);
    button.title = found.record.title;
    button.addEventListener("click", () =>
      openLesson(id).catch((error) => status(error.message, true)),
    );
    $("prerequisites").append(button);
  }
}
function preferredReadingView(tutorial = false) {
  const value = pref("reading." + trackId);
  if (typeof value === "boolean") return value;
  try {
    const old = localStorage.getItem("ds60.module.reading-view." + trackId);
    if (old === "reading" || old === "practice") return old === "reading";
  } catch (_) {}
  return tutorial || ["llm-theory", "llm-applied"].includes(trackId);
}
function setReadingView(focused) {
  readingFocused = focused;
  $("authored").className = "panes" + (focused ? " reading-focus" : "");
  $("reading-toggle").setAttribute("aria-pressed", String(focused));
  $("reading-toggle").textContent = focused
    ? "Show code and notes"
    : "Focus on reading";
}
function renderSections() {
  $("section-jump").replaceChildren();
  const first = node("option", "Choose a section");
  first.value = "";
  $("section-jump").append(first);
  for (const heading of [
    ...$("guide").querySelectorAll("h2,h3,h4,h5,h6"),
  ].slice(0, 200)) {
    if (!heading.id) continue;
    let text = heading.textContent.replace(/\s*#\s*$/, "").trim();
    if (/^stat-\d+-\d+/.test(text))
      text =
        heading.nextElementSibling?.querySelector("strong")?.textContent ||
        text;
    const option = node("option", text);
    option.value = heading.id;
    $("section-jump").append(option);
  }
}
function updateControls() {
  $("cancel").disabled = !activeJob;
  $("cancel").hidden = current?.engine === "legacy" && !activeJob;
  $("cancel").textContent = activeJobRecord
    ? "Cancel " + activeJobRecord.lesson_id + " job"
    : "Cancel job";
  if (!current) return;
  showCapability(current.capability);
}
function showCapability(cap) {
  const reading = current.runtime_profile === "reading";
  const activity = activeJobRecord
    ? " A job for " +
      activeJobRecord.lesson_id +
      " is active or awaiting confirmation."
    : legacyRunActive
      ? " A bounded Python or SQL run is active. Wait for its result before running again."
      : "";
  $("capability").textContent =
    (reading
      ? "Read the guide and record your reasoning. This lesson needs no code runtime."
      : cap.ready
        ? "Ready to run in your local classroom. " +
          (current.engine === "legacy" ? cap.detail || "" : "")
        : (cap.profile || current.runtime_profile) +
          " is not ready. " +
          (cap.detail || "")) + activity;
  $("capability").className =
    "notice" + (!cap.ready && !reading ? " warn" : "");
  $("runtime-setup").hidden =
    cap.ready ||
    reading ||
    (!current.setup_commands?.length && !current.runtime_guidance);
  $("runtime-commands").textContent = (current.setup_commands || []).join(
    "\n\n",
  );
  $("runtime-setup-note").textContent =
    current.engine === "legacy" ? current.runtime_guidance || "" : "";
  $("run").disabled =
    !cap.ready ||
    reading ||
    activeJob !== null ||
    submitInFlight ||
    legacyRunActive;
  $("run").textContent = reading
    ? "Reading and reasoning"
    : legacyRunActive
      ? "Running..."
      : "Run code";
  $("timeout").disabled = reading || legacyRunActive;
  if (current.engine === "legacy") {
    const allowed = current.effective.allowed_timeout_seconds || [15, 60, 120];
    const old = Number($("timeout").value);
    $("timeout").replaceChildren();
    for (const seconds of allowed) {
      const option = node("option", seconds + " seconds");
      option.value = String(seconds);
      $("timeout").append(option);
    }
    $("timeout").value = String(
      allowed.includes(old)
        ? old
        : current.effective.timeout_seconds || allowed[0],
    );
  }
}
function resetResult() {
  resultRevision++;
  $("run-storage-status").textContent = "";
  $("receipt-source-details").hidden = true;
  $("receipt-source").replaceChildren();
  displayedJob = null;
  $("recover").hidden = true;
  $("reconnect").hidden = true;
  $("job-status").textContent = "No run yet for this lesson.";
  $("output").textContent =
    "Actual output and compiler diagnostics will appear here.";
  $("checks").replaceChildren();
  $("sql-results").replaceChildren();
  $("figures").replaceChildren();
  $("error-line").hidden = true;
}
function renderHistory(records) {
  $("history").replaceChildren();
  for (const job of records) {
    const button = node(
      "button",
      (job.created_at || "") +
        " · " +
        job.status +
        " · " +
        (job.source_sha256 || "").slice(0, 10),
    );
    button.addEventListener("click", () => showJob(job));
    $("history").append(button);
  }
}

// BEGIN DIAGNOSTIC PURE HELPERS
function tracebackLine(output, lineCount) {
  let line = null;
  for (const text of output.split("\n")) {
    const match = text.match(/^\s*File "([^"\n]+)", line (\d+)/);
    if (!match) continue;
    const filename = match[1].split(/[\\/]/).at(-1);
    if (
      filename !== "practice.py" &&
      !/^\.submission-[A-Za-z0-9_-]{1,64}\.py$/.test(filename)
    )
      continue;
    const candidate = Number(match[2]);
    if (
      Number.isSafeInteger(candidate) &&
      candidate > 0 &&
      candidate <= lineCount
    )
      line = candidate;
  }
  return line;
}
// END DIAGNOSTIC PURE HELPERS

function sourceErrorLine(job) {
  if (
    !current ||
    job.lesson_id !== current.id ||
    typeof job.source !== "string" ||
    job.source !== $("source").value
  )
    return null;
  const output = job.output || "",
    count = $("source").value.split("\n").length;
  let matches = [];
  if (job.legacy && current.language === "python")
    return tracebackLine(output, count);
  if (current.language === "python")
    matches = [
      ...output.matchAll(
        /(?:^|\n)\s*File\s+["'](?:[^"'\n]*[\/\\])?main\.py["'],\s*line\s+(\d+)/g,
      ),
    ];
  else if (current.language === "cpp")
    matches = [
      ...output.matchAll(/(?:^|\n)(?:[^\n]*[\/\\])?main\.cpp:(\d+)(?::\d+)?:/g),
    ];
  else if (current.language === "java")
    matches = [
      ...output.matchAll(
        /(?:^|\n)(?:[^\n]*[\/\\])?Main\.java:(\d+):|\(Main\.java:(\d+)\)/g,
      ),
    ];
  else if (current.language === "javascript")
    matches = [
      ...output.matchAll(/(?:^|[\s(/])(?:[^\s()]*\/)?main\.mjs:(\d+)/g),
    ];
  else if (current.language === "typescript")
    matches = [...output.matchAll(/(?:^|\n)main\.mts\((\d+),\d+\)/g)];
  else if (current.language === "scala")
    matches = [
      ...output.matchAll(
        /(?:^|\n)(?:[^\n]*[\/\\])?Main\.scala:(\d+):|\(Main\.scala:(\d+)\)/g,
      ),
    ];
  if (!matches.length) return null;
  const match =
      current.language === "python" ? matches[matches.length - 1] : matches[0],
    line = Number(match[1] || match[2]);
  return Number.isInteger(line) && line >= 1 && line <= count ? line : null;
}
function updateErrorJump() {
  const job = displayedJob,
    line = job ? sourceErrorLine(job) : null;
  $("error-line").hidden = line === null;
  if (line === null) return;
  $("error-line").textContent = "Inspect source line " + line;
  $("error-line").onclick = () => {
    const currentLine = sourceErrorLine(job);
    if (currentLine === null) {
      $("error-line").hidden = true;
      status(
        "The source changed. Compare the saved job source before inspecting its diagnostic.",
      );
      return;
    }
    const lines = $("source").value.split("\n"),
      start =
        lines.slice(0, currentLine - 1).join("\n").length +
        (currentLine > 1 ? 1 : 0);
    $("source").focus();
    $("source").setSelectionRange(
      start,
      start + (lines[currentLine - 1] || "").length,
    );
  };
}
function showJob(job) {
  if (!current || current.id !== job.lesson_id) return;
  displayedJob = job;
  const canReconnect = !finished.has(job.status),
    otherActive = activeJob && activeJob !== job.job_id;
  $("reconnect").hidden = !canReconnect;
  $("reconnect").disabled = !!otherActive;
  $("reconnect").textContent = otherActive
    ? "Another job is active"
    : "Reconnect saved job";
  $("reconnect").onclick = () => {
    if (adoptJob(job, false)) {
      monitorPaused = false;
      poll();
    }
  };
  $("recover").hidden = job.status !== "interrupted";
  $("recover").disabled = !!otherActive;
  $("recover").onclick = () => recoverInterrupted(job);
  $("job-status").textContent =
    job.status +
    " · " +
    Number(job.elapsed_seconds || 0).toFixed(1) +
    "s · " +
    (job.detail || "") +
    (job.truncated
      ? " · Log truncated; exit status and checks remain explicit."
      : "");
  $("output").textContent = job.output || "(No output yet.)";
  $("checks").replaceChildren();
  for (const check of job.checks || [])
    $("checks").append(
      node(
        "li",
        (check.passed ? "PASS: " : "FAIL: ") +
          check.name +
          " · " +
          check.detail,
      ),
    );
  if (job.status === "succeeded" && !(job.checks || []).length)
    $("checks").append(
      node(
        "li",
        "Execution finished successfully. No semantic verifier ran for this lesson.",
      ),
    );
  updateErrorJump();
}
async function recoverInterrupted(job) {
  if (job.status !== "interrupted" || !current || current.id !== job.lesson_id)
    return;
  if (activeJob && activeJob !== job.job_id) {
    status("Another job is active. Its monitor was preserved.", true);
    return;
  }
  const intent = {
    job_id: job.job_id,
    lesson_id: job.lesson_id,
    version: intentVersion,
    source: $("source").value,
  };
  const cluster = job.profile === "k8s-kind",
    confirmation = cluster ? "CLUSTER RELEASED" : "WORKER RESTARTED";
  const instruction = cluster
    ? "First release only the owned disposable cluster through its host preparation tool and check its ownership receipt."
    : "First restart only the owned " +
      job.profile +
      " worker through Docker Compose or the optional host launcher and confirm that its previous process is gone.";
  const answer = prompt(
    "Manual recovery for " +
      job.lesson_id +
      " (job " +
      job.job_id +
      ").\n\n" +
      instruction +
      "\n\nThis records your recovery confirmation. It does not verify cleanup or mastery and never submits your source again.\n\nType " +
      confirmation +
      " only after completing that recovery action.",
    "",
  );
  if (answer !== confirmation) {
    status(
      "No recovery was recorded. Complete the recovery action before entering the exact confirmation.",
    );
    return;
  }
  const sameView = () =>
    current &&
    current.id === intent.lesson_id &&
    intentVersion === intent.version &&
    displayedJob &&
    displayedJob.job_id === intent.job_id &&
    $("source").value === intent.source;
  if (!sameView() || (activeJob && activeJob !== intent.job_id)) return;
  $("recover").disabled = true;
  try {
    const result = await api("module-recover", {
      job_id: intent.job_id,
      confirmation,
    });
    if (activeJob && activeJob !== intent.job_id) return;
    if (!sameView() && activeJob !== intent.job_id) return;
    activeJob = intent.job_id;
    activeJobRecord = result;
    monitorPaused = false;
    if (sameView()) showJob(result);
    updateControls();
    if (pollInFlight) pollAgain = true;
    else await poll();
    if (sameView())
      status(
        result.recovery?.type === "operator-confirmed"
          ? "Manual recovery was recorded. The prior result remains unavailable; your source was retained and was not run again."
          : "The saved job status was refreshed. No manual recovery was recorded and no source was run again.",
      );
  } catch (error) {
    if (sameView()) {
      status("Recovery was not confirmed. " + error.message, true);
      $("recover").disabled = false;
    }
  }
}
function adoptJob(job, start = true) {
  if (!job || finished.has(job.status)) return false;
  if (activeJob && activeJob !== job.job_id) {
    status("Another job is already active. Its monitor was preserved.", true);
    return false;
  }
  activeJob = job.job_id;
  activeJobRecord = job;
  monitorPaused = false;
  updateControls();
  if (current && job.lesson_id === current.id) showJob(job);
  if (start) poll();
  return true;
}
async function poll() {
  if (!activeJob || pollInFlight || monitorPaused) return;
  if (pollTimer !== null) {
    clearTimeout(pollTimer);
    pollTimer = null;
  }
  const key = activeJob;
  pollInFlight = true;
  try {
    const job = await api("module-job", { job_id: key });
    if (activeJob !== key) return;
    activeJobRecord = job;
    if (current && job.lesson_id === current.id) showJob(job);
    if (finished.has(job.status)) {
      activeJob = null;
      activeJobRecord = null;
      monitorPaused = false;
      updateControls();
      const selected = current?.engine === "module" && current.id;
      if (selected) {
        const latest = await api("module-lesson", { lesson_id: selected });
        if (current && latest.id === current.id) renderHistory(latest.history);
      }
    } else if (job.status === "interrupted") {
      monitorPaused = true;
      status(
        "The saved job needs reconnection. Its source was not submitted again.",
      );
    }
  } catch (error) {
    if (activeJob === key) {
      monitorPaused = true;
      if (activeJobRecord) {
        activeJobRecord = {
          ...activeJobRecord,
          status: "interrupted",
          detail:
            "Monitoring interrupted; the worker outcome is not confirmed.",
        };
        if (current && activeJobRecord.lesson_id === current.id)
          showJob(activeJobRecord);
      }
      status(
        "Connection interrupted. Use Reconnect saved job before starting another experiment. " +
          error.message,
        true,
      );
    }
  } finally {
    pollInFlight = false;
    if (!activeJob) pollAgain = false;
    if (pollAgain && activeJob) {
      pollAgain = false;
      monitorPaused = false;
      if (pollTimer !== null) clearTimeout(pollTimer);
      pollTimer = setTimeout(() => {
        pollTimer = null;
        poll();
      }, 0);
    } else if (activeJob && !monitorPaused && pollTimer === null)
      pollTimer = setTimeout(() => {
        pollTimer = null;
        poll();
      }, 1000);
  }
}

const legacyReceipts = new Map();
function showLegacyResult(result, context, source) {
  legacyReceipts.set(context.key, { result, context, source });
  if (workspaceKey() !== context.key) {
    status(
      "The run for " +
        context.id +
        " finished with exit " +
        result.returncode +
        ". Return to that workspace to inspect it.",
    );
    return;
  }
  resetResult();
  const displayRevision = resultRevision;
  $("run-storage-status").textContent =
    result.receipt_saved === true
      ? "Saved run" +
        (result.saved_at
          ? " from " + new Date(result.saved_at).toLocaleString()
          : "") +
        ". This output belongs to its recorded source; viewing it does not change your current pad."
      : result.receipt_saved === false
        ? "This run finished, but its result could not be saved. Copy any output you need before leaving or reloading. " +
          (result.receipt_error || "") +
          " No automatic retry was started."
        : "A durable receipt was not confirmed for this run. Keep a copy of any output you need.";
  $("receipt-source-details").hidden = false;
  const submitted = node("pre", source, "result-log");
  $("receipt-source").replaceChildren(submitted);
  classroom("classroom-highlight", { source, language: context.language })
    .then((data) => {
      if (workspaceKey() === context.key && resultRevision === displayRevision)
        $("receipt-source").innerHTML = data.html;
    })
    .catch(() => {});
  $("job-status").textContent =
    "Exit " +
    result.returncode +
    " · " +
    result.elapsed_seconds +
    " seconds" +
    (result.stopped ? " · stopped: " + result.stopped : "") +
    (result.output_truncated
      ? " · Middle output was omitted; exit status and final messages are retained."
      : "");
  $("output").textContent = result.output || "(No printed output.)";
  if (result.language === "sql" && result.mode !== "lesson")
    showSqlResults(result.output);
  for (const [position, source] of (result.figures || []).entries()) {
    if (
      typeof source !== "string" ||
      !/^data:image\/(?:png|jpeg|webp);base64,/.test(source)
    )
      continue;
    const image = node("img");
    image.src = source;
    image.alt = "Python figure " + (position + 1) + " from this run";
    const figure = node("figure");
    figure.append(image, node("figcaption", image.alt));
    $("figures").append(figure);
  }
  displayedJob = {
    lesson_id: context.id,
    source,
    output: result.output || "",
    legacy: true,
  };
  updateErrorJump();
  $("checks").append(
    node(
      "li",
      result.returncode === 0
        ? "Execution finished successfully. Explain the result; this does not automatically demonstrate mastery."
        : "The program reported an error. Use the diagnostic to investigate a small reproducible example.",
    ),
  );
}
function receiptScope(context) {
  return {
    lesson_id: context.id,
    language: context.language,
    mode: context.mode || "snippet",
  };
}
async function openRunReceipt(
  context,
  receiptId,
  version = intentVersion,
  expectedRevision = resultRevision,
) {
  const sequence = ++receiptLoadSequence;
  try {
    const data = await classroom("classroom-run-result", {
      ...receiptScope(context),
      receipt_id: receiptId,
    });
    if (
      workspaceKey() !== context.key ||
      intentVersion !== version ||
      sequence !== receiptLoadSequence ||
      resultRevision !== expectedRevision
    )
      return;
    const receipt = data.receipt;
    if (
      receipt.lesson_id !== context.id ||
      receipt.language !== context.language ||
      receipt.mode !== (context.mode || "snippet")
    )
      throw new Error("The saved run does not belong to this workspace.");
    showLegacyResult(
      {
        ...receipt.result,
        receipt_id: receipt.id,
        receipt_saved: true,
        saved_at: receipt.saved_at,
      },
      context,
      receipt.source,
    );
  } catch (error) {
    if (
      workspaceKey() === context.key &&
      intentVersion === version &&
      sequence === receiptLoadSequence
    )
      status(
        "Could not open the saved run. Your source is unchanged. " +
          error.message,
        true,
      );
  }
}
async function refreshRunHistory({ showLatest = false } = {}) {
  if (current?.engine !== "legacy" || current.runtime_profile === "reading")
    return;
  const context = contextOf(),
    version = intentVersion,
    sequence = ++runHistorySequence,
    revision = resultRevision;
  const data = await classroom("classroom-history", receiptScope(context));
  if (
    workspaceKey() !== context.key ||
    intentVersion !== version ||
    sequence !== runHistorySequence
  )
    return;
  $("history").replaceChildren();
  for (const receipt of data.history) {
    const button = node(
      "button",
      new Date(receipt.saved_at).toLocaleString() +
        " · Exit " +
        receipt.returncode +
        " · " +
        receipt.status +
        " · " +
        receipt.source_sha256.slice(0, 10),
    );
    button.type = "button";
    button.addEventListener("click", () =>
      openRunReceipt(context, receipt.id, version),
    );
    $("history").append(button);
  }
  if (!data.history.length)
    $("history").append(
      node("p", "No saved runs for this language and workspace yet.", "muted"),
    );
  if (showLatest && data.history.length && resultRevision === revision)
    await openRunReceipt(context, data.history[0].id, version, revision);
}
function showSqlResults(output) {
  let parsed;
  try {
    parsed = JSON.parse(output);
  } catch (_) {
    return;
  }
  let number = 0;
  for (const result of parsed.results || []) {
    if (!Array.isArray(result.columns) || !Array.isArray(result.rows)) continue;
    const table = node("table");
    table.append(node("caption", "Query result " + ++number));
    const head = node("thead"),
      headings = node("tr");
    for (const column of result.columns) {
      const cell = node("th", String(column));
      cell.scope = "col";
      headings.append(cell);
    }
    head.append(headings);
    table.append(head);
    const body = node("tbody");
    for (const row of result.rows) {
      const line = node("tr");
      for (const value of row)
        line.append(node("td", value === null ? "NULL" : String(value)));
      body.append(line);
    }
    table.append(body);
    $("sql-results").append(table);
    if (result.truncated)
      $("sql-results").append(
        node(
          "p",
          "This result was truncated at the runtime row limit.",
          "muted",
        ),
      );
  }
}
async function runCode() {
  if (
    !current ||
    !current.capability.ready ||
    current.runtime_profile === "reading" ||
    activeJob ||
    submitInFlight ||
    legacyRunActive
  )
    return;
  submitInFlight = true;
  updateControls();
  const context = contextOf(),
    intent = {
      id: current.id,
      source: $("source").value,
      timeout: Number($("timeout").value),
      version: intentVersion,
    };
  try {
    await flushSave();
    if (
      workspaceKey() !== context.key ||
      intentVersion !== intent.version ||
      $("source").value !== intent.source
    ) {
      status(
        "The lesson or draft changed while saving. Review it and press Run again.",
      );
      return;
    }
    if (context.engine === "legacy") {
      legacyRunActive = true;
      updateControls();
      resetResult();
      $("output").textContent =
        "Running your code. This request has a " +
        intent.timeout +
        "-second backend deadline.";
      status(
        "Your source and notes are saved. You may read another lesson while this bounded run finishes.",
      );
      try {
        const result = await lab(
          context.mode === "lesson" ? "run-lesson" : "run",
          {
            lesson_id: context.id,
            language: context.language,
            ...(context.mode ? { mode: context.mode } : {}),
            code: intent.source,
            timeout_seconds: intent.timeout,
          },
          false,
        );
        showLegacyResult(result, context, intent.source);
        if (workspaceKey() === context.key) {
          const updates = await Promise.allSettled([
            refreshPadHistory(),
            refreshRunHistory({ showLatest: false }),
          ]);
          if (
            workspaceKey() === context.key &&
            updates.some((update) => update.status === "rejected")
          )
            status(
              "The run finished, but its saved-history list could not be refreshed. The actual result remains visible; no code was rerun.",
              true,
            );
        }
      } catch (error) {
        throw new Error(
          "The result is not confirmed. Do not resubmit until the original run deadline has passed. " +
            error.message,
        );
      } finally {
        legacyRunActive = false;
      }
    } else {
      const job = await api("module-run", {
        lesson_id: intent.id,
        source: intent.source,
        timeout_seconds: intent.timeout,
        request_id: crypto.randomUUID().replaceAll("-", ""),
      });
      if (current?.id === job.lesson_id) showJob(job);
      if (!adoptJob(job)) updateControls();
    }
  } catch (error) {
    status(error.message, true);
  } finally {
    submitInFlight = false;
    updateControls();
  }
}
async function refreshPadHistory() {
  if (current?.engine !== "legacy" || current.runtime_profile === "reading")
    return;
  const context = contextOf(),
    data = await lab("pad-history", {
      lesson_id: context.id,
      language: context.language,
      ...(context.mode ? { mode: context.mode } : {}),
    });
  if (workspaceKey() !== context.key) return;
  $("pad-history").replaceChildren();
  const placeholder = node(
    "option",
    data.history.length
      ? "Choose an earlier saved version"
      : "No earlier versions yet",
  );
  placeholder.value = "";
  $("pad-history").append(placeholder);
  for (const entry of data.history) {
    const option = node(
      "option",
      new Date(entry.saved_at).toLocaleString() +
        " · " +
        entry.bytes +
        " bytes",
    );
    option.value = entry.id;
    $("pad-history").append(option);
  }
  $("load-history").disabled = true;
}
async function switchRunner() {
  if (current?.engine !== "legacy") return;
  const desired = { language: $("runner").value, mode: $("pad-mode").value };
  try {
    await openLesson(current.id, true, desired);
    if (current?.engine === "legacy") {
      $("runner").value = current.runner.id;
      $("pad-mode").value = current.mode || "";
    }
  } catch (_) {
    if (current?.engine === "legacy") {
      $("runner").value = current.runner.id;
      $("pad-mode").value = current.mode || "";
    }
  }
}
function selectedViewIntent() {
  return { key: workspaceKey(), version: intentVersion };
}
function sameView(intent) {
  return intent.key === workspaceKey() && intent.version === intentVersion;
}
for (const id of ["home-button", "paths-button", "back-paths"])
  $(id).addEventListener("click", () =>
    showHome().catch((error) =>
      status(
        "Navigation paused to protect your unsaved work. " + error.message,
        true,
      ),
    ),
  );
$("theme-toggle").addEventListener("click", () => {
  remember("dark", !darkMode);
  setTheme(!darkMode);
});
$("pace").addEventListener("change", () => {
  remember("pace", Number($("pace").value));
  if (track()) renderLessons();
});
$("catalog-search").addEventListener("input", () => {
  clearTimeout(catalogSearchTimer);
  catalogSearchTimer = setTimeout(renderHome, 100);
});
$("subject-select").addEventListener("change", () =>
  switchTrack($("subject-select").value).catch((error) => {
    $("subject-select").value = trackId;
    status(error.message, true);
  }),
);
$("lesson-menu").addEventListener("click", () => {
  const open = $("workspace-view").dataset.navigation !== "open";
  $("workspace-view").dataset.navigation = open ? "open" : "closed";
  $("lesson-menu").setAttribute("aria-expanded", String(open));
});
for (const id of ["lesson-query", "stage"])
  $(id).addEventListener(id === "stage" ? "change" : "input", () => {
    if (!index) return;
    remember("filters." + trackId, {
      query: $("lesson-query").value,
      stage: $("stage").value,
    });
    renderLessons();
  });
for (const [id, offset] of [
  ["previous-lesson", -1],
  ["next-lesson", 1],
])
  $(id).addEventListener("click", () => {
    const rows = track()?.lessons || [],
      position = rows.findIndex((item) => hasLessonId(item, lessonId));
    if (rows[position + offset])
      openLesson(rows[position + offset].id).catch((error) =>
        status(error.message, true),
      );
  });
$("variant").addEventListener("change", () =>
  openLesson($("variant").value).catch((error) => {
    if (current) $("variant").value = current.id;
    status(error.message, true);
  }),
);
$("runner").addEventListener("change", switchRunner);
$("pad-mode").addEventListener("change", switchRunner);
$("reading-toggle").addEventListener("click", () => {
  if (!current) return;
  setReadingView(!readingFocused);
  remember("reading." + trackId, readingFocused);
  if (!readingFocused) $("pad-title").scrollIntoView({ block: "start" });
});
$("section-jump").addEventListener("change", () => {
  const target = document.getElementById($("section-jump").value);
  if (target && $("guide").contains(target)) {
    target.setAttribute("tabindex", "-1");
    target.scrollIntoView({ block: "start" });
    target.focus({ preventScroll: true });
  }
});
for (const id of [
  "source",
  "prediction",
  "explanation",
  "read-chapter",
  "phase-note",
])
  $(id).addEventListener("input", markDirty);
$("phase").addEventListener("change", () => {
  phaseNotes[phase] = $("phase-note").value;
  phase = $("phase").value;
  $("phase-note").value = phaseNotes[phase] || "";
  $("phase-label").textContent = {
    read: "Reading notes",
    attempt: "Attempt and observations",
    compare: "Comparison notes",
  }[phase];
});
$("source").addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    editorEscape = true;
    status("Press Tab to leave the coding pad.");
    return;
  }
  if (event.key === "Tab") {
    if (editorEscape || event.shiftKey) {
      editorEscape = false;
      return;
    }
    event.preventDefault();
    const input = event.target;
    input.setRangeText("    ", input.selectionStart, input.selectionEnd, "end");
    input.dispatchEvent(new Event("input"));
  } else editorEscape = false;
});
$("run").addEventListener("click", runCode);
$("cancel").addEventListener("click", async () => {
  if (!activeJob) return;
  const key = activeJob;
  try {
    const job = await api("module-cancel", { job_id: key });
    if (activeJob !== key) return;
    activeJobRecord = job;
    if (current?.id === job.lesson_id) showJob(job);
    monitorPaused = false;
    await poll();
  } catch (error) {
    if (activeJob === key)
      status("Cancellation not confirmed. " + error.message, true);
  }
});
$("save").addEventListener("click", () => flushSave().catch(() => {}));
$("refresh").addEventListener("click", async () => {
  if (!current) return;
  const intent = selectedViewIntent(),
    context = contextOf();
  try {
    if (context.engine === "module") {
      const latest = await api("module-lesson", { lesson_id: context.id });
      if (!sameView(intent)) return;
      current.capability = latest.capability;
      renderHistory(latest.history);
    } else {
      const capabilities = await lab("capabilities", { lesson_id: context.id });
      if (!sameView(intent)) return;
      const selected = capabilities.runners.find(
        (item) => item.id === context.language,
      );
      if (!selected)
        throw new Error(
          "This language is no longer registered for the lesson. Reopen the lesson.",
        );
      current.capabilities = capabilities;
      current.runner = selected;
      current.effective = {
        ...selected,
        ...(selected.modes || []).find((item) => item.id === context.mode),
      };
      current.capability = {
        profile: selected.id,
        ready: Boolean(
          current.effective.can_run && current.effective.available,
        ),
        detail: current.effective.reason || "",
      };
    }
    updateControls();
    status("Runtime check refreshed. Your current draft is unchanged.");
  } catch (error) {
    if (sameView(intent)) status(error.message, true);
  }
});
$("download-source").addEventListener("click", () => {
  if (!current) return;
  const url = URL.createObjectURL(
      new Blob([$("source").value], { type: "text/plain;charset=utf-8" }),
    ),
    link = node("a");
  link.href = url;
  link.download = current.source_filename || "source.txt";
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
$("starter").addEventListener("click", async () => {
  if (current?.engine !== "legacy" || current.runtime_profile === "reading")
    return;
  const intent = selectedViewIntent();
  if (
    !confirm(
      "Save the current pad, then replace the visible draft with this lesson's starter? Earlier changed saves remain recoverable.",
    )
  )
    return;
  try {
    await flushSave();
    if (!sameView(intent)) return;
    $("source").value =
      current.runner.executor === "sql" && current.mode !== "lesson"
        ? current.sql_snippet_starter || "SELECT 42 AS answer;\n"
        : current.learner_code || current.learner || "";
    markDirty();
    resetResult();
    status("Starter loaded. Read its TODOs before running.");
  } catch (error) {
    status(error.message, true);
  }
});
$("pad-history").addEventListener("change", () => {
  $("load-history").disabled = !$("pad-history").value;
});
$("refresh-history").addEventListener("click", () =>
  refreshPadHistory().catch((error) => status(error.message, true)),
);
$("load-history").addEventListener("click", async () => {
  if (current?.engine !== "legacy" || !$("pad-history").value) return;
  const intent = selectedViewIntent(),
    context = contextOf(),
    historyId = $("pad-history").value;
  try {
    await flushSave();
    if (!sameView(intent)) return;
    const data = await lab("read-history", {
      lesson_id: context.id,
      language: context.language,
      ...(context.mode ? { mode: context.mode } : {}),
      history_id: historyId,
    });
    if (!sameView(intent)) return;
    $("source").value = data.code;
    markDirty();
    resetResult();
    status("Earlier source loaded into the pad. It has not been run.");
  } catch (error) {
    status(error.message, true);
  }
});
$("prepare-sql").addEventListener("click", async () => {
  if (current?.engine !== "legacy" || current.runner.executor !== "sql") return;
  if (legacyRunActive || submitInFlight) {
    status("Wait for the current run before resetting SQL.", true);
    return;
  }
  const answer = prompt(
    "This drops and recreates only the disposable course training schema. Saved pads are retained. Type RESET TRAINING to continue.",
    "",
  );
  if (answer !== "RESET TRAINING") return;
  const intent = selectedViewIntent();
  try {
    legacyRunActive = true;
    updateControls();
    const result = await lab("prepare-sql", { confirmation: answer }, false);
    if (sameView(intent)) {
      resetResult();
      $("output").textContent = result.output;
      $("job-status").textContent =
        "SQL preparation exited with status " + result.returncode;
    }
    status(
      "SQL training preparation exited with status " + result.returncode,
      result.returncode !== 0,
    );
  } catch (error) {
    status(error.message, true);
  } finally {
    legacyRunActive = false;
    updateControls();
  }
});
$("hint-button").addEventListener("click", async () => {
  if (current?.engine !== "legacy") return;
  const intent = selectedViewIntent();
  try {
    const data = await lab("hint", {
      lesson_id: current.id,
      number: hintNumber,
    });
    if (!sameView(intent)) return;
    hintNumber++;
    $("hint").textContent = data.hint;
    status(
      "Hint " +
        data.number +
        " of " +
        data.total +
        ". Try a small change before asking again.",
    );
  } catch (error) {
    if (sameView(intent)) status(error.message, true);
  }
});
$("complete").addEventListener("click", async () => {
  if (current?.engine !== "legacy") return;
  const intent = selectedViewIntent(),
    id = current.id;
  try {
    await flushSave();
    if (!sameView(intent)) return;
    await lab("complete", { lesson_id: id, confirmed: $("confirmed").checked });
    if (!sameView(intent)) return;
    const completed = locate(id);
    if (completed) completed.record.completed = true;
    renderLessons();
    status(
      "Your demonstrated lesson record was saved with its evidence. This is a personal record, not automatic grading.",
    );
  } catch (error) {
    if (sameView(intent)) status(error.message, true);
  }
});
$("reveal").addEventListener("click", async () => {
  if (!current || current.learning_mode === "tutorial") return;
  const intent = selectedViewIntent(),
    id = current.id;
  if (
    !confirm(
      "Reveal the separate official solutions? Try the exercises and progressive hints first.",
    )
  )
    return;
  try {
    const data = await classroom("classroom-solutions", {
      lesson_id: id,
      reveal: true,
    });
    if (!sameView(intent)) return;
    $("solutions").replaceChildren();
    for (const document of data.documents) {
      const article = node("article", undefined, "guide");
      article.innerHTML = document.html;
      $("solutions").append(article);
    }
    $("solutions").hidden = false;
    $("solutions").tabIndex = -1;
    $("solutions").focus();
  } catch (error) {
    if (sameView(intent)) status(error.message, true);
  }
});
document.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
    event.preventDefault();
    flushSave().catch(() => {});
  }
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter" && current) {
    event.preventDefault();
    runCode();
  }
});
window.addEventListener("beforeunload", (event) => {
  if (
    current &&
    (saveTimer ||
      pendingSaves ||
      (draftRevisions.get(workspaceKey()) || 0) >
        (savedRevisions.get(workspaceKey()) || 0))
  ) {
    stashDraft(workspaceKey(), values());
    event.preventDefault();
    event.returnValue = "";
  }
});
async function boot() {
  try {
    $("pace").value = String(
      [15, 30, 60, 90].includes(pref("pace")) ? pref("pace") : 30,
    );
    setTheme(
      pref(
        "dark",
        typeof matchMedia === "function" &&
          matchMedia("(prefers-color-scheme: dark)").matches,
      ),
    );
    index = await classroom("classroom-index");
    renderHome();
    if (index.active_job && !finished.has(index.active_job.status))
      adoptJob(index.active_job);
    const query = new URLSearchParams(location.search),
      fragment = new URLSearchParams(location.hash.slice(1)),
      id = query.get("lesson") || fragment.get("lesson");
    if (id && locate(id))
      await openLesson(id, false, {
        language: query.get("language") || fragment.get("language"),
        mode: query.get("mode") || fragment.get("mode"),
        _history: "replace",
      });
    else {
      recordRoute("/classroom", "replace");
      status(
        "Choose any path. Start anywhere, switch subjects freely, and learn at your own pace.",
      );
    }
  } catch (error) {
    status("Cannot load the classroom. " + error.message, true);
  }
}
function recordRoute(url, mode = "push") {
  if (mode === "replace" || url === visibleRoute)
    history.replaceState(null, "", url);
  else history.pushState(null, "", url);
  visibleRoute = url;
}
window.addEventListener("popstate", async () => {
  if (!index) return;
  const target = new URLSearchParams(location.hash.slice(1)),
    id = target.get("lesson");
  try {
    if (id && locate(id))
      await openLesson(id, true, {
        language: target.get("language"),
        mode: target.get("mode"),
        _history: "replace",
      });
    else if (!location.hash) await showHome("replace");
  } catch (error) {
    history.replaceState(null, "", visibleRoute);
    status(
      "Navigation paused to protect your unsaved work. " + error.message,
      true,
    );
  }
});
function scrollToGuideFragment(fragment) {
  if (!fragment) return false;
  let id;
  try {
    id = decodeURIComponent(fragment.replace(/^#/, ""));
  } catch (_) {
    return false;
  }
  const unprefixed = id.replace(
    /^(?:guide|reference|module-guide|lab-guide)--/,
    "",
  );
  const target = [...$("guide").querySelectorAll("[id]")].find(
    (element) =>
      element.id === id ||
      element.id === unprefixed ||
      element.id.endsWith("--" + unprefixed),
  );
  if (!target) return false;
  target.setAttribute("tabindex", "-1");
  target.scrollIntoView({ block: "start" });
  target.focus({ preventScroll: true });
  return true;
}
async function followGuideLink(event) {
  if (
    event.defaultPrevented ||
    event.button > 0 ||
    event.ctrlKey ||
    event.metaKey ||
    event.shiftKey ||
    event.altKey
  )
    return;
  const anchor = event.target.closest?.("a[href]");
  if (
    !anchor ||
    (anchor.getAttribute("download") !== null &&
      anchor.getAttribute("download") !== undefined)
  )
    return;
  const target = anchor.getAttribute("target");
  if (target && target.toLowerCase() !== "_self") return;
  let url;
  try {
    url = new URL(anchor.getAttribute("href"), location.href);
  } catch (_) {
    return;
  }
  if (url.origin !== location.origin) return;
  const linked = /^\/lesson-pages\/([^/]+)\.html$/.exec(url.pathname),
    params = new URLSearchParams(url.hash.slice(1));
  const mapped = Object.prototype.hasOwnProperty.call(
    index?.lesson_links || {},
    url.pathname,
  )
    ? index.lesson_links[url.pathname]
    : null;
  const id =
    mapped ||
    linked?.[1] ||
    (["/classroom", "/learn", "/journeys"].includes(url.pathname)
      ? params.get("lesson")
      : null);
  if (typeof id === "string" && locate(id)) {
    event.preventDefault();
    const opening = openLesson(id),
      version = intentVersion;
    try {
      await opening;
      if (
        current?.id === id &&
        version === intentVersion &&
        !params.has("lesson")
      ) {
        if (/^#solutions?(?:[-_]|$)/i.test(url.hash)) {
          if (current.learning_mode === "tutorial")
            status(
              "Worked explanations are already included in this tutorial chapter.",
            );
          else {
            $("reveal").scrollIntoView({ block: "center" });
            $("reveal").focus({ preventScroll: true });
            status("Choose Reveal solutions to open this comparison.");
          }
        } else scrollToGuideFragment(url.hash);
      }
    } catch (error) {
      status(
        "Navigation paused to protect your unsaved work. " + error.message,
        true,
      );
    }
    return;
  }
  if (url.pathname === location.pathname && url.hash && !params.has("lesson")) {
    if (scrollToGuideFragment(url.hash)) event.preventDefault();
  }
}
$("guide").addEventListener("click", followGuideLink);
$("solutions").addEventListener("click", followGuideLink);
function updatePreviewVisibility() {
  $("syntax-preview").hidden = !previewVisible;
  $("syntax-toggle").setAttribute("aria-pressed", String(previewVisible));
  $("syntax-toggle").textContent = previewVisible
    ? "Hide syntax preview"
    : "Syntax preview";
  ++highlightSequence;
  clearTimeout(highlightTimer);
  if (previewVisible && current) renderSyntaxPreview();
}
async function renderSyntaxPreview() {
  if (!current || !previewVisible) return;
  const key = workspaceKey(),
    source = $("source").value,
    sequence = ++highlightSequence;
  $("preview-status").textContent = "Updating syntax colors...";
  try {
    const result = await classroom("classroom-highlight", {
      source,
      language: current.language,
    });
    if (
      sequence !== highlightSequence ||
      workspaceKey() !== key ||
      !previewVisible ||
      $("source").value !== source
    )
      return;
    $("syntax-code").innerHTML = result.html;
    $("preview-status").textContent =
      "Read-only syntax preview. Edit in the coding pad above.";
  } catch (error) {
    if (
      sequence === highlightSequence &&
      workspaceKey() === key &&
      previewVisible
    ) {
      $("syntax-code").replaceChildren();
      $("preview-status").textContent =
        "Syntax preview unavailable. Your editable source is unchanged. " +
        error.message;
    }
  }
}
$("syntax-toggle").addEventListener("click", () => {
  if (!current) return;
  previewVisible = !previewVisible;
  remember("preview." + trackId, previewVisible);
  updatePreviewVisibility();
});
$("source").addEventListener("input", () => {
  ++highlightSequence;
  clearTimeout(highlightTimer);
  if (previewVisible) {
    $("preview-status").textContent =
      "Preview is updating for your edited source...";
    highlightTimer = setTimeout(renderSyntaxPreview, 600);
  }
});
boot();
