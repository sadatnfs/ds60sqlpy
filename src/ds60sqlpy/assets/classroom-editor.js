"use strict";
// classroom.js loads first and defines the open lesson as a shared script global.
/* global current */
// Progressive enhancement: replace the visible source textarea with the bundled
// offline code editor. The textarea stays in the DOM and keeps its value API, so
// saving, running, history and recovery code continue to read and write it.
(() => {
  const textarea = document.getElementById("source");
  const factory = globalThis.DS60Editor;
  const native =
    typeof HTMLTextAreaElement === "function"
      ? Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, "value")
      : null;
  if (!textarea || typeof factory?.create !== "function" || !native?.get || !native?.set) return;

  const lesson = () => (typeof current === "object" && current ? current : null);
  const host = document.createElement("div");
  host.className = "code-editor";
  host.id = "source-editor";
  textarea.insertAdjacentElement("afterend", host);

  let editor;
  try {
    editor = factory.create(host, {
      doc: native.get.call(textarea),
      ariaLabel: "Source code editor",
      ariaDescribedBy: "source-help",
      onChange(text) {
        native.set.call(textarea, text);
        textarea.dispatchEvent(new Event("input", { bubbles: true }));
      },
    });
  } catch (error) {
    host.remove();
    console.warn("The code editor could not start; the plain text area remains available.", error);
    return;
  }

  // Long code scrolls inside the editor; an explicit tab stop on the editable
  // content tells assistive checks that the scrolling region is reachable.
  editor.view?.contentDOM?.setAttribute("tabindex", "0");

  let languageKey = null;
  function syncLanguage() {
    const data = lesson();
    const names = data
      ? [
          data.runtime_profile === "dbt-duckdb" ? "sql" : null,
          data.runtime_profile === "html-browser" ? "html" : null,
          data.runtime_profile === "javascript-browser" ? "javascript" : null,
          data.runner?.id,
          data.language,
          data.runtime_profile,
        ]
      : [];
    const key = factory.resolveLanguage(...names);
    if (key !== languageKey) languageKey = editor.setLanguage(...names);
    host.dataset.language = languageKey || "text";
    editor.setLabel(
      (data?.language ? data.language + " " : "") + "source code editor",
      "source-help",
    );
  }

  Object.defineProperty(textarea, "value", {
    configurable: true,
    get: () => editor.getValue(),
    set(value) {
      native.set.call(textarea, value);
      syncLanguage();
      editor.setValue(value);
    },
  });
  textarea.focus = () => editor.focus();
  textarea.setSelectionRange = (start, end) => editor.select(start, end);
  textarea.classList.add("source-enhanced");
  textarea.setAttribute("aria-hidden", "true");
  textarea.tabIndex = -1;
  document.body.classList.add("has-code-editor");
  document.querySelector('label[for="source"]')?.addEventListener("click", (event) => {
    event.preventDefault();
    editor.focus();
  });
  globalThis.DS60SourceEditor = {
    focus: () => editor.focus(),
    hasFocus: () => editor.hasFocus(),
    contains: (element) => host.contains(element),
    markErrorLine: (line) => editor.markErrorLine?.(line) ?? false,
    goToLine: (line, column) => editor.goToLine?.(line, column) ?? false,
    // Undoable replacement chosen by the learner; reports the change like typing.
    replace: (text) => {
      if (typeof editor.replace !== "function") return false;
      syncLanguage();
      return editor.replace(text);
    },
    undo: () => (typeof editor.undo === "function" ? editor.undo() : false),
    // Character offset of the caret, used to pick the SQL statement to step through.
    cursor: () => editor.view?.state.selection.main.head ?? null,
  };

  // A keyboard- and pointer-operable handle sets the editor height; the choice
  // is remembered on this computer. Double-click returns to the automatic height.
  const handle = document.createElement("div"),
    storageKey = "ds60.classroom.editor-height",
    clampHeight = (value) =>
      Math.round(Math.max(160, Math.min(value, Math.max(320, window.innerHeight - 140))));
  handle.className = "editor-resize";
  handle.tabIndex = 0;
  handle.setAttribute("role", "separator");
  handle.setAttribute("aria-orientation", "horizontal");
  handle.setAttribute("aria-label", "Editor height. Use the up and down arrow keys to resize.");
  host.insertAdjacentElement("afterend", handle);
  // A focusable separator reports its value; the automatic height is measured.
  function describeHeight(automatic) {
    const max = Math.max(320, window.innerHeight - 140),
      height = Math.min(max, Math.max(160, Math.round(host.getBoundingClientRect().height)));
    handle.setAttribute("aria-valuemin", "160");
    handle.setAttribute("aria-valuemax", String(max));
    handle.setAttribute("aria-valuenow", String(height));
    handle.setAttribute(
      "aria-valuetext",
      (automatic ? "Automatic height, " : "") + height + " pixels",
    );
  }
  function applyHeight(value, save) {
    if (value === null) {
      host.style.removeProperty("--editor-height");
      delete host.dataset.sized;
    } else {
      const height = clampHeight(value);
      host.style.setProperty("--editor-height", height + "px");
      host.dataset.sized = "true";
    }
    describeHeight(value === null);
    if (!save) return;
    try {
      if (value === null) localStorage.removeItem(storageKey);
      else localStorage.setItem(storageKey, String(clampHeight(value)));
    } catch (_) {}
  }
  try {
    const saved = Number(localStorage.getItem(storageKey));
    if (saved > 0) applyHeight(saved, false);
    else describeHeight(true);
  } catch (_) {
    describeHeight(true);
  }
  handle.addEventListener("focus", () => describeHeight(host.dataset.sized !== "true"));
  handle.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;
    event.preventDefault();
    const startY = event.clientY,
      startHeight = host.getBoundingClientRect().height;
    handle.setPointerCapture(event.pointerId);
    handle.dataset.dragging = "true";
    const move = (moveEvent) => applyHeight(startHeight + moveEvent.clientY - startY, false);
    const stop = (upEvent) => {
      handle.removeEventListener("pointermove", move);
      handle.removeEventListener("pointerup", stop);
      handle.removeEventListener("pointercancel", stop);
      delete handle.dataset.dragging;
      applyHeight(startHeight + upEvent.clientY - startY, true);
    };
    handle.addEventListener("pointermove", move);
    handle.addEventListener("pointerup", stop);
    handle.addEventListener("pointercancel", stop);
  });
  handle.addEventListener("keydown", (event) => {
    const step = event.shiftKey ? 120 : 40;
    if (event.key === "ArrowUp" || event.key === "ArrowDown") {
      event.preventDefault();
      const height = host.getBoundingClientRect().height;
      applyHeight(height + (event.key === "ArrowDown" ? step : -step), true);
    } else if (event.key === "Home" || event.key === "Escape") {
      event.preventDefault();
      applyHeight(null, true);
    }
  });
  handle.addEventListener("dblclick", () => applyHeight(null, true));
  syncLanguage();
})();
