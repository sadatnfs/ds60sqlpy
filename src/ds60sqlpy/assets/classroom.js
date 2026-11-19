"use strict";
// One workspace with separate legacy, worker and browser observation histories.
const $ = (id) => document.getElementById(id);
const phases = ["read", "predict", "attempt", "compare", "explain"];
const finished = new Set(["succeeded", "failed", "cancelled", "timed_out", "blocked"]);
const themes = {
  "python-web": ["#745018", "#fff0d6", "#f2ca86", "#43341f", "PyW"],
  "advanced-spark-modeling": ["#3d4a8f", "#eceffc", "#b7c5ff", "#2b324d", "Sp+"],
  "custom-likelihood-pytorch": ["#8c3056", "#fbeaf2", "#f5b4ce", "#452d3b", "MLE"],
  "tmb-modeling": ["#17636b", "#e3f5f4", "#93d8db", "#223e42", "TMB"],
  "apache-data-platforms": ["#7e3e26", "#fff0e6", "#f4ba99", "#443127", "Data"],
  "data-ml-engineering": ["#26576d", "#e4f3fa", "#9fcfe5", "#233b47", "Eng"],
  polars: ["#275ea1", "#e8f2ff", "#a5cfff", "#24364d", "Pl"],
  dbt: ["#925126", "#fff0df", "#f3c18f", "#443328", "dbt"],
  "ml-engineering": ["#206860", "#e0f6f1", "#96dfd0", "#213c38", "ML"],
  "llm-evaluation": ["#79438f", "#f7eafd", "#deb6ee", "#402b48", "Eval"],
  "applied-science": ["#386d35", "#eaf6e5", "#b7dea9", "#293c25", "Sci"],
  "bayesian-computing": ["#795821", "#fff4db", "#eed093", "#403624", "Bayes"],
  julia: ["#6e4397", "#f2eafa", "#d6b6f2", "#382b46", "Jl"],
  python: ["#795405", "#fff3cd", "#f2ce79", "#3d3421", "Py"],
  sql: ["#2458a6", "#e9f0ff", "#a9caff", "#22334c", "SQL"],
  bridge: ["#006c7a", "#e1f5f8", "#89dce7", "#203b42", "↔"],
  kubernetes: ["#2854af", "#e9efff", "#aec8ff", "#25334e", "K8s"],
  cpp: ["#67429d", "#f0eaff", "#cfb6ff", "#352b48", "C++"],
  java: ["#9a3b26", "#ffede6", "#ffb39d", "#492d28", "Jv"],
  c: ["#435368", "#edf1f5", "#c3d0e1", "#2b3441", "C"],
  go: ["#006677", "#e0f7fc", "#80dcea", "#203d46", "Go"],
  csharp: ["#65338f", "#f4e9ff", "#dfbaff", "#3b284d", "C#"],
  rust: ["#914b24", "#fff0e4", "#efc29a", "#423426", "Rs"],
  swift: ["#a23d12", "#fff0e5", "#ffb89c", "#482f27", "Sw"],
  docker: ["#0063a8", "#e7f5ff", "#9bd5ff", "#213b50", "Dc"],
  cuda: ["#785516", "#fff3d8", "#ffd47e", "#3e3421", "GPU"],
  "web-development": ["#8b3563", "#ffedf5", "#f5b8d7", "#472d3d", "Web"],
  "javascript-typescript": ["#735700", "#fff4ca", "#f1d778", "#3d3522", "JS"],
  "scala-spark": ["#9a3043", "#ffeaf0", "#ffb1c0", "#482b35", "Sp"],
  "deep-learning-tensorflow": ["#934412", "#fff0df", "#ffc18a", "#433327", "TF"],
  "deep-learning-pytorch": ["#a02d43", "#ffe9ee", "#ffafc0", "#482a34", "PT"],
  "llm-theory": ["#5542a5", "#eeeaff", "#c9bdff", "#322c4b", "Lm"],
  "llm-applied": ["#006b60", "#def6ee", "#8adfc9", "#223e38", "AI"],
  dax: ["#875516", "#fff1dc", "#f2c383", "#443522", "DAX"],
  jax: ["#6844a8", "#f0eaff", "#cbb3f8", "#34294b", "JAX"],
  r: ["#235e91", "#e8f3ff", "#a8cce9", "#24384b", "R"],
  "data-visualization": ["#136c61", "#e2f7f0", "#97ddc9", "#243e37", "Viz"],
  nlp: ["#923875", "#fbe8f4", "#f3b5df", "#432c3e", "Aa"],
  "statistics-ml": ["#70428b", "#f4e9fa", "#ddbcf3", "#3c2e45", "Σ"],
  "spark-deployment": ["#2c5d8f", "#e7f1fb", "#a3c8ef", "#22364a", "SpD"],
};
// Contents areas for the catalog. Unlisted subjects appear under "More subjects".
const subjectAreas = [
  {
    id: "start",
    short: "Start here",
    title: "Start here",
    summary: "Python, PostgreSQL and the two together: the base most other paths build on.",
    ink: ["#1d4fb8", "#9dbcff"],
    subjects: ["python", "sql", "bridge"],
  },
  {
    id: "analysis",
    short: "Data analysis",
    title: "Data analysis and visualization",
    summary: "DataFrames, statistical languages and charts that explain data.",
    ink: ["#0e6f66", "#7fd8cb"],
    subjects: ["polars", "data-visualization", "r", "julia", "dax"],
  },
  {
    id: "stats",
    short: "Statistics",
    title: "Statistics and scientific modeling",
    summary: "Inference, experiments, Bayesian computation and likelihood models.",
    ink: ["#6a3d9a", "#c9a8f0"],
    subjects: [
      "statistics-ml",
      "applied-science",
      "bayesian-computing",
      "jax",
      "custom-likelihood-pytorch",
      "tmb-modeling",
    ],
  },
  {
    id: "ai",
    short: "ML and AI",
    title: "Machine learning and AI",
    summary: "Neural networks, language models, evaluation and GPU computing.",
    ink: ["#9b2463", "#f2a3cb"],
    subjects: [
      "deep-learning-pytorch",
      "deep-learning-tensorflow",
      "nlp",
      "llm-theory",
      "llm-applied",
      "llm-evaluation",
      "cuda",
    ],
  },
  {
    id: "dataeng",
    short: "Data engineering",
    title: "Data and ML engineering",
    summary: "Pipelines, transformations, streaming platforms, Spark and ML systems.",
    ink: ["#9a4510", "#f5b183"],
    subjects: [
      "dbt",
      "ml-engineering",
      "data-ml-engineering",
      "apache-data-platforms",
      "scala-spark",
      "spark-deployment",
      "advanced-spark-modeling",
    ],
  },
  {
    id: "languages",
    short: "Languages",
    title: "Programming languages",
    summary: "Systems and application languages, from a first program to larger designs.",
    ink: ["#2f6a1c", "#a6dc8c"],
    subjects: ["c", "cpp", "go", "rust", "java", "csharp", "swift", "javascript-typescript"],
  },
  {
    id: "infra",
    short: "Web and infrastructure",
    title: "Web and infrastructure",
    summary: "Pages, web services, containers and Kubernetes operations.",
    ink: ["#3a4a66", "#b3c2de"],
    subjects: ["web-development", "python-web", "docker", "kubernetes"],
  },
];
const otherArea = {
  id: "more",
  short: "More",
  title: "More subjects",
  summary: "Additional learning paths.",
  ink: ["#4a4f5c", "#c3c8d4"],
  subjects: [],
};
let subjectArea = "all";
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
  codeFocused = false,
  runTimer = null,
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
const browserPreview =
  typeof globalThis.DS60BrowserPreview === "function"
    ? new globalThis.DS60BrowserPreview($("browser-preview"))
    : null;
let browserPreviewContext = null;
let browserLiveKey = null,
  browserLivePaused = false,
  browserLiveTimer = null,
  browserLiveGeneration = 0,
  browserStudioFocused = false,
  browserLiveFocus = null;

function isBrowserLesson() {
  return Boolean(
    current && ["html-browser", "javascript-browser"].includes(current.runtime_profile),
  );
}
function browserLiveEnabled() {
  return isBrowserLesson() && browserLiveKey === workspaceKey();
}
function browserLiveStatus(message, state = "idle") {
  if ($("browser-live-state").textContent !== message)
    $("browser-live-state").textContent = message;
  $("browser-live-state").dataset.state = state;
}
function clearBrowserLive() {
  clearTimeout(browserLiveTimer);
  browserLiveTimer = null;
  browserLiveGeneration++;
  browserLiveKey = null;
  browserLivePaused = false;
  browserLiveFocus = null;
  $("browser-live-toggle").checked = false;
  browserLiveStatus("Live preview is off. Your code runs only when you choose.");
}
function sourceHasFocus() {
  return (
    document.activeElement === $("source") || Boolean(globalThis.DS60SourceEditor?.hasFocus?.())
  );
}
function preserveBrowserEditorFocus() {
  if (
    browserLiveFocus?.editor &&
    browserLiveEnabled() &&
    browserLiveFocus.generation === browserLiveGeneration &&
    browserPreviewContext === browserLiveFocus.context &&
    document.activeElement === browserPreview?.frame
  )
    $("source").focus({ preventScroll: true });
}
function updateBrowserLayout() {
  $("authored").className =
    "panes" +
    (readingFocused ? " reading-focus" : "") +
    (codeFocused && !isBrowserLesson() ? " code-focus" : "") +
    (browserStudioFocused && isBrowserLesson() ? " browser-focus" : "");
  $("browser-studio-toggle").setAttribute("aria-pressed", String(browserStudioFocused));
  $("browser-studio-toggle").textContent = browserStudioFocused
    ? "Return to lesson layout"
    : "Focus on editor & preview";
}
function updateBrowserViewport() {
  const value = $("browser-viewport").value;
  const width = ["1280", "768", "390"].includes(value) ? Number(value) : null;
  $("browser-preview").style.width = width ? width + "px" : "100%";
  const measured = width || Math.round($("browser-preview").clientWidth || 0);
  $("browser-viewport-label").textContent = measured ? measured + " px viewport" : "Fit to space";
}
function updateBrowserLiveControls() {
  const eligible = isBrowserLesson();
  $("browser-live-controls").hidden = !eligible;
  $("browser-preview-home").hidden = !eligible;
  $("browser-studio").dataset.browser = String(eligible);
  $("browser-live-toggle").checked = browserLiveEnabled();
  $("browser-live-toggle").disabled =
    !eligible ||
    !browserPreview ||
    !current?.capability?.ready ||
    Boolean(activeJob) ||
    submitInFlight ||
    legacyRunActive;
  $("browser-live-pause").disabled = !browserLiveEnabled();
  $("browser-live-pause").textContent = browserLivePaused ? "Resume updates" : "Pause updates";
  $("browser-live-pause").setAttribute("aria-pressed", String(browserLivePaused));
  $("browser-live-stop").disabled = !browserLiveEnabled() && !browserPreview?.active;
  $("browser-preview-empty").hidden = Boolean(browserPreview?.active);
  $("browser-preview-title").textContent =
    current?.runtime_profile === "html-browser" ? "Page preview" : "Visualization preview";
  if (!eligible) browserStudioFocused = false;
  updateBrowserLayout();
  updateBrowserViewport();
}
function scheduleBrowserLive(delay = 650) {
  if (!browserLiveEnabled() || browserLivePaused || submitInFlight) return;
  clearTimeout(browserLiveTimer);
  const generation = ++browserLiveGeneration;
  const context = contextOf();
  browserLiveStatus("Waiting for a pause in typing...", "pending");
  browserLiveTimer = setTimeout(() => {
    browserLiveTimer = null;
    if (
      !browserLiveEnabled() ||
      browserLivePaused ||
      generation !== browserLiveGeneration ||
      workspaceKey() !== context.key
    )
      return;
    void renderBrowserLive(context, generation, $("source").value);
  }, delay);
  updateControls();
}
async function renderBrowserLive(context, generation, source) {
  if (!browserPreview || !browserLiveEnabled() || generation !== browserLiveGeneration) return;
  const stillCurrent = () =>
    browserLiveEnabled() &&
    generation === browserLiveGeneration &&
    workspaceKey() === context.key &&
    browserPreviewContext === context;
  resetResult();
  browserPreviewContext = context;
  browserLiveFocus = {
    context,
    generation,
    editor: sourceHasFocus(),
  };
  $("browser-preview-panel").hidden = false;
  $("browser-fullscreen-status").textContent = "";
  $("job-status").textContent = "Live preview is updating...";
  outputNote("Refreshing your preview...");
  $("browser-observation-save").disabled = true;
  browserLiveStatus("Refreshing your preview...", "pending");
  try {
    const promise = browserPreview.start(
      source,
      (snapshot, type) => {
        if (!stillCurrent()) return;
        programOutput(snapshot.output || "(No console output.)");
        if (type === "interaction-error") {
          $("job-status").textContent = "Live preview: failed";
          browserLiveStatus("The preview needs attention. Check the console.", "error");
          $("browser-observation-save").disabled = false;
        }
      },
      current.runtime_profile === "html-browser" ? "html" : "javascript",
    );
    updateBrowserFullscreenControls();
    updateControls();
    const observation = await promise;
    if (!stillCurrent()) return;
    preserveBrowserEditorFocus();
    $("job-status").textContent = "Live preview: " + observation.status;
    programOutput(observation.output || "(No console output.)");
    $("run-storage-status").textContent =
      "Live preview is not added to saved runs. Choose Save observation to keep this output and its source.";
    $("browser-observation-save").disabled = !browserPreview.active;
    browserLiveStatus(
      browserLivePaused
        ? "Updates are paused. The preview shows the last rendered version."
        : observation.status === "failed"
          ? "The preview needs attention. Edit your code to try again."
          : "Preview is up to date.",
      observation.status === "failed" ? "error" : "ready",
    );
  } catch (error) {
    if (!stillCurrent()) return;
    $("job-status").textContent = "Live preview: failed";
    programOutput(error.message);
    browserLiveStatus("The preview needs attention. Check the console.", "error");
  } finally {
    if (browserLiveFocus?.context === context) browserLiveFocus = null;
    if (stillCurrent()) updateControls();
  }
}
let browserFullscreenPending = false,
  browserFullscreenSequence = 0,
  browserWasFullscreen = false;
function browserPreviewIsFullscreen() {
  return document.fullscreenElement === $("browser-preview-panel");
}
function updateBrowserFullscreenControls() {
  const panel = $("browser-preview-panel"),
    button = $("browser-fullscreen"),
    fullscreen = browserPreviewIsFullscreen(),
    supported =
      typeof panel.requestFullscreen === "function" &&
      typeof document.exitFullscreen === "function" &&
      document.fullscreenEnabled !== false;
  button.hidden = !supported && !fullscreen;
  button.disabled = browserFullscreenPending || (!fullscreen && !browserPreview?.active);
  button.textContent = fullscreen ? "Exit fullscreen" : "Fullscreen preview";
  button.setAttribute("aria-pressed", String(fullscreen));
  button.setAttribute(
    "aria-label",
    fullscreen ? "Exit fullscreen visualization preview" : "Show visualization preview fullscreen",
  );
}
async function exitBrowserPreviewFullscreen() {
  if (!browserPreviewIsFullscreen()) return;
  try {
    await document.exitFullscreen();
  } catch (_) {
    if (browserPreviewIsFullscreen())
      $("browser-fullscreen-status").textContent =
        "Could not leave fullscreen. Use the Exit fullscreen control or press Escape.";
  } finally {
    if (!browserPreview?.active && !browserPreviewIsFullscreen())
      $("browser-preview-panel").hidden = true;
    updateBrowserFullscreenControls();
  }
}
async function toggleBrowserFullscreen() {
  if (browserFullscreenPending) return;
  const panel = $("browser-preview-panel"),
    fullscreen = browserPreviewIsFullscreen();
  if (
    !fullscreen &&
    (panel.hidden ||
      !browserPreview?.active ||
      typeof panel.requestFullscreen !== "function" ||
      typeof document.exitFullscreen !== "function" ||
      document.fullscreenEnabled === false)
  )
    return;
  const sequence = ++browserFullscreenSequence;
  browserFullscreenPending = true;
  $("browser-fullscreen-status").textContent = "";
  updateBrowserFullscreenControls();
  try {
    if (fullscreen) await exitBrowserPreviewFullscreen();
    else {
      // Keep the existing iframe and its live chart in place. Fullscreen is
      // presentation only: it must not save, reload or execute learner source.
      await panel.requestFullscreen();
      if (sequence !== browserFullscreenSequence || !browserPreview?.active || panel.hidden)
        await exitBrowserPreviewFullscreen();
      else if (browserPreviewIsFullscreen())
        $("browser-fullscreen-status").textContent =
          "Fullscreen preview. Press Escape or choose Exit fullscreen to return.";
    }
  } catch (_) {
    if (sequence === browserFullscreenSequence)
      $("browser-fullscreen-status").textContent =
        "Fullscreen is unavailable in this browser or window. Your preview and saved work are unchanged.";
  } finally {
    browserFullscreenPending = false;
    updateBrowserFullscreenControls();
  }
}
function syncBrowserFullscreen() {
  const fullscreen = browserPreviewIsFullscreen();
  if (fullscreen && !browserPreview?.active) void exitBrowserPreviewFullscreen();
  if (!fullscreen) {
    if (!browserPreview?.active) $("browser-preview-panel").hidden = true;
    if (browserWasFullscreen && browserPreview?.active && !$("browser-preview-panel").hidden) {
      $("browser-fullscreen-status").textContent =
        "Returned to the lesson. The same visualization is still running.";
      $("browser-fullscreen").focus();
    }
  }
  browserWasFullscreen = fullscreen;
  updateBrowserFullscreenControls();
}
function stopBrowserPreview(reason = "Preview stopped.") {
  clearBrowserLive();
  ++browserFullscreenSequence;
  void exitBrowserPreviewFullscreen();
  browserPreview?.stop(reason);
  browserPreviewContext = null;
  $("browser-observation-save").disabled = true;
  // Keep the Exit control visible until native fullscreen has actually ended.
  $("browser-preview-panel").hidden = !browserPreviewIsFullscreen();
  $("browser-preview-empty").hidden = false;
  updateBrowserLiveControls();
  updateBrowserFullscreenControls();
}
function showBrowserObservation(receipt) {
  if (!current || current.id !== receipt.lesson_id) return;
  resetResult();
  displayedJob = receipt;
  $("job-status").textContent =
    "Browser observation: " +
    receipt.status +
    " · " +
    Number(receipt.elapsed_seconds).toFixed(2) +
    " seconds";
  programOutput(receipt.output || "(No console output.)");
  $("run-storage-status").textContent =
    "Saved browser observation. This is client-reported output, not a server verifier result. " +
    "Viewing it leaves your current pad unchanged and does not run the source.";
  $("receipt-source-details").hidden = false;
  const submitted = highlightedSourceBlock(receipt.source);
  $("receipt-source").replaceChildren(submitted.pre);
  const revision = resultRevision;
  classroom("classroom-highlight", { source: receipt.source, language: receipt.language })
    .then((data) => {
      if (resultRevision === revision && current?.id === receipt.lesson_id)
        submitted.code.innerHTML = data.html;
    })
    .catch(() => {});
  $("checks").append(
    node("li", "Browser observations do not provide independent semantic verification."),
  );
}
async function saveBrowserObservation(context, observation, show = true) {
  const result = await api("module-browser-record", {
    lesson_id: context.id,
    fields: {
      source: observation.source,
      output: observation.output,
      status: observation.status,
      elapsed_seconds: Math.min(3600, Math.max(0, observation.elapsed_seconds || 0)),
    },
  });
  if (workspaceKey() === context.key) {
    if (show && browserPreviewContext === context) showBrowserObservation(result.receipt);
    const latest = await api("module-browser-history", { lesson_id: context.id });
    if (workspaceKey() === context.key) renderHistory(latest.history);
  }
  return result.receipt;
}
async function runBrowserPreview(context, intent) {
  if (!browserPreview)
    throw new Error("The browser preview component did not load. Reload the classroom.");
  stopBrowserPreview("Replaced by another preview.");
  resetResult();
  browserPreviewContext = context;
  $("browser-preview-panel").hidden = false;
  $("browser-fullscreen-status").textContent = "";
  outputNote("Starting the isolated browser preview...");
  const observationPromise = browserPreview.start(
    intent.source,
    (snapshot, type) => {
      if (workspaceKey() !== context.key || browserPreviewContext !== context) return;
      programOutput(snapshot.output || "(No console output.)");
      if (type === "interaction-error") {
        $("job-status").textContent =
          "An interaction raised a browser error after the initial run.";
        $("run-storage-status").textContent =
          "Inspect the console, then save the latest observation if useful. Earlier receipts stay unchanged.";
      }
    },
    current.runtime_profile === "html-browser" ? "html" : "javascript",
  );
  updateBrowserFullscreenControls();
  updateControls();
  const observation = await observationPromise;
  if (workspaceKey() === context.key && browserPreviewContext === context) {
    $("job-status").textContent = "Browser observation: " + observation.status;
    programOutput(observation.output || "(No console output.)");
    $("browser-observation-save").disabled = !browserPreview.active;
  }
  try {
    await saveBrowserObservation(context, observation);
  } catch (error) {
    if (workspaceKey() === context.key)
      $("run-storage-status").textContent =
        "The browser result could not be saved. Its current output is retained; copy it before leaving. " +
        error.message;
  }
}

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
const LEGACY_RUN_NOTE =
  "Your source and notes are saved. You may read another lesson while this bounded run finishes.";
function pref(key, fallback = null) {
  try {
    return JSON.parse(localStorage.getItem("ds60.classroom." + key)) ?? fallback;
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
  return record.id === id || (record.variants || []).some((variant) => variant.id === id);
}
function locate(id) {
  for (const subject of index?.tracks || []) {
    const record = subject.lessons.find((item) => hasLessonId(item, id));
    if (record) return { subject, record };
  }
  return null;
}
function workspaceKey(data = current) {
  return data
    ? data.id +
        (data.engine === "legacy" ? ":" + data.runner.id + ":" + (data.mode || "snippet") : "")
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
    localStorage.setItem("ds60.classroom.unsaved." + key, JSON.stringify(fields));
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
    if (response.status === 403 && /session token/i.test(data.error || ""))
      throw new Error(
        "The classroom restarted after this page opened. Reload the page to reconnect; work saved in the classroom is kept.",
      );
    if (!response.ok) throw new Error(data.error || "The local classroom rejected this action.");
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
  if (context.engine === "module") return api("module-save", { lesson_id: context.id, fields });
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
          $("save-state").textContent = "Saved in your local learning workspace.";
          try {
            localStorage.removeItem("ds60.classroom.unsaved." + context.key);
            if (context.engine === "module")
              localStorage.removeItem("ds60.module.unsaved." + context.id);
          } catch (_) {}
        } else if (sameView) {
          $("save-state").textContent = "Unsaved changes. Your newer draft is waiting to save.";
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
    "#2f3fb3",
    "#ebedfb",
    "#aab4ff",
    "#2c3150",
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
  return minutes > 0 ? Math.max(1, Math.ceil(minutes / Number($("pace").value || 30))) : null;
}
function areaOf(subject) {
  return subjectAreas.find((area) => area.subjects.includes(subject.id)) || otherArea;
}
function levelSpan(subject) {
  const order = ["beginner", "intermediate", "advanced"],
    present = order.filter((level) => subject.lessons.some((item) => item.level === level)),
    name = (level) => level[0].toUpperCase() + level.slice(1);
  if (!present.length) return "";
  return present.length === 1 ? name(present[0]) : name(present[0]) + " to " + present.at(-1);
}
function firstSentence(text) {
  const value = String(text || "").trim(),
    match = /^(.{30,200}?[.!?])(?:\s|$)/.exec(value);
  return match ? match[1] : value;
}
function subjectEntry(subject) {
  const card = node("button", undefined, "subject-card");
  card.type = "button";
  const icon = theme(subject, card),
    authored = subject.lessons.filter((item) => item.status !== "planned").length,
    done = subject.lessons.filter((item) => item.completed).length,
    main = node("span", undefined, "toc-main"),
    meta = node("span", undefined, "toc-meta");
  main.append(
    node("span", subject.title, "toc-title"),
    node(
      "span",
      firstSentence(subject.description) || "Lessons, worked examples and coding exercises.",
      "toc-summary",
    ),
  );
  meta.append(
    node("span", String(authored), "toc-count"),
    node(
      "span",
      subject.id === "statistics-ml" ? "tutorial chapters" : "lessons",
      "toc-count-label",
    ),
    node("span", levelSpan(subject), "toc-levels"),
  );
  if (done) meta.append(node("span", done + " of " + authored + " done", "toc-progress"));
  card.append(node("span", icon, "subject-icon"), main, meta);
  card.setAttribute("aria-label", subject.title + ", " + authored + " lessons");
  card.addEventListener("click", () =>
    switchTrack(subject.id).catch((error) => status(error.message, true)),
  );
  const item = node("li");
  item.append(card);
  return item;
}
function areaInk(area, element) {
  element.style.setProperty("--area-ink", area.ink[darkMode ? 1 : 0]);
  element.style.setProperty("--area-on-ink", darkMode ? "#14161b" : "#ffffff");
  element.style.setProperty("--area-text", area.ink[darkMode ? 1 : 0]);
}
function renderHome() {
  if (!index) return;
  const query = $("catalog-search").value.trim().toLowerCase(),
    terms = query.split(/\s+/).filter(Boolean),
    matches = (text) => terms.every((term) => String(text).toLowerCase().includes(term));
  const areas = [...subjectAreas, otherArea],
    members = new Map(areas.map((area) => [area.id, []]));
  for (const subject of index.tracks) members.get(areaOf(subject).id).push(subject);
  for (const area of areas)
    members.get(area.id).sort((a, b) => area.subjects.indexOf(a.id) - area.subjects.indexOf(b.id));
  if (subjectArea !== "all" && !areas.some((area) => area.id === subjectArea)) subjectArea = "all";
  const filters = $("subject-filters");
  filters.replaceChildren();
  const tab = (id, label, count, area) => {
    const button = node("button", label, "thumb-tab");
    button.type = "button";
    if (area) button.title = area.title;
    button.append(node("small", String(count)));
    button.setAttribute("aria-pressed", String(subjectArea === id && !query));
    if (area) areaInk(area, button);
    button.addEventListener("click", () => {
      subjectArea = id;
      remember("area", id);
      if (query) $("catalog-search").value = "";
      renderHome();
    });
    filters.append(button);
  };
  tab("all", "All subjects", index.tracks.length, null);
  for (const area of areas)
    if (members.get(area.id).length) tab(area.id, area.short, members.get(area.id).length, area);
  const cards = $("subject-cards");
  cards.replaceChildren();
  let count = 0;
  for (const area of areas) {
    if (!query && subjectArea !== "all" && subjectArea !== area.id) continue;
    const visible = members
      .get(area.id)
      .filter(
        (subject) =>
          !query || matches(subject.title + " " + subject.description + " " + subject.id),
      );
    if (!visible.length) continue;
    count += visible.length;
    const part = node("section", undefined, "toc-part"),
      head = node("div", undefined, "toc-part-head"),
      list = node("ol", undefined, "toc-list"),
      lessons = visible.reduce(
        (total, subject) =>
          total + subject.lessons.filter((item) => item.status !== "planned").length,
        0,
      );
    part.dataset.area = area.id;
    part.setAttribute("aria-label", area.title);
    areaInk(area, part);
    head.append(
      node("h3", area.title),
      node("p", area.summary),
      node(
        "span",
        visible.length +
          (visible.length === 1 ? " subject · " : " subjects · ") +
          lessons.toLocaleString("en-US") +
          " lessons",
        "toc-part-count",
      ),
    );
    for (const subject of visible) list.append(subjectEntry(subject));
    part.append(head, list);
    cards.append(part);
  }
  const results = [];
  if (query)
    for (const subject of index.tracks)
      for (const record of subject.lessons)
        if (matches(record.title + " " + record.id + " " + (record.concepts || []).join(" ")))
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
      (results.length > 40 ? " (showing the first 40; refine your search)." : ".")
    : "";
  $("no-results").hidden = count > 0 || results.length > 0;
  const countLessons = index.tracks.reduce(
    (total, subject) => total + subject.lessons.filter((item) => item.status !== "planned").length,
    0,
  );
  $("catalog-summary").textContent =
    countLessons.toLocaleString("en-US") +
    " lessons and chapters · " +
    index.tracks.length +
    " subjects · runs on your machine, offline once prepared";
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
  clearBrowserLive();
  const version = ++intentVersion;
  await flushSave();
  if (version !== intentVersion) return;
  if (
    current &&
    (draftRevisions.get(workspaceKey()) || 0) > (savedRevisions.get(workspaceKey()) || 0)
  ) {
    status(
      "Your draft changed while it was saving. Save the latest version before leaving this lesson.",
    );
    return;
  }
  stopBrowserPreview("Stopped when returning to all subjects.");
  ++loadSequence;
  $("home-view").hidden = false;
  $("workspace-view").hidden = true;
  theme(null);
  renderHome();
  recordRoute("/classroom", historyMode);
  document.title = "DS60 Classroom · Course catalog";
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
  const terms = $("lesson-query").value.toLowerCase().split(/\s+/).filter(Boolean);
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
    if (hasLessonId(item, lessonId)) button.setAttribute("aria-current", "page");
    const sessions = estimatedSessions(item),
      position = (track()?.lessons || []).indexOf(item) + 1;
    button.append(
      node(
        "small",
        item.id +
          (item.completed ? " · Demonstrated" : "") +
          " · " +
          (item.level || "") +
          (sessions ? " · ~" + sessions + (sessions === 1 ? " session" : " sessions") : ""),
      ),
    );
    const folio = node("span", item.completed ? "✓" : String(position), "lesson-num");
    folio.setAttribute("aria-hidden", "true");
    if (item.completed) button.dataset.completed = "true";
    button.append(folio);
    button.addEventListener("click", () =>
      openLesson(item.id).catch((error) => status(error.message, true)),
    );
    list.append(button);
  }
  if (!rows.length)
    list.append(node("p", "No lessons match. Clear the search or choose another stage.", "muted"));
}
function renderPager() {
  const rows = track()?.lessons || [],
    position = rows.findIndex((item) => hasLessonId(item, lessonId));
  $("previous-lesson").disabled = position <= 0;
  $("next-lesson").disabled = position < 0 || position >= rows.length - 1;
  $("journey-position").textContent = position >= 0 ? position + 1 + " of " + rows.length : "";
  $("lesson-folio").textContent = position >= 0 ? String(position + 1) : "";
  if (position > 0)
    $("previous-lesson").setAttribute("aria-label", "Previous: " + rows[position - 1].title);
  if (position >= 0 && position < rows.length - 1)
    $("next-lesson").setAttribute("aria-label", "Next: " + rows[position + 1].title);
}
async function switchTrack(id) {
  const subject = index.tracks.find((item) => item.id === id);
  if (!subject) return;
  const remembered = pref("lastTrack." + id);
  const first = subject.lessons.find((item) => item.status !== "planned") || subject.lessons[0];
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
    capabilities.runners.find((item) => item.id === capabilities.default_runner);
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
  const lessonStarter =
    selected.executor === "python" &&
    selected.id === capabilities.default_runner &&
    typeof data.learner_code === "string" &&
    data.learner_code.trim() &&
    data.learner_code.length <= (selected.max_code_bytes || 0)
      ? data.learner_code
      : "";
  const source =
    pad.saved === true
      ? pad.code
      : pad.code ||
        lessonStarter ||
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
      mode === "lesson" ? data.lesson_path.split("/").at(-1) : "practice" + selected.file_suffix,
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
      item.title + (item.kind === "reading" ? "" : item.can_run ? "" : " (save only)"),
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
  $("starter").disabled = data.runner.id !== data.capabilities.default_runner;
  $("coaching-prompt").textContent = data.coaching_prompt || "";
  $("confirmed").checked = false;
  $("hint").textContent = "";
  hintNumber = 1;
  phase = "read";
  phaseNotes = Object.fromEntries(phases.map((item) => [item, data.session[item] || ""]));
  $("phase").value = phase;
  $("phase-note").value = phaseNotes[phase];
  $("phase-label").textContent = "Reading notes";
}
async function openLesson(id, save = true, requested = {}) {
  clearBrowserLive();
  requested = {
    ...pref("context." + id, {}),
    ...Object.fromEntries(
      Object.entries(requested).filter(([, value]) => value !== null && value !== undefined),
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
    (draftRevisions.get(workspaceKey()) || 0) > (savedRevisions.get(workspaceKey()) || 0)
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
    stopBrowserPreview("Stopped when leaving the visualization workspace.");
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
    $("capability").textContent = "Planned content has no coding workspace or claimed runtime yet.";
    $("runtime-setup").hidden = true;
    $("llm-reading-route").hidden = true;
    recordRoute("/classroom#" + new URLSearchParams({ lesson: id }), requested._history || "push");
    status("This lesson is planned. Choose an authored lesson to read and practice.");
    return;
  }
  status("Opening " + found.record.title + "...");
  let data;
  try {
    data = await fetchLesson(id, found.subject, requested);
  } catch (error) {
    if (sequence === loadSequence && version === intentVersion)
      status(
        "Could not open this lesson. Your previous workspace is still here. " + error.message,
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
  stopBrowserPreview("Stopped when leaving the visualization workspace.");
  current = data;
  browserStudioFocused = false;
  trackId = found.subject.id;
  lessonId = id;
  theme(found.subject);
  $("home-view").hidden = true;
  $("workspace-view").hidden = false;
  $("workspace-view").dataset.navigation = "closed";
  $("lesson-menu").setAttribute("aria-expanded", "false");
  const filters = pref("filters." + trackId, {});
  $("stage").value = ["beginner", "intermediate", "advanced"].includes(filters.stage)
    ? filters.stage
    : "all";
  $("lesson-query").value = typeof filters.query === "string" ? filters.query : "";
  renderNavigation();
  renderVariants(found.record, id);
  renderLegacyControls(data);
  const tutorial = data.learning_mode === "tutorial";
  setReadingView(preferredReadingView(tutorial));
  setCodeFocus(!readingFocused && pref("code." + trackId) === true);
  $("solution-section").hidden = tutorial;
  $("chapter-read-label").hidden = !tutorial;
  $("read-chapter").checked = data.session.review === "read";
  $("prediction-label").hidden = tutorial;
  $("prediction").hidden = tutorial;
  $("pad-title").textContent = tutorial ? "Worked examples and notes" : "Code and reflection";
  $("explanation-label").textContent = tutorial
    ? "Notes and interpretations"
    : "Explain the evidence";
  $("learning-guidance").textContent = tutorial
    ? "Tutorial chapters include complete worked examples. There are no exams or withheld solutions. Mark a chapter as read to save your review status."
    : data.execution_mode === "draft"
      ? "Use the notes to explain your context trace and compare it with the named worked reference."
      : "Execution status reports runtime behavior. Use the notes to explain results and record checks.";
  $("title").textContent = data.title || found.record.title;
  $("outcome").textContent =
    data.outcome || found.record.outcome || (data.topics || []).join(" · ");
  $("badges").replaceChildren(
    node("span", found.subject.title, "badge subject"),
    node("span", found.record.level || data.level, "badge"),
    node("span", tutorial ? "Tutorial chapter" : "Practice lesson", "badge"),
  );
  if (data.estimated_minutes || found.record.estimated_minutes)
    $("badges").append(
      node(
        "span",
        (data.estimated_minutes || found.record.estimated_minutes) + " min suggested study",
        "badge",
      ),
    );
  renderPrerequisites(data.prerequisites || found.record.prerequisites || []);
  $("llm-reading-route").hidden = !["llm-theory", "llm-applied"].includes(trackId);
  $("guide").innerHTML = data.guide_html;
  hideRepeatedLevel();
  enhanceGuideCode();
  renderSections();
  $("source").value = data.source || "";
  $("prediction").value = data.session.prediction || "";
  $("explanation").value = data.session.explanation || "";
  $("solutions").replaceChildren();
  $("solutions").hidden = true;
  $("offline-cases").replaceChildren();
  let recovered = false;
  const key = workspaceKey();
  try {
    const backup = JSON.parse(
      localStorage.getItem("ds60.classroom.unsaved." + key) ||
        (data.engine === "module" ? localStorage.getItem("ds60.module.unsaved." + id) : null) ||
        "null",
    );
    if (
      backup &&
      ["source", "prediction", "explanation"].every((field) => typeof backup[field] === "string")
    ) {
      for (const field of ["source", "prediction", "explanation"]) $(field).value = backup[field];
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
    data.language + (data.runtime_profile !== data.language ? " · " + data.runtime_profile : "");
  $("runtime-details").hidden = !data.runtime_guidance;
  $("runtime-guidance").textContent = data.runtime_guidance || "";
  $("planned").hidden = true;
  $("authored").hidden = false;
  resetResult();
  renderHistory(data.history || []);
  const resumable = (data.history || []).find((job) => !finished.has(job.status));
  if (!activeJob && resumable) adoptJob(resumable, false);
  if (activeJobRecord?.lesson_id === id) showJob(activeJobRecord);
  else if (data.history?.length) showJob(data.history[0]);
  updateControls();
  loadExercises();
  if (activeJob && !monitorPaused) poll();
  if (data.engine === "legacy" && legacyReceipts.has(key)) {
    const saved = legacyReceipts.get(key);
    showLegacyResult(saved.result, saved.context, saved.source);
  }
  // The code editor highlights syntax itself and hides the preview toggle.
  previewVisible = !globalThis.DS60SourceEditor && pref("preview." + trackId, false);
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
  const recentTracks = pref("recentTracks", []);
  remember(
    "recentTracks",
    [
      trackId,
      ...(Array.isArray(recentTracks) ? recentTracks : []).filter((item) => item !== trackId),
    ]
      .filter((item) => typeof item === "string")
      .slice(0, 8),
  );
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
  window.scrollTo({ top: 0 });
  status(
    tutorial
      ? "Chapter and saved notes loaded."
      : "Your guide, code, and notes are ready. Choose a small idea to try.",
  );
}
function renderPrerequisites(ids) {
  $("prerequisites").replaceChildren();
  if (!ids.length) {
    $("prerequisites").append(node("span", "Start here: no earlier lesson is required."));
    return;
  }
  $("prerequisites").append(node("span", "Prerequisite lessons: "));
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
  if (focused) {
    codeFocused = false;
    browserStudioFocused = false;
    if (browserLiveEnabled()) stopBrowserPreview("Paused while focusing on the lesson.");
  }
  updateBrowserLayout();
  syncCodeFocusToggle();
  $("reading-toggle").setAttribute("aria-pressed", String(focused));
  $("reading-toggle").textContent = focused ? "Show code and notes" : "Focus on reading";
}
// Focus on code gives the listing and its result the whole workspace; the lesson
// stays one click away. Browser lessons keep their own editor-and-preview studio.
function setCodeFocus(focused) {
  codeFocused = Boolean(focused) && !isBrowserLesson();
  if (codeFocused && readingFocused) {
    readingFocused = false;
    $("reading-toggle").setAttribute("aria-pressed", "false");
    $("reading-toggle").textContent = "Focus on reading";
  }
  updateBrowserLayout();
  syncCodeFocusToggle();
}
function syncCodeFocusToggle() {
  $("code-focus-toggle").setAttribute("aria-pressed", String(codeFocused));
  $("code-focus-toggle").textContent = codeFocused ? "Show the lesson too" : "Focus on code";
}
function renderSections() {
  $("section-jump").replaceChildren();
  const first = node("option", "Choose a section");
  first.value = "";
  $("section-jump").append(first);
  for (const heading of [...$("guide").querySelectorAll("h2,h3,h4,h5,h6")].slice(0, 200)) {
    if (!heading.id) continue;
    let text = heading.textContent.replace(/\s*#\s*$/, "").trim();
    if (/^stat-\d+-\d+/.test(text))
      text = heading.nextElementSibling?.querySelector("strong")?.textContent || text;
    const option = node("option", text);
    option.value = heading.id;
    $("section-jump").append(option);
  }
}
function updateControls() {
  $("cancel").disabled = !activeJob && !browserPreview?.active && !browserLiveEnabled();
  $("cancel").hidden = current?.engine === "legacy" && !activeJob;
  $("cancel").textContent =
    browserPreview?.active || browserLiveEnabled()
      ? "Stop preview"
      : activeJobRecord
        ? "Cancel " + activeJobRecord.lesson_id + " job"
        : "Cancel job";
  updateBrowserLiveControls();
  if (!current) return;
  showCapability(current.capability);
}
function showCapability(cap) {
  const reading = current.runtime_profile === "reading";
  const draft = current.execution_mode === "draft";
  $("prediction-label").textContent = draft
    ? "Predict before you compare"
    : "Predict before you run";
  $("source-help").textContent = draft
    ? "Tab indents. Escape then Tab leaves the editor. Ctrl/Cmd+S saves. Use Open worked comparison to inspect the named reference."
    : "Tab indents. Escape then Tab leaves the editor. Ctrl/Cmd+S saves; Ctrl/Cmd+Enter runs.";
  $("runtime-summary").textContent = draft ? "About this offline workspace" : "How this code runs";
  $("run").hidden = draft;
  $("refresh").hidden = draft;
  $("runtime-results").hidden = draft;
  $("offline-workspace").hidden = !draft;
  if (draft && !activeJob) $("cancel").hidden = true;
  const browser = ["javascript-browser", "html-browser"].includes(current.runtime_profile);
  const activity = activeJobRecord
    ? " A job for " + activeJobRecord.lesson_id + " is active or awaiting confirmation."
    : legacyRunActive
      ? " A bounded Python or SQL run is active. Wait for its result before running again."
      : "";
  const runtimeId = cap.profile || current.runtime_profile;
  if (!draft && !reading && !cap.ready)
    // Name the runtime by the profile ID that the launcher's --profile option accepts.
    $("capability").replaceChildren(
      ...(runtimeId ? ["The ", node("code", runtimeId), " runtime"] : ["This lesson's runtime"]),
      " is not ready. " + (cap.detail || "") + activity,
    );
  else
    $("capability").textContent =
      (draft
        ? cap.detail
        : reading
          ? "Read the guide and record your reasoning. This lesson needs no code runtime."
          : "Ready to run in your local classroom. " +
            (current.engine === "legacy" ? cap.detail || "" : "")) + activity;
  $("capability").className = "notice" + (!cap.ready && !reading ? " warn" : "");
  $("runtime-setup").hidden =
    cap.ready || reading || draft || (!current.setup_commands?.length && !current.runtime_guidance);
  $("runtime-commands").textContent = (current.setup_commands || []).join("\n\n");
  $("runtime-setup-note").textContent =
    current.engine === "legacy" ? current.runtime_guidance || "" : "";
  $("run").disabled =
    !cap.ready || reading || draft || activeJob !== null || submitInFlight || legacyRunActive;
  $("run").textContent = reading
    ? "Reading and reasoning"
    : legacyRunActive
      ? "Running..."
      : browser
        ? "Run browser preview"
        : "Run code";
  $("run-shortcut").hidden = $("run").hidden || reading || draft;
  $("source-label").textContent = reading ? "Worksheet" : draft ? "Draft" : "Your code";
  $("code-focus-toggle").hidden = browser;
  $("timeout").disabled = reading || browser || legacyRunActive;
  $("timeout").hidden = browser || draft;
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
      allowed.includes(old) ? old : current.effective.timeout_seconds || allowed[0],
    );
  }
}
function resetResult() {
  resultRevision++;
  $("results-title").textContent = "Result";
  $("run-storage-status").textContent = "";
  $("receipt-source-details").hidden = true;
  $("receipt-source").replaceChildren();
  displayedJob = null;
  $("recover").hidden = true;
  $("reconnect").hidden = true;
  $("job-status").textContent = "No run yet. Press Run code to try this lesson.";
  outputNote("Press Run code. What your program prints, and any error messages, appear here.");
  $("raw-output").textContent = "";
  $("raw-log").hidden = true;
  $("raw-log").open = false;
  $("checks").replaceChildren();
  $("sql-results").replaceChildren();
  $("figures").replaceChildren();
  plottedReceiptKey = "";
  $("error-line").hidden = true;
  showRunExplanation(null);
  stopRunTimer();
}
function renderHistory(records) {
  $("history").replaceChildren();
  for (const job of records) {
    const button = node(
      "button",
      (job.purpose === "solution" ? "Worked solution · " : "") +
        (job.created_at || "") +
        " · " +
        job.status +
        " · " +
        (job.source_sha256 || "").slice(0, 10),
    );
    button.addEventListener("click", () => {
      if (job.kind === "browser_observation") {
        stopBrowserPreview("Stopped before viewing a saved observation.");
        updateControls();
      }
      showJob(job);
    });
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
      filename !== "main.py" &&
      !/^\.submission-[A-Za-z0-9_-]{1,64}\.py$/.test(filename)
    )
      continue;
    const candidate = Number(match[2]);
    if (Number.isSafeInteger(candidate) && candidate > 0 && candidate <= lineCount)
      line = candidate;
  }
  return line;
}
function expandedCompilerLine(output, language, lineCount) {
  const names = {
      c: "main.c",
      go: "main.go",
      csharp: "Program.cs",
      rust: "main.rs",
      swift: "main.swift",
      julia: "main.jl",
    },
    filename = names[language];
  if (!filename) return null;
  const escaped = filename.replaceAll(".", "\\."),
    path = "((?:[^\\s()\"'<>]*[\\\\/])?" + escaped + ")",
    prefix = "(?:^|[\\s(\"'<>])",
    location =
      language === "csharp"
        ? "(?:\\((\\d+)(?:,\\d+)?\\)|:line\\s+(\\d+))"
        : ":(\\d+)(?::\\d+)?(?=[:\\s,)]|$)",
    pattern = new RegExp(prefix + path + location, "g");
  const match = [...output.matchAll(pattern)].find((candidate) => {
    const normalized = candidate[1].replaceAll("\\", "/").replace(/^file:\/\//, "");
    // Runtime backtraces can mention a dependency's own main.go/main.rs.
    // Only the submitted filename outside known library/build trees is useful.
    return (
      !/(?:^|\/)(?:node_modules|site-packages|rustlib|registry|library|include|obj|target|deps)(?:\/|$)/i.test(
        normalized,
      ) && !/^\/(?:usr|opt|lib|System)\//.test(normalized)
    );
  });
  if (!match) return null;
  const line = Number(match[2] || match[3]);
  return Number.isSafeInteger(line) && line >= 1 && line <= lineCount ? line : null;
}
// END DIAGNOSTIC PURE HELPERS

function sourceErrorLine(job) {
  if (
    !current ||
    job.lesson_id !== current.id ||
    typeof job.source !== "string" ||
    job.source !== $("source").value ||
    (typeof job.language === "string" && job.language !== current.language)
  )
    return null;
  const output = job.output || "",
    count = $("source").value.split("\n").length;
  if (["c", "go", "csharp", "rust", "swift", "julia"].includes(current.language))
    return expandedCompilerLine(output, current.language, count);
  let matches = [];
  if (job.legacy && current.language === "python") return tracebackLine(output, count);
  if (current.language === "python")
    matches = [
      ...output.matchAll(/(?:^|\n)\s*File\s+["'](?:[^"'\n]*[/\\])?main\.py["'],\s*line\s+(\d+)/g),
    ];
  else if (current.language === "r")
    matches = [...output.matchAll(/(?:^|[\s(])(?:[^\s()]*\/)?main\.R:(\d+)(?::\d+)?:/g)];
  else if (current.language === "stan")
    matches = [
      ...output.matchAll(/(?:^|\n)[^\n]*["'](?:[^"'\n]*\/)?main\.stan["'],\s*line\s+(\d+)/g),
    ];
  else if (current.language === "cpp")
    matches = [...output.matchAll(/(?:^|\n)(?:[^\n]*[/\\])?main\.cpp:(\d+)(?::\d+)?:/g)];
  else if (current.language === "java")
    matches = [
      ...output.matchAll(/(?:^|\n)(?:[^\n]*[/\\])?Main\.java:(\d+):|\(Main\.java:(\d+)\)/g),
    ];
  else if (current.language === "javascript")
    matches = [...output.matchAll(/(?:^|[\s(/])(?:[^\s()]*\/)?main\.mjs:(\d+)/g)];
  else if (current.language === "typescript")
    matches = [...output.matchAll(/(?:^|\n)main\.mts\((\d+),\d+\)/g)];
  else if (current.language === "scala")
    matches = [
      ...output.matchAll(/(?:^|\n)(?:[^\n]*[/\\])?Main\.scala:(\d+):|\(Main\.scala:(\d+)\)/g),
    ];
  if (!matches.length) return null;
  const match = current.language === "python" ? matches[matches.length - 1] : matches[0],
    line = Number(match[1] || match[2]);
  return Number.isInteger(line) && line >= 1 && line <= count ? line : null;
}
function updateErrorJump() {
  const job = displayedJob,
    line = job ? sourceErrorLine(job) : null;
  $("error-line").hidden = line === null;
  if (line === null) return;
  $("error-line").textContent = "Show line " + line + " in the editor";
  $("error-line").onclick = () => {
    const currentLine = sourceErrorLine(job);
    if (currentLine === null) {
      $("error-line").hidden = true;
      status("The source changed. Compare the saved job source before inspecting its diagnostic.");
      return;
    }
    const lines = $("source").value.split("\n"),
      start = lines.slice(0, currentLine - 1).join("\n").length + (currentLine > 1 ? 1 : 0);
    $("source").focus();
    $("source").setSelectionRange(start, start + (lines[currentLine - 1] || "").length);
  };
}
// Plain-language run states. Each keeps the worker's own status word, which the
// result reveal in classroom-shell.js uses to color the state.
const PLAIN_STATUS = {
  queued: "Waiting to start",
  running: "Running",
  succeeded: "Finished",
  failed: "Stopped with an error",
  timed_out: "Stopped at the time limit",
  cancelled: "Cancelled",
  blocked: "Could not start",
  interrupted: "Interrupted",
};
function formatSeconds(value) {
  const seconds = Number(value) || 0;
  return (seconds < 1 ? seconds.toFixed(2) : seconds.toFixed(1)) + " s";
}
function jobStatusText(state, seconds) {
  const raw = String(state || "").replaceAll("_", " "),
    plain = PLAIN_STATUS[state] || raw,
    time = formatSeconds(seconds);
  if (state === "queued" || state === "running") return plain + " · " + raw + " · " + time;
  const word = plain.toLowerCase() === raw ? "" : " · " + raw;
  return plain + word + (state === "succeeded" ? " in " : " after ") + time;
}
const PRINT_EXAMPLES = {
  python: "print(value)",
  javascript: "console.log(value)",
  typescript: "console.log(value)",
  java: "System.out.println(value);",
  c: 'printf("%d\\n", value);',
  cpp: "std::cout << value << '\\n';",
  csharp: "Console.WriteLine(value);",
  go: "fmt.Println(value)",
  rust: 'println!("{value}");',
  swift: "print(value)",
  php: "echo $value;",
  r: "print(value)",
  julia: "println(value)",
  scala: "println(value)",
};
function emptyOutputMessage(succeeded, solution = false) {
  if (solution)
    return succeeded
      ? "The worked solution finished without printing anything. Read its code to see what it computes."
      : "(The worked solution stopped before it printed anything.)";
  if (!succeeded) return "(The program stopped before it printed anything.)";
  if (current?.language === "sql")
    return "The statements ran and returned no rows to show. A SELECT statement shows its rows here.";
  const example = PRINT_EXAMPLES[current?.language];
  return (
    "Your program finished without printing anything." +
    (example ? " To see a value, add a line such as " + example : "")
  );
}
// `Backticks` in an explanation mark code; each part stays plain text.
function explanationText(tag, text, cls) {
  const element = node(tag, undefined, cls);
  String(text)
    .split("`")
    .forEach((part, index) => {
      if (part) element.append(index % 2 ? node("code", part) : document.createTextNode(part));
    });
  return element;
}
function showRunExplanation(explanation, job = null) {
  const box = $("run-explanation"),
    editor = globalThis.DS60SourceEditor;
  box.replaceChildren();
  editor?.markErrorLine?.(null);
  if (!explanation || typeof explanation.title !== "string" || !explanation.title) {
    box.hidden = true;
    return;
  }
  box.dataset.kind = typeof explanation.kind === "string" ? explanation.kind : "unknown";
  box.append(explanationText("p", explanation.title, "run-explanation-title"));
  if (typeof explanation.hint === "string" && explanation.hint)
    box.append(explanationText("p", explanation.hint, "run-explanation-hint"));
  if (typeof explanation.raw === "string" && explanation.raw)
    box.append(node("code", explanation.raw, "run-explanation-raw"));
  const line = Number.isInteger(explanation.line) && explanation.line > 0 ? explanation.line : null;
  if (line && typeof job?.source === "string" && job.source === $("source").value) {
    const column = Number.isInteger(explanation.column) ? explanation.column : 1,
      button = node("button", "Show line " + line + " in the editor");
    button.type = "button";
    button.addEventListener("click", () => {
      if (job.source !== $("source").value) {
        status(
          "The code changed after this run, so line " +
            line +
            " may point somewhere else. Run again for a fresh explanation.",
        );
        return;
      }
      if (editor?.goToLine?.(line, column)) return;
      const lines = $("source").value.split("\n"),
        start = lines.slice(0, line - 1).join("\n").length + (line > 1 ? 1 : 0);
      $("source").focus();
      $("source").setSelectionRange(start, start + (lines[line - 1] || "").length);
    });
    box.append(button);
    editor?.markErrorLine?.(line);
    $("error-line").hidden = true;
  }
  box.hidden = false;
}
function startRunTimer() {
  stopRunTimer();
  const started = Date.now(),
    tick = () => {
      $("run-timer").textContent = ((Date.now() - started) / 1000).toFixed(1) + " s";
      runTimer = setTimeout(tick, 250);
    };
  tick();
}
function outputNote(text) {
  $("output").textContent = text;
  $("output").dataset.note = "true";
}
function programOutput(text) {
  $("output").textContent = text;
  delete $("output").dataset.note;
}
function stopRunTimer() {
  clearTimeout(runTimer);
  runTimer = null;
  $("run-timer").textContent = "";
}
async function copyText(text, button, done = "Copied") {
  try {
    await navigator.clipboard.writeText(text);
    const label = button.textContent;
    button.textContent = done;
    setTimeout(() => {
      button.textContent = label;
    }, 1400);
  } catch (_) {
    status(
      "This browser blocked copying. Select the text and press Ctrl+C (Cmd+C on a Mac).",
      true,
    );
  }
}
function editorLanguage(...names) {
  const resolve = globalThis.DS60Editor?.resolveLanguage;
  for (const name of names)
    if (typeof name === "string" && name) {
      const key = typeof resolve === "function" ? resolve(name) : name.toLowerCase();
      if (key) return key;
    }
  return null;
}
// The level badge already names the level; a guide line that only repeats it is hidden.
function hideRepeatedLevel() {
  for (const paragraph of $("guide").querySelectorAll(":scope > p"))
    if (/^Level:\s*(?:beginner|intermediate|advanced)\.?$/i.test(paragraph.textContent.trim()))
      paragraph.hidden = true;
}
// Guide examples get Copy, and Try in editor when the example is in the pad's language.
function enhanceGuideCode() {
  const runnable =
    current &&
    current.runtime_profile !== "reading" &&
    current.execution_mode !== "draft" &&
    !(current.engine === "legacy" && current.mode === "lesson");
  const padLanguage = runnable
    ? editorLanguage(
        current.runtime_profile === "dbt-duckdb" ? "sql" : null,
        current.runner?.id,
        current.language,
        current.runtime_profile,
      )
    : null;
  for (const pre of $("guide").querySelectorAll("pre")) {
    const code = pre.querySelector("code");
    if (!code || pre.parentElement?.classList.contains("code-block")) continue;
    const block = node("div", undefined, "code-block"),
      tools = node("div", undefined, "code-tools"),
      copy = node("button", "Copy");
    copy.type = "button";
    copy.setAttribute("aria-label", "Copy this example");
    copy.addEventListener("click", () => copyText(code.textContent || "", copy));
    tools.append(copy);
    const language = (String(code.className).match(/language-([\w+#.-]+)/) || [])[1];
    if (padLanguage && language && editorLanguage(language) === padLanguage) {
      const tryIt = node("button", "Try in editor");
      tryIt.type = "button";
      tryIt.setAttribute("aria-label", "Try in editor: put this example in the code editor");
      tryIt.addEventListener("click", () => tryExample(code.textContent || ""));
      tools.append(tryIt);
    }
    pre.replaceWith(block);
    block.append(pre, tools);
  }
}
async function tryExample(text) {
  if (!current || $("source").disabled) return;
  const intent = selectedViewIntent();
  if (
    !confirm(
      "Replace the code in the editor with this example? Your current code is saved first. " +
        "To bring it back, press Ctrl+Z (Cmd+Z on a Mac) in the editor" +
        (current.engine === "legacy" ? " or use Recover an earlier saved pad." : "."),
    )
  )
    return;
  try {
    await flushSave();
    if (!sameView(intent)) return;
    replaceSource(text.replace(/\s+$/, "") + "\n");
    resetResult();
    status("The example is in the editor. Press Run code to try it, then change one thing.");
    $("pad-title").scrollIntoView({ block: "start" });
  } catch (error) {
    status(error.message, true);
  }
}
// A learner-chosen replacement of the whole editor text. The code editor records
// it as one undoable step; the plain text area falls back to a direct write.
function replaceSource(text) {
  const editor = globalThis.DS60SourceEditor;
  if (typeof editor?.replace === "function") return editor.replace(text) !== false;
  if ($("source").value === text) return false;
  $("source").value = text;
  markDirty();
  return true;
}

// Exercises: the lesson's problems beside the editor, with progressive hints,
// worked solutions behind an explicit choice, a solution run that never changes
// the learner's code, and a line-by-line comparison with the learner's code.
const exercise = {
  lesson: "",
  list: [],
  steps: [],
  index: 0,
  reference: false,
  solutions: new Map(),
  programs: null,
  view: null,
  confirming: null,
  comparing: false,
  undo: null,
  sequence: 0,
};
function exerciseProgress() {
  const value = pref("exercises." + exercise.lesson, {});
  return value && typeof value === "object" && !Array.isArray(value) ? value : {};
}
function exerciseState(number) {
  const value = exerciseProgress()[number];
  return value && typeof value === "object" ? value : {};
}
function updateExerciseProgress(change) {
  remember("exercises." + exercise.lesson, { ...exerciseProgress(), ...change });
}
function updateExerciseState(number, change) {
  updateExerciseProgress({ [number]: { ...exerciseState(number), ...change } });
}
function padLanguage() {
  if (!current || current.runtime_profile === "reading" || current.execution_mode === "draft")
    return null;
  return editorLanguage(
    current.runtime_profile === "dbt-duckdb" ? "sql" : null,
    current.runner?.id,
    current.language,
    current.runtime_profile,
  );
}
function sqlLessonMode() {
  return current?.engine === "legacy" && current.mode === "lesson";
}
function canEditSource() {
  return Boolean(current) && !$("source").disabled && !sqlLessonMode() && padLanguage() !== null;
}
function solutionBlocks(view) {
  const language = padLanguage();
  if (!language || !view) return [];
  return view.code.filter(
    (block) =>
      block &&
      typeof block.text === "string" &&
      block.text.trim() &&
      editorLanguage(block.language) === language,
  );
}
function solutionCode(view) {
  const blocks = solutionBlocks(view);
  return blocks.length
    ? blocks.map((block) => block.text.replace(/\s+$/, "")).join("\n\n") + "\n"
    : "";
}
function solutionIsStandalone(view) {
  const blocks = solutionBlocks(view);
  if (!blocks.length) return false;
  if (typeof view.joined_standalone === "boolean") return view.joined_standalone;
  return blocks.every((block) => block.standalone === true);
}
function canRunSolution(view) {
  return (
    solutionIsStandalone(view) &&
    Boolean(current?.capability?.ready) &&
    !isBrowserLesson() &&
    current.execution_mode !== "draft"
  );
}
function exerciseTitle(item) {
  const title = typeof item.title === "string" ? item.title.trim() : "";
  return (
    "Exercise " + item.number + (title && title !== "Exercise " + item.number ? ": " + title : "")
  );
}
async function loadExercises() {
  const sequence = ++exercise.sequence,
    data = current,
    intent = selectedViewIntent();
  exercise.lesson = data?.id || "";
  exercise.list = [];
  exercise.steps = [];
  exercise.reference = false;
  exercise.solutions = new Map();
  exercise.programs = null;
  exercise.view = null;
  exercise.undo = null;
  closeExerciseConfirm();
  $("exercise-dock").hidden = true;
  $("exercise-solution").hidden = true;
  $("exercise-reference").hidden = true;
  $("exercise-status").replaceChildren();
  if (!data) return;
  try {
    const result = await classroom("classroom-exercises", { lesson_id: data.id });
    if (sequence !== exercise.sequence || !sameView(intent)) return;
    exercise.list = (Array.isArray(result.exercises) ? result.exercises : []).filter(
      (item) => item && Number.isInteger(item.number) && typeof item.prompt_html === "string",
    );
    exercise.reference = result.reference_program === true;
    if (!exercise.list.length) return;
    const intro = typeof result.intro_html === "string" ? result.intro_html.trim() : "";
    $("exercise-intro-html").innerHTML = intro;
    $("exercise-intro").hidden = !intro;
    $("exercise-intro").open = false;
    const saved = exerciseProgress().current,
      position = exercise.list.findIndex((item) => item.number === saved);
    exercise.index = position >= 0 ? position : 0;
    buildExerciseSteps();
    $("exercise-dock").hidden = false;
    setExerciseCollapsed(pref("exercises.collapsed", false) === true);
    renderExercise();
    linkGuideExercises();
  } catch (_) {
    // The chapter still lists every exercise; the panel simply stays hidden.
  }
}
function buildExerciseSteps() {
  exercise.steps = exercise.list.map((item, position) => {
    const button = node("button", String(item.number), "exercise-step");
    button.type = "button";
    button.addEventListener("click", () => selectExercise(position));
    return button;
  });
  $("exercise-steps").replaceChildren(
    ...exercise.steps.map((button) => {
      const entry = node("li");
      entry.append(button);
      return entry;
    }),
  );
}
function updateExerciseSteps() {
  const progress = exerciseProgress();
  let solved = 0;
  exercise.list.forEach((item, position) => {
    const state = progress[item.number] || {},
      button = exercise.steps[position];
    if (state.solved) solved++;
    if (!button) return;
    button.dataset.state = state.solved ? "solved" : "";
    button.setAttribute(
      "aria-label",
      exerciseTitle(item) + (state.solved ? ", solved" : state.seen ? ", solution viewed" : ""),
    );
    if (position === exercise.index) button.setAttribute("aria-current", "step");
    else button.removeAttribute("aria-current");
  });
  $("exercise-progress").textContent = solved + " of " + exercise.list.length + " solved";
  $("exercise-prev").disabled = exercise.index === 0;
  $("exercise-next").disabled = exercise.index >= exercise.list.length - 1;
}
function fillExerciseFacts(list, details) {
  list.replaceChildren();
  for (const detail of details) {
    const value = node("dd");
    value.innerHTML = detail.html;
    list.append(node("dt", detail.label), value);
  }
  list.hidden = !details.length;
}
function renderExerciseHints(item) {
  const hints = (Array.isArray(item.hints) ? item.hints : []).filter(
      (hint) => typeof hint === "string" && hint,
    ),
    shown = Math.min(Number(exerciseState(item.number).hints) || 0, hints.length),
    button = $("exercise-hint");
  $("exercise-hints").replaceChildren();
  hints.slice(0, shown).forEach((hint, position) => {
    const entry = node("li"),
      body = node("div", undefined, "guide exercise-text");
    body.innerHTML = hint;
    entry.append(
      node(
        "span",
        (item.hints_shared === true ? "Lesson hint " : "Hint ") + (position + 1),
        "exercise-hint-label",
      ),
      body,
    );
    $("exercise-hints").append(entry);
  });
  $("exercise-hints").hidden = !shown;
  button.hidden = !hints.length;
  button.disabled = shown >= hints.length;
  button.textContent =
    shown >= hints.length
      ? hints.length === 1
        ? "Hint shown"
        : "All hints shown"
      : shown === 0
        ? hints.length === 1
          ? "Show a hint"
          : "Show a hint (1 of " + hints.length + ")"
        : "Show the next hint (" + (shown + 1) + " of " + hints.length + ")";
}
function updateExerciseDone(item) {
  const solved = exerciseState(item.number).solved === true;
  $("exercise-done").setAttribute("aria-pressed", solved ? "true" : "false");
  $("exercise-done").textContent = solved ? "Solved" : "Mark as solved";
}
function renderExercise() {
  const item = exercise.list[exercise.index];
  if (!item) return;
  updateExerciseSteps();
  $("exercise-title").textContent = exerciseTitle(item);
  $("exercise-prompt").innerHTML = item.prompt_html;
  const facts = [],
    checks = [];
  for (const detail of Array.isArray(item.details) ? item.details : [])
    if (detail && typeof detail.label === "string" && typeof detail.html === "string")
      (/verif|check/i.test(detail.label) ? checks : facts).push(detail);
  fillExerciseFacts($("exercise-facts"), facts);
  fillExerciseFacts($("exercise-check-facts"), checks);
  $("exercise-check").hidden = !checks.length;
  $("exercise-check").open = false;
  $("exercise-mode-note").hidden = !sqlLessonMode();
  renderExerciseHints(item);
  $("exercise-solve").hidden = item.has_solution !== true;
  updateExerciseDone(item);
  closeExerciseConfirm();
  if (exercise.view?.kind === "exercise") hideExerciseSolution(false);
  $("exercise-reference").hidden = !exercise.reference || exercise.view?.kind === "reference";
}
function selectExercise(position, { focusStep = false } = {}) {
  if (position < 0 || position >= exercise.list.length || position === exercise.index) return;
  exercise.index = position;
  exercise.undo = null;
  updateExerciseProgress({ current: exercise.list[position].number });
  renderExercise();
  $("exercise-status").textContent =
    "Showing exercise " + (position + 1) + " of " + exercise.list.length + ".";
  if (focusStep) exercise.steps[position]?.focus();
}
function setExerciseCollapsed(collapsed) {
  $("exercise-body").hidden = collapsed;
  $("exercise-dock").dataset.collapsed = collapsed ? "true" : "false";
  $("exercise-collapse").setAttribute("aria-expanded", collapsed ? "false" : "true");
  $("exercise-collapse").textContent = collapsed ? "Show" : "Hide";
}
function openExerciseConfirm(kind) {
  exercise.confirming = kind;
  $("exercise-confirm-yes").textContent =
    kind === "reference" ? "Show the reference program" : "Show the solution";
  $("exercise-confirm").hidden = false;
  $("exercise-confirm-yes").focus();
}
function closeExerciseConfirm() {
  exercise.confirming = null;
  $("exercise-confirm").hidden = true;
}
function openSolutionView(view) {
  exercise.view = view;
  exercise.comparing = false;
  $("exercise-solution-title").textContent = view.title;
  const container = $("exercise-solution-html");
  if (view.html) {
    container.innerHTML = view.html;
    // The panel already shows the problem; a restated "Prompt:" paragraph is dropped.
    const first = container.firstElementChild;
    if (
      first?.tagName === "P" &&
      first.firstElementChild?.tagName === "STRONG" &&
      /^prompt:?$/i.test(first.firstElementChild.textContent.trim())
    )
      first.remove();
    enhanceCodeBlocks(container);
  } else {
    container.replaceChildren();
    for (const block of view.code) {
      const listing = highlightedSourceBlock(block.text),
        language = typeof block.language === "string" ? block.language : "text";
      container.append(listing.pre);
      classroom("classroom-highlight", { source: block.text, language })
        .then((data) => {
          if (exercise.view === view) listing.code.innerHTML = data.html;
        })
        .catch(() => {});
    }
  }
  const code = solutionCode(view);
  $("exercise-run-solution").hidden = !canRunSolution(view);
  $("exercise-compare").hidden = !code || sqlLessonMode();
  $("exercise-use-solution").hidden = !code || !canEditSource();
  $("exercise-compare").setAttribute("aria-pressed", "false");
  $("exercise-diff").replaceChildren();
  $("exercise-diff").hidden = true;
  $("exercise-solution-note").textContent = solutionNote(view, code);
  $("exercise-solution").hidden = false;
  $("exercise-reference").hidden = view.kind === "reference" || !exercise.reference;
  $("exercise-solution-title").focus();
}
function solutionNote(view, code) {
  const source = view.kind === "reference" && view.path ? "From " + view.path + ". " : "";
  if (!code) return source;
  if (solutionIsStandalone(view) && !canRunSolution(view) && !isBrowserLesson())
    return source + "Run the solution becomes available when this lesson's runtime is ready.";
  if (!solutionIsStandalone(view))
    return (
      source +
      "This answer builds on code from the lesson, so it does not run on its own. Compare it with your code, or put it in your editor next to the rest of the program."
    );
  return source;
}
function hideExerciseSolution(focus = true) {
  const kind = exercise.view?.kind;
  exercise.view = null;
  exercise.comparing = false;
  $("exercise-solution").hidden = true;
  $("exercise-solution-html").replaceChildren();
  $("exercise-diff").replaceChildren();
  $("exercise-diff").hidden = true;
  $("exercise-reference").hidden = !exercise.reference;
  if (focus) (kind === "reference" ? $("exercise-reference-show") : $("exercise-solve")).focus();
}
async function showExerciseSolution(item) {
  const lesson = exercise.lesson,
    intent = selectedViewIntent();
  $("exercise-solve").disabled = true;
  try {
    let data = exercise.solutions.get(item.number);
    if (!data) {
      data = await classroom("classroom-exercise-solution", {
        lesson_id: lesson,
        number: item.number,
        reveal: true,
      });
      exercise.solutions.set(item.number, data);
    }
    if (
      !sameView(intent) ||
      exercise.lesson !== lesson ||
      exercise.list[exercise.index]?.number !== item.number
    )
      return;
    openSolutionView({
      kind: "exercise",
      number: item.number,
      title: "Worked solution for exercise " + item.number,
      html: typeof data.html === "string" ? data.html : "",
      code: Array.isArray(data.code) ? data.code : [],
      joined_standalone: data.joined_standalone,
    });
  } catch (error) {
    if (sameView(intent))
      $("exercise-status").textContent = "The solution could not be opened. " + error.message;
  } finally {
    $("exercise-solve").disabled = false;
  }
}
async function showReferenceProgram() {
  const lesson = exercise.lesson,
    intent = selectedViewIntent();
  $("exercise-reference-show").disabled = true;
  try {
    if (!exercise.programs) {
      const data = await classroom("classroom-reference-program", {
        lesson_id: lesson,
        reveal: true,
      });
      exercise.programs = (Array.isArray(data.programs) ? data.programs : []).filter(
        (program) => program && typeof program.text === "string" && program.text.trim(),
      );
    }
    if (!sameView(intent) || exercise.lesson !== lesson) return;
    updateExerciseProgress({ reference_seen: true });
    const language = padLanguage(),
      program =
        exercise.programs.find((item) => editorLanguage(item.language) === language) ||
        exercise.programs[0];
    if (!program) {
      $("exercise-status").textContent = "This lesson has no separate reference program.";
      return;
    }
    openSolutionView({
      kind: "reference",
      title: "Reference program",
      path: typeof program.path === "string" ? program.path : "",
      html: "",
      code: [program],
      joined_standalone: program.standalone === true,
    });
  } catch (error) {
    if (sameView(intent))
      $("exercise-status").textContent =
        "The reference program could not be opened. " + error.message;
  } finally {
    $("exercise-reference-show").disabled = false;
  }
}
// Copy buttons on code blocks inside rendered solution text.
function enhanceCodeBlocks(container) {
  for (const pre of container.querySelectorAll("pre")) {
    const code = pre.querySelector("code");
    if (!code || pre.parentElement?.classList.contains("code-block")) continue;
    const block = node("div", undefined, "code-block"),
      tools = node("div", undefined, "code-tools"),
      copy = node("button", "Copy");
    copy.type = "button";
    copy.setAttribute("aria-label", "Copy this code");
    copy.addEventListener("click", () => copyText(code.textContent || "", copy));
    tools.append(copy);
    pre.replaceWith(block);
    block.append(pre, tools);
  }
}
// BEGIN EXERCISE COMPARISON HELPERS
// Lines are compared without trailing spaces, runs of spaces or blank lines, so
// a learner sees differences in meaning rather than in layout.
function lineDiff(mine, theirs, limit = 250000) {
  const lines = (text) =>
      String(text)
        .split("\n")
        .map((line) => line.replace(/\s+$/, ""))
        .filter((line) => line.trim()),
    a = lines(mine),
    b = lines(theirs),
    key = (line) => line.trim().replace(/\s+/g, " "),
    ka = a.map(key),
    kb = b.map(key);
  if (a.length * b.length > limit) return null;
  const width = b.length + 1,
    table = new Uint32Array((a.length + 1) * width);
  for (let i = a.length - 1; i >= 0; i--)
    for (let j = b.length - 1; j >= 0; j--)
      table[i * width + j] =
        ka[i] === kb[j]
          ? table[(i + 1) * width + j + 1] + 1
          : Math.max(table[(i + 1) * width + j], table[i * width + j + 1]);
  const steps = [];
  let i = 0,
    j = 0;
  while (i < a.length && j < b.length) {
    if (ka[i] === kb[j]) {
      steps.push({ kind: "same", text: b[j] });
      i++;
      j++;
    } else if (table[(i + 1) * width + j] >= table[i * width + j + 1])
      steps.push({ kind: "mine", text: a[i++] });
    else steps.push({ kind: "solution", text: b[j++] });
  }
  while (i < a.length) steps.push({ kind: "mine", text: a[i++] });
  while (j < b.length) steps.push({ kind: "solution", text: b[j++] });
  return steps;
}
// Long runs of matching lines fold to a count, keeping two lines of context.
function foldedDiff(steps, context = 2) {
  const rows = [];
  let start = 0;
  while (start < steps.length) {
    if (steps[start].kind !== "same") {
      rows.push(steps[start++]);
      continue;
    }
    let end = start;
    while (end < steps.length && steps[end].kind === "same") end++;
    const lead = start === 0 ? 0 : context,
      tail = end === steps.length ? 0 : context;
    if (end - start > lead + tail + 1) {
      rows.push(...steps.slice(start, start + lead));
      rows.push({ kind: "skip", count: end - start - lead - tail });
      rows.push(...steps.slice(end - tail, end));
    } else rows.push(...steps.slice(start, end));
    start = end;
  }
  return rows;
}
// END EXERCISE COMPARISON HELPERS
function diffSummary(steps) {
  const count = { same: 0, mine: 0, solution: 0 };
  for (const step of steps) count[step.kind]++;
  if (!count.mine && !count.solution)
    return "Your code matches the solution line for line. Spacing and blank lines are ignored.";
  const plural = (n, word) => n + " " + word + (n === 1 ? "" : "s"),
    verb = (n, one, many) => (n === 1 ? one : many);
  return (
    plural(count.same, "line") +
    verb(count.same, " matches. ", " match. ") +
    (count.mine
      ? plural(count.mine, "line") +
        " marked Yours " +
        verb(count.mine, "appears", "appear") +
        " only in your code. "
      : "") +
    (count.solution
      ? plural(count.solution, "line") +
        " marked Solution " +
        verb(count.solution, "appears", "appear") +
        " only in the solution. "
      : "") +
    "Different does not mean wrong: compare what each version does."
  );
}
function renderExerciseDiff() {
  const view = exercise.view,
    container = $("exercise-diff"),
    mine = $("source").value;
  container.replaceChildren();
  if (!mine.trim()) {
    container.append(
      node(
        "p",
        "Your editor is empty, so there is nothing to compare yet. Write your attempt first.",
        "exercise-diff-summary",
      ),
    );
    return;
  }
  const steps = lineDiff(mine, solutionCode(view));
  if (steps === null) {
    container.append(
      node(
        "p",
        "These are too long to compare here. Copy the solution and compare the parts you are working on.",
        "exercise-diff-summary",
      ),
    );
    return;
  }
  container.append(node("p", diffSummary(steps), "exercise-diff-summary"));
  const list = node("ol", undefined, "exercise-diff-lines");
  list.setAttribute("aria-label", "Your code compared with the solution");
  for (const row of foldedDiff(steps)) {
    const entry = node("li");
    entry.dataset.kind = row.kind;
    if (row.kind === "skip") entry.textContent = "  " + row.count + " matching lines";
    else
      entry.append(
        node(
          "span",
          row.kind === "mine" ? "Yours" : row.kind === "solution" ? "Solution" : "",
          "exercise-diff-tag",
        ),
        node("code", row.text),
      );
    list.append(entry);
  }
  container.append(list);
}
async function runSolution() {
  const view = exercise.view,
    code = solutionCode(view);
  if (!view || !code || !canRunSolution(view) || activeJob || submitInFlight || legacyRunActive)
    return;
  submitInFlight = true;
  updateControls();
  const context = contextOf(),
    timeout = Number($("timeout").value) || 60;
  try {
    if (context.engine === "legacy") {
      legacyRunActive = true;
      updateControls();
      resetResult();
      $("results-title").textContent = "Result of the worked solution";
      outputNote("Running the worked solution. Your code is not changed.");
      startRunTimer();
      try {
        const result = await lab(
          "run",
          {
            lesson_id: context.id,
            language: context.language,
            mode: "snippet",
            code,
            timeout_seconds: timeout,
            purpose: "solution",
          },
          false,
        );
        showLegacyResult(result, { ...context, mode: "snippet" }, code);
      } finally {
        legacyRunActive = false;
        stopRunTimer();
      }
    } else {
      startRunTimer();
      const job = await api("module-run", {
        lesson_id: context.id,
        source: code,
        timeout_seconds: timeout,
        request_id: crypto.randomUUID().replaceAll("-", ""),
        purpose: "solution",
      });
      if (current?.id === job.lesson_id) showJob(job);
      if (!adoptJob(job)) updateControls();
    }
    $("exercise-status").textContent =
      "The solution's output is in the Result below. Your code was not changed.";
  } catch (error) {
    if (!activeJob) stopRunTimer();
    status(error.message, true);
  } finally {
    submitInFlight = false;
    updateControls();
  }
}
async function useSolutionCode() {
  const view = exercise.view,
    code = solutionCode(view);
  if (!view || !code || !canEditSource()) return;
  const intent = selectedViewIntent();
  try {
    await flushSave();
  } catch (error) {
    $("exercise-status").textContent = error.message;
    return;
  }
  if (!sameView(intent) || exercise.view !== view) return;
  const previous = $("source").value;
  if (!replaceSource(code)) {
    $("exercise-status").textContent = "Your editor already holds this code.";
    return;
  }
  exercise.undo = { previous, replaced: $("source").value };
  const undo = node("button", "Undo", "quiet");
  undo.type = "button";
  undo.addEventListener("click", () => {
    if (!exercise.undo) return;
    const { previous: restored } = exercise.undo;
    exercise.undo = null;
    replaceSource(restored);
    $("exercise-status").textContent = "Your previous code is back in the editor.";
    globalThis.DS60SourceEditor?.focus?.();
  });
  $("exercise-status").replaceChildren(
    node(
      "span",
      (view.kind === "reference" ? "The reference program" : "The solution") +
        " is in your editor. Run it, then change one thing and predict what happens. " +
        "To bring your code back, press Undo or Ctrl+Z (Cmd+Z on a Mac) in the editor.",
    ),
    undo,
  );
  $("source-section").scrollIntoView({ block: "nearest" });
}
// One quiet link from the chapter's exercise section to the panel on the code page.
function linkGuideExercises() {
  for (const heading of $("guide").querySelectorAll("h3, h4, h5")) {
    if (!/^\s*(exercises|practice)\b/i.test(heading.textContent || "")) continue;
    const button = node("button", "Work through these in the code pad", "exercise-jump");
    button.type = "button";
    button.addEventListener("click", () => {
      if (readingFocused) setReadingView(false);
      setExerciseCollapsed(false);
      remember("exercises.collapsed", false);
      $("exercise-dock").scrollIntoView({ block: "start" });
      $("exercise-title").focus({ preventScroll: true });
    });
    heading.insertAdjacentElement("afterend", button);
    return;
  }
}
let plottedReceiptKey = "";
// BEGIN SAVED FIGURE DOWNLOAD HELPERS
function showWithheldArtifacts(records) {
  if (!Array.isArray(records) || records.length > 2) return;
  let bytes = 0;
  const positions = new Set();
  for (const record of records) {
    if (
      !record ||
      !Number.isInteger(record.position) ||
      record.position < 1 ||
      record.position > 2 ||
      positions.has(record.position) ||
      typeof record.reason !== "string" ||
      !record.reason ||
      record.reason.length > 1000 ||
      typeof record.raw_json !== "string"
    )
      return;
    const size = new TextEncoder().encode(record.raw_json).length;
    if (size > 180000) return;
    bytes += size;
    positions.add(record.position);
  }
  if (bytes > 384000) return;
  for (const record of records) {
    const figure = node("figure", undefined, "withheld-figure");
    figure.dataset.savedArtifactPosition = String(record.position);
    figure.append(
      node("figcaption", "Saved figure " + record.position + ": original JSON retained"),
      node("p", record.reason),
    );
    const download = node("button", "Download original figure JSON", "quiet");
    download.type = "button";
    download.addEventListener("click", () => {
      // This is server-preserved text, never JSON.parse/JSON.stringify input.
      // Parsing first would round the exact historical integer literals.
      const url = URL.createObjectURL(new Blob([record.raw_json], { type: "application/json" }));
      const link = node("a");
      link.href = url;
      link.download = "saved-figure-" + record.position + ".json";
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
    figure.append(download);
    $("figures").append(figure);
  }
}
// END SAVED FIGURE DOWNLOAD HELPERS

function showPlotArtifacts(artifacts, key, append = false, withheld = []) {
  if (plottedReceiptKey === key) return;
  plottedReceiptKey = key;
  if (!append) $("figures").replaceChildren();
  const withheldPositions = new Set(
    (Array.isArray(withheld) ? withheld : [])
      .filter(
        (item) =>
          item && Number.isInteger(item.position) && item.position >= 1 && item.position <= 2,
      )
      .map((item) => item.position),
  );
  const visiblePositions = [1, 2].filter((position) => !withheldPositions.has(position));
  for (const [position, artifact] of (artifacts || []).entries()) {
    const originalPosition = visiblePositions[position] || position + 1;
    const figure = node("figure"),
      title = artifact.description || "Figure " + originalPosition;
    figure.dataset.savedArtifactPosition = String(originalPosition);
    figure.append(node("figcaption", title));
    if (artifact.kind === "png") {
      const img = node("img");
      img.src = "data:image/png;base64," + artifact.data;
      img.alt = title;
      figure.append(img);
    } else if (artifact.kind === "plotly") {
      const frame = node("iframe"),
        note = node("p", "Loading saved chart...", "muted");
      frame.title = title;
      frame.className = "saved-plot";
      frame.setAttribute("sandbox", "allow-scripts allow-downloads");
      frame.src = "/plot-sandbox";
      frame.addEventListener(
        "load",
        () => {
          if (!frame.isConnected) return;
          const channel = new MessageChannel();
          const timer = setTimeout(() => {
            if (frame.isConnected)
              note.textContent =
                "Chart is taking longer to render. The saved source and table remain available.";
            channel.port1.close();
          }, 20000);
          channel.port1.onmessage = (event) => {
            if (!frame.isConnected) {
              clearTimeout(timer);
              channel.port1.close();
              return;
            }
            if (event.data?.type === "ready") {
              note.textContent = "Saved chart. Hover, zoom or select from its controls.";
              clearTimeout(timer);
              channel.port1.close();
            } else if (event.data?.type === "error") {
              note.textContent = "Chart rendering failed: " + event.data.message;
              clearTimeout(timer);
              channel.port1.close();
            }
          };
          channel.port1.start();
          frame.contentWindow.postMessage(
            { type: "ds60-plot-connect", figure: artifact.figure },
            "*",
            [channel.port2],
          );
        },
        { once: true },
      );
      figure.append(frame, note);
      const download = node("button", "Download figure JSON", "quiet");
      download.type = "button";
      download.addEventListener("click", () => {
        const url = URL.createObjectURL(
          new Blob([JSON.stringify(artifact.figure, null, 2)], { type: "application/json" }),
        );
        const link = node("a");
        link.href = url;
        link.download = "figure-" + originalPosition + ".json";
        document.body.append(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
      });
      figure.append(download);
      if (artifact.table) {
        const table = node("table"),
          head = node("thead"),
          row = node("tr"),
          body = node("tbody");
        table.append(node("caption", "Data for " + title));
        for (const label of artifact.table.columns) {
          const cell = node("th", label);
          cell.scope = "col";
          row.append(cell);
        }
        head.append(row);
        table.append(head);
        for (const values of artifact.table.rows) {
          const line = node("tr");
          for (const value of values)
            line.append(node("td", value === null ? "Missing" : String(value)));
          body.append(line);
        }
        table.append(body);
        const details = node("details");
        details.append(node("summary", "Accessible data table"), table);
        figure.append(details);
      }
    }
    if (artifact.kind === "table" || artifact.kind === "json") {
      const data = artifact.kind === "table" ? artifact.table : artifact.data;
      if (artifact.kind === "table") {
        const table = node("table"),
          head = node("thead"),
          row = node("tr"),
          body = node("tbody");
        table.append(node("caption", title, "sr-only"));
        for (const label of data.columns) {
          const cell = node("th", label);
          cell.scope = "col";
          row.append(cell);
        }
        head.append(row);
        table.append(head);
        for (const values of data.rows) {
          const line = node("tr");
          for (const value of values)
            line.append(node("td", value === null ? "Missing" : String(value)));
          body.append(line);
        }
        table.append(body);
        const container = node("div", "", "structured-table");
        container.append(table);
        figure.append(container);
      } else {
        const pre = node("pre"),
          code = node("code", JSON.stringify(data, null, 2));
        pre.className = "highlighted-code language-json";
        pre.append(code);
        figure.append(pre);
        if (new TextEncoder().encode(code.textContent).length <= 60000)
          classroom("classroom-highlight", { source: code.textContent, language: "json" })
            .then((result) => {
              if (plottedReceiptKey === key && code.isConnected) code.innerHTML = result.html;
            })
            .catch(() => {});
      }
      const download = node("button", "Download result JSON", "quiet");
      download.type = "button";
      download.addEventListener("click", () => {
        const url = URL.createObjectURL(
          new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }),
        );
        const link = node("a");
        link.href = url;
        link.download = "result-" + originalPosition + ".json";
        document.body.append(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
      });
      figure.append(download);
    }
    $("figures").append(figure);
  }
  showWithheldArtifacts(withheld);
  const ordered = [...$("figures").children]
    .filter((figure) => figure.dataset.savedArtifactPosition)
    .sort(
      (left, right) =>
        Number(left.dataset.savedArtifactPosition) - Number(right.dataset.savedArtifactPosition),
    );
  for (const figure of ordered) $("figures").append(figure);
}
const SOLUTION_JOB_NOTE =
  "This output comes from the worked solution. Your code and saved draft were not changed.";
function showJob(job) {
  if (job.kind === "browser_observation") {
    showBrowserObservation(job);
    return;
  }
  if (!current || current.id !== job.lesson_id) return;
  displayedJob = job;
  const canReconnect = !finished.has(job.status),
    otherActive = activeJob && activeJob !== job.job_id;
  $("reconnect").hidden = !canReconnect;
  $("reconnect").disabled = !!otherActive;
  $("reconnect").textContent = otherActive ? "Another job is active" : "Reconnect saved job";
  $("reconnect").onclick = () => {
    if (adoptJob(job, false)) {
      monitorPaused = false;
      poll();
    }
  };
  $("recover").hidden = job.status !== "interrupted";
  $("recover").disabled = !!otherActive;
  $("recover").onclick = () => recoverInterrupted(job);
  const solution = job.purpose === "solution";
  $("results-title").textContent = solution ? "Result of the worked solution" : "Result";
  $("job-status").textContent =
    (solution ? "Worked solution · " : "") +
    jobStatusText(job.status, Number(job.elapsed_seconds || 0)) +
    (job.detail ? " · " + job.detail : "") +
    (job.truncated ? " · Log truncated; exit status and checks remain explicit." : "");
  $("run-storage-status").textContent = solution
    ? SOLUTION_JOB_NOTE
    : $("run-storage-status").textContent === SOLUTION_JOB_NOTE
      ? ""
      : $("run-storage-status").textContent;
  if (job.output) programOutput(job.output);
  else
    outputNote(
      finished.has(job.status)
        ? emptyOutputMessage(job.status === "succeeded", solution)
        : "(No output yet.)",
    );
  if (finished.has(job.status) || job.status === "interrupted") stopRunTimer();
  // The Result shows the program's own output; the unfiltered log stays one click away.
  const raw =
    typeof job.raw_output === "string" && job.raw_output.trim() && job.raw_output !== job.output
      ? job.raw_output
      : "";
  $("raw-output").textContent = raw;
  $("raw-log").hidden = !raw;
  if (!raw) $("raw-log").open = false;
  showPlotArtifacts(
    job.artifacts || [],
    job.job_id + ":" + JSON.stringify([job.artifacts || [], job.withheld_artifacts || []]),
    false,
    job.withheld_artifacts || [],
  );
  $("checks").replaceChildren();
  for (const check of job.checks || [])
    $("checks").append(
      node("li", (check.passed ? "PASS: " : "FAIL: ") + check.name + " · " + check.detail),
    );
  if (job.status === "succeeded" && !(job.checks || []).length)
    $("checks").append(
      node("li", "Execution finished successfully. No semantic verifier ran for this lesson."),
    );
  updateErrorJump();
  showRunExplanation(job.explanation, job);
}
async function recoverInterrupted(job) {
  if (job.status !== "interrupted" || !current || current.id !== job.lesson_id) return;
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
      status("The saved job needs reconnection. Its source was not submitted again.");
    }
  } catch (error) {
    if (activeJob === key) {
      monitorPaused = true;
      if (activeJobRecord) {
        activeJobRecord = {
          ...activeJobRecord,
          status: "interrupted",
          detail: "Monitoring interrupted; the worker outcome is not confirmed.",
        };
        if (current && activeJobRecord.lesson_id === current.id) showJob(activeJobRecord);
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
function highlightedSourceBlock(source, highlightedHtml = null) {
  const pre = node("pre", undefined, "highlighted-code"),
    code = node("code");
  if (highlightedHtml === null) code.textContent = source;
  else code.innerHTML = highlightedHtml;
  pre.append(code);
  return { pre, code };
}
function showLegacyResult(result, context, source) {
  const solution = result.purpose === "solution";
  if (!solution) legacyReceipts.set(context.key, { result, context, source });
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
  if (solution) $("results-title").textContent = "Result of the worked solution";
  const displayRevision = resultRevision;
  $("run-storage-status").textContent = solution
    ? "This output comes from the worked solution. It is not saved with your runs, and your code was not changed."
    : result.receipt_saved === true
      ? "Saved run" +
        (result.saved_at ? " from " + new Date(result.saved_at).toLocaleString() : "") +
        ". It keeps the code that produced it, so opening it later never changes your editor."
      : result.receipt_saved === false
        ? "This run finished, but its result could not be saved. Copy any output you need before leaving or reloading. " +
          (result.receipt_error || "") +
          " No automatic retry was started."
        : "A durable receipt was not confirmed for this run. Keep a copy of any output you need.";
  $("receipt-source-details").hidden = false;
  const submitted = highlightedSourceBlock(source);
  $("receipt-source").replaceChildren(submitted.pre);
  classroom("classroom-highlight", { source, language: context.language })
    .then((data) => {
      if (workspaceKey() === context.key && resultRevision === displayRevision)
        submitted.code.innerHTML = data.html;
    })
    .catch(() => {});
  $("job-status").textContent =
    (result.returncode === 0 && !result.stopped
      ? "Finished · exit 0 in "
      : result.stopped === "time limit"
        ? "Stopped at the time limit (timed out) · exit " + result.returncode + " after "
        : result.stopped === "output limit"
          ? "Stopped: too much output (output limit reached) · exit " +
            result.returncode +
            " after "
          : "Stopped with an error · exit " + result.returncode + " after ") +
    formatSeconds(result.elapsed_seconds) +
    (result.stopped ? " · stopped: " + result.stopped : "") +
    (result.output_truncated
      ? " · Middle output was omitted; exit status and final messages are retained."
      : "");
  if (result.output)
    programOutput(
      result.output +
        (result.stopped === "output limit"
          ? "\n\n[The output stops here: the program printed more than the output limit allows.]"
          : ""),
    );
  else outputNote(emptyOutputMessage(result.returncode === 0, solution));
  if (result.language === "sql" && context.mode !== "lesson") {
    const transcript = sqlTranscript(result.output, result.sql_display);
    if (transcript) programOutput(transcript);
    showSqlResults(result.output, result.sql_display);
  }
  for (const [position, source] of (result.figures || []).entries()) {
    if (typeof source !== "string" || !/^data:image\/(?:png|jpeg|webp);base64,/.test(source))
      continue;
    const image = node("img");
    image.src = source;
    image.alt = "Python figure " + (position + 1) + " from this run";
    const figure = node("figure");
    figure.append(image, node("figcaption", image.alt));
    $("figures").append(figure);
  }
  showPlotArtifacts(
    result.artifacts || [],
    "legacy:" + displayRevision,
    true,
    result.withheld_artifacts || [],
  );
  displayedJob = {
    lesson_id: context.id,
    source,
    output: result.output || "",
    legacy: true,
  };
  updateErrorJump();
  showRunExplanation(result.explanation, displayedJob);
  // A failed run's explanation already names the next step; the generic tip would repeat it.
  if (result.returncode === 0 || !result.explanation)
    $("checks").append(
      node(
        "li",
        result.returncode === 0
          ? "Finished without errors. Next, explain in your notes why it printed what it did."
          : "The program stopped with an error. Read the last lines of the output, change one thing, and run again.",
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
        ...(receipt.language === "sql" && receipt.mode === "snippet"
          ? { sql_display: data.sql_display ?? null }
          : {}),
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
      status("Could not open the saved run. Your source is unchanged. " + error.message, true);
  }
}
async function refreshRunHistory({ showLatest = false } = {}) {
  if (current?.engine !== "legacy" || current.runtime_profile === "reading") return;
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
    button.addEventListener("click", () => openRunReceipt(context, receipt.id, version));
    $("history").append(button);
  }
  if (!data.history.length)
    $("history").append(node("p", "No saved runs for this language and workspace yet.", "muted"));
  if (showLatest && data.history.length && resultRevision === revision)
    await openRunReceipt(context, data.history[0].id, version, revision);
}
// BEGIN SQL TRANSCRIPT HELPERS
// The SQL snippet runner reports JSON; the result log shows it as plain sentences.
const SQL_TRANSACTION_NOTES = {
  "Committed success; explicit COMMIT/ROLLBACK change boundaries.":
    "Changes were saved (committed). Any COMMIT or ROLLBACK you wrote decides where each transaction ends.",
  "Current transaction rolled back; earlier explicit commits are preserved.":
    "Nothing from this transaction was saved (rolled back). Anything you committed earlier is kept.",
};
function sqlTranscript(output, projection = undefined) {
  let data = projection;
  if (data === undefined || data === null) {
    if (typeof output !== "string" || !output.trim().startsWith("{") || output.length > 4000000)
      return null;
    try {
      data = JSON.parse(output);
    } catch (_) {
      return null;
    }
  }
  if (!data || typeof data !== "object" || Array.isArray(data)) return null;
  const transaction =
    typeof data.transaction === "string"
      ? SQL_TRANSACTION_NOTES[data.transaction] || data.transaction
      : "";
  if (typeof data.message === "string" && "error_type" in data) {
    const lines = ["ERROR: " + data.message],
      where = [];
    if (typeof data.sqlstate === "string" && /^[0-9A-Z]{5}$/.test(data.sqlstate))
      where.push("SQLSTATE " + data.sqlstate);
    if (Number.isSafeInteger(data.error_line) && data.error_line > 0)
      where.push("in the statement on line " + data.error_line);
    if (where.length) lines.push(where.join(" · "));
    if (transaction) lines.push("", transaction);
    return lines.join("\n");
  }
  if (!Array.isArray(data.results)) return null;
  const lines = [],
    total = data.results.length;
  let tables = 0;
  data.results.forEach((result, position) => {
    const prefix = total > 1 ? "Statement " + (position + 1) + ": " : "";
    if (result && Array.isArray(result.columns) && Array.isArray(result.rows)) {
      const rows = result.rows.length,
        counted = rows + (rows === 1 ? " row" : " rows");
      tables++;
      lines.push(
        total > 1
          ? prefix +
              (result.truncated ? "more than " + counted + ", first " + rows + " shown" : counted) +
              " in Query result " +
              tables +
              " below."
          : result.truncated
            ? "The query returned more than " +
              counted +
              ". The table below shows the first " +
              rows +
              "."
            : "The query returned " + counted + "." + (rows ? " They are in the table below." : ""),
      );
    } else if (result && typeof result.status === "string") lines.push(prefix + result.status);
  });
  if (!lines.length) lines.push("The SQL ran and returned nothing to show.");
  if (transaction) lines.push("", transaction);
  return lines.join("\n");
}
// END SQL TRANSCRIPT HELPERS
function showSqlResults(output, projection = undefined) {
  let parsed;
  if (projection !== undefined) {
    // Saved transcripts remain unchanged. Null means raw text has no safe table view.
    if (projection === null || typeof projection !== "object") return;
    parsed = projection;
  } else {
    try {
      parsed = JSON.parse(output);
    } catch (_) {
      return;
    }
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
      for (const value of row) line.append(node("td", value === null ? "NULL" : String(value)));
      body.append(line);
    }
    table.append(body);
    $("sql-results").append(table);
    if (result.truncated)
      $("sql-results").append(
        node("p", "This result was truncated at the runtime row limit.", "muted"),
      );
  }
}
async function runCode() {
  if (
    !current ||
    !current.capability.ready ||
    current.runtime_profile === "reading" ||
    current.execution_mode === "draft" ||
    activeJob ||
    submitInFlight ||
    legacyRunActive
  )
    return;
  if (isBrowserLesson()) stopBrowserPreview("Preparing a saved preview.");
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
      status("The lesson or draft changed while saving. Review it and press Run again.");
      return;
    }
    if (["javascript-browser", "html-browser"].includes(current.runtime_profile)) {
      await runBrowserPreview(context, intent);
    } else if (context.engine === "legacy") {
      legacyRunActive = true;
      updateControls();
      resetResult();
      outputNote(
        "Running your code. It stops after " + intent.timeout + " seconds if it has not finished.",
      );
      startRunTimer();
      status(LEGACY_RUN_NOTE);
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
        stopRunTimer();
        // A fast run must not leave "while this run finishes" on screen afterward.
        if ($("status").textContent === LEGACY_RUN_NOTE) status("");
      }
    } else {
      startRunTimer();
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
    if (!activeJob) stopRunTimer();
    status(error.message, true);
  } finally {
    submitInFlight = false;
    updateControls();
  }
}
async function refreshPadHistory() {
  if (current?.engine !== "legacy" || current.runtime_profile === "reading") return;
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
    data.history.length ? "Choose an earlier saved version" : "No earlier versions yet",
  );
  placeholder.value = "";
  $("pad-history").append(placeholder);
  for (const entry of data.history) {
    const option = node(
      "option",
      new Date(entry.saved_at).toLocaleString() + " · " + entry.bytes + " bytes",
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
      status("Navigation paused to protect your unsaved work. " + error.message, true),
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
      openLesson(rows[position + offset].id).catch((error) => status(error.message, true));
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
  remember("code." + trackId, codeFocused);
  if (!readingFocused) $("pad-title").scrollIntoView({ block: "start" });
});
$("code-focus-toggle").addEventListener("click", () => {
  if (!current) return;
  setCodeFocus(!codeFocused);
  remember("code." + trackId, codeFocused);
  remember("reading." + trackId, readingFocused);
  $("pad-title").scrollIntoView({ block: "start" });
});
$("copy-output").addEventListener("click", () =>
  copyText($("output").textContent || "", $("copy-output")),
);
if (typeof navigator === "object" && /Mac|iPhone|iPad/.test(navigator.platform || ""))
  $("run-shortcut").textContent = "⌘ Enter";
$("section-jump").addEventListener("change", () => {
  const target = document.getElementById($("section-jump").value);
  if (target && $("guide").contains(target)) {
    target.setAttribute("tabindex", "-1");
    target.scrollIntoView({ block: "start" });
    target.focus({ preventScroll: true });
  }
});
for (const id of ["source", "prediction", "explanation", "read-chapter", "phase-note"])
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

$("browser-live-toggle").addEventListener("change", () => {
  if (!isBrowserLesson() || !browserPreview) return;
  if (!$("browser-live-toggle").checked) {
    stopBrowserPreview("Live preview turned off.");
    updateControls();
    return;
  }
  browserLiveKey = workspaceKey();
  browserLivePaused = false;
  browserStudioFocused = true;
  setReadingView(false);
  updateBrowserLiveControls();
  scheduleBrowserLive(0);
});
$("browser-live-pause").addEventListener("click", () => {
  if (!browserLiveEnabled()) return;
  browserLivePaused = !browserLivePaused;
  clearTimeout(browserLiveTimer);
  browserLiveTimer = null;
  browserLiveStatus(
    browserLivePaused
      ? "Updates are paused. The preview shows the last rendered version."
      : "Resuming live preview...",
    browserLivePaused ? "paused" : "pending",
  );
  updateBrowserLiveControls();
  if (!browserLivePaused) scheduleBrowserLive(0);
});
$("browser-live-stop").addEventListener("click", () => {
  stopBrowserPreview("Stopped by the learner.");
  updateControls();
  status("The preview is stopped. Your draft and saved observations are kept.");
});
$("browser-studio-toggle").addEventListener("click", () => {
  if (!isBrowserLesson()) return;
  browserStudioFocused = !browserStudioFocused;
  setReadingView(false);
  updateBrowserLiveControls();
  $("source").focus({ preventScroll: true });
  $("browser-live-controls").scrollIntoView({ block: "start" });
});
$("browser-viewport").addEventListener("change", updateBrowserViewport);
$("browser-console-focus").addEventListener("click", () => {
  $("output").scrollIntoView({ block: "center" });
  $("output").focus({ preventScroll: true });
});
$("source").addEventListener("input", () => scheduleBrowserLive());
window.addEventListener("resize", updateBrowserViewport);
// Restore on a new task, after the browser completes its focus transition.
// Synchronous refocusing from blur can leave keyboard routing in the old frame.
window.addEventListener("blur", () => setTimeout(preserveBrowserEditorFocus, 0));
if (typeof ResizeObserver === "function")
  new ResizeObserver(updateBrowserViewport).observe($("browser-preview-stage"));

$("run").addEventListener("click", runCode);
$("browser-fullscreen").addEventListener("click", toggleBrowserFullscreen);
document.addEventListener("fullscreenchange", syncBrowserFullscreen);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && browserPreviewIsFullscreen()) void exitBrowserPreviewFullscreen();
});
updateBrowserFullscreenControls();
$("browser-observation-save").addEventListener("click", async () => {
  const context = browserPreviewContext,
    snapshot = browserPreview?.snapshot();
  if (!context || !snapshot || snapshot.status === "running" || workspaceKey() !== context.key)
    return;
  if (browserLiveEnabled()) {
    clearTimeout(browserLiveTimer);
    browserLiveTimer = null;
    browserLivePaused = true;
    browserLiveStatus("Updates are paused while you keep this observation.", "paused");
    updateBrowserLiveControls();
  }
  try {
    await saveBrowserObservation(context, snapshot);
    status("The latest console observation was saved without rerunning the preview.");
  } catch (error) {
    status("Could not save the observation. " + error.message, true);
  }
});
$("cancel").addEventListener("click", async () => {
  if (browserPreview?.active || browserLiveEnabled()) {
    stopBrowserPreview("Stopped by the learner.");
    updateControls();
    status("The preview was closed. Source and saved observations were retained.");
    return;
  }
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
    if (activeJob === key) status("Cancellation not confirmed. " + error.message, true);
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
      const selected = capabilities.runners.find((item) => item.id === context.language);
      if (!selected)
        throw new Error("This language is no longer registered for the lesson. Reopen the lesson.");
      current.capabilities = capabilities;
      current.runner = selected;
      current.effective = {
        ...selected,
        ...(selected.modes || []).find((item) => item.id === context.mode),
      };
      current.capability = {
        profile: selected.id,
        ready: Boolean(current.effective.can_run && current.effective.available),
        detail: current.effective.reason || "",
      };
    }
    updateControls();
    status("Runtime check refreshed. Your current draft is unchanged.");
  } catch (error) {
    if (sameView(intent)) status(error.message, true);
  }
});
$("offline-compare").addEventListener("click", async () => {
  if (current?.execution_mode !== "draft") return;
  const intent = selectedViewIntent();
  try {
    await flushSave();
    if (!sameView(intent)) return;
    const result = await api("module-worked-examples", { lesson_id: current.id, reveal: true });
    if (!sameView(intent)) return;
    const host = $("offline-cases");
    host.replaceChildren(node("p", "Worked reference: " + result.reference_path, "muted"));
    host.append(
      node("p", "Model: " + result.model_path + ". BLANK denotes a missing DAX value.", "muted"),
    );
    const reference = node("details"),
      pre = node("pre", result.reference_source, "result-log");
    reference.append(node("summary", "Reference source, separate from your draft"), pre);
    host.append(reference);
    for (const item of result.cases) {
      const section = node("section"),
        trace = node("ol"),
        table = node("table");
      section.append(node("h4", item.title), node("p", item.context));
      for (const step of item.trace) trace.append(node("li", step));
      section.append(trace);
      table.append(node("caption", "Hand-derived result for " + item.title));
      const head = node("thead"),
        headings = node("tr");
      for (const column of item.columns) {
        const cell = node("th", column.name);
        cell.scope = "col";
        headings.append(cell);
      }
      head.append(headings);
      table.append(head);
      const body = node("tbody");
      for (const row of item.rows) {
        const line = node("tr");
        for (const value of row) line.append(node("td", value === null ? "BLANK" : String(value)));
        body.append(line);
      }
      table.append(body);
      section.append(table, node("p", item.note, "muted"));
      host.append(section);
    }
    status("Opened the named reference. Your draft is unchanged and was not executed.");
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
  if (current?.engine !== "legacy" || current.runtime_profile === "reading") return;
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
    if (
      !replaceSource(
        current.runner.executor === "sql" && current.mode !== "lesson"
          ? current.sql_snippet_starter || "SELECT 42 AS answer;\n"
          : current.learner_code || current.learner || "",
      )
    )
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
    if (!replaceSource(data.code)) markDirty();
    resetResult();
    status("Earlier source loaded into the pad. It has not been run.");
  } catch (error) {
    status(error.message, true);
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
      "Hint " + data.number + " of " + data.total + ". Try a small change before asking again.",
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
$("exercise-collapse").addEventListener("click", () => {
  const collapsed = !$("exercise-body").hidden;
  setExerciseCollapsed(collapsed);
  remember("exercises.collapsed", collapsed);
});
$("exercise-prev").addEventListener("click", () => {
  selectExercise(exercise.index - 1);
  if (exercise.index === 0) $("exercise-title").focus();
});
$("exercise-next").addEventListener("click", () => {
  selectExercise(exercise.index + 1);
  if (exercise.index >= exercise.list.length - 1) $("exercise-title").focus();
});
$("exercise-steps").addEventListener("keydown", (event) => {
  const last = exercise.list.length - 1,
    target = {
      ArrowLeft: exercise.index - 1,
      ArrowUp: exercise.index - 1,
      ArrowRight: exercise.index + 1,
      ArrowDown: exercise.index + 1,
      Home: 0,
      End: last,
    }[event.key];
  if (target === undefined) return;
  event.preventDefault();
  selectExercise(Math.max(0, Math.min(target, last)), { focusStep: true });
});
$("exercise-hint").addEventListener("click", () => {
  const item = exercise.list[exercise.index];
  if (!item) return;
  const total = (Array.isArray(item.hints) ? item.hints : []).length,
    shown = Number(exerciseState(item.number).hints) || 0;
  if (shown >= total) return;
  updateExerciseState(item.number, { hints: shown + 1 });
  renderExerciseHints(item);
  $("exercise-status").textContent = "Showing hint " + (shown + 1) + " of " + total + ".";
  if ($("exercise-hint").disabled) $("exercise-solve").focus();
});
$("exercise-solve").addEventListener("click", () => {
  const item = exercise.list[exercise.index];
  if (!item || item.has_solution !== true) return;
  if (exerciseState(item.number).seen) showExerciseSolution(item);
  else openExerciseConfirm("exercise");
});
$("exercise-reference-show").addEventListener("click", () => {
  if (exerciseProgress().reference_seen) showReferenceProgram();
  else openExerciseConfirm("reference");
});
$("exercise-confirm-yes").addEventListener("click", () => {
  const kind = exercise.confirming,
    item = exercise.list[exercise.index];
  closeExerciseConfirm();
  if (kind === "reference") showReferenceProgram();
  else if (item) {
    updateExerciseState(item.number, { seen: true });
    updateExerciseSteps();
    showExerciseSolution(item);
  }
});
$("exercise-confirm-no").addEventListener("click", () => {
  const kind = exercise.confirming,
    hint = $("exercise-hint");
  closeExerciseConfirm();
  const hintsLeft = !hint.hidden && !hint.disabled;
  $("exercise-status").textContent = hintsLeft
    ? "Good call. If you are stuck, a hint shows the next step without giving the answer away."
    : "Good call. Try one small change, run it, and read the result.";
  (kind === "reference"
    ? $("exercise-reference-show")
    : hintsLeft
      ? hint
      : $("exercise-solve")
  ).focus();
});
$("exercise-hide-solution").addEventListener("click", () => hideExerciseSolution());
$("exercise-run-solution").addEventListener("click", () => runSolution());
$("exercise-compare").addEventListener("click", () => {
  if (!exercise.view) return;
  exercise.comparing = !exercise.comparing;
  $("exercise-compare").setAttribute("aria-pressed", exercise.comparing ? "true" : "false");
  if (exercise.comparing) renderExerciseDiff();
  else $("exercise-diff").replaceChildren();
  $("exercise-diff").hidden = !exercise.comparing;
});
$("exercise-use-solution").addEventListener("click", () => useSolutionCode());
$("exercise-done").addEventListener("click", () => {
  const item = exercise.list[exercise.index];
  if (!item) return;
  const solved = exerciseState(item.number).solved !== true;
  updateExerciseState(item.number, { solved });
  updateExerciseDone(item);
  updateExerciseSteps();
  const count = exercise.list.filter((entry) => exerciseState(entry.number).solved).length,
    total = exercise.list.length;
  if (!solved) {
    $("exercise-status").textContent =
      "Exercise " + item.number + " is no longer marked as solved.";
    return;
  }
  if (count === total) {
    $("exercise-status").textContent =
      "All " +
      total +
      " exercises are marked as solved. Explain one of them in your own words below.";
    return;
  }
  const next = exercise.list.findIndex(
    (entry, position) => position > exercise.index && !exerciseState(entry.number).solved,
  );
  const message = node(
    "span",
    "Exercise " + item.number + " is marked as solved. " + count + " of " + total + " solved.",
  );
  if (next < 0) {
    $("exercise-status").replaceChildren(message);
    return;
  }
  const onward = node("button", "Next: exercise " + exercise.list[next].number, "quiet");
  onward.type = "button";
  onward.addEventListener("click", () => {
    selectExercise(next);
    $("exercise-title").focus();
  });
  $("exercise-status").replaceChildren(message, onward);
});
$("exercise-snippet").addEventListener("click", () => {
  if (!sqlLessonMode()) return;
  const snippet = (current.runner?.modes || []).find((mode) => mode.id !== "lesson");
  if (!snippet) return;
  $("pad-mode").value = snippet.id;
  switchRunner();
});
// An offered Undo only applies until the learner edits the replaced code; an
// open comparison follows the learner's edits.
let compareTimer = null;
$("source").addEventListener("input", () => {
  if (exercise.undo && $("source").value !== exercise.undo.replaced) {
    exercise.undo = null;
    $("exercise-status").replaceChildren();
  }
  if (exercise.comparing && exercise.view) {
    clearTimeout(compareTimer);
    compareTimer = setTimeout(() => {
      compareTimer = null;
      if (exercise.comparing && exercise.view) renderExerciseDiff();
    }, 300);
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
      (draftRevisions.get(workspaceKey()) || 0) > (savedRevisions.get(workspaceKey()) || 0))
  ) {
    stashDraft(workspaceKey(), values());
    event.preventDefault();
    event.returnValue = "";
  }
});
async function boot() {
  try {
    $("pace").value = String([15, 30, 60, 90].includes(pref("pace")) ? pref("pace") : 30);
    subjectArea = typeof pref("area") === "string" ? pref("area") : "all";
    setTheme(
      pref(
        "dark",
        typeof matchMedia === "function" && matchMedia("(prefers-color-scheme: dark)").matches,
      ),
    );
    index = await classroom("classroom-index");
    renderHome();
    if (index.active_job && !finished.has(index.active_job.status)) adoptJob(index.active_job);
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
        "Select a subject or search for a lesson. Saved work is retained when you switch subjects.",
      );
    }
  } catch (error) {
    status("Cannot load the classroom. " + error.message, true);
  }
}
function recordRoute(url, mode = "push") {
  if (mode === "replace" || url === visibleRoute) history.replaceState(null, "", url);
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
    status("Navigation paused to protect your unsaved work. " + error.message, true);
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
  const unprefixed = id.replace(/^(?:guide|reference|module-guide|lab-guide)--/, "");
  const target = [...$("guide").querySelectorAll("[id]")].find(
    (element) =>
      element.id === id || element.id === unprefixed || element.id.endsWith("--" + unprefixed),
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
    (anchor.getAttribute("download") !== null && anchor.getAttribute("download") !== undefined)
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
  const mapped = Object.prototype.hasOwnProperty.call(index?.lesson_links || {}, url.pathname)
    ? index.lesson_links[url.pathname]
    : null;
  const id =
    mapped ||
    linked?.[1] ||
    (["/classroom", "/learn", "/journeys"].includes(url.pathname) ? params.get("lesson") : null);
  if (typeof id === "string" && locate(id)) {
    event.preventDefault();
    const opening = openLesson(id),
      version = intentVersion;
    try {
      await opening;
      if (current?.id === id && version === intentVersion && !params.has("lesson")) {
        if (/^#solutions?(?:[-_]|$)/i.test(url.hash)) {
          if (current.learning_mode === "tutorial")
            status("Worked explanations are already included in this tutorial chapter.");
          else {
            $("reveal").scrollIntoView({ block: "center" });
            $("reveal").focus({ preventScroll: true });
            status("Choose Reveal solutions to open this comparison.");
          }
        } else scrollToGuideFragment(url.hash);
      }
    } catch (error) {
      status("Navigation paused to protect your unsaved work. " + error.message, true);
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
  $("syntax-toggle").textContent = previewVisible ? "Hide syntax preview" : "Syntax preview";
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
      language: current.runtime_profile === "dbt-duckdb" ? "sql+jinja" : current.language,
    });
    if (
      sequence !== highlightSequence ||
      workspaceKey() !== key ||
      !previewVisible ||
      $("source").value !== source
    )
      return;
    $("syntax-code").replaceChildren(highlightedSourceBlock(source, result.html).pre);
    $("preview-status").textContent = "Read-only syntax preview. Edit in the coding pad above.";
  } catch (error) {
    if (sequence === highlightSequence && workspaceKey() === key && previewVisible) {
      $("syntax-code").replaceChildren();
      $("preview-status").textContent =
        "Syntax preview unavailable. Your editable source is unchanged. " + error.message;
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
    $("preview-status").textContent = "Preview is updating for your edited source...";
    highlightTimer = setTimeout(renderSyntaxPreview, 600);
  }
});
boot();
