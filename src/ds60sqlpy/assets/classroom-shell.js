"use strict";
// classroom.js loads first and defines these shared script globals.
/* global current, index, themes, locate, theme, openLesson, switchTrack, showHome, lab */
// Workspace conveniences layered over classroom.js: the Ctrl/Cmd+K lesson index,
// the resizable spread gutter, sidebar and mobile navigation, reading progress,
// the status slug and result reveal. Everything degrades to the plain page.
(() => {
  const byId = (id) => document.getElementById(id);
  const store = {
    get(key, fallback) {
      try {
        const value = localStorage.getItem("ds60.classroom." + key);
        return value === null ? fallback : JSON.parse(value);
      } catch (_) {
        return fallback;
      }
    },
    set(key, value) {
      try {
        localStorage.setItem("ds60.classroom." + key, JSON.stringify(value));
      } catch (_) {}
    },
  };
  const library = () => (typeof index === "object" && index ? index : null);
  const report = (error) => {
    if (typeof status === "function") status(error.message, true);
  };
  const wide = typeof matchMedia === "function" ? matchMedia("(min-width: 1100px)") : null;
  const isWide = () => Boolean(wide?.matches);
  const typing = (target) =>
    Boolean(
      target &&
        (target.isContentEditable ||
          /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName) ||
          target.closest?.(".cm-editor")),
    );

  // Ctrl/Cmd+K index ---------------------------------------------------------
  const dialog = byId("palette"),
    input = byId("palette-input"),
    list = byId("palette-results");
  let entries = null,
    options = [],
    active = 0,
    returnFocus = null;

  function buildEntries() {
    const data = library();
    if (!data) return [];
    const rows = [];
    for (const subject of data.tracks) {
      const mark = themes?.[subject.theme_key || subject.id]?.[4] || subject.title.slice(0, 2);
      rows.push({
        kind: "subject",
        id: subject.id,
        title: subject.title,
        detail: subject.lessons.length + " lessons",
        mark,
        subject,
        haystack: (subject.title + " " + subject.id).toLowerCase(),
      });
      subject.lessons.forEach((record, position) => {
        if (record.status === "planned") return;
        rows.push({
          kind: "lesson",
          id: record.id,
          title: record.title,
          detail: subject.title + " · " + record.id,
          meta: record.level || "",
          mark,
          subject,
          position,
          haystack: [record.title, record.id, subject.title, ...(record.concepts || [])]
            .join(" ")
            .toLowerCase(),
        });
      });
    }
    return rows;
  }

  function score(entry, query, terms) {
    if (!terms.every((term) => entry.haystack.includes(term))) return -1;
    const title = entry.title.toLowerCase();
    let value = 0;
    if (entry.id.toLowerCase() === query) value += 400;
    if (title === query) value += 300;
    if (title.startsWith(query)) value += 160;
    else if (title.includes(query)) value += 90;
    if (entry.id.toLowerCase().startsWith(query)) value += 60;
    for (const term of terms) if (title.includes(term)) value += 12;
    if (entry.kind === "subject") value += 25;
    return value - (entry.position || 0) * 0.01;
  }

  function quickEntries() {
    const rows = [];
    const recent = store.get("lastLesson", null);
    const found = recent && typeof locate === "function" ? locate(recent.id) : null;
    if (found)
      rows.push({
        kind: "continue",
        id: recent.id,
        context: recent.context || {},
        title: "Continue: " + found.record.title,
        detail: found.subject.title + " · " + recent.id,
        mark: themes?.[found.subject.theme_key || found.subject.id]?.[4] || "↗",
        group: "Pick up where you left off",
        subject: found.subject,
      });
    const data = library();
    for (const id of store.get("recentTracks", []) || []) {
      const subject = data?.tracks.find((item) => item.id === id);
      if (!subject) continue;
      rows.push({
        kind: "subject",
        id: subject.id,
        title: subject.title,
        detail: subject.lessons.length + " lessons",
        mark: themes?.[subject.theme_key || subject.id]?.[4] || "↗",
        group: "Recent subjects",
        subject,
      });
    }
    rows.push(
      {
        kind: "action",
        id: "home",
        title: "All subjects",
        detail: "Open the contents page",
        mark: "≡",
        group: "Actions",
      },
      {
        kind: "action",
        id: "theme",
        title: byId("theme-toggle")?.textContent.trim() || "Switch appearance",
        detail: "Switch between light and dark pages",
        mark: "◐",
        group: "Actions",
      },
    );
    return rows;
  }

  function renderOptions() {
    const query = input.value.trim().toLowerCase();
    entries ??= buildEntries();
    if (!query) options = quickEntries();
    else {
      const terms = query.split(/\s+/).filter(Boolean);
      options = entries
        .map((entry) => ({ entry, value: score(entry, query, terms) }))
        .filter((item) => item.value >= 0)
        .sort((a, b) => b.value - a.value)
        .slice(0, 60)
        .map((item) => item.entry);
    }
    active = Math.min(active, Math.max(0, options.length - 1));
    list.replaceChildren();
    if (!options.length) {
      const empty = document.createElement("li");
      empty.className = "palette-empty";
      empty.setAttribute("role", "presentation");
      empty.textContent = entries.length
        ? "No lessons or subjects match. Try a shorter word or a lesson ID."
        : "The library is still loading.";
      list.append(empty);
      input.removeAttribute("aria-activedescendant");
      return;
    }
    let group = null;
    options.forEach((option, position) => {
      const heading = option.group || (option.kind === "subject" ? "Subjects" : "Lessons");
      if (heading !== group && (!query || option.group)) {
        group = heading;
        const label = document.createElement("li");
        label.className = "palette-group";
        label.setAttribute("role", "presentation");
        label.textContent = heading;
        list.append(label);
      }
      const item = document.createElement("li");
      item.className = "palette-option";
      item.id = "palette-option-" + position;
      item.setAttribute("role", "option");
      item.setAttribute("aria-selected", String(position === active));
      if (option.subject && typeof theme === "function") theme(option.subject, item);
      const mark = document.createElement("span");
      mark.className = "subject-icon";
      mark.setAttribute("aria-hidden", "true");
      mark.textContent = option.mark;
      const title = document.createElement("span");
      title.className = "palette-option-title";
      title.textContent = option.title;
      const detail = document.createElement("span");
      detail.className = "palette-option-detail";
      detail.textContent = option.detail;
      item.append(mark, title, detail);
      if (option.meta) {
        const meta = document.createElement("span");
        meta.className = "palette-option-meta";
        meta.textContent = option.meta;
        item.append(meta);
      }
      item.addEventListener("mousemove", () => {
        if (active !== position) setActive(position);
      });
      item.addEventListener("click", () => choose(position));
      list.append(item);
    });
    setActive(active);
  }

  function setActive(position) {
    active = position;
    for (const item of list.querySelectorAll('[role="option"]'))
      item.setAttribute("aria-selected", String(item.id === "palette-option-" + position));
    const selected = byId("palette-option-" + position);
    if (selected) {
      input.setAttribute("aria-activedescendant", selected.id);
      selected.scrollIntoView({ block: "nearest" });
    }
  }

  function choose(position) {
    const option = options[position];
    if (!option) return;
    closePalette(false);
    let action;
    if (option.kind === "lesson") action = openLesson(option.id);
    else if (option.kind === "continue") action = openLesson(option.id, true, option.context);
    else if (option.kind === "subject") action = switchTrack(option.id);
    else if (option.id === "home") action = showHome();
    else if (option.id === "theme") byId("theme-toggle")?.click();
    Promise.resolve(action).catch(report);
  }

  function openPalette() {
    if (!dialog || typeof dialog.showModal !== "function" || dialog.open) return;
    returnFocus = document.activeElement;
    entries = buildEntries();
    input.value = "";
    active = 0;
    renderOptions();
    dialog.showModal();
    input.focus();
  }

  function closePalette(restore = true) {
    if (!dialog?.open) return;
    dialog.close();
    if (restore && returnFocus?.isConnected) returnFocus.focus({ preventScroll: true });
  }

  if (dialog && input && list) {
    byId("palette-button")?.addEventListener("click", openPalette);
    input.addEventListener("input", () => {
      active = 0;
      renderOptions();
    });
    input.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        if (!options.length) return;
        const step = event.key === "ArrowDown" ? 1 : -1;
        setActive((active + step + options.length) % options.length);
      } else if (event.key === "Home" && options.length && !input.value) {
        event.preventDefault();
        setActive(0);
      } else if (event.key === "End" && options.length && !input.value) {
        event.preventDefault();
        setActive(options.length - 1);
      } else if (event.key === "Enter") {
        event.preventDefault();
        choose(active);
      }
    });
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) closePalette();
    });
    const shortcut = byId("palette-button")?.querySelector(".search-kbd");
    if (shortcut && /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent))
      shortcut.textContent = "⌘K";
  }

  // Keyboard shortcuts --------------------------------------------------------
  let lastRun = 0;
  window.addEventListener(
    "keydown",
    (event) => {
      const mod = event.ctrlKey || event.metaKey;
      if (mod && !event.altKey && !event.shiftKey && event.key.toLowerCase() === "k") {
        event.preventDefault();
        event.stopPropagation();
        if (dialog?.open) closePalette();
        else openPalette();
        return;
      }
      if (mod && event.key === "Enter") lastRun = Date.now();
      if (event.key === "/" && !mod && !event.altKey && !typing(event.target) && !dialog?.open) {
        event.preventDefault();
        openPalette();
      }
    },
    true,
  );

  // Home quick starts ----------------------------------------------------------
  function updateQuickStarts() {
    const data = library();
    for (const button of document.querySelectorAll("[data-open-subject]")) {
      const id = button.dataset.openSubject,
        subject = data?.tracks.find((item) => item.id === id);
      button.hidden = Boolean(data) && !subject;
      if (!subject) continue;
      const name = { python: "Python", sql: "SQL" }[id] || subject.title;
      button.textContent = (store.get("lastTrack." + id, null) ? "Resume " : "Start ") + name;
    }
  }
  for (const button of document.querySelectorAll("[data-open-subject]"))
    button.addEventListener("click", () => {
      Promise.resolve(switchTrack(button.dataset.openSubject)).catch(report);
    });
  const summary = byId("catalog-summary");
  if (summary && typeof MutationObserver === "function")
    new MutationObserver(updateQuickStarts).observe(summary, {
      childList: true,
      characterData: true,
      subtree: true,
    });
  updateQuickStarts();

  // Spread gutter ---------------------------------------------------------------
  const panes = byId("authored"),
    readingPane = panes?.querySelector(".reading-pane"),
    practicePane = panes?.querySelector(".practice-pane");
  const SPLIT_MIN = 30,
    SPLIT_MAX = 72,
    SPLIT_DEFAULT = 56;
  if (panes && readingPane && practicePane) {
    const gutter = document.createElement("div");
    gutter.className = "pane-gutter";
    gutter.tabIndex = 0;
    gutter.setAttribute("role", "separator");
    gutter.setAttribute("aria-orientation", "vertical");
    gutter.setAttribute("aria-label", "Resize the lesson and editor pages");
    gutter.setAttribute("aria-valuemin", String(SPLIT_MIN));
    gutter.setAttribute("aria-valuemax", String(SPLIT_MAX));
    gutter.title = "Drag or use the arrow keys to resize. Double-click to reset.";
    readingPane.after(gutter);
    const clamp = (value) =>
      Math.min(SPLIT_MAX, Math.max(SPLIT_MIN, Number(value) || SPLIT_DEFAULT));
    let split = clamp(store.get("split", SPLIT_DEFAULT));
    const apply = (save = false) => {
      panes.style.setProperty("--split", split + "%");
      gutter.setAttribute("aria-valuenow", String(Math.round(split)));
      gutter.setAttribute(
        "aria-valuetext",
        "Lesson " + Math.round(split) + " percent, editor " + Math.round(100 - split) + " percent",
      );
      if (save) store.set("split", Math.round(split));
    };
    apply();
    gutter.addEventListener("pointerdown", (event) => {
      if (event.button !== 0) return;
      event.preventDefault();
      gutter.setPointerCapture(event.pointerId);
      gutter.dataset.dragging = "true";
      document.body.style.userSelect = "none";
    });
    gutter.addEventListener("pointermove", (event) => {
      if (gutter.dataset.dragging !== "true") return;
      const box = panes.getBoundingClientRect();
      if (box.width > 0) {
        split = clamp(((event.clientX - box.left) / box.width) * 100);
        apply();
      }
    });
    const stop = (event) => {
      if (gutter.dataset.dragging !== "true") return;
      gutter.dataset.dragging = "false";
      document.body.style.userSelect = "";
      if (gutter.hasPointerCapture?.(event.pointerId))
        gutter.releasePointerCapture(event.pointerId);
      apply(true);
    };
    gutter.addEventListener("pointerup", stop);
    gutter.addEventListener("pointercancel", stop);
    gutter.addEventListener("dblclick", () => {
      split = SPLIT_DEFAULT;
      apply(true);
    });
    gutter.addEventListener("keydown", (event) => {
      const moves = {
        ArrowLeft: -2,
        ArrowRight: 2,
        Home: SPLIT_MIN - split,
        End: SPLIT_MAX - split,
      };
      if (!(event.key in moves)) return;
      event.preventDefault();
      split = clamp(split + moves[event.key]);
      apply(true);
    });
  }

  // Lesson list visibility -------------------------------------------------------
  const view = byId("workspace-view"),
    sidebarToggle = byId("sidebar-toggle");
  if (view && sidebarToggle) {
    const applySidebar = (hidden) => {
      view.dataset.sidebar = hidden ? "hidden" : "shown";
      sidebarToggle.setAttribute("aria-expanded", String(!hidden));
      sidebarToggle.textContent = hidden ? "Show lesson list" : "Hide lesson list";
    };
    applySidebar(store.get("sidebarHidden", false) === true);
    sidebarToggle.addEventListener("click", () => {
      const hidden = view.dataset.sidebar !== "hidden";
      store.set("sidebarHidden", hidden);
      applySidebar(hidden);
    });
  }

  // Small screens: jump between the lesson, code and result -----------------------
  for (const button of document.querySelectorAll("[data-spread-target]"))
    button.addEventListener("click", () => {
      const target = byId(button.dataset.spreadTarget);
      if (!target) return;
      target.scrollIntoView({ block: "start" });
      if (target.tabIndex < 0 || target.hasAttribute("tabindex"))
        target.focus({ preventScroll: true });
    });

  // Reading progress and fresh scroll positions per lesson ------------------------
  const progress = document.querySelector(".reading-progress span"),
    guide = byId("guide");
  function updateProgress() {
    if (!progress || !readingPane || !guide) return;
    let ratio = 0;
    if (isWide()) {
      const range = readingPane.scrollHeight - readingPane.clientHeight;
      ratio = range > 0 ? readingPane.scrollTop / range : 0;
    } else {
      const box = guide.getBoundingClientRect(),
        range = box.height - window.innerHeight;
      ratio = range > 0 ? Math.min(1, Math.max(0, -box.top / range)) : 0;
    }
    progress.style.transform = "scaleX(" + ratio.toFixed(3) + ")";
  }
  readingPane?.addEventListener("scroll", updateProgress, { passive: true });
  window.addEventListener("scroll", updateProgress, { passive: true });
  wide?.addEventListener?.("change", updateProgress);
  if (guide && typeof MutationObserver === "function")
    new MutationObserver(() => {
      if (readingPane) readingPane.scrollTop = 0;
      if (practicePane) practicePane.scrollTop = 0;
      updateProgress();
    }).observe(guide, { childList: true });

  // Status slug: visible briefly, errors stay until replaced ------------------------
  const slug = byId("status");
  let slugTimer = null;
  if (slug && typeof MutationObserver === "function") {
    const show = () => {
      clearTimeout(slugTimer);
      if (!slug.textContent.trim()) return;
      slug.dataset.visible = "true";
      if (!slug.classList.contains("error"))
        slugTimer = setTimeout(() => {
          slug.dataset.visible = "false";
        }, 5200);
    };
    new MutationObserver(show).observe(slug, {
      childList: true,
      characterData: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["class"],
    });
    slug.dataset.visible = "false";
  }

  // Run state and result reveal ------------------------------------------------------
  const jobStatus = byId("job-status"),
    results = byId("runtime-results");
  byId("run")?.addEventListener("click", () => {
    lastRun = Date.now();
  });
  function classify(text) {
    if (
      /failed|error|exit [1-9]|timed[_ ]?out|cancel|blocked|killed|unavailable|stopped/i.test(text)
    )
      return "error";
    if (/succeeded|exit 0\b|passed|completed|up to date/i.test(text)) return "success";
    if (/queued|running|starting|submitting|updating|waiting|refreshing/i.test(text))
      return "running";
    return "";
  }
  if (jobStatus && results && typeof MutationObserver === "function")
    new MutationObserver(() => {
      const state = classify(jobStatus.textContent);
      if (state) jobStatus.dataset.state = state;
      else delete jobStatus.dataset.state;
      if ((state === "success" || state === "error") && Date.now() - lastRun < 180000) {
        lastRun = 0;
        results.dataset.fresh = "true";
        setTimeout(() => delete results.dataset.fresh, 700);
        const reduce =
          typeof matchMedia === "function" &&
          matchMedia("(prefers-reduced-motion: reduce)").matches;
        results.scrollIntoView({ block: "nearest", behavior: reduce ? "auto" : "smooth" });
      }
    }).observe(jobStatus, { childList: true, characterData: true, subtree: true });

  // Course database readiness for lessons and snippets that use PostgreSQL ----------
  const dbPanel = byId("sql-readiness"),
    dbText = byId("sql-readiness-text"),
    dbAction = byId("sql-ready-action"),
    dbReset = byId("sql-ready-reset"),
    dbRefresh = byId("sql-ready-refresh");
  let dbSequence = 0,
    dbLesson = null,
    dbBusy = false;
  const sqlLesson = () => {
    const data = typeof current === "object" && current ? current : null;
    return data &&
      data.engine === "legacy" &&
      (data.course_database === true || data.runner?.executor === "sql")
      ? data
      : null;
  };
  function renderReadiness(readiness) {
    if (!dbPanel) return;
    const data = sqlLesson(),
      project = readiness.project_schema
        ? "the " +
          readiness.project_schema +
          " schema that " +
          readiness.creator +
          " (" +
          readiness.creator_title +
          ") creates"
        : "";
    let state = readiness.state,
      text = "",
      action = "";
    if (state === "ready" && readiness.project_state === "missing") {
      state = "project";
      text =
        "The training tables are loaded. This lesson continues a project and also needs " +
        project +
        ". It is built automatically when you first run code here, or build it now.";
      action = "Build the " + readiness.project_schema + " schema";
    } else if (state === "ready") {
      text =
        "Ready. The course training tables are loaded" +
        (readiness.project_schema ? ", and so is " + project : "") +
        (data?.mode === "lesson"
          ? ". Lesson scripts leave the training tables as they found them."
          : ". Changes you run here are kept; Reset training data restores the original rows.");
    } else if (state === "missing") {
      text =
        "The course training tables (customers, orders, products and more) are not loaded " +
        "yet. They load automatically the first time you run code here, or load them now. " +
        "It takes a few seconds and only happens once." +
        (project ? " " + project[0].toUpperCase() + project.slice(1) + " is built too." : "");
      action = "Load course tables";
    } else if (state === "changed") {
      text =
        "The training tables no longer match the original course data, so results can differ " +
        "from this lesson's expected output. Reset them to the original data; your saved code " +
        "and notes are kept." +
        (readiness.detail ? " (" + readiness.detail + ")" : "");
    } else if (/reload the page/i.test(readiness.detail || "")) {
      text = readiness.detail;
    } else {
      text =
        "The course database is not reachable right now. Start the classroom with ./classroom " +
        "(it starts PostgreSQL too), then choose Check again." +
        (readiness.detail ? " Details: " + readiness.detail : "");
    }
    dbPanel.dataset.state = state;
    dbText.textContent = text;
    dbAction.hidden = !action;
    dbAction.textContent = action;
    dbReset.hidden = !(state === "changed" || state === "ready" || state === "project");
    dbReset.className = state === "changed" ? "primary" : "";
    dbRefresh.hidden = state === "ready";
  }
  async function refreshReadiness() {
    const data = sqlLesson();
    document.body.classList.toggle("has-db-status", Boolean(data));
    if (!dbPanel) return;
    dbPanel.hidden = !data;
    if (!data) {
      // Forget the last database lesson so returning to it checks again, and
      // drop any status response still in flight for it.
      dbLesson = null;
      dbSequence++;
      return;
    }
    const sequence = ++dbSequence;
    dbLesson = data.id;
    dbPanel.dataset.state = "checking";
    dbText.textContent = "Checking the course database...";
    dbAction.hidden = true;
    try {
      const response = await lab("sql-status", { lesson_id: data.id });
      if (sequence === dbSequence && sqlLesson()?.id === data.id)
        renderReadiness(response.readiness);
    } catch (error) {
      if (sequence === dbSequence) renderReadiness({ state: "unavailable", detail: error.message });
    }
  }
  async function prepareDatabase(reset) {
    const data = sqlLesson();
    if (!data || dbBusy) return;
    if (
      reset &&
      !confirm(
        "Reset the course training tables to the original data? This replaces only the " +
          "disposable training schema. Your saved code, notes and run history are kept.",
      )
    )
      return;
    dbBusy = true;
    const sequence = ++dbSequence;
    dbPanel.dataset.state = "working";
    dbText.textContent = reset
      ? "Resetting the training tables..."
      : "Preparing the course database. This takes a few seconds...";
    for (const button of [dbAction, dbReset, dbRefresh]) button.disabled = true;
    try {
      if (reset) {
        const result = await lab("prepare-sql", { confirmation: "RESET TRAINING" }, false);
        if (result.returncode !== 0)
          throw new Error("The reset reported status " + result.returncode);
        status("The training tables were reset to the original course data.");
        await refreshReadiness();
      } else {
        const result = await lab("sql-prepare", { lesson_id: data.id }, false);
        if (sequence === dbSequence) renderReadiness(result.readiness);
        status(
          result.readiness.actions?.length
            ? "The course database is ready for " + data.id + "."
            : "Nothing needed preparing.",
        );
      }
    } catch (error) {
      status("Could not prepare the course database. " + error.message, true);
      await refreshReadiness();
    } finally {
      dbBusy = false;
      for (const button of [dbAction, dbReset, dbRefresh]) button.disabled = false;
    }
  }
  dbAction?.addEventListener("click", () => prepareDatabase(false));
  dbReset?.addEventListener("click", () => prepareDatabase(true));
  dbRefresh?.addEventListener("click", refreshReadiness);
  refreshReadiness();
  if (guide && typeof MutationObserver === "function")
    new MutationObserver(() => {
      if (sqlLesson()?.id !== dbLesson || !sqlLesson()) refreshReadiness();
    }).observe(guide, { childList: true });
  const runner = byId("runner"),
    padMode = byId("pad-mode");
  for (const control of [runner, padMode])
    control?.addEventListener("change", () => setTimeout(refreshReadiness, 400));
  // Runs prepare absent course data on the server; say so next to the result.
  if (typeof lab === "function") {
    const original = lab;
    globalThis.lab = async (action, fields = {}, bounded = true) => {
      const running = action === "run" || action === "run-lesson",
        // A run may finish after the learner opens another lesson; only that
        // lesson's own panel and status may show its preparation note.
        stillOnRunLesson = () => sqlLesson()?.id === fields.lesson_id,
        preparing =
          running &&
          dbPanel &&
          !dbPanel.hidden &&
          stillOnRunLesson() &&
          (dbPanel.dataset.state === "missing" || dbPanel.dataset.state === "project");
      if (preparing) {
        dbPanel.dataset.state = "working";
        dbText.textContent =
          "Preparing the course database before your run. This takes a few seconds the first time.";
        dbAction.hidden = true;
      }
      const recheck = () => {
        if (!dbBusy) refreshReadiness();
      };
      let result;
      try {
        result = await original(action, fields, bounded);
      } catch (error) {
        if (preparing && stillOnRunLesson()) recheck();
        throw error;
      }
      if (running && result?.database_preparation) {
        const note = result.database_preparation.message;
        setTimeout(() => {
          if (!stillOnRunLesson()) {
            // The data changed for every lesson; let the open one re-check.
            recheck();
            return;
          }
          const storage = byId("run-storage-status");
          if (storage) storage.textContent = note + " " + storage.textContent;
          status(note);
          if (result.database_preparation.readiness)
            renderReadiness(result.database_preparation.readiness);
        }, 0);
      } else if (preparing && stillOnRunLesson()) recheck();
      return result;
    };
  }

  // Keep the editor label in step with the lesson's language badge.
  const badge = byId("language");
  if (badge && typeof MutationObserver === "function")
    new MutationObserver(() => {
      badge.hidden = !badge.textContent.trim();
    }).observe(badge, { childList: true, characterData: true, subtree: true });

  // One code text size for the editor and its output, remembered on this computer.
  const sizes = [12, 13, 14, 15, 16, 18, 20],
    pane = document.querySelector(".practice-pane"),
    smaller = byId("code-smaller"),
    larger = byId("code-larger");
  let codeSize = sizes.includes(store.get("code-size", 14)) ? store.get("code-size", 14) : 14;
  function applyCodeSize() {
    pane?.style.setProperty("--code-size", codeSize / 16 + "rem");
    if (smaller) smaller.disabled = codeSize <= sizes[0];
    if (larger) larger.disabled = codeSize >= sizes[sizes.length - 1];
  }
  function stepCodeSize(direction) {
    const next = sizes[sizes.indexOf(codeSize) + direction];
    if (!next) return;
    codeSize = next;
    store.set("code-size", codeSize);
    applyCodeSize();
  }
  smaller?.addEventListener("click", () => stepCodeSize(-1));
  larger?.addEventListener("click", () => stepCodeSize(1));
  applyCodeSize();
})();
