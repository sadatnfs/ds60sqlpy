#!/usr/bin/env python3
"""Build the portable, dependency-free DS60 learning guide.

The generated ``START_HERE.html`` embeds the checked-in catalog so it works
from a clone or USB drive without a web server or network connection.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "START_HERE.html"
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ds60sqlpy.lesson_reader import (  # noqa: E402
    COURSE_GUIDE_REFERENCE_PATHS,
    reference_relative_path,
)


def _catalog_payload() -> dict[str, Any]:
    path = REPO_ROOT / "curriculum" / "catalog.json"
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    lessons = payload.get("lessons")
    if not isinstance(lessons, list) or not lessons:
        raise ValueError("curriculum/catalog.json has no lessons")
    return payload


def _embedded_catalog(payload: dict[str, Any]) -> str:
    """Return JSON that is safe inside an inline script element."""

    compact = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return compact.replace("</", "<\\/")


def build_html(payload: dict[str, Any]) -> str:
    """Render the self-contained guide from a catalog payload."""

    lessons = payload["lessons"]
    track_counts: dict[str, int] = {}
    for lesson in lessons:
        track = str(lesson["track"])
        track_counts[track] = track_counts.get(track, 0) + 1

    lesson_count = len(lessons)
    python_count = track_counts.get("python", 0)
    sql_count = track_counts.get("sql", 0)
    bridge_count = track_counts.get("bridge", 0)
    catalog_json = _embedded_catalog(payload)

    document = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <meta
    http-equiv="Content-Security-Policy"
    content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; connect-src 'self'; form-action 'none'"
  >
  <title>DS60 Learning Guide</title>
  <style>
    :root {
      --paper: #f7f3ea;
      --surface: #fffdf8;
      --surface-strong: #ffffff;
      --ink: #17221e;
      --muted: #56635d;
      --line: #d7d7ca;
      --navy: #173f5f;
      --navy-soft: #e8f0f5;
      --green: #0f6b4f;
      --green-soft: #e4f3ec;
      --gold: #9d6515;
      --gold-soft: #f7ead2;
      --red: #9c3f35;
      --shadow: 0 18px 45px rgb(28 45 37 / 10%);
      --radius: 18px;
      font-family:
        Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at 5% 0%, rgb(15 107 79 / 10%), transparent 28rem),
        radial-gradient(circle at 100% 10%, rgb(23 63 95 / 11%), transparent 30rem),
        var(--paper);
      line-height: 1.55;
    }
    a { color: var(--navy); text-underline-offset: 0.18em; }
    a:hover { color: var(--green); }
    button, input, select { font: inherit; }
    button, .button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.45rem;
      min-height: 2.65rem;
      border: 1px solid var(--navy);
      border-radius: 999px;
      padding: 0.55rem 1rem;
      color: #fff;
      background: var(--navy);
      cursor: pointer;
      text-decoration: none;
      font-weight: 700;
    }
    button:hover, .button:hover { background: var(--green); border-color: var(--green); color: #fff; }
    button.secondary, .button.secondary { color: var(--navy); background: transparent; }
    button.secondary:hover, .button.secondary:hover { color: #fff; background: var(--navy); }
    button.ghost { color: var(--ink); background: transparent; border-color: var(--line); }
    button.ghost:hover { color: var(--ink); background: var(--gold-soft); border-color: var(--gold); }
    button:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible {
      outline: 3px solid #efb74c;
      outline-offset: 3px;
    }
    code, pre {
      font-family: "Cascadia Code", "SFMono-Regular", Consolas, monospace;
    }
    code {
      border-radius: 0.35rem;
      padding: 0.08rem 0.3rem;
      background: rgb(23 63 95 / 8%);
    }
    pre {
      margin: 0.75rem 0 0;
      overflow: auto;
      border: 1px solid #294958;
      border-radius: 12px;
      padding: 1rem;
      color: #eaf4ef;
      background: #152d35;
      white-space: pre-wrap;
    }
    .skip-link {
      position: fixed;
      z-index: 100;
      top: 0.5rem;
      left: 0.5rem;
      transform: translateY(-150%);
      padding: 0.65rem 1rem;
      color: #fff;
      background: var(--navy);
    }
    .skip-link:focus { transform: translateY(0); }
    .shell { width: min(1180px, calc(100% - 2rem)); margin: 0 auto; }
    #top { scroll-margin-top: 9rem; }
    .topbar {
      position: sticky;
      z-index: 20;
      top: 0;
      border-bottom: 1px solid rgb(215 215 202 / 75%);
      background: rgb(247 243 234 / 90%);
      backdrop-filter: blur(14px);
    }
    .topbar-inner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      min-height: 4rem;
      gap: 1rem;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 0.7rem;
      color: var(--ink);
      text-decoration: none;
      font-weight: 850;
      letter-spacing: -0.02em;
    }
    .brand-mark {
      display: grid;
      width: 2.35rem;
      height: 2.35rem;
      place-items: center;
      border-radius: 0.7rem;
      color: #fff;
      background: linear-gradient(145deg, var(--navy), var(--green));
      font-size: 0.76rem;
      letter-spacing: 0.04em;
    }
    nav { display: flex; flex-wrap: wrap; gap: 0.35rem; }
    nav a {
      border-radius: 999px;
      padding: 0.45rem 0.75rem;
      color: var(--muted);
      text-decoration: none;
      font-size: 0.92rem;
      font-weight: 650;
    }
    nav a:hover { color: var(--navy); background: var(--navy-soft); }
    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(17rem, 0.7fr);
      align-items: center;
      gap: 3rem;
      padding: clamp(3rem, 8vw, 7rem) 0 4rem;
    }
    .eyebrow {
      margin: 0 0 0.65rem;
      color: var(--green);
      font-size: 0.82rem;
      font-weight: 850;
      letter-spacing: 0.13em;
      text-transform: uppercase;
    }
    h1, h2, h3 { margin-top: 0; line-height: 1.13; text-wrap: balance; }
    h1 {
      max-width: 13ch;
      margin-bottom: 1.25rem;
      font-size: clamp(3rem, 7vw, 6.2rem);
      letter-spacing: -0.065em;
    }
    h2 { font-size: clamp(2rem, 4vw, 3.25rem); letter-spacing: -0.045em; }
    h3 { letter-spacing: -0.025em; }
    .hero-copy {
      max-width: 63ch;
      color: var(--muted);
      font-size: clamp(1.05rem, 2vw, 1.25rem);
    }
    .hero-actions { display: flex; flex-wrap: wrap; gap: 0.7rem; margin-top: 1.5rem; }
    .hero-card {
      position: relative;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: 1.5rem;
      background: var(--surface);
      box-shadow: var(--shadow);
    }
    .hero-card::before {
      position: absolute;
      top: -5rem;
      right: -5rem;
      width: 12rem;
      height: 12rem;
      border-radius: 50%;
      background: var(--green-soft);
      content: "";
    }
    .stats {
      position: relative;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
    }
    .stat {
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 1rem;
      background: var(--surface-strong);
    }
    .stat strong { display: block; color: var(--navy); font-size: 1.8rem; line-height: 1; }
    .stat span { color: var(--muted); font-size: 0.82rem; }
    .offline-note {
      position: relative;
      margin: 1rem 0 0;
      border-left: 4px solid var(--green);
      padding-left: 0.8rem;
      color: var(--muted);
      font-size: 0.9rem;
    }
    main section { padding: 4.5rem 0; scroll-margin-top: 9rem; }
    .section-head {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 1.5rem;
      margin-bottom: 1.7rem;
    }
    .section-head p { max-width: 64ch; margin: 0; color: var(--muted); }
    .grid { display: grid; gap: 1rem; }
    .grid.three { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .panel {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 1.35rem;
      background: var(--surface);
      box-shadow: 0 8px 25px rgb(28 45 37 / 5%);
    }
    .panel h3 { margin-bottom: 0.55rem; }
    .panel p:last-child { margin-bottom: 0; }
    .step-number {
      display: grid;
      width: 2.3rem;
      height: 2.3rem;
      place-items: center;
      margin-bottom: 1rem;
      border-radius: 50%;
      color: #fff;
      background: var(--green);
      font-weight: 850;
    }
    .os-tabs { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0; }
    .os-tabs button[aria-selected="true"] { color: #fff; background: var(--green); border-color: var(--green); }
    .os-panel[hidden] { display: none; }
    .checklist { display: grid; gap: 0.7rem; padding: 0; list-style: none; }
    .checklist label { display: flex; align-items: flex-start; gap: 0.65rem; }
    .checklist input { width: 1.15rem; height: 1.15rem; margin-top: 0.2rem; accent-color: var(--green); }
    .path-card { position: relative; overflow: hidden; }
    .path-card::after {
      position: absolute;
      right: -1.8rem;
      bottom: -2rem;
      width: 6rem;
      height: 6rem;
      border-radius: 50%;
      background: var(--navy-soft);
      content: "";
    }
    .path-card ul { padding-left: 1.2rem; color: var(--muted); }
    .path-card .button { position: relative; z-index: 1; }
    .workflow {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 0.75rem;
      counter-reset: workflow;
    }
    .workflow article {
      position: relative;
      border-top: 4px solid var(--navy);
      border-radius: 0 0 var(--radius) var(--radius);
      padding: 1.15rem;
      background: var(--surface);
      counter-increment: workflow;
    }
    .workflow article::before {
      display: block;
      margin-bottom: 0.5rem;
      color: var(--green);
      content: "0" counter(workflow);
      font-size: 0.78rem;
      font-weight: 900;
      letter-spacing: 0.12em;
    }
    .workflow p { margin-bottom: 0; color: var(--muted); }
    .callout {
      border: 1px solid #bfd7cb;
      border-radius: var(--radius);
      padding: 1.25rem;
      background: var(--green-soft);
    }
    .callout.warning { border-color: #ead09c; background: var(--gold-soft); }
    .controls {
      display: grid;
      grid-template-columns: minmax(15rem, 2fr) repeat(3, minmax(9rem, 1fr));
      gap: 0.75rem;
      margin-bottom: 1rem;
    }
    .control {
      display: grid;
      gap: 0.3rem;
      color: var(--muted);
      font-size: 0.8rem;
      font-weight: 750;
    }
    .control input, .control select {
      width: 100%;
      min-height: 2.75rem;
      border: 1px solid var(--line);
      border-radius: 11px;
      padding: 0.6rem 0.75rem;
      color: var(--ink);
      background: var(--surface-strong);
    }
    .catalog-toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.8rem;
      margin: 1rem 0;
    }
    .catalog-toolbar p { margin: 0; color: var(--muted); }
    .catalog-toolbar .actions { display: flex; flex-wrap: wrap; gap: 0.45rem; }
    .lesson-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.85rem;
    }
    .lesson-card {
      display: flex;
      flex-direction: column;
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 15px;
      padding: 1rem;
      background: var(--surface);
      transition: transform 120ms ease, box-shadow 120ms ease;
    }
    .lesson-card:hover { transform: translateY(-2px); box-shadow: 0 12px 28px rgb(28 45 37 / 9%); }
    .lesson-card.complete { border-color: #78ad96; background: linear-gradient(145deg, var(--surface), var(--green-soft)); }
    .lesson-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 0.6rem; }
    .lesson-id {
      display: inline-flex;
      border-radius: 999px;
      padding: 0.25rem 0.55rem;
      color: var(--navy);
      background: var(--navy-soft);
      font-family: "Cascadia Code", Consolas, monospace;
      font-size: 0.73rem;
      font-weight: 800;
    }
    .completion {
      display: flex;
      align-items: center;
      gap: 0.35rem;
      color: var(--muted);
      font-size: 0.78rem;
      font-weight: 700;
    }
    .completion input { width: 1rem; height: 1rem; accent-color: var(--green); }
    .lesson-card h3 { margin: 0.75rem 0 0.45rem; font-size: 1.04rem; }
    .lesson-meta { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.65rem; }
    .tag {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 0.16rem 0.45rem;
      color: var(--muted);
      background: var(--surface-strong);
      font-size: 0.68rem;
    }
    .lesson-phase { margin: 0 0 0.7rem; color: var(--muted); font-size: 0.82rem; }
    .prereqs { margin: 0 0 0.8rem; color: var(--muted); font-size: 0.76rem; }
    .lesson-links { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: auto; }
    .lesson-links a, .lesson-links button {
      border-radius: 7px;
      padding: 0.25rem 0.45rem;
      background: rgb(23 63 95 / 7%);
      border: 0;
      min-height: auto;
      color: var(--navy);
      font-size: 0.74rem;
      font-weight: 700;
      text-decoration: none;
    }
    .lesson-links a.lesson-start {
      color: #fff;
      background: var(--navy);
    }
    .lesson-links a.lesson-start:hover { background: var(--green); }
    .lesson-links button:hover { color: #fff; }
    .empty {
      grid-column: 1 / -1;
      border: 1px dashed var(--line);
      border-radius: var(--radius);
      padding: 2rem;
      color: var(--muted);
      text-align: center;
    }
    .progress-panel {
      display: grid;
      grid-template-columns: auto 1fr;
      align-items: center;
      gap: 1rem;
    }
    .progress-ring {
      display: grid;
      width: 5.5rem;
      height: 5.5rem;
      place-items: center;
      border-radius: 50%;
      background: conic-gradient(var(--green) var(--progress), var(--line) 0);
    }
    .progress-ring::before {
      display: grid;
      width: 4.35rem;
      height: 4.35rem;
      place-items: center;
      border-radius: 50%;
      background: var(--surface);
      content: attr(data-label);
      font-weight: 850;
    }
    .track-progress-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.65rem;
      margin-top: 1rem;
    }
    .track-progress {
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.65rem 0.75rem;
      background: rgb(255 255 255 / 45%);
    }
    .track-progress strong, .track-progress span { display: block; }
    .track-progress span { color: var(--muted); font-size: 0.78rem; }
    .progress-bar {
      height: 0.45rem;
      overflow: hidden;
      margin-top: 0.45rem;
      border-radius: 999px;
      background: var(--line);
    }
    .progress-bar i {
      display: block;
      width: var(--track-progress);
      height: 100%;
      border-radius: inherit;
      background: var(--green);
    }
    .launcher-panel {
      border: 2px solid var(--green);
      background: linear-gradient(135deg, var(--surface), var(--green-soft));
    }
    .launcher-actions { display: flex; flex-wrap: wrap; gap: 0.5rem; }
    .launcher-status { min-height: 1.35rem; margin: 0.7rem 0 0; }
    .readiness-box {
      margin-top: 1rem;
      border-top: 1px solid var(--line);
      padding-top: 1rem;
    }
    .readiness-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      flex-wrap: wrap;
    }
    .readiness-head h4 { margin: 0; }
    .readiness-results {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.45rem;
      margin-top: 0.75rem;
    }
    .readiness-item {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 0.15rem 0.55rem;
      align-items: start;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 0.55rem 0.65rem;
      background: rgb(255 255 255 / 55%);
    }
    .readiness-mark {
      grid-row: 1 / 3;
      color: var(--green);
      font-weight: 900;
    }
    .readiness-item[data-status="warn"] .readiness-mark { color: #9a5b05; }
    .readiness-item[data-status="fail"] .readiness-mark { color: var(--red); }
    .readiness-item strong { font-size: 0.82rem; }
    .readiness-item span:last-child { color: var(--muted); font-size: 0.74rem; }
    .mode-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      border-radius: 999px;
      padding: 0.25rem 0.55rem;
      color: var(--green);
      background: #fff;
      font-size: 0.76rem;
      font-weight: 800;
    }
    .prompt-box textarea {
      width: 100%;
      min-height: 10rem;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.9rem;
      color: var(--ink);
      background: var(--surface-strong);
      font: 0.9rem/1.5 "Cascadia Code", Consolas, monospace;
    }
    .prompt-actions { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.7rem; }
    .microcopy { color: var(--muted); font-size: 0.82rem; }
    footer { border-top: 1px solid var(--line); padding: 2.5rem 0 4rem; color: var(--muted); }
    footer .shell { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }
    .noscript { border: 2px solid var(--red); padding: 1rem; background: #fff; }
    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      clip-path: inset(50%);
    }
    @media (max-width: 900px) {
      .hero { grid-template-columns: 1fr; }
      .grid.three, .lesson-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .workflow { grid-template-columns: repeat(2, 1fr); }
      .controls { grid-template-columns: 1fr 1fr; }
    }
    @media (max-width: 620px) {
      .shell { width: min(100% - 1.15rem, 1180px); }
      .topbar-inner { align-items: flex-start; flex-direction: column; padding: 0.6rem 0; }
      nav { width: 100%; overflow-x: auto; flex-wrap: nowrap; padding-bottom: 0.25rem; }
      .hero { padding-top: 2.5rem; }
      h1 { font-size: clamp(2.8rem, 17vw, 4.4rem); }
      .grid.three, .grid.two, .lesson-grid, .workflow, .controls { grid-template-columns: 1fr; }
      .section-head { align-items: flex-start; flex-direction: column; }
      .progress-panel, .track-progress-grid, .readiness-results { grid-template-columns: 1fr; }
    }
    @media (prefers-reduced-motion: reduce) {
      html { scroll-behavior: auto; }
      *, *::before, *::after { transition-duration: 0.01ms !important; }
    }
    @media print {
      .topbar, .hero-actions, .controls, .catalog-toolbar .actions, .completion, .prompt-actions { display: none; }
      body { background: #fff; }
      .shell { width: 100%; }
      .hero { padding: 1rem 0; }
      .lesson-grid { grid-template-columns: repeat(2, 1fr); }
      .lesson-card { break-inside: avoid; }
    }
  </style>
</head>
<body>
  <a class="skip-link" href="#main">Skip to main content</a>
  <header class="topbar">
    <div class="shell topbar-inner">
      <a class="brand" href="START_HERE.html" aria-label="DS60 guide home">
        <span class="brand-mark" aria-hidden="true">DS60</span>
        <span>Learning Guide</span>
      </a>
      <nav aria-label="Primary">
        <a href="#setup">Set up</a>
        <a href="#paths">Choose a path</a>
        <a href="#workflow">Study loop</a>
        <a href="#catalog">Lessons</a>
        <a href="#codex">Codex coach</a>
      </nav>
    </div>
  </header>

  <div id="top" class="shell hero">
    <div>
      <p class="eyebrow">Python · PostgreSQL · Engineering</p>
      <h1>Learn by doing, one honest attempt at a time.</h1>
      <p class="hero-copy">
        This is the portable front door to the DS60 repository. Set up a new
        machine, choose a route, open the right artifacts, track local progress,
        and ask Codex for coaching without giving away the solution.
      </p>
      <div class="hero-actions">
        <a class="button" href="#windows-quick-start">Windows: start here</a>
        <a class="button secondary" href="#setup">macOS/Linux setup</a>
        <a class="button secondary" href="#catalog">Browse all lessons</a>
      </div>
    </div>
    <aside class="hero-card" aria-label="Course inventory">
      <div class="stats">
        <div class="stat"><strong>__LESSON_COUNT__</strong><span>cataloged lessons</span></div>
        <div class="stat"><strong>3</strong><span>connected tracks</span></div>
        <div class="stat"><strong>__PYTHON_COUNT__</strong><span>Python modules</span></div>
        <div class="stat"><strong>__SQL_COUNT__</strong><span>SQL modules</span></div>
        <div class="stat"><strong>__BRIDGE_COUNT__</strong><span>bridge modules</span></div>
        <div class="stat"><strong>1×</strong><span>connected bootstrap</span></div>
      </div>
      <p class="offline-note">
        This file contains no external scripts, fonts, analytics, or internet
        requests. Optional launcher mode talks only to its loopback server.
        Lesson code is designed for offline study after setup.
      </p>
    </aside>
  </div>

  <noscript>
    <div class="shell noscript">
      JavaScript is disabled. The setup links still work, but catalog filtering
      and browser-local progress require JavaScript. Use
      <a href="README.md">README.md</a> and
      <a href="docs/curriculum-map.md">the curriculum map</a> instead.
    </div>
  </noscript>

  <main id="main">
    <section id="setup">
      <div class="shell">
        <div class="section-head">
          <div>
            <p class="eyebrow">Step 1</p>
            <h2>Prepare this machine once.</h2>
          </div>
          <p>
            Work from the repository root in VS Code. Choose your operating
            system; the commands below deliberately use the repository
            interpreter so PATH and activation mistakes are visible.
          </p>
        </div>

        <div class="os-tabs" role="tablist" aria-label="Operating system">
          <button class="secondary" type="button" role="tab" aria-selected="true" aria-controls="os-windows" id="tab-windows" data-os-tab="windows">Windows</button>
          <button class="secondary" type="button" role="tab" aria-selected="false" aria-controls="os-macos" id="tab-macos" data-os-tab="macos">macOS</button>
          <button class="secondary" type="button" role="tab" aria-selected="false" aria-controls="os-linux" id="tab-linux" data-os-tab="linux">Linux</button>
        </div>

        <div id="os-windows" class="os-panel panel" role="tabpanel" aria-labelledby="tab-windows" data-os-panel="windows">
          <div class="callout" id="windows-quick-start">
            <p class="eyebrow">Recommended Windows route</p>
            <h3>Double-click <code>START_DS60.cmd</code>.</h3>
            <p>
              Open the cloned repository in File Explorer and double-click
              <code>START_DS60.cmd</code>. It checks or prepares the course
              environment, runs readiness diagnostics, and reopens this guide
              in private launcher mode. Keep its terminal window open while
              studying so lesson buttons can open VS Code and Jupyter for you.
            </p>
            <p class="microcopy">
              The first connected start installs missing course packages.
              Missing system tools are diagnosed with guided next steps;
              installing them through WinGet remains an explicit opt-in.
              Normal lessons can run offline afterward.
            </p>
          </div>
          <details style="margin-top: 1rem">
            <summary><strong>Manual setup or repair commands</strong></summary>
          <h3>Windows PowerShell</h3>
          <p>
            If Anaconda and PostgreSQL are installed but absent from PATH, use
            the one-off discovery bootstrap. It detects common installs,
            prepares the process safely, creates <code>.venv</code>, installs
            IPython/Jupyter, and registers the course kernel.
          </p>
          <pre><code>Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
&amp; .\scripts\bootstrap_windows.ps1
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
&amp; $CoursePython scripts\course.py doctor
&amp; $CoursePython -m jupyter lab</code></pre>
          <p class="microcopy">
            Need every optional course package while connected? Add
            <code>-Profile Advanced</code>. System-tool installation and persistent
            PATH changes are opt-in; read
            <a href="docs/setup/windows.md">the Windows guide</a> first.
          </p>
          </details>
        </div>

        <div id="os-macos" class="os-panel panel" role="tabpanel" aria-labelledby="tab-macos" data-os-panel="macos" hidden>
          <h3>macOS terminal</h3>
          <pre><code>bash scripts/setup.sh
.venv/bin/python scripts/course.py doctor
.venv/bin/python -m jupyter lab</code></pre>
          <p class="microcopy">
            See <a href="docs/setup/macos.md">the complete macOS guide</a> for
            Python, PostgreSQL, VS Code, Apple Silicon, and shell details.
          </p>
        </div>

        <div id="os-linux" class="os-panel panel" role="tabpanel" aria-labelledby="tab-linux" data-os-panel="linux" hidden>
          <h3>Linux terminal</h3>
          <pre><code>bash scripts/setup.sh
.venv/bin/python scripts/course.py doctor
.venv/bin/python -m jupyter lab</code></pre>
          <p class="microcopy">
            See <a href="docs/setup/linux.md">the complete Linux guide</a> for
            supported package-manager examples and PostgreSQL service setup.
          </p>
        </div>

        <div class="grid three" style="margin-top: 1rem">
          <article class="panel">
            <span class="step-number">1</span>
            <h3>Open the root</h3>
            <p>
              In VS Code, open the folder containing <code>README.md</code>,
              <code>AGENTS.md</code>, and <code>pyproject.toml</code>.
            </p>
          </article>
          <article class="panel">
            <span class="step-number">2</span>
            <h3>Select the kernel</h3>
            <p>
              Pick <strong>Python (ds60sqlpy)</strong> in the notebook kernel
              picker. A terminal interpreter and notebook kernel can differ.
            </p>
          </article>
          <article class="panel">
            <span class="step-number">3</span>
            <h3>Verify, then study</h3>
            <p>
              Run the doctor and fix failures before a lesson. Warnings identify
              optional groups you may not need yet.
            </p>
          </article>
        </div>

        <div class="grid two" style="margin-top: 1rem">
          <div class="callout">
            <h3>PostgreSQL inside Jupyter</h3>
            <p>
              The optional <code>bridge-jupyter-01</code> lab uses JupySQL
              <code>%sql</code>/<code>%%sql</code> magics, SQLAlchemy, and
              Psycopg 3. The database URL stays in
              <code>DS60_DATABASE_URL</code>; it never belongs in a notebook.
            </p>
            <a href="docs/setup/jupyter-postgresql.md">Open the safe setup guide</a>
          </div>
          <div class="callout warning">
            <h3>Database safety boundary</h3>
            <p>
              <code>sql/postgres-60day/00_setup.sql</code> drops and recreates
              the course-owned <code>training</code> schema. Use only the
              disposable <code>advanced_sql_training</code> database—never a
              shared or valuable database.
            </p>
          </div>
        </div>

        <div class="panel launcher-panel" id="launcher-panel" style="margin-top: 1rem" hidden>
          <span class="mode-badge">● Private localhost mode</span>
          <h3>Launch your workspace from this page</h3>
          <p>
            This optional mode is bound only to <code>127.0.0.1</code>. It can
            open allowlisted VS Code/Jupyter targets and saves lesson
            completion to ignored <code>.learning/progress.json</code>. It
            cannot run arbitrary commands or accept arbitrary file paths.
          </p>
          <p class="microcopy">
            See <a href="docs/learning-portal.md">portal modes, portability,
            and security</a>.
          </p>
          <div class="launcher-actions">
            <button type="button" data-launch-action="open-repo">Open repository in VS Code</button>
            <button type="button" class="secondary" data-launch-action="jupyter-python">Launch Python JupyterLab</button>
            <button type="button" class="secondary" data-launch-action="jupyter-sql">Launch PostgreSQL notebook lab</button>
          </div>
          <p class="microcopy launcher-status" id="launcher-status" aria-live="polite"></p>
          <div class="readiness-box">
            <div class="readiness-head">
              <div>
                <h4>This computer</h4>
                <p class="microcopy" id="readiness-summary">
                  Checking the repository environment…
                </p>
              </div>
              <button type="button" class="secondary" id="check-readiness">
                Run checks again
              </button>
            </div>
            <div class="readiness-results" id="readiness-results"></div>
            <p class="microcopy">
              Docker and PostgreSQL are optional until you enter the SQL track.
              A warning is a next-step prompt, not necessarily a blocker.
            </p>
          </div>
        </div>

        <div class="panel" style="margin-top: 1rem">
          <h3>Machine readiness checklist</h3>
          <ul class="checklist" id="setup-checklist">
            <li><label><input type="checkbox" data-setup-check="root"> VS Code opened at the repository root</label></li>
            <li><label><input type="checkbox" data-setup-check="venv"> Repository <code>.venv</code> created successfully</label></li>
            <li><label><input type="checkbox" data-setup-check="kernel"> <strong>Python (ds60sqlpy)</strong> selected as notebook kernel</label></li>
            <li><label><input type="checkbox" data-setup-check="doctor"> Course doctor has no unexplained failures</label></li>
            <li><label><input type="checkbox" data-setup-check="postgres"> PostgreSQL course database verified, if studying SQL</label></li>
            <li><label><input type="checkbox" data-setup-check="offline"> Optional packages and first-use datasets cached before going offline</label></li>
          </ul>
          <p class="microcopy">
            Checklist state stays in this browser. Lesson completion is also
            browser-local in the plain HTML file, or saved to the ignored
            <code>.learning/progress.json</code> file in private launcher mode.
            No machine details leave the computer.
          </p>
        </div>
      </div>
    </section>

    <section id="paths">
      <div class="shell">
        <div class="section-head">
          <div>
            <p class="eyebrow">Step 2</p>
            <h2>Choose a route, not a deadline.</h2>
          </div>
          <p>
            “Day” is an ordering key. Repeat difficult material and use
            prerequisites—not calendar pressure—to decide what comes next.
          </p>
        </div>
        <div class="grid three">
          <article class="panel path-card">
            <h3>New to both</h3>
            <ul>
              <li>Python Days 1–15</li>
              <li><code>sql-found-01</code> and <code>sql-found-02</code></li>
              <li>SQL Days 1–15</li>
              <li>Alternate Python/SQL and add the bridge</li>
            </ul>
            <button type="button" class="secondary" data-path-filter="new">Show the starting sequence</button>
          </article>
          <article class="panel path-card">
            <h3>Python and data science</h3>
            <ul>
              <li>Language and engineering habits</li>
              <li>NumPy, pandas, and visualization</li>
              <li>Statistics and machine learning</li>
              <li>Professional delivery specializations</li>
            </ul>
            <button type="button" class="secondary" data-path-filter="python">Show Python</button>
          </article>
          <article class="panel path-card">
            <h3>PostgreSQL and engineering</h3>
            <ul>
              <li>Relational foundations before Day 1</li>
              <li>Querying and analytical SQL</li>
              <li>Performance, operations, and projects</li>
              <li>Python/PostgreSQL application bridge</li>
            </ul>
            <button type="button" class="secondary" data-path-filter="sql-bridge">Show SQL + bridge</button>
          </article>
        </div>
        <p class="microcopy" style="margin-top: 1rem">
          See the narrative <a href="docs/curriculum-map.md">curriculum map</a>
          and <a href="docs/professional-paths.md">professional paths</a> for
          milestone advice and specialization lanes.
        </p>
      </div>
    </section>

    <section id="workflow">
      <div class="shell">
        <div class="section-head">
          <div>
            <p class="eyebrow">Step 3</p>
            <h2>Use the same learning loop every time.</h2>
          </div>
          <p>
            The course separates explanation, active work, and solutions on
            purpose. Keep that friction—it is where learning happens.
          </p>
        </div>
        <div class="workflow">
          <article>
            <h3>Read the guide</h3>
            <p>Define vocabulary, check prerequisites, and predict the worked example.</p>
          </article>
          <article>
            <h3>Run the learner artifact</h3>
            <p>Execute one cell or statement at a time. Explain the result before moving on.</p>
          </article>
          <article>
            <h3>Attempt every exercise</h3>
            <p>Use progressive hints. Save error messages and revise from evidence.</p>
          </article>
          <article>
            <h3>Study the solution</h3>
            <p>Compare reasoning and edge cases, then reproduce the idea from a blank file.</p>
          </article>
        </div>
        <div class="callout" style="margin-top: 1rem">
          <strong>Completion means evidence.</strong>
          Mark a lesson complete when you can explain the core idea and produce
          a working attempt—not when you merely opened every file.
        </div>
      </div>
    </section>

    <section id="catalog">
      <div class="shell">
        <div class="section-head">
          <div>
            <p class="eyebrow">Step 4</p>
            <h2>Find your next lesson.</h2>
          </div>
          <div class="progress-panel" aria-live="polite">
            <div class="progress-ring" id="progress-ring" style="--progress: 0%" data-label="0%"></div>
            <div>
              <strong id="progress-count">0 of __LESSON_COUNT__ complete</strong>
              <div class="microcopy" id="next-ready">Choose a track to see a next step.</div>
            </div>
          </div>
        </div>
        <div class="track-progress-grid" id="track-progress" aria-label="Progress by track">
          <div class="track-progress" data-progress-track="python">
            <strong>Python</strong><span>0 complete</span>
            <div class="progress-bar"><i style="--track-progress: 0%"></i></div>
          </div>
          <div class="track-progress" data-progress-track="sql">
            <strong>SQL</strong><span>0 complete</span>
            <div class="progress-bar"><i style="--track-progress: 0%"></i></div>
          </div>
          <div class="track-progress" data-progress-track="bridge">
            <strong>Bridge</strong><span>0 complete</span>
            <div class="progress-bar"><i style="--track-progress: 0%"></i></div>
          </div>
        </div>

        <div class="controls">
          <label class="control">
            Search title, ID, phase, or prerequisite
            <input id="lesson-search" type="search" placeholder="Try “window functions” or “python-06”" autocomplete="off">
          </label>
          <label class="control">
            Track
            <select id="track-filter">
              <option value="">All tracks</option>
              <option value="python">Python</option>
              <option value="sql">SQL</option>
              <option value="bridge">Bridge</option>
            </select>
          </label>
          <label class="control">
            Level
            <select id="level-filter"><option value="">All levels</option></select>
          </label>
          <label class="control">
            Status
            <select id="status-filter">
              <option value="">All lessons</option>
              <option value="ready">Ready now</option>
              <option value="incomplete">Incomplete</option>
              <option value="complete">Complete</option>
            </select>
          </label>
        </div>

        <div class="catalog-toolbar">
          <p id="result-count" aria-live="polite">Loading catalog…</p>
          <div class="actions">
            <button type="button" class="ghost" id="export-progress">Export progress</button>
            <button type="button" class="ghost" id="import-progress">Import progress</button>
            <button type="button" class="ghost" id="clear-progress">Clear local progress</button>
            <input class="sr-only" id="progress-file" type="file" accept="application/json">
          </div>
        </div>

        <div id="lesson-grid" class="lesson-grid" aria-live="polite"></div>
        <div style="display: grid; place-items: center; margin-top: 1.25rem">
          <button type="button" class="secondary" id="load-more">Show 30 more</button>
        </div>
      </div>
    </section>

    <section id="codex">
      <div class="shell">
        <div class="section-head">
          <div>
            <p class="eyebrow">Optional coach</p>
            <h2>Give Codex a disciplined tutoring brief.</h2>
          </div>
          <p>
            Open this repository root in Codex. Its <code>AGENTS.md</code>,
            catalog, and repo-local tutor skill explain the course. The prompt
            below keeps the session active rather than answer-first.
          </p>
        </div>
        <div class="grid two">
          <div class="panel prompt-box">
            <label for="codex-lesson"><strong>Lesson to coach</strong></label>
            <select id="codex-lesson" style="width: 100%; margin: 0.5rem 0 0.8rem"></select>
            <label for="codex-prompt"><strong>Copy-ready prompt</strong></label>
            <textarea id="codex-prompt" readonly></textarea>
            <div class="prompt-actions">
              <button type="button" id="copy-prompt">Copy prompt</button>
              <a class="button secondary" href="docs/learning-with-codex.md">Full Codex guide</a>
            </div>
            <p class="microcopy" id="copy-status" aria-live="polite"></p>
          </div>
          <div class="panel">
            <h3>What the coach should do</h3>
            <ul>
              <li>Inspect the actual OS, selected interpreter, kernel, and lesson entry.</li>
              <li>Check prerequisites with short questions before teaching.</li>
              <li>Ask for a prediction and an attempt before revealing code.</li>
              <li>Use conceptual, structural, and partial hints in that order.</li>
              <li>Run safe local evidence and explain the first failure precisely.</li>
              <li>Open official solutions only when requested or after the attempt.</li>
            </ul>
            <div class="callout warning">
              Codex can be online while the course runs offline. Never paste a
              password, private database URL, token, or production data into a
              prompt, notebook, progress note, or source file.
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <div class="shell">
      <span>DS60 portable learning guide · generated from <code>curriculum/catalog.json</code></span>
      <span><a href="README.md">README</a> · <a href="AGENTS.md">Agent guide</a> · <a href="docs/validation.md">Validation</a></span>
    </div>
  </footer>

  <script>
    "use strict";
    const course = __CATALOG_JSON__;
    const lessons = course.lessons;
    const lessonById = new Map(lessons.map((lesson) => [lesson.id, lesson]));
    const STORAGE_KEY = "ds60sqlpy.portable-guide.v1";
    const SERVER_TOKEN = "";
    const launcherMode = Boolean(
      SERVER_TOKEN &&
      location.protocol === "http:" &&
      location.hostname === "127.0.0.1"
    );
    const state = loadState();

    function loadState() {
      const fallback = { completed: [], setup: {}, os: "windows" };
      try {
        const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
        if (!parsed || !Array.isArray(parsed.completed)) return fallback;
        return {
          completed: parsed.completed.filter((id) => lessonById.has(id)),
          setup: parsed.setup && typeof parsed.setup === "object" ? parsed.setup : {},
          os: ["windows", "macos", "linux"].includes(parsed.os) ? parsed.os : "windows"
        };
      } catch {
        return fallback;
      }
    }

    function saveState() {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      } catch {
        // Some file:// privacy modes disable localStorage. The in-memory state
        // still works for this page view.
      }
    }

    function setLauncherStatus(message, failed = false) {
      const status = document.querySelector("#launcher-status");
      status.textContent = message;
      status.style.color = failed ? "var(--red)" : "var(--muted)";
    }

    async function apiRequest(path, options = {}) {
      const response = await fetch(path, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          "X-DS60-Token": SERVER_TOKEN,
          ...(options.headers || {})
        }
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || `Portal request failed (${response.status})`);
      return payload;
    }

    async function loadServerProgress() {
      if (!launcherMode) return;
      document.querySelector("#launcher-panel").hidden = false;
      try {
        const payload = await apiRequest("/api/status");
        state.completed = payload.completed.filter((id) => lessonById.has(id));
        saveState();
        renderCatalog();
        renderProgress();
        renderReadiness(payload.diagnostics || []);
        setLauncherStatus(
          payload.launches_enabled
            ? "Launcher ready. Progress is synchronized with .learning/progress.json."
            : "Progress is synchronized; native launches are disabled for this session."
        );
      } catch (error) {
        setLauncherStatus(`Could not synchronize launcher mode: ${error.message}`, true);
      }
    }

    function renderReadiness(diagnostics) {
      const results = document.querySelector("#readiness-results");
      const summary = document.querySelector("#readiness-summary");
      results.replaceChildren();
      diagnostics.forEach((item) => {
        const row = document.createElement("div");
        row.className = "readiness-item";
        row.dataset.status = item.status;
        const mark = document.createElement("span");
        mark.className = "readiness-mark";
        mark.textContent = item.status === "pass" ? "✓" : item.status === "warn" ? "!" : "×";
        const name = document.createElement("strong");
        name.textContent = item.name;
        const detail = document.createElement("span");
        detail.textContent = item.detail;
        row.append(mark, name, detail);
        results.append(row);
      });
      const failed = diagnostics.filter((item) => item.status === "fail").length;
      const warned = diagnostics.filter((item) => item.status === "warn").length;
      summary.textContent = failed
        ? `${failed} required check(s) need attention before lessons can run.`
        : warned
          ? `Core checks passed; ${warned} optional or track-specific item(s) need attention.`
          : "Everything checked by the course is ready.";
    }

    async function syncCompletion(lessonId, complete) {
      if (!launcherMode) return;
      try {
        await apiRequest("/api/progress", {
          method: "POST",
          body: JSON.stringify({ lesson_id: lessonId, complete })
        });
        setLauncherStatus(
          `${lessonId} ${complete ? "saved as complete" : "saved as incomplete"}.`
        );
      } catch (error) {
        setLauncherStatus(
          `Browser progress changed, but the progress file was not updated: ${error.message}`,
          true
        );
      }
    }

    async function replaceServerProgress() {
      if (!launcherMode) return;
      await apiRequest("/api/progress/replace", {
        method: "POST",
        body: JSON.stringify({ completed: state.completed })
      });
    }

    const completedSet = () => new Set(state.completed);
    const escapeHtml = (value) => String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

    function isReady(lesson, completed = completedSet()) {
      return lesson.prerequisites.every((id) => completed.has(id));
    }

    function relativeLink(path) {
      return String(path).split("/").map(encodeURIComponent).join("/");
    }

    function renderCard(lesson) {
      const completed = completedSet().has(lesson.id);
      const reader = relativeLink(`lesson-pages/${lesson.id}.html`);
      const prerequisites = lesson.prerequisites.length
        ? lesson.prerequisites.map((id) => `<code>${escapeHtml(id)}</code>`).join(", ")
        : "none";
      const solutions = lesson.solution_paths
        .map((_path, index) => `<a href="${reader}#solution-${index + 1}">Solution ${index + 1}</a>`)
        .join("");
      return `
        <article class="lesson-card ${completed ? "complete" : ""}" data-lesson-id="${escapeHtml(lesson.id)}">
          <div class="lesson-top">
            <span class="lesson-id">${escapeHtml(lesson.id)}</span>
            <label class="completion">
              <input type="checkbox" data-complete="${escapeHtml(lesson.id)}" ${completed ? "checked" : ""}>
              Complete
            </label>
          </div>
          <h3>${escapeHtml(lesson.title)}</h3>
          <div class="lesson-meta">
            <span class="tag">${escapeHtml(lesson.track)}</span>
            <span class="tag">${escapeHtml(lesson.level)}</span>
            <span class="tag">${escapeHtml(lesson.estimated_minutes)} min</span>
            <span class="tag">${isReady(lesson) ? "ready" : "prerequisites pending"}</span>
            <span class="tag">${escapeHtml(lesson.network)}</span>
          </div>
          <p class="lesson-phase">${escapeHtml(lesson.phase)}</p>
          <p class="prereqs"><strong>Prerequisites:</strong> ${prerequisites}</p>
          <div class="lesson-links">
            <a class="lesson-start" href="${reader}">Start lesson</a>
            <a href="${reader}#guide">Guide</a>
            <a href="${reader}#learner">Learner artifact</a>
            ${solutions}
            ${launcherMode ? `<button type="button" class="ghost" data-open-lesson="${escapeHtml(lesson.id)}">Open in VS Code</button>` : ""}
          </div>
        </article>`;
    }

    const search = document.querySelector("#lesson-search");
    const trackFilter = document.querySelector("#track-filter");
    const levelFilter = document.querySelector("#level-filter");
    const statusFilter = document.querySelector("#status-filter");
    const lessonGrid = document.querySelector("#lesson-grid");
    const resultCount = document.querySelector("#result-count");
    const loadMore = document.querySelector("#load-more");
    let activePath = "";
    let visibleLimit = 30;

    [...new Set(lessons.map((lesson) => lesson.level))].sort().forEach((level) => {
      const option = document.createElement("option");
      option.value = level;
      option.textContent = level[0].toUpperCase() + level.slice(1);
      levelFilter.append(option);
    });

    function filteredLessons() {
      const query = search.value.trim().toLowerCase();
      const completed = completedSet();
      return lessons.filter((lesson) => {
        const haystack = [
          lesson.id,
          lesson.title,
          lesson.phase,
          lesson.track,
          lesson.level,
          ...lesson.prerequisites
        ].join(" ").toLowerCase();
        if (query && !haystack.includes(query)) return false;
        if (trackFilter.value && lesson.track !== trackFilter.value) return false;
        if (levelFilter.value && lesson.level !== levelFilter.value) return false;
        if (statusFilter.value === "complete" && !completed.has(lesson.id)) return false;
        if (statusFilter.value === "incomplete" && completed.has(lesson.id)) return false;
        if (statusFilter.value === "ready" && (completed.has(lesson.id) || !isReady(lesson, completed))) return false;
        if (
          activePath === "new" &&
          !(
            (lesson.track === "python" && lesson.day >= 1 && lesson.day <= 15) ||
            ["sql-found-01", "sql-found-02"].includes(lesson.id) ||
            (lesson.track === "sql" && lesson.day >= 1 && lesson.day <= 15)
          )
        ) return false;
        if (activePath === "python" && lesson.track !== "python") return false;
        if (
          activePath === "sql-bridge" &&
          !["sql", "bridge"].includes(lesson.track)
        ) return false;
        return true;
      });
    }

    function renderCatalog() {
      const filtered = filteredLessons();
      const visible = filtered.slice(0, visibleLimit);
      lessonGrid.innerHTML = visible.length
        ? visible.map(renderCard).join("")
        : '<p class="empty">No lessons match those filters. Clear one filter and try again.</p>';
      const pathSuffix = activePath ? ` in the selected path` : "";
      resultCount.textContent = filtered.length > visible.length
        ? `Showing ${visible.length} of ${filtered.length} matches${pathSuffix}`
        : `Showing ${filtered.length} of ${lessons.length} lessons${pathSuffix}`;
      loadMore.hidden = visible.length >= filtered.length;
      lessonGrid.querySelectorAll("[data-complete]").forEach((input) => {
        input.addEventListener("change", (event) => {
          const id = event.currentTarget.dataset.complete;
          const completed = completedSet();
          event.currentTarget.checked ? completed.add(id) : completed.delete(id);
          state.completed = [...completed].sort();
          saveState();
          void syncCompletion(id, event.currentTarget.checked);
          renderCatalog();
          renderProgress();
        });
      });
      lessonGrid.querySelectorAll("[data-open-lesson]").forEach((button) => {
        button.addEventListener("click", () => {
          void launchNative("open-lesson", {
            lesson_id: button.dataset.openLesson,
            artifact: "lesson"
          });
        });
      });
    }

    function renderProgress() {
      const completed = completedSet();
      const percentage = Math.round((completed.size / lessons.length) * 100);
      const ring = document.querySelector("#progress-ring");
      ring.style.setProperty("--progress", `${percentage}%`);
      ring.dataset.label = `${percentage}%`;
      document.querySelector("#progress-count").textContent =
        `${completed.size} of ${lessons.length} complete`;
      const next = lessons.find((lesson) => !completed.has(lesson.id) && isReady(lesson, completed));
      document.querySelector("#next-ready").textContent = next
        ? `Next ready: ${next.id} — ${next.title}`
        : completed.size === lessons.length
          ? "Every cataloged lesson is complete."
          : "Complete prerequisites to unlock the next cataloged lesson.";
      ["python", "sql", "bridge"].forEach((track) => {
        const trackLessons = lessons.filter((lesson) => lesson.track === track);
        const trackComplete = trackLessons.filter((lesson) => completed.has(lesson.id)).length;
        const trackPercentage = Math.round((trackComplete / trackLessons.length) * 100);
        const panel = document.querySelector(`[data-progress-track="${track}"]`);
        panel.querySelector("span").textContent =
          `${trackComplete} of ${trackLessons.length} complete`;
        panel.querySelector("i").style.setProperty("--track-progress", `${trackPercentage}%`);
      });
    }

    async function launchNative(action, detail = {}) {
      if (!launcherMode) return;
      setLauncherStatus(`Starting ${action}…`);
      try {
        const payload = await apiRequest("/api/launch", {
          method: "POST",
          body: JSON.stringify({ action, ...detail })
        });
        setLauncherStatus(`${payload.action} started (process ${payload.process_id}).`);
      } catch (error) {
        setLauncherStatus(`Could not launch ${action}: ${error.message}`, true);
      }
    }

    document.querySelectorAll("[data-launch-action]").forEach((button) => {
      button.addEventListener("click", () => {
        void launchNative(button.dataset.launchAction);
      });
    });
    document.querySelector("#check-readiness").addEventListener("click", () => {
      document.querySelector("#readiness-summary").textContent = "Checking this computer…";
      void loadServerProgress();
    });

    [search, trackFilter, levelFilter, statusFilter].forEach((control) => {
      control.addEventListener(control === search ? "input" : "change", () => {
        activePath = "";
        visibleLimit = 30;
        renderCatalog();
      });
    });

    document.querySelectorAll("[data-path-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        const path = button.dataset.pathFilter;
        activePath = path;
        visibleLimit = 30;
        search.value = "";
        levelFilter.value = "";
        statusFilter.value = "";
        trackFilter.value = "";
        renderCatalog();
        document.querySelector("#catalog").scrollIntoView();
      });
    });

    loadMore.addEventListener("click", () => {
      visibleLimit += 30;
      renderCatalog();
    });

    function selectOs(os) {
      state.os = os;
      saveState();
      document.querySelectorAll("[data-os-tab]").forEach((button) => {
        const selected = button.dataset.osTab === os;
        button.setAttribute("aria-selected", String(selected));
        button.tabIndex = selected ? 0 : -1;
      });
      document.querySelectorAll("[data-os-panel]").forEach((panel) => {
        panel.hidden = panel.dataset.osPanel !== os;
      });
    }

    document.querySelectorAll("[data-os-tab]").forEach((button) => {
      button.addEventListener("click", () => selectOs(button.dataset.osTab));
      button.addEventListener("keydown", (event) => {
        if (!["ArrowLeft", "ArrowRight"].includes(event.key)) return;
        const systems = ["windows", "macos", "linux"];
        const current = systems.indexOf(state.os);
        const offset = event.key === "ArrowRight" ? 1 : -1;
        const next = systems[(current + offset + systems.length) % systems.length];
        selectOs(next);
        document.querySelector(`[data-os-tab="${next}"]`).focus();
      });
    });

    document.querySelectorAll("[data-setup-check]").forEach((input) => {
      input.checked = Boolean(state.setup[input.dataset.setupCheck]);
      input.addEventListener("change", () => {
        state.setup[input.dataset.setupCheck] = input.checked;
        saveState();
      });
    });

    function downloadProgress() {
      const payload = {
        format: "ds60sqlpy-portable-guide-progress",
        version: 1,
        completed: state.completed,
        setup: state.setup
      };
      const blob = new Blob([JSON.stringify(payload, null, 2) + "\n"], { type: "application/json" });
      const anchor = document.createElement("a");
      anchor.href = URL.createObjectURL(blob);
      anchor.download = "ds60sqlpy-progress.json";
      anchor.click();
      URL.revokeObjectURL(anchor.href);
    }

    document.querySelector("#export-progress").addEventListener("click", downloadProgress);
    document.querySelector("#import-progress").addEventListener("click", () => {
      document.querySelector("#progress-file").click();
    });
    document.querySelector("#progress-file").addEventListener("change", async (event) => {
      const file = event.currentTarget.files[0];
      if (!file) return;
      try {
        const payload = JSON.parse(await file.text());
        if (payload.format !== "ds60sqlpy-portable-guide-progress" || !Array.isArray(payload.completed)) {
          throw new Error("not a DS60 portable-guide progress file");
        }
        state.completed = payload.completed.filter((id) => lessonById.has(id));
        state.setup = payload.setup && typeof payload.setup === "object" ? payload.setup : {};
        saveState();
        await replaceServerProgress();
        document.querySelectorAll("[data-setup-check]").forEach((input) => {
          input.checked = Boolean(state.setup[input.dataset.setupCheck]);
        });
        renderCatalog();
        renderProgress();
      } catch (error) {
        window.alert(`Could not import progress: ${error.message}`);
      } finally {
        event.currentTarget.value = "";
      }
    });
    document.querySelector("#clear-progress").addEventListener("click", () => {
      if (!window.confirm("Clear lesson and setup progress stored by this browser?")) return;
      state.completed = [];
      state.setup = {};
      saveState();
      void replaceServerProgress().catch((error) => {
        setLauncherStatus(`Could not clear the progress file: ${error.message}`, true);
      });
      document.querySelectorAll("[data-setup-check]").forEach((input) => {
        input.checked = false;
      });
      renderCatalog();
      renderProgress();
    });

    const codexLesson = document.querySelector("#codex-lesson");
    lessons.forEach((lesson) => {
      const option = document.createElement("option");
      option.value = lesson.id;
      option.textContent = `${lesson.id} — ${lesson.title}`;
      codexLesson.append(option);
    });

    function renderPrompt() {
      const lesson = lessonById.get(codexLesson.value) || lessons[0];
      const prerequisites = lesson.prerequisites.length
        ? lesson.prerequisites.join(", ")
        : "none";
      document.querySelector("#codex-prompt").value =
`Use $guide-ds60sqlpy-learning to coach me through ${lesson.id} — ${lesson.title}.

Work from this repository root and inspect the catalog entry, companion guide, and learner artifact. My operating system is ${state.os}. The catalog prerequisites are ${prerequisites}.

First verify that I am using the repository interpreter/kernel and ask 2–3 short prerequisite questions. Then teach one concept at a time. Ask me to predict behavior and attempt each exercise. Use progressive hints—concept, structure, partial answer—before any full answer. Do not open files under solutions/ until I ask or finish an honest attempt. Inspect my actual code/query and output, explain evidence precisely, and end with a short retrieval quiz plus the next concrete step.`;
    }

    codexLesson.addEventListener("change", renderPrompt);
    document.querySelector("#copy-prompt").addEventListener("click", async () => {
      const prompt = document.querySelector("#codex-prompt");
      try {
        await navigator.clipboard.writeText(prompt.value);
        document.querySelector("#copy-status").textContent = "Prompt copied.";
      } catch {
        prompt.select();
        document.execCommand("copy");
        document.querySelector("#copy-status").textContent =
          "Prompt selected; press Ctrl+C or Command+C if it was not copied.";
      }
    });

    selectOs(state.os);
    renderCatalog();
    renderProgress();
    renderPrompt();
    void loadServerProgress();
  </script>
</body>
</html>
"""

    replacements = {
        "__LESSON_COUNT__": str(lesson_count),
        "__PYTHON_COUNT__": str(python_count),
        "__SQL_COUNT__": str(sql_count),
        "__BRIDGE_COUNT__": str(bridge_count),
        "__CATALOG_JSON__": catalog_json,
    }
    for marker, value in replacements.items():
        document = document.replace(marker, value)
    for source_path in COURSE_GUIDE_REFERENCE_PATHS:
        source_href = f'href="{source_path}"'
        if source_href not in document:
            raise ValueError(f"course-guide reference is no longer linked: {source_path}")
        document = document.replace(
            source_href,
            f'href="{reference_relative_path(source_path)}"',
        )
    if "__" in document:
        unresolved = sorted(
            {token for token in document.split() if token.startswith("__") and token.endswith("__")}
        )
        if unresolved:
            raise ValueError(f"unresolved template markers: {unresolved}")
    return document


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output path (default: repository START_HERE.html)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when the checked-in output differs from a fresh render.",
    )
    return parser


def _display_path(path: Path) -> str:
    """Render repository paths compactly and external output paths safely."""

    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    """Build or verify the checked-in guide."""

    args = _parser().parse_args(argv)
    try:
        rendered = build_html(_catalog_payload())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not build course guide: {exc}", file=sys.stderr)
        return 2

    output = args.output.resolve()
    if args.check:
        try:
            current = output.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Course guide is missing or unreadable: {exc}", file=sys.stderr)
            return 1
        if current != rendered:
            print(
                f"{_display_path(output)} is stale; run python scripts/build_course_guide.py",
                file=sys.stderr,
            )
            return 1
        print(f"{_display_path(output)} matches curriculum/catalog.json")
        return 0

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    except OSError as exc:
        print(f"Could not write course guide: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote {_display_path(output)} with {len(_catalog_payload()['lessons'])} lessons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
