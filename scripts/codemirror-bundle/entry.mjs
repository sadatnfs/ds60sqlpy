// Offline code editor bundle for the DS60 classroom. The build exposes one
// global, DS60Editor, so the classroom can enhance its plain source textarea
// without a module loader, network request or CDN.
import { closeBrackets, closeBracketsKeymap } from "@codemirror/autocomplete";
import { defaultKeymap, history, historyKeymap, indentWithTab, undo } from "@codemirror/commands";
import { cpp } from "@codemirror/lang-cpp";
import { css } from "@codemirror/lang-css";
import { go } from "@codemirror/lang-go";
import { html } from "@codemirror/lang-html";
import { java } from "@codemirror/lang-java";
import { javascript } from "@codemirror/lang-javascript";
import { json } from "@codemirror/lang-json";
import { markdown } from "@codemirror/lang-markdown";
import { php } from "@codemirror/lang-php";
import { python } from "@codemirror/lang-python";
import { rust } from "@codemirror/lang-rust";
import { PostgreSQL, sql } from "@codemirror/lang-sql";
import { yaml } from "@codemirror/lang-yaml";
import {
  StreamLanguage,
  bracketMatching,
  foldKeymap,
  indentOnInput,
  indentUnit,
  syntaxHighlighting,
} from "@codemirror/language";
import { csharp, kotlin, scala } from "@codemirror/legacy-modes/mode/clike";
import { dockerFile } from "@codemirror/legacy-modes/mode/dockerfile";
import { julia } from "@codemirror/legacy-modes/mode/julia";
import { r } from "@codemirror/legacy-modes/mode/r";
import { shell } from "@codemirror/legacy-modes/mode/shell";
import { swift } from "@codemirror/legacy-modes/mode/swift";
import { toml } from "@codemirror/legacy-modes/mode/toml";
import { highlightSelectionMatches, searchKeymap } from "@codemirror/search";
import {
  Compartment,
  EditorSelection,
  EditorState,
  RangeSet,
  RangeSetBuilder,
  StateEffect,
  StateField,
  Transaction,
} from "@codemirror/state";
import {
  Decoration,
  EditorView,
  GutterMarker,
  ViewPlugin,
  drawSelection,
  dropCursor,
  gutterLineClass,
  highlightActiveLine,
  highlightActiveLineGutter,
  highlightSpecialChars,
  keymap,
  lineNumbers,
  rectangularSelection,
} from "@codemirror/view";
import { classHighlighter } from "@lezer/highlight";

const legacy = (mode) => () => StreamLanguage.define(mode);
const LANGUAGES = {
  python: () => python(),
  sql: () => sql({ dialect: PostgreSQL }),
  javascript: () => javascript(),
  typescript: () => javascript({ typescript: true }),
  html: () => html(),
  css: () => css(),
  json: () => json(),
  cpp: () => cpp(),
  java: () => java(),
  rust: () => rust(),
  go: () => go(),
  php: () => php(),
  markdown: () => markdown(),
  yaml: () => yaml(),
  r: legacy(r),
  julia: legacy(julia),
  swift: legacy(swift),
  scala: legacy(scala),
  csharp: legacy(csharp),
  kotlin: legacy(kotlin),
  shell: legacy(shell),
  dockerfile: legacy(dockerFile),
  toml: legacy(toml),
};
const ALIASES = {
  py: "python",
  ipynb: "python",
  postgres: "sql",
  postgresql: "sql",
  "sql+jinja": "sql",
  dbt: "sql",
  js: "javascript",
  mjs: "javascript",
  node: "javascript",
  ts: "typescript",
  mts: "typescript",
  c: "cpp",
  "c++": "cpp",
  cc: "cpp",
  cu: "cpp",
  cuda: "cpp",
  stan: "cpp",
  rs: "rust",
  golang: "go",
  cs: "csharp",
  "c#": "csharp",
  sh: "shell",
  bash: "shell",
  yml: "yaml",
  md: "markdown",
  jl: "julia",
};

// Wrapped lines keep their indentation plus a two-column continuation indent, so a
// long comment or call never looks like a new, unindented line of code.
const hangCache = new Map();
function hangDecoration(columns) {
  let decoration = hangCache.get(columns);
  if (!decoration) {
    decoration = Decoration.line({
      class: "cm-hang",
      attributes: { style: `--hang:${columns}ch` },
    });
    hangCache.set(columns, decoration);
  }
  return decoration;
}
const hangingIndent = ViewPlugin.fromClass(
  class {
    constructor(view) {
      this.decorations = this.build(view);
    }
    update(update) {
      if (update.docChanged || update.viewportChanged) this.decorations = this.build(update.view);
    }
    build(view) {
      const builder = new RangeSetBuilder();
      const { doc, tabSize } = view.state;
      for (const { from, to } of view.visibleRanges) {
        for (let position = from; position <= to; ) {
          const line = doc.lineAt(position);
          let columns = 0;
          for (const character of line.text) {
            if (character === " ") columns += 1;
            else if (character === "\t") columns += tabSize - (columns % tabSize);
            else break;
          }
          builder.add(line.from, line.from, hangDecoration(Math.min(columns, 80) + 2));
          position = line.to + 1;
        }
      }
      return builder.finish();
    }
  },
  { decorations: (plugin) => plugin.decorations },
);

// One diagnostic line from the latest run. Any edit clears it, because the old
// line number may no longer point at the same code.
const setErrorLine = StateEffect.define();
const errorLineMark = Decoration.line({ class: "cm-errorLine" });
const errorGutterMark = new (class extends GutterMarker {
  elementClass = "cm-errorGutter";
})();
const errorLineField = StateField.define({
  create: () => null,
  update(value, transaction) {
    for (const effect of transaction.effects) if (effect.is(setErrorLine)) value = effect.value;
    return value && transaction.docChanged ? null : value;
  },
  provide: (field) => [
    EditorView.decorations.from(field, (value) =>
      value === null ? Decoration.none : Decoration.set([errorLineMark.range(value)]),
    ),
    gutterLineClass.from(field, (value) =>
      value === null ? RangeSet.empty : RangeSet.of([errorGutterMark.range(value)]),
    ),
  ],
});

/** Map a classroom language or runtime name to a supported grammar key. */
export function resolveLanguage(...names) {
  for (const raw of names) {
    if (typeof raw !== "string" || !raw) continue;
    const name = raw.toLowerCase();
    if (LANGUAGES[name]) return name;
    if (ALIASES[name]) return ALIASES[name];
    const stem = name.split(/[-_.\s]/)[0];
    if (LANGUAGES[stem]) return stem;
    if (ALIASES[stem]) return ALIASES[stem];
  }
  return null;
}

function languageExtensions(key) {
  const support = key && LANGUAGES[key] ? LANGUAGES[key]() : [];
  return [support, indentUnit.of(key === "go" ? "\t" : "    ")];
}

/**
 * Create an editor in host. Callbacks: onChange(text) after learner edits.
 * Mod-Enter is consumed without inserting text so the page shortcut runs code.
 */
export function create(host, options = {}) {
  const language = new Compartment(),
    editable = new Compartment(),
    attributes = new Compartment(),
    undoHistory = new Compartment();
  let quiet = false;
  const contentAttributes = (label, describedBy) =>
    EditorView.contentAttributes.of({
      "aria-label": label || "Source code editor",
      ...(describedBy ? { "aria-describedby": describedBy } : {}),
      spellcheck: "false",
      autocapitalize: "off",
      autocorrect: "off",
    });
  const view = new EditorView({
    parent: host,
    state: EditorState.create({
      doc: options.doc || "",
      extensions: [
        lineNumbers(),
        highlightActiveLineGutter(),
        highlightSpecialChars(),
        undoHistory.of(history()),
        drawSelection(),
        dropCursor(),
        EditorState.allowMultipleSelections.of(true),
        indentOnInput(),
        syntaxHighlighting(classHighlighter),
        bracketMatching(),
        closeBrackets(),
        rectangularSelection(),
        highlightActiveLine(),
        highlightSelectionMatches(),
        EditorView.lineWrapping,
        hangingIndent,
        errorLineField,
        keymap.of([
          { key: "Mod-Enter", run: () => true },
          ...closeBracketsKeymap,
          ...defaultKeymap,
          ...searchKeymap,
          ...historyKeymap,
          ...foldKeymap,
          indentWithTab,
        ]),
        language.of(languageExtensions(resolveLanguage(options.language))),
        editable.of([
          EditorState.readOnly.of(Boolean(options.readOnly)),
          EditorView.editable.of(!options.readOnly),
        ]),
        attributes.of(contentAttributes(options.ariaLabel, options.ariaDescribedBy)),
        EditorView.updateListener.of((update) => {
          if (update.docChanged && !quiet && typeof options.onChange === "function")
            options.onChange(update.state.doc.toString());
        }),
      ],
    }),
  });
  return {
    view,
    getValue: () => view.state.doc.toString(),
    setValue(text) {
      const value = String(text ?? ""),
        same = value === view.state.doc.toString();
      quiet = true;
      try {
        // Loading text is not a user action: never scroll the page to the editor,
        // and always start a fresh undo history, even when two lessons share the
        // same starter, so Undo cannot bring back another lesson's code.
        view.dispatch({
          ...(same
            ? {}
            : {
                changes: { from: 0, to: view.state.doc.length, insert: value },
                selection: EditorSelection.cursor(0),
              }),
          annotations: Transaction.addToHistory.of(false),
          effects: undoHistory.reconfigure([]),
        });
        view.dispatch({ effects: undoHistory.reconfigure(history()) });
        if (!same) {
          view.scrollDOM.scrollTop = 0;
          view.scrollDOM.scrollLeft = 0;
        }
      } finally {
        quiet = false;
      }
    },
    // A learner-chosen replacement (for example a worked solution): it is one
    // undoable step and reports the change like typing does.
    replace(text) {
      const value = String(text ?? "");
      if (value === view.state.doc.toString()) return false;
      view.dispatch({
        changes: { from: 0, to: view.state.doc.length, insert: value },
        selection: EditorSelection.cursor(0),
        userEvent: "input.replace",
        scrollIntoView: true,
      });
      view.scrollDOM.scrollLeft = 0;
      return true;
    },
    undo: () => undo(view),
    setLanguage(...names) {
      const key = resolveLanguage(...names);
      view.dispatch({ effects: language.reconfigure(languageExtensions(key)) });
      return key;
    },
    setReadOnly(readOnly) {
      view.dispatch({
        effects: editable.reconfigure([
          EditorState.readOnly.of(Boolean(readOnly)),
          EditorView.editable.of(!readOnly),
        ]),
      });
    },
    setLabel(label, describedBy) {
      view.dispatch({ effects: attributes.reconfigure(contentAttributes(label, describedBy)) });
    },
    select(start, end = start) {
      const length = view.state.doc.length,
        from = Math.max(0, Math.min(Number(start) || 0, length)),
        to = Math.max(from, Math.min(Number(end) || 0, length));
      view.dispatch({ selection: EditorSelection.range(from, to), scrollIntoView: true });
    },
    markErrorLine(line) {
      const number = Math.trunc(Number(line));
      const valid = number >= 1 && number <= view.state.doc.lines;
      view.dispatch({ effects: setErrorLine.of(valid ? view.state.doc.line(number).from : null) });
      return valid;
    },
    goToLine(line, column = 1) {
      const number = Math.trunc(Number(line));
      if (!(number >= 1 && number <= view.state.doc.lines)) return false;
      const target = view.state.doc.line(number),
        offset = Math.max(0, Math.min(target.length, Math.trunc(Number(column) || 1) - 1));
      view.dispatch({
        selection: EditorSelection.cursor(target.from + offset),
        effects: EditorView.scrollIntoView(target.from + offset, { y: "center" }),
      });
      view.focus();
      return true;
    },
    focus: () => view.focus(),
    hasFocus: () => view.hasFocus,
    destroy: () => view.destroy(),
  };
}

export const version = "6";
