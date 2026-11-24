"use strict";
// classroom.js loads first and defines these shared script globals.
/* global current, exercise, contextOf, lab, solutionCode, solutionIsStandalone, manualOpen, hideManual, openLesson, lessonId, pref, remember, status */
// Guided help layered over the workspace: the step-through player that walks a
// beginner through Python or SQL one step at a time, and the page tour that
// points at each part of a lesson. Both only read the page; neither saves code.
(() => {
  const byId = (id) => document.getElementById(id);
  const make = (tag, text, cls) => {
    const item = document.createElement(tag);
    if (text !== undefined && text !== null) item.textContent = text;
    if (cls) item.className = cls;
    return item;
  };
  const reduceMotion = () =>
    typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;
  const typing = (target) =>
    target instanceof HTMLElement &&
    (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName)) &&
    !(target instanceof HTMLInputElement && target.type === "range");
  const shorten = (text, limit = 80) => {
    const flat = String(text ?? "")
      .replace(/\s+/g, " ")
      .trim();
    return flat.length > limit ? flat.slice(0, limit - 1) + "\u2026" : flat;
  };
  const plural = (count, word) => count + " " + word + (count === 1 ? "" : "s");

  // Step-through ---------------------------------------------------------------
  const panel = byId("step-panel"),
    startButton = byId("step-through"),
    solutionButton = byId("exercise-step-solution"),
    runButton = byId("run");
  if (!panel || !startButton || !runButton) return;
  const title = byId("step-title"),
    sourceLabel = byId("step-source"),
    statusLine = byId("step-status"),
    narration = byId("step-narration"),
    body = byId("step-body"),
    range = byId("step-range"),
    count = byId("step-count"),
    controls = {
      first: byId("step-first"),
      prev: byId("step-prev"),
      next: byId("step-next"),
      last: byId("step-last"),
    };
  let walk = null,
    position = 0,
    sequence = 0,
    busy = false,
    origin = null;

  function stepLanguage() {
    if (typeof current !== "object" || !current || current.engine !== "legacy") return null;
    if (current.runtime_profile === "reading" || current.execution_mode === "draft") return null;
    const language = contextOf()?.language;
    return language === "python" || language === "sql" ? language : null;
  }
  function solutionSteppable(view) {
    const language = stepLanguage();
    if (!language || !view || !solutionCode(view)) return false;
    return language === "sql" || solutionIsStandalone(view);
  }
  function syncButtons() {
    const language = stepLanguage(),
      blocked = runButton.disabled || runButton.hidden || busy;
    startButton.hidden = !language;
    startButton.disabled = blocked;
    startButton.textContent = busy ? "Preparing steps..." : "Step through";
    startButton.title =
      language === "sql"
        ? "Walk through the query under your cursor one clause at a time"
        : "Run your code one line at a time and watch the values change";
    if (solutionButton) {
      const view = typeof exercise === "object" ? exercise?.view : null;
      solutionButton.hidden = !solutionSteppable(view);
      solutionButton.disabled = blocked;
    }
  }
  if (typeof MutationObserver === "function")
    new MutationObserver(syncButtons).observe(runButton, {
      attributes: true,
      attributeFilter: ["disabled", "hidden"],
    });
  document.addEventListener("ds60:solution-view", syncButtons);
  document.addEventListener("ds60:lesson-opened", () => {
    // A walk belongs to the lesson it was made for.
    sequence++;
    busy = false;
    closePanel(false);
    syncButtons();
  });
  byId("runner")?.addEventListener("change", () => setTimeout(syncButtons, 0));

  function openPanel() {
    panel.hidden = false;
    panel.scrollIntoView({ block: "nearest", behavior: reduceMotion() ? "auto" : "smooth" });
  }
  function closePanel(restore = true) {
    if (panel.hidden) return;
    panel.hidden = true;
    walk = null;
    body.replaceChildren();
    if (restore && origin && !origin.hidden && document.contains(origin)) origin.focus();
  }
  function setControls(total) {
    const empty = total < 1;
    range.max = String(Math.max(total, 1));
    range.disabled = total < 2;
    for (const button of Object.values(controls)) button.disabled = empty;
    byId("step-controls").hidden = empty;
  }
  function showMessage(text, error = false) {
    statusLine.textContent = text;
    statusLine.dataset.state = error ? "error" : "";
  }

  async function startWalk(purpose, trigger) {
    const language = stepLanguage();
    if (!language || busy) return;
    const view = purpose === "solution" ? exercise?.view : null;
    const code = purpose === "solution" ? solutionCode(view) : byId("source").value;
    origin = trigger;
    title.textContent =
      purpose === "solution"
        ? "Step through the worked solution"
        : language === "sql"
          ? "Step through your query"
          : "Step through your code";
    sourceLabel.textContent =
      purpose === "solution"
        ? (view?.title || "Worked solution") + ". Your own code is not changed."
        : language === "sql"
          ? "The query under your cursor, taken apart clause by clause in the order the database works."
          : "A snapshot of the code in your editor, run one line at a time.";
    narration.textContent = "";
    body.replaceChildren();
    setControls(0);
    openPanel();
    if (!code?.trim()) {
      showMessage(
        language === "sql"
          ? "There is no query in the editor yet. Write a SELECT statement, then choose Step through."
          : "There is no code in the editor yet. Write a line or two, then choose Step through.",
        true,
      );
      title.focus();
      return;
    }
    const fields = {
      lesson_id: current.id,
      language,
      code,
      purpose: purpose === "solution" ? "solution" : "practice",
      timeout_seconds: Number(byId("timeout")?.value) || 60,
    };
    if (purpose === "solution" && view?.kind === "exercise" && Number.isInteger(view.number))
      fields.exercise = view.number;
    if (language === "sql" && purpose !== "solution") {
      const editor = globalThis.DS60SourceEditor,
        cursor = editor?.cursor?.() ?? byId("source").selectionStart;
      if (Number.isInteger(cursor)) fields.cursor_offset = cursor;
    }
    const ticket = ++sequence,
      lessonAtStart = current.id;
    busy = true;
    syncButtons();
    panel.setAttribute("aria-busy", "true");
    showMessage(
      language === "sql"
        ? "Taking the query apart. Each clause runs on its own so you can see what it does..."
        : "Running the code once and recording every step. Nothing is saved...",
    );
    try {
      const result = await lab("step-through", fields, false);
      if (ticket !== sequence || current?.id !== lessonAtStart) return;
      walk = { ...result, purpose, language, code, lesson: lessonAtStart };
      render(true);
    } catch (error) {
      if (ticket !== sequence) return;
      showMessage("Step-through could not start. " + error.message, true);
      title.focus();
    } finally {
      if (ticket === sequence) {
        busy = false;
        panel.removeAttribute("aria-busy");
        syncButtons();
      }
    }
  }
  startButton.addEventListener("click", () => startWalk("practice", startButton));
  solutionButton?.addEventListener("click", () => startWalk("solution", solutionButton));
  byId("step-close")?.addEventListener("click", () => closePanel(true));

  function render(fresh = false) {
    if (!walk) return;
    const steps = walk.steps || [],
      notes = [];
    if (walk.database_preparation?.message) notes.push(walk.database_preparation.message);
    if (walk.kind === "sql") {
      if (walk.unsupported) notes.push(walk.unsupported);
      else if (walk.error && !steps.length) notes.push(walk.error);
    } else if (!steps.length) {
      notes.push(
        walk.error
          ? "The code stopped before its first step. " + describeError(walk.error)
          : "There was nothing to step through. Add a line that does something, such as print(1).",
      );
    }
    if (fresh) position = 0;
    position = Math.min(Math.max(position, 0), Math.max(steps.length - 1, 0));
    setControls(steps.length);
    range.value = String(position + 1);
    count.textContent = steps.length ? "Step " + (position + 1) + " of " + steps.length : "";
    range.setAttribute(
      "aria-valuetext",
      steps.length ? "Step " + (position + 1) + " of " + steps.length : "No steps",
    );
    controls.first.disabled = controls.prev.disabled = position === 0 || !steps.length;
    controls.next.disabled = controls.last.disabled = position >= steps.length - 1;
    panel.dataset.kind = walk.kind;
    if (steps.length && walk.kind === "python") notes.push(...pythonEnding(position, steps));
    if (steps.length && walk.kind === "sql" && position === steps.length - 1)
      notes.push(sqlEnding(steps));
    showMessage(
      notes.join(" "),
      Boolean(!steps.length || (walk.kind === "sql" && walk.unsupported)),
    );
    if (!steps.length) {
      narration.textContent = "";
      body.replaceChildren();
      title.focus();
      return;
    }
    if (walk.kind === "sql") renderSql(steps, position);
    else renderPython(steps, position);
    if (fresh) controls.next.disabled ? controls.prev.focus() : controls.next.focus();
  }
  function go(target) {
    if (!walk?.steps?.length) return;
    const next = Math.min(Math.max(target, 0), walk.steps.length - 1);
    if (next === position) return;
    position = next;
    render();
  }
  controls.first.addEventListener("click", () => go(0));
  controls.prev.addEventListener("click", () => go(position - 1));
  controls.next.addEventListener("click", () => go(position + 1));
  controls.last.addEventListener("click", () => go((walk?.steps?.length || 1) - 1));
  range.addEventListener("input", () => go(Number(range.value) - 1));
  panel.addEventListener("keydown", (event) => {
    if (event.target === range || typing(event.target) || event.altKey || event.metaKey) return;
    if (event.ctrlKey) return;
    const moves = {
      ArrowRight: position + 1,
      ArrowLeft: position - 1,
      Home: 0,
      End: (walk?.steps?.length || 1) - 1,
    };
    if (event.key === "Escape") {
      event.preventDefault();
      closePanel(true);
    } else if (event.key in moves && walk?.steps?.length) {
      event.preventDefault();
      go(moves[event.key]);
    }
  });

  // Python ----------------------------------------------------------------------
  const where = (name) => (!name || name === "<module>" ? "the main program" : name + "()");
  function describeError(error) {
    if (!error) return "";
    const kind = error.type || "Error";
    return (
      kind +
      (error.message ? ": " + error.message : "") +
      (error.line ? " (line " + error.line + ")" : "") +
      "."
    );
  }
  function pythonEnding(index, steps) {
    if (index !== steps.length - 1) return [];
    if (walk.step_limit_reached)
      return [
        "Stepping stopped after " +
          plural(steps.length, "step") +
          " to keep things readable. Long loops are cut short here; Run code runs the whole program.",
      ];
    if (walk.stopped)
      return ["Stepping stopped at the time limit. Run code shows the complete result."];
    if (walk.error) return ["The program stopped with an error. " + describeError(walk.error)];
    return ["That is the last step. The program finished without an error."];
  }
  function lineText(number) {
    return (walk.code || "").split("\n")[number - 1] ?? "";
  }
  function frameVariables(step) {
    const frames = step?.stack || [];
    return frames.length ? frames[frames.length - 1] : null;
  }
  function narratePython(steps, index) {
    const step = steps[index],
      previous = steps[index - 1],
      code = shorten(lineText(step.line), 70),
      parts = [];
    if (step.event === "call") {
      const inputs = (frameVariables(step)?.variables || [])
        .slice(0, 4)
        .map((item) => item.name + " = " + shorten(item.value, 24));
      parts.push(
        "Python calls " +
          where(step.function) +
          (inputs.length ? " with " + inputs.join(", ") : "") +
          ". It jumps to line " +
          step.line +
          ".",
      );
    } else if (step.event === "return") {
      parts.push(
        step.function === "<module>"
          ? "The program reaches its end."
          : where(step.function) +
              " finishes and hands back " +
              (step.return_value === undefined || step.return_value === null
                ? "nothing (None)"
                : shorten(step.return_value, 40)) +
              ".",
      );
    } else if (step.event === "exception") {
      parts.push(
        "Line " + step.line + " raises an error: " + shorten(step.exception || "error", 90) + ".",
      );
    } else {
      parts.push("Next, Python runs line " + step.line + (code ? ": " + code : "") + ".");
    }
    if (previous && step.output_length > previous.output_length) {
      const printed = (walk.output || "").slice(previous.output_length, step.output_length);
      parts.push(
        "Line " + previous.line + " printed " + JSON.stringify(shorten(printed, 50)) + ".",
      );
    }
    return parts.join(" ");
  }
  function renderPython(steps, index) {
    const step = steps[index],
      previous = steps[index - 1];
    narration.textContent = narratePython(steps, index);
    const grid = make("div", null, "step-grid"),
      listing = make("div", null, "step-listing"),
      lines = make("ol", null, "step-code");
    listing.setAttribute("aria-label", "Code with the current line marked");
    listing.tabIndex = 0;
    const source = (walk.code || "").replace(/\n$/, "").split("\n");
    source.forEach((text, offset) => {
      const number = offset + 1,
        row = make("li");
      row.append(make("span", String(number), "step-ln"), make("code", text || " "));
      if (number === step.line) {
        row.className = step.event === "exception" ? "is-current is-error" : "is-current";
        row.setAttribute("aria-current", "step");
        row.prepend(make("span", step.event === "exception" ? "Error here" : "Next", "sr-only"));
      } else if (previous && number === previous.line && previous.line !== step.line) {
        row.className = "is-previous";
      }
      lines.append(row);
    });
    listing.append(lines);
    grid.append(listing, pythonSide(step, previous));
    body.replaceChildren(grid);
    const marked = lines.querySelector(".is-current");
    if (marked) {
      const top = marked.offsetTop - listing.clientHeight / 2 + marked.offsetHeight / 2;
      listing.scrollTop = Math.max(0, top);
    }
  }
  function pythonSide(step, previous) {
    const side = make("div", null, "step-side"),
      frame = frameVariables(step),
      before = frameVariables(previous),
      sameFrame =
        before &&
        frame &&
        before.function === frame.function &&
        (previous.stack || []).length === (step.stack || []).length;
    const vars = make("section", null, "step-vars");
    vars.append(make("h4", "Variables in " + where(frame?.function || step.function)));
    const known = new Map(
      sameFrame ? (before.variables || []).map((item) => [item.name, item.value]) : [],
    );
    const items = frame?.variables || [];
    if (!items.length) {
      vars.append(
        make(
          "p",
          "No variables yet. They appear here as soon as a line gives a name a value.",
          "step-empty",
        ),
      );
    } else {
      const table = make("table", null, "step-table"),
        head = make("tr");
      head.append(make("th", "Name"), make("th", "Value"), make("th", "Type"));
      const headGroup = make("thead");
      headGroup.append(head);
      const rows = make("tbody");
      for (const item of items) {
        const row = make("tr"),
          name = make("td", null, "step-name");
        name.append(make("code", item.name));
        let change = "";
        if (sameFrame && !known.has(item.name)) change = "new";
        else if (sameFrame && known.get(item.name) !== item.value) change = "changed";
        if (change) {
          row.dataset.change = change;
          name.append(make("span", change, "step-flag"));
        }
        const value = make("td", null, "step-value");
        value.append(make("code", item.value));
        row.append(name, value, make("td", item.type, "step-type"));
        rows.append(row);
      }
      table.append(headGroup, rows);
      vars.append(table);
    }
    side.append(vars);
    const stack = step.stack || [];
    if (stack.length > 1) {
      const calls = make("section", null, "step-stack"),
        list = make("ol");
      calls.append(make("h4", "Calls in progress"));
      stack.forEach((item, offset) => {
        const entry = make(
          "li",
          where(item.function) + ", line " + item.line,
          offset === stack.length - 1 ? "is-current" : "",
        );
        list.append(entry);
      });
      calls.append(
        list,
        make(
          "p",
          "The bottom one is running now. When it finishes, Python goes back to the one above it.",
          "step-empty",
        ),
      );
      side.append(calls);
    }
    const out = make("section", null, "step-output"),
      printed = (walk.output || "").slice(0, step.output_length || 0),
      fresh = previous ? Math.max(0, (step.output_length || 0) - (previous.output_length || 0)) : 0;
    out.append(make("h4", "Printed so far"));
    const log = make("pre", null, "result-log step-log");
    if (!printed) {
      log.dataset.note = "true";
      log.textContent = "Nothing printed yet.";
    } else {
      log.append(printed.slice(0, printed.length - fresh));
      if (fresh) log.append(make("mark", printed.slice(printed.length - fresh)));
    }
    out.append(log);
    side.append(out);
    return side;
  }

  // SQL -------------------------------------------------------------------------
  function sqlEnding(steps) {
    const last = steps[steps.length - 1];
    if (last.error) return "This clause stopped with an error: " + last.error;
    return (
      "That is the whole query. Its final result has " +
      plural(last.row_count ?? 0, "row") +
      ". Run code runs it for real."
    );
  }
  function renderSql(steps, index) {
    const step = steps[index];
    narration.textContent =
      "Step " + (index + 1) + ": " + (step.title || step.clause) + ". " + (step.explanation || "");
    const wrap = make("div", null, "step-sql"),
      timeline = make("ol", null, "step-clauses");
    timeline.setAttribute("aria-label", "Clauses in the order the database works on them");
    steps.forEach((item, offset) => {
      const entry = make("li"),
        button = make("button", null, "step-clause");
      button.type = "button";
      button.append(make("span", String(offset + 1), "step-clause-num"), item.clause);
      if (offset === index) button.setAttribute("aria-current", "step");
      if (offset < index) button.dataset.done = "true";
      button.addEventListener("click", () => {
        go(offset);
        timeline.querySelectorAll("button")[offset]?.focus();
      });
      entry.append(button);
      timeline.append(entry);
    });
    const statement = make("pre", null, "step-statement"),
      text = walk.statement || "",
      [start, end] = Array.isArray(step.highlight) ? step.highlight : [0, 0];
    statement.setAttribute("aria-label", "The query, with this step's clause marked");
    if (end > start) {
      statement.append(text.slice(0, start));
      statement.append(make("mark", text.slice(start, end)));
      statement.append(text.slice(end));
    } else statement.textContent = text;
    const detail = make("div", null, "step-sql-detail");
    detail.append(make("h4", step.title || step.clause));
    if (step.explanation) detail.append(make("p", step.explanation, "step-explain"));
    if (step.error) {
      detail.append(make("p", step.error, "step-error"));
    } else {
      const total = step.row_count ?? (step.rows || []).length;
      detail.append(
        make(
          "p",
          plural(total, "row") +
            " after this step" +
            (step.rows_truncated ? ". Showing the first " + (step.rows || []).length + "." : "."),
          "step-rows",
        ),
      );
      if ((step.columns || []).length) detail.append(sqlTable(step));
    }
    if (step.sql) {
      const peek = make("details", null, "step-peek"),
        summary = make("summary", "The query the classroom ran for this step");
      peek.append(summary, make("pre", step.sql, "step-statement"));
      detail.append(peek);
    }
    wrap.append(timeline, statement, detail);
    body.replaceChildren(wrap);
  }
  function sqlTable(step) {
    const scroll = make("div", null, "sql-results step-sql-table"),
      table = make("table"),
      head = make("thead"),
      headRow = make("tr"),
      rows = make("tbody");
    for (const column of step.columns) headRow.append(make("th", column));
    head.append(headRow);
    for (const row of step.rows || []) {
      const line = make("tr");
      for (const cell of row) line.append(make("td", cell === null ? "NULL" : String(cell)));
      rows.append(line);
    }
    table.append(head, rows);
    scroll.append(table);
    return scroll;
  }

  // Page tour -------------------------------------------------------------------
  const tourButton = byId("tour-start"),
    manualTour = byId("manual-tour");
  const visible = (element) => {
    if (!element || element.hidden || element.closest("[hidden]")) return false;
    const box = element.getBoundingClientRect();
    return box.width > 0 && box.height > 0;
  };
  const tourSteps = () => [
    {
      target: () =>
        visible(byId("lesson-sidebar")) ? byId("lesson-sidebar") : byId("lesson-menu"),
      title: "The lesson list",
      text: "Every lesson in this subject, in order. Choose one to open it. Switch subject and search for a topic at the top of the list.",
    },
    {
      target: () => document.querySelector(".lesson-heading"),
      title: "Where you are",
      text: "The lesson title and what you will be able to do afterwards. Previous and Next move through the subject one lesson at a time.",
    },
    {
      target: () => byId("capability"),
      title: "Is this lesson ready?",
      text: "This line says whether the code runner for this lesson is ready. If it is not, it tells you what to start.",
    },
    {
      target: () => document.querySelector(".reading-pane"),
      title: "Read the lesson",
      text: "Explanations and worked examples. Read it first. Contents jumps to a section, and Focus on reading widens the page.",
    },
    {
      target: () => byId("exercise-dock"),
      title: "Exercises",
      text: "Practice problems for this lesson. Open one, try it in your editor, use the hints, and only then reveal the worked solution.",
    },
    {
      target: () => byId("source-section"),
      title: "Your code",
      text: "Type here. Your work is saved on this computer as you go, so you can leave and come back.",
    },
    {
      target: () => document.querySelector(".run-tools"),
      title: "Run it",
      text: "Run code runs everything in the editor (Ctrl+Enter, or Cmd+Enter on a Mac). For Python and SQL, Step through runs it one step at a time so you can watch what changes. Run settings holds the time limit.",
    },
    {
      target: () => byId("runtime-results"),
      title: "See what happened",
      text: "Printed output, tables and error messages appear here. An error names the line to look at.",
    },
  ];
  let tour = null;
  function endTour() {
    if (!tour) return;
    const { layer, back, onMove } = tour;
    tour = null;
    layer.remove();
    window.removeEventListener("resize", onMove);
    window.removeEventListener("scroll", onMove, true);
    remember("tour-seen", true);
    byId("tour-offer")?.remove();
    if (back && document.contains(back) && !back.hidden) back.focus();
  }
  function placeTour() {
    if (!tour) return;
    const { spot, card, steps } = tour,
      target = steps[tour.index].target();
    if (!visible(target)) return;
    const box = target.getBoundingClientRect(),
      pad = 6,
      top = Math.max(box.top - pad, 4),
      left = Math.max(box.left - pad, 4),
      width = Math.min(box.width + pad * 2, innerWidth - left - 4),
      height = Math.min(box.height + pad * 2, innerHeight - top - 4);
    Object.assign(spot.style, {
      transform: "translate(" + left + "px, " + top + "px)",
      width: width + "px",
      height: height + "px",
    });
    const cardBox = card.getBoundingClientRect(),
      gap = 14;
    let x, y;
    if (left + width + gap + cardBox.width <= innerWidth - 12) {
      x = left + width + gap;
      y = top;
    } else if (top + height + gap + cardBox.height <= innerHeight - 12) {
      x = left;
      y = top + height + gap;
    } else if (top - gap - cardBox.height >= 12) {
      x = left;
      y = top - gap - cardBox.height;
    } else if (left - gap - cardBox.width >= 12) {
      x = left - gap - cardBox.width;
      y = top;
    } else {
      x = innerWidth - cardBox.width - 24;
      y = innerHeight - cardBox.height - 24;
    }
    x = Math.min(Math.max(x, 12), innerWidth - cardBox.width - 12);
    y = Math.min(Math.max(y, 12), innerHeight - cardBox.height - 12);
    card.style.transform = "translate(" + Math.round(x) + "px, " + Math.round(y) + "px)";
  }
  function showTourStep(index) {
    if (!tour) return;
    tour.index = index;
    const step = tour.steps[index],
      { card } = tour;
    card.querySelector(".tour-count").textContent =
      "Part " + (index + 1) + " of " + tour.steps.length;
    card.querySelector(".tour-title").textContent = step.title;
    card.querySelector(".tour-text").textContent = step.text;
    card.querySelector(".tour-back").disabled = index === 0;
    const next = card.querySelector(".tour-next");
    next.textContent = index === tour.steps.length - 1 ? "Finish" : "Next";
    const target = step.target();
    target.scrollIntoView({ block: "center", behavior: "auto" });
    placeTour();
    card.querySelector(".tour-title").focus();
  }
  function startTour(back = document.activeElement) {
    if (tour || typeof current !== "object" || !current) return;
    if (manualOpen) return;
    byId("tour-offer")?.remove();
    const steps = tourSteps().filter((step) => visible(step.target()));
    if (!steps.length) return;
    const layer = make("div", null, "tour-layer"),
      spot = make("div", null, "tour-spot"),
      card = make("section", null, "tour-card");
    card.setAttribute("role", "dialog");
    card.setAttribute("aria-modal", "true");
    card.setAttribute("aria-labelledby", "tour-title");
    card.setAttribute("aria-describedby", "tour-text");
    const heading = make("h2", null, "tour-title"),
      text = make("p", null, "tour-text"),
      actions = make("div", null, "tour-actions"),
      skip = make("button", "End tour", "quiet tour-skip"),
      backButton = make("button", "Back", "tour-back"),
      next = make("button", "Next", "primary tour-next");
    heading.id = "tour-title";
    heading.tabIndex = -1;
    text.id = "tour-text";
    for (const button of [skip, backButton, next]) button.type = "button";
    actions.append(skip, backButton, next);
    card.append(make("p", null, "tour-count"), heading, text, actions);
    spot.setAttribute("aria-hidden", "true");
    layer.append(spot, card);
    document.body.append(layer);
    let frame = 0;
    const onMove = () => {
      if (frame) return;
      frame = requestAnimationFrame(() => {
        frame = 0;
        placeTour();
      });
    };
    tour = { layer, spot, card, steps, index: 0, back, onMove };
    window.addEventListener("resize", onMove);
    window.addEventListener("scroll", onMove, true);
    skip.addEventListener("click", endTour);
    backButton.addEventListener("click", () => showTourStep(Math.max(0, tour.index - 1)));
    next.addEventListener("click", () =>
      tour.index >= tour.steps.length - 1 ? endTour() : showTourStep(tour.index + 1),
    );
    layer.addEventListener("click", (event) => {
      if (event.target === layer) card.querySelector(".tour-title").focus();
    });
    layer.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        endTour();
      } else if (event.key === "ArrowRight" && !typing(event.target)) {
        event.preventDefault();
        if (tour.index < tour.steps.length - 1) showTourStep(tour.index + 1);
      } else if (event.key === "ArrowLeft" && !typing(event.target)) {
        event.preventDefault();
        if (tour.index > 0) showTourStep(tour.index - 1);
      } else if (event.key === "Tab") {
        const focusable = [...card.querySelectorAll("button:not(:disabled)")],
          first = focusable[0],
          last = focusable[focusable.length - 1];
        if (
          event.shiftKey &&
          (document.activeElement === first || document.activeElement === heading)
        ) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    });
    showTourStep(0);
  }
  tourButton?.addEventListener("click", () => startTour(tourButton));

  // "Show me on a lesson page" in the manual: return to the open lesson, then start the tour.
  function waitForLesson() {
    return new Promise((resolve) => {
      const done = () => {
        document.removeEventListener("ds60:lesson-opened", done);
        resolve();
      };
      document.addEventListener("ds60:lesson-opened", done);
      setTimeout(done, 15000);
    });
  }
  async function tourFromAnywhere() {
    try {
      const lesson = typeof current === "object" && current && lessonId;
      if (!lesson) {
        status("Choose a lesson before starting the tour.");
        return;
      }
      if (manualOpen) await hideManual();
      else if (byId("workspace-view")?.hidden) {
        const opened = waitForLesson();
        await openLesson(lessonId, true);
        await opened;
      }
      setTimeout(() => startTour(tourButton), 60);
    } catch (error) {
      if (typeof status === "function") status(error.message, true);
    }
  }
  manualTour?.addEventListener("click", tourFromAnywhere);
  byId("home-tour")?.addEventListener("click", tourFromAnywhere);

  // First visit: offer the tour once, quietly, next to its button.
  document.addEventListener("ds60:lesson-opened", () => {
    syncButtons();
    if (pref("tour-seen", false) || byId("tour-offer") || tour || !tourButton) return;
    if (byId("workspace-view")?.hidden || byId("authored")?.hidden) return;
    const offer = make("p", null, "tour-offer"),
      take = make("button", "Take the 1-minute tour", "primary"),
      later = make("button", "No thanks", "quiet");
    offer.id = "tour-offer";
    offer.setAttribute("role", "status");
    take.type = later.type = "button";
    offer.append(make("span", "First time here?"), take, later);
    take.addEventListener("click", () => startTour(tourButton));
    later.addEventListener("click", () => {
      remember("tour-seen", true);
      offer.remove();
      tourButton.focus();
    });
    tourButton.after(offer);
  });

  syncButtons();
})();
