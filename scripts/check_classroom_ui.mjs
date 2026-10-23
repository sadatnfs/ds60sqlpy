// Regression harness for the real unified classroom script. It controls async
// response order; actual layout and browser behavior are qualified separately.
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
const filename = process.argv[2] || "src/ds60sqlpy/assets/classroom.js";
const script = fs.readFileSync(filename, "utf8");
class Element {
  constructor(tag = "div") {
    this.tagName = tag.toUpperCase();
    this.value = "";
    this.textContent = "";
    this.hidden = false;
    this.disabled = false;
    this.checked = false;
    this.children = [];
    this.handlers = {};
    this.innerHTML = "";
    this.dataset = {};
    this.style = {
      setProperty: (key, value) => {
        this.style[key] = value;
      },
    };
  }
  addEventListener(name, fn) {
    (this.handlers[name] ??= []).push(fn);
  }
  append(...children) {
    this.children.push(...children);
  }
  replaceChildren(...children) {
    this.children = children;
  }
  setAttribute(name, value) {
    this[name] = value;
  }
  removeAttribute(name) {
    delete this[name];
  }
  focus() {
    this.focused = true;
  }
  scrollIntoView() {}
  querySelectorAll() {
    return [];
  }
  querySelector() {
    return null;
  }
  contains(node) {
    return this.children.includes(node);
  }
  setSelectionRange(start, end) {
    this.selection = [start, end];
  }
  setRangeText(text, start, end) {
    this.value = this.value.slice(0, start) + text + this.value.slice(end);
  }
  dispatchEvent(event) {
    for (const fn of this.handlers[event.type] || [])
      fn({ ...event, target: this });
  }
}
function deferred() {
  let resolve, reject;
  const promise = new Promise((a, b) => {
    resolve = a;
    reject = b;
  });
  return { promise, resolve, reject };
}
const settle = async () => {
  for (let i = 0; i < 18; i++) await Promise.resolve();
};
function moduleData(record, source = record.id) {
  return {
    ...record,
    language: "python",
    runtime_profile: "python-core",
    source,
    guide_html: "guide",
    session: {},
    history: [],
    capability: { profile: "python-core", ready: true, detail: "Fixture" },
  };
}
function environment() {
  const elements = new Map(),
    requests = [],
    timers = new Map(),
    storage = new Map(),
    windowHandlers = new Map(),
    locations = [];
  let timer = 0;
  const element = (id) => {
    if (!elements.has(id)) elements.set(id, new Element());
    return elements.get(id);
  };
  const location = new URL("http://127.0.0.1:8765/classroom");
  const writeLocation = (mode, url) => {
    locations.push({ mode, url });
    location.href = new URL(url, location).href;
  };
  const context = vm.createContext({
    console,
    SERVER_TOKEN: "fixture-token",
    AbortController,
    URL,
    URLSearchParams,
    Blob,
    Event: class {
      constructor(type) {
        this.type = type;
      }
    },
    document: {
      getElementById: element,
      createElement: (tag) => new Element(tag),
      addEventListener: () => {},
      body: element("body"),
      documentElement: element("documentElement"),
    },
    window: {
      addEventListener: (name, fn) => windowHandlers.set(name, fn),
      scrollTo: () => {},
    },
    location,
    history: {
      replaceState: (_a, _b, url) => writeLocation("replace", url),
      pushState: (_a, _b, url) => writeLocation("push", url),
    },
    confirm: () => true,
    prompt: () => null,
    matchMedia: () => ({ matches: false }),
    crypto: { randomUUID: () => "12345678-1234-1234-1234-123456789abc" },
    localStorage: {
      getItem: (key) => storage.get(key) ?? null,
      setItem: (key, value) => storage.set(key, value),
      removeItem: (key) => storage.delete(key),
    },
    setTimeout: (fn, ms) => {
      const id = ++timer;
      timers.set(id, { fn, ms });
      return id;
    },
    clearTimeout: (id) => timers.delete(id),
    fetch: (url, options) => {
      const body = JSON.parse(options.body),
        pending = deferred();
      requests.push({ url, body, pending });
      return pending.promise;
    },
  });
  element("stage").value = "all";
  element("pace").value = "30";
  element("workspace-view").hidden = true;
  vm.runInContext(script, context, { filename });
  const run = (code) => vm.runInContext(code, context);
  const current = (id = "llm-009", language = "python") => {
    context.fixture = {
      id,
      engine: "module",
      language,
      runtime_profile: "python-core",
      capability: {
        profile: "python-core",
        ready: true,
        detail: "Fixture ready",
      },
    };
    run("current=fixture;lessonId=fixture.id;");
    element("timeout").value = "60";
  };
  const resolve = (request, data) => {
    assert.ok(request, "expected API request");
    request.pending.resolve({ ok: true, json: async () => data });
  };
  const reject = (request, message = "fixture failure") =>
    request.pending.reject(new Error(message));
  const next = (action) =>
    requests.findLast((item) => item.body.action === action);
  const event = (id, name = "click") => {
    const handlers = element(id).handlers[name] || [];
    return Promise.all(
      handlers.map((fn) => fn({ target: element(id), preventDefault() {} })),
    );
  };
  return {
    context,
    run,
    current,
    element,
    requests,
    timers,
    storage,
    resolve,
    reject,
    next,
    event,
    windowHandlers,
    locations,
    location,
  };
}
let checks = 0;
async function test(name, fn) {
  await fn();
  checks++;
  console.log("PASS " + name);
}
await test("old save acknowledgement cannot mark newer draft saved", async () => {
  const e = environment();
  e.current();
  e.element("source").value = "older";
  assert.equal(e.next("classroom-index").url, "/api/classroom");
  const saving = e.run("queueSave()");
  await settle();
  const request = e.next("module-save");
  e.element("source").value = "newer";
  await e.event("source", "input");
  e.resolve(request, { session: {} });
  await saving;
  assert.match(e.element("save-state").textContent, /Unsaved/);
  assert.equal(
    JSON.parse(e.storage.get("ds60.classroom.unsaved.llm-009")).source,
    "newer",
  );
});
await test("latest save acknowledges the matching draft and clears only its backup", async () => {
  const e = environment();
  e.current();
  e.element("source").value = "latest";
  await e.event("source", "input");
  const saving = e.run("queueSave()");
  await settle();
  e.resolve(e.next("module-save"), { session: {} });
  await saving;
  assert.match(e.element("save-state").textContent, /^Saved/);
  assert.equal(e.storage.has("ds60.classroom.unsaved.llm-009"), false);
});
await test("navigation while saving invalidates an old Run intent", async () => {
  const e = environment();
  e.current();
  e.element("source").value = "print(42)";
  const clicked = e.event("run");
  await settle();
  e.run("intentVersion++;");
  e.resolve(e.next("module-save"), { session: {} });
  await clicked;
  assert.equal(
    e.requests.filter((r) => r.body.action === "module-run").length,
    0,
  );
  assert.match(e.element("status").textContent, /changed while saving/);
});
await test("double Run cannot submit two requests while the save is pending", async () => {
  const e = environment();
  e.current();
  e.element("source").value = "print(42)";
  const first = e.event("run"),
    second = e.event("run");
  await settle();
  assert.equal(
    e.requests.filter((r) => r.body.action === "module-save").length,
    1,
  );
  e.resolve(e.next("module-save"), { session: {} });
  await settle();
  assert.equal(
    e.requests.filter((r) => r.body.action === "module-run").length,
    1,
  );
  e.resolve(e.next("module-run"), {
    job_id: "a",
    lesson_id: "llm-009",
    status: "succeeded",
    source: "print(42)",
    checks: [],
  });
  await Promise.all([first, second]);
  assert.equal(e.run("submitInFlight"), false);
});
await test("late solution response cannot enter a different lesson", async () => {
  const e = environment();
  e.current();
  const clicked = e.event("reveal");
  await settle();
  e.current("tf-008");
  e.run("intentVersion++;");
  e.resolve(e.next("classroom-solutions"), {
    documents: [{ html: "OLD SOLUTION" }],
  });
  await clicked;
  assert.equal(e.element("solutions").children.length, 0);
});
await test("diagnostic jumps require exact current source and submitted filename", async () => {
  const e = environment();
  e.current();
  e.element("source").value = "one\ntwo\nthree";
  e.context.job = {
    job_id: "a",
    lesson_id: "llm-009",
    source: "one\ntwo\nthree",
    output:
      'File "/job/verify.py", line 88\nFile "/job/main.py", line 2\nValueError',
  };
  assert.equal(e.run("sourceErrorLine(job)"), 2);
  e.context.job.output = 'File "/job/verify.py", line 2';
  assert.equal(e.run("sourceErrorLine(job)"), null);
  e.context.job.output = 'File "/job/main.py", line 99';
  assert.equal(e.run("sourceErrorLine(job)"), null);
  e.context.job.output = 'File "/job/main.py", line 0';
  assert.equal(e.run("sourceErrorLine(job)"), null);
  e.context.job.output = 'File "/job/main.py", line 2';
  e.element("source").value = "edited";
  assert.equal(e.run("sourceErrorLine(job)"), null);
});
await test("Scala capitalization and C++ line/column locations are supported", async () => {
  const e = environment();
  e.current("spark-003", "scala");
  e.element("source").value = "one\ntwo";
  e.context.job = {
    lesson_id: "spark-003",
    source: "one\ntwo",
    output: "Main.scala:2: error: fixture",
  };
  assert.equal(e.run("sourceErrorLine(job)"), 2);
  e.current("cpp-003", "cpp");
  e.context.job.lesson_id = "cpp-003";
  e.context.job.output = "main.cpp:2:8: error: fixture";
  assert.equal(e.run("sourceErrorLine(job)"), 2);
});
await test("editing after displaying a diagnostic removes its stale jump", async () => {
  const e = environment();
  e.current();
  e.element("source").value = "one\ntwo";
  e.context.job = {
    lesson_id: "llm-009",
    source: "one\ntwo",
    output: 'File "/job/main.py", line 2',
    status: "failed",
  };
  e.run("showJob(job)");
  assert.equal(e.element("error-line").hidden, false);
  e.element("source").value = "edited";
  await e.event("source", "input");
  assert.equal(e.element("error-line").hidden, true);
});
await test("overlapping poll requests use one in-flight request and one timer", async () => {
  const e = environment();
  e.current();
  e.context.job = { job_id: "a", lesson_id: "llm-009", status: "running" };
  e.run("adoptJob(job,false)");
  const first = e.run("poll()"),
    second = e.run("poll()");
  await settle();
  assert.equal(
    e.requests.filter((r) => r.body.action === "module-job").length,
    1,
  );
  e.resolve(e.next("module-job"), e.context.job);
  await Promise.all([first, second]);
  assert.equal([...e.timers.values()].filter((t) => t.ms === 1000).length, 1);
});
await test("old terminal response cannot clear a newer active job", async () => {
  const e = environment();
  e.current();
  e.context.job = { job_id: "old", lesson_id: "llm-009", status: "running" };
  e.run("adoptJob(job,false)");
  const pending = e.run("poll()");
  await settle();
  e.context.newJob = { job_id: "new", lesson_id: "llm-009", status: "running" };
  e.run("activeJob=null;activeJobRecord=null;adoptJob(newJob,false)");
  e.resolve(e.next("module-job"), { ...e.context.job, status: "succeeded" });
  await pending;
  assert.equal(e.run("activeJob"), "new");
  assert.equal(e.run("activeJobRecord.job_id"), "new");
});
await test("reconnecting an old record cannot steal another active monitor", async () => {
  const e = environment();
  e.current();
  e.context.job = { job_id: "new", lesson_id: "llm-009", status: "running" };
  e.run("adoptJob(job,false)");
  e.context.old = {
    job_id: "old",
    lesson_id: "llm-009",
    status: "interrupted",
  };
  assert.equal(e.run("adoptJob(old,false)"), false);
  assert.equal(e.run("activeJob"), "new");
  e.run("showJob(old)");
  assert.equal(e.element("reconnect").disabled, true);
});
await test("saved interrupted job is adopted without source resubmission", async () => {
  const e = environment();
  e.current();
  e.context.job = {
    job_id: "resume",
    lesson_id: "llm-009",
    status: "interrupted",
  };
  assert.equal(e.run("adoptJob(job,false)"), true);
  assert.equal(e.element("cancel").disabled, false);
  assert.equal(e.element("run").disabled, true);
  assert.equal(
    e.requests.some((r) => r.body.action === "module-run"),
    false,
  );
});

await test("startup monitors the persisted job while keeping the opening page a choice", async () => {
  const e = environment();
  const lesson = {
    id: "cpp-009",
    title: "Ownership",
    level: "beginner",
    status: "authored",
    prerequisites: [],
    outcome: "Observe ownership",
  };
  const job = {
    job_id: "resume",
    lesson_id: "cpp-009",
    status: "running",
    source: "int main(){}",
    source_sha256: "a".repeat(64),
    created_at: "2026-10-22",
  };
  e.resolve(e.next("classroom-index"), {
    active_job: job,
    tracks: [
      {
        id: "cpp",
        title: "C++",
        engine: "module",
        description: "C++ systems",
        lessons: [lesson],
      },
    ],
  });
  await settle();
  assert.equal(e.next("module-lesson"), undefined);
  assert.equal(e.run("activeJob"), "resume");
  assert.equal(e.next("module-job").body.job_id, "resume");
  assert.equal(
    e.requests.some((r) => r.body.action === "module-run"),
    false,
  );
  assert.equal(e.element("subject-cards").children.length, 1);
});

await test("out-of-order lesson responses cannot replace the latest source", async () => {
  const e = environment();
  const one = {
      id: "a",
      title: "A",
      level: "beginner",
      status: "authored",
      prerequisites: [],
      outcome: "A",
    },
    two = { ...one, id: "b", title: "B" };
  e.context.navigation = {
    tracks: [{ id: "t", title: "Track", lessons: [one, two] }],
  };
  e.run("index=navigation;trackId='t';");
  const a = e.run("openLesson('a',false)"),
    first = e.next("module-lesson");
  const b = e.run("openLesson('b',false)"),
    second = e.next("module-lesson");
  const data = (record) => ({
    ...record,
    language: "python",
    runtime_profile: "python-core",
    source: record.id,
    guide_html: record.id,
    session: {},
    history: [],
    capability: { profile: "python-core", ready: true, detail: "Fixture" },
  });
  e.resolve(second, data(two));
  await b;
  e.resolve(first, data(one));
  await a;
  assert.equal(e.run("current.id"), "b");
  assert.equal(e.element("source").value, "b");
});
await test("curated PySpark alias selects its own session and preserves base navigation", async () => {
  const e = environment();
  const base = {
    id: "spark-013",
    title: "Rows",
    level: "intermediate",
    status: "authored",
    prerequisites: [],
    outcome: "Rows",
    variants: [
      { id: "spark-013", title: "Scala" },
      { id: "spark-013@pyspark", title: "PySpark" },
    ],
  };
  e.context.navigation = {
    tracks: [{ id: "spark", title: "Spark", lessons: [base] }],
  };
  e.run("index=navigation;trackId='spark';");
  const opening = e.run("openLesson('spark-013@pyspark',false)");
  const requested = e.next("module-lesson");
  assert.equal(requested.body.lesson_id, "spark-013@pyspark");
  e.resolve(requested, {
    ...base,
    id: "spark-013@pyspark",
    base_id: "spark-013",
    language: "python",
    runtime_profile: "spark-local-python",
    source: "print(42)",
    guide_html: "guide",
    session: {},
    history: [],
    capability: {
      profile: "spark-local-python",
      ready: true,
      detail: "Fixture",
    },
  });
  await opening;
  assert.equal(e.run("lesson().id"), "spark-013");
  assert.equal(e.element("variant").hidden, false);
  assert.equal(e.element("variant").value, "spark-013@pyspark");
  assert.equal(e.run("current.language"), "python");
  const saving = e.run("queueSave()");
  await settle();
  assert.equal(e.next("module-save").body.lesson_id, "spark-013@pyspark");
  e.resolve(e.next("module-save"), { session: {} });
  await saving;
});

function interrupted(e, profile = "cpp20") {
  e.current("cpp-009", profile === "k8s-kind" ? "yaml" : "cpp");
  e.element("source").value = "retained draft";
  const job = {
    job_id: "recover",
    lesson_id: "cpp-009",
    profile,
    status: "interrupted",
    source: "submitted source",
    checks: [],
    source_sha256: "a".repeat(64),
  };
  e.context.job = job;
  e.run("adoptJob(job,false);showJob(job)");
  return job;
}
async function resolveRecovery(e, job, clicked) {
  const result = {
    ...job,
    status: "failed",
    detail: "Operator confirmed recovery; prior result unavailable.",
    recovery: { type: "operator-confirmed" },
  };
  e.resolve(e.next("module-recover"), result);
  await settle();
  e.resolve(e.next("module-job"), result);
  await settle();
  e.resolve(e.next("module-lesson"), { id: job.lesson_id, history: [result] });
  await clicked;
}
await test("manual recovery requires the exact acknowledgement before any API call", async () => {
  const e = environment(),
    job = interrupted(e);
  e.context.prompt = () => "yes";
  await e.element("recover").onclick();
  assert.equal(e.next("module-recover"), undefined);
  assert.equal(e.run("activeJob"), job.job_id);
  assert.equal(e.element("source").value, "retained draft");
});
await test("worker recovery retains source and polls the failed receipt without resubmission", async () => {
  const e = environment(),
    job = interrupted(e);
  let message = "";
  e.context.prompt = (text) => {
    message = text;
    return "WORKER RESTARTED";
  };
  const clicked = e.element("recover").onclick();
  await settle();
  assert.match(message, /restart only the owned cpp20 worker/);
  assert.match(message, /does not verify cleanup or mastery/);
  assert.deepEqual(e.next("module-recover").body, {
    action: "module-recover",
    job_id: "recover",
    confirmation: "WORKER RESTARTED",
  });
  await resolveRecovery(e, job, clicked);
  assert.equal(e.run("activeJob"), null);
  assert.equal(e.element("source").value, "retained draft");
  assert.equal(
    e.requests.some((r) => r.body.action === "module-run"),
    false,
  );
  assert.equal(e.element("recover").hidden, true);
});
await test("Kubernetes recovery requires release of the owned cluster with distinct confirmation", async () => {
  const e = environment(),
    job = interrupted(e, "k8s-kind");
  let message = "";
  e.context.prompt = (text) => {
    message = text;
    return "CLUSTER RELEASED";
  };
  const clicked = e.element("recover").onclick();
  await settle();
  assert.match(message, /release only the owned disposable cluster/);
  assert.equal(e.next("module-recover").body.confirmation, "CLUSTER RELEASED");
  await resolveRecovery(e, job, clicked);
  assert.equal(
    e.requests.some((r) => r.body.action === "module-run"),
    false,
  );
});
await test("manual recovery of an old receipt cannot steal an active monitor", async () => {
  const e = environment(),
    job = interrupted(e);
  let prompted = false;
  e.context.prompt = () => {
    prompted = true;
    return "WORKER RESTARTED";
  };
  e.context.newJob = { ...job, job_id: "new", status: "running" };
  e.run("activeJob=null;adoptJob(newJob,false);showJob(job)");
  assert.equal(e.element("recover").disabled, true);
  await e.element("recover").onclick();
  assert.equal(prompted, false);
  assert.equal(e.next("module-recover"), undefined);
  assert.equal(e.run("activeJob"), "new");
});
await test("late recovery response preserves a newer monitor and edited draft", async () => {
  const e = environment(),
    job = interrupted(e);
  e.context.prompt = () => "WORKER RESTARTED";
  const clicked = e.element("recover").onclick();
  await settle();
  e.element("source").value = "new draft";
  e.context.newJob = { ...job, job_id: "new", status: "running" };
  e.run("intentVersion++;activeJob=null;adoptJob(newJob,false)");
  e.resolve(e.next("module-recover"), { ...job, status: "failed" });
  await clicked;
  assert.equal(e.run("activeJob"), "new");
  assert.equal(e.element("source").value, "new draft");
  assert.equal(e.next("module-job"), undefined);
});
await test("recovery refresh survives an older in-flight interrupted poll using one follow-up", async () => {
  const e = environment(),
    job = interrupted(e);
  e.context.prompt = () => "WORKER RESTARTED";
  const old = e.run("poll()");
  await settle();
  const oldRequest = e.next("module-job");
  const clicked = e.element("recover").onclick();
  await settle();
  e.resolve(e.next("module-recover"), { ...job, status: "failed" });
  await clicked;
  e.resolve(oldRequest, job);
  await old;
  const immediate = [...e.timers.entries()].filter(
    ([, timer]) => timer.ms === 0,
  );
  assert.equal(immediate.length, 1);
  e.timers.delete(immediate[0][0]);
  immediate[0][1].fn();
  await settle();
  assert.equal(
    e.requests.filter((r) => r.body.action === "module-job").length,
    2,
  );
  const result = { ...job, status: "failed" };
  e.resolve(e.next("module-job"), result);
  await settle();
  e.resolve(e.next("module-lesson"), { id: job.lesson_id, history: [result] });
  await settle();
  assert.equal(e.run("activeJob"), null);
  assert.equal(
    e.requests.some((r) => r.body.action === "module-run"),
    false,
  );
});
await test("recovery that reconnects a live job does not claim operator recovery was recorded", async () => {
  const e = environment(),
    job = interrupted(e);
  e.context.prompt = () => "WORKER RESTARTED";
  const clicked = e.element("recover").onclick();
  await settle();
  const running = {
    ...job,
    status: "running",
    detail: "Existing job is active.",
  };
  e.resolve(e.next("module-recover"), running);
  await settle();
  e.resolve(e.next("module-job"), running);
  await clicked;
  assert.equal(e.run("activeJob"), job.job_id);
  assert.match(
    e.element("status").textContent,
    /No manual recovery was recorded/,
  );
  assert.equal(
    e.requests.some((r) => r.body.action === "module-run"),
    false,
  );
});
await test("Java and Node diagnostics point only to the submitted source", async () => {
  const e = environment();
  e.current("java-001", "java");
  e.element("source").value = "one\ntwo";
  e.context.job = {
    lesson_id: "java-001",
    source: "one\ntwo",
    output: "Main.java:2: error: fixture",
  };
  assert.equal(e.run("sourceErrorLine(job)"), 2);
  e.context.job.output = "at Main.main(Main.java:2)";
  assert.equal(e.run("sourceErrorLine(job)"), 2);
  e.current("js-001", "javascript");
  e.context.job.lesson_id = "js-001";
  e.context.job.output = "file:///tmp/job/main.mjs:2:4";
  assert.equal(e.run("sourceErrorLine(job)"), 2);
  e.context.job.output = "file:///tmp/job/notmain.mjs:2:4";
  assert.equal(e.run("sourceErrorLine(job)"), null);
});
await test("TypeScript does not confuse emitted JavaScript lines with source lines", async () => {
  const e = environment();
  e.current("js-019", "typescript");
  e.element("source").value = "one\ntwo";
  e.context.job = {
    lesson_id: "js-019",
    source: "one\ntwo",
    output: "main.mts(2,7): error TS2322: fixture",
  };
  assert.equal(e.run("sourceErrorLine(job)"), 2);
  e.context.job.output = "file:///tmp/job/compiled/main.mjs:2:4";
  assert.equal(e.run("sourceErrorLine(job)"), null);
});
await test("tutorial reading markers save explicitly without prediction or solution gates", async () => {
  const e = environment();
  const chapter = {
    id: "statistics-001",
    title: "Inference",
    level: "beginner",
    outcome: "Understand inference",
    prerequisites: [],
    status: "authored",
    concepts: ["bootstrap"],
    variants: [],
  };
  e.context.plan = { tracks: [{ id: "statistics-ml", lessons: [chapter] }] };
  e.run("index=plan;trackId='statistics-ml';");
  const opened = e.run("openLesson('statistics-001',false)");
  await settle();
  e.resolve(e.next("module-lesson"), {
    ...chapter,
    learning_mode: "tutorial",
    language: "python",
    runtime_profile: "python-core",
    source: "print(42)",
    guide_html: "chapter",
    session: { review: "read" },
    history: [],
    capability: { profile: "python-core", ready: true, detail: "Fixture" },
  });
  await opened;
  assert.equal(e.element("solution-section").hidden, true);
  assert.equal(e.element("prediction").hidden, true);
  assert.equal(e.element("chapter-read-label").hidden, false);
  assert.equal(e.element("read-chapter").checked, true);
  e.element("read-chapter").checked = false;
  await e.event("read-chapter", "input");
  const saved = e.run("queueSave()");
  await settle();
  assert.equal(e.next("module-save").body.fields.review, "");
  e.resolve(e.next("module-save"), { session: { review: "" } });
  await saved;
  assert.equal(
    e.requests.some((r) => r.body.action === "module-run"),
    false,
  );
});
await test("topic search finds method names across stages within the chosen journey", async () => {
  const e = environment();
  e.context.plan = {
    tracks: [
      {
        id: "statistics-ml",
        lessons: [
          {
            id: "statistics-001",
            title: "Reasoning",
            level: "beginner",
            status: "authored",
            concepts: ["estimand"],
          },
          {
            id: "statistics-019",
            title: "Supervised models",
            level: "advanced",
            status: "authored",
            concepts: ["Random forest", "Boosted trees"],
          },
        ],
      },
    ],
  };
  e.run("index=plan;trackId='statistics-ml';");
  e.element("lesson-query").value = "random forest";
  await e.event("lesson-query", "input");
  assert.equal(e.element("stage").value, "all");
  assert.equal(e.element("lessons").children.length, 1);
  assert.match(
    e.element("lessons").children[0].children[0].textContent,
    /statistics-019/,
  );
});

await test("reading view keeps source and notes intact while changing layout", async () => {
  const e = environment();
  e.current("statistics-001");
  e.element("source").value = "retained source";
  e.element("explanation").value = "retained notes";
  await e.event("reading-toggle");
  assert.match(e.element("authored").className, /reading-focus/);
  assert.equal(e.element("reading-toggle")["aria-pressed"], "true");
  await e.event("reading-toggle");
  assert.equal(e.element("authored").className, "panes");
  assert.equal(e.element("source").value, "retained source");
  assert.equal(e.element("explanation").value, "retained notes");
  assert.equal(
    e.requests.filter((r) => r.body.action !== "classroom-index").length,
    0,
  );
});
await test("section navigation includes nested rendered chapter headings", async () => {
  const e = environment();
  const headings = [
    {
      id: "module-guide--section",
      textContent: "Mechanism#",
      querySelector: () => ({ textContent: "#" }),
    },
    {
      id: "module-guide--stat-01-01",
      textContent: "Descriptive analysis#",
      querySelector: () => ({ textContent: "#" }),
    },
  ];
  e.element("guide").querySelectorAll = (selector) => {
    assert.match(selector, /h4/);
    assert.match(selector, /h5/);
    return headings;
  };
  e.run("renderSections()");
  assert.equal(e.element("section-jump").children.length, 3);
  assert.equal(e.element("section-jump").children[1].textContent, "Mechanism");
  assert.equal(
    e.element("section-jump").children[2].value,
    "module-guide--stat-01-01",
  );
});
await test("journey progression respects canonical variants and planned boundaries", async () => {
  const e = environment();
  const rows = [
    {
      id: "spark-013",
      title: "Rows",
      level: "beginner",
      status: "authored",
      variants: [{ id: "spark-013@pyspark", title: "Python" }],
    },
    {
      id: "spark-014",
      title: "Next topic",
      level: "intermediate",
      status: "planned",
      prerequisites: ["spark-013"],
      lab: "Future lab",
      verification: "Future check",
    },
  ];
  e.context.plan = { tracks: [{ id: "scala-spark", lessons: rows }] };
  e.run(
    "index=plan;trackId='scala-spark';lessonId='spark-013@pyspark';current=null;renderPager();",
  );
  assert.equal(e.element("journey-position").textContent, "1 of 2");
  assert.equal(e.element("previous-lesson").disabled, true);
  await e.event("next-lesson");
  assert.equal(e.run("lessonId"), "spark-014");
  assert.equal(e.element("journey-position").textContent, "2 of 2");
  assert.equal(e.element("next-lesson").disabled, true);
  assert.equal(e.element("authored").hidden, true);
  assert.equal(e.element("planned").hidden, false);
  assert.equal(
    e.requests.some((r) => r.body.action === "module-run"),
    false,
  );
});
await test("All stages preserves the selected variant and unsaved draft", async () => {
  const e = environment();
  const rows = [
    {
      id: "spark-013",
      title: "Rows",
      level: "beginner",
      status: "authored",
      variants: [{ id: "spark-013@pyspark", title: "Python" }],
    },
    {
      id: "spark-014",
      title: "Joins",
      level: "intermediate",
      status: "authored",
    },
  ];
  e.context.plan = { tracks: [{ id: "scala-spark", lessons: rows }] };
  e.current("spark-013@pyspark");
  e.run("index=plan;trackId='scala-spark';");
  e.element("source").value = "my unsaved code";
  e.element("stage").value = "all";
  await e.event("stage", "change");
  assert.equal(e.run("lessonId"), "spark-013@pyspark");
  assert.equal(e.element("source").value, "my unsaved code");
  assert.equal(e.element("lessons").children.length, 2);
  assert.equal(
    e.requests.filter((r) => r.body.action !== "classroom-index").length,
    0,
  );
});
await test("empty stage or search filters keep the current lesson without a request", async () => {
  const e = environment();
  e.context.plan = {
    tracks: [
      {
        id: "cpp",
        lessons: [
          {
            id: "cpp-002",
            title: "Values",
            level: "beginner",
            status: "authored",
          },
        ],
      },
    ],
  };
  e.current("cpp-002", "cpp");
  e.run("index=plan;trackId='cpp';");
  e.element("source").value = "retained";
  e.element("stage").value = "advanced";
  await e.event("stage", "change");
  assert.equal(e.element("lessons").children.length, 1);
  assert.match(
    e.element("lessons").children[0].textContent,
    /No lessons match/,
  );
  e.element("stage").value = "beginner";
  e.element("lesson-query").value = "no-such-topic";
  await e.event("stage", "change");
  assert.equal(e.run("lessonId"), "cpp-002");
  assert.equal(e.element("source").value, "retained");
  assert.equal(
    e.requests.filter((r) => r.body.action !== "classroom-index").length,
    0,
  );
});
await test("a new stage filters options without silently navigating or saving a draft", async () => {
  const e = environment();
  const one = {
      id: "cpp-002",
      title: "Values",
      level: "beginner",
      status: "authored",
    },
    two = { ...one, id: "cpp-020", title: "Ownership", level: "advanced" };
  e.context.plan = { tracks: [{ id: "cpp", lessons: [one, two] }] };
  e.current("cpp-002", "cpp");
  e.run("index=plan;trackId='cpp';");
  e.element("source").value = "retained source";
  e.element("stage").value = "advanced";
  await e.event("stage", "change");
  assert.equal(e.next("module-lesson"), undefined);
  assert.equal(e.next("module-save"), undefined);
  assert.equal(e.run("lessonId"), "cpp-002");
  assert.equal(e.element("lessons").children.length, 1);
  assert.equal(e.element("source").value, "retained source");
});

await test("changing filters during a pending save keeps the same selected draft", async () => {
  const e = environment();
  const rows = [
    { id: "cpp-002", title: "Values", level: "beginner", status: "authored" },
    {
      id: "cpp-020",
      title: "Ownership",
      level: "advanced",
      status: "authored",
    },
  ];
  e.context.plan = { tracks: [{ id: "cpp", lessons: rows }] };
  e.current("cpp-002", "cpp");
  e.run("index=plan;trackId='cpp';");
  e.element("source").value = "my source";
  await e.event("source", "input");
  const saving = e.run("queueSave()");
  await settle();
  const save = e.next("module-save");
  e.element("stage").value = "advanced";
  await e.event("stage", "change");
  e.element("stage").value = "all";
  e.element("lesson-query").value = "ownership";
  await e.event("lesson-query", "input");
  e.resolve(save, { session: {} });
  await saving;
  assert.equal(e.run("current.id"), "cpp-002");
  assert.equal(e.element("source").value, "my source");
  assert.equal(e.next("module-lesson"), undefined);
  assert.deepEqual(JSON.parse(e.storage.get("ds60.classroom.filters.cpp")), {
    query: "ownership",
    stage: "all",
  });
});

await test("latest per-path filter preference survives an explicitly requested lesson load", async () => {
  const e = environment();
  const one = {
      id: "cpp-002",
      title: "Values",
      level: "beginner",
      status: "authored",
      prerequisites: [],
    },
    two = { ...one, id: "cpp-020", title: "Ownership", level: "advanced" };
  e.context.plan = { tracks: [{ id: "cpp", lessons: [one, two] }] };
  e.run("index=plan;trackId='cpp';lessonId='cpp-002';");
  const opening = e.run("openLesson('cpp-020',false)");
  await settle();
  const loading = e.next("module-lesson");
  e.element("stage").value = "all";
  await e.event("stage", "change");
  e.resolve(loading, moduleData(two, "loaded source"));
  await opening;
  assert.equal(e.run("current.id"), "cpp-020");
  assert.equal(e.element("stage").value, "all");
  assert.equal(e.element("source").value, "loaded source");
});

await test("LLM journeys default to textbook width without removing practice contracts", async () => {
  const e = environment();
  const row = {
    id: "llm-002",
    title: "Tokens",
    level: "beginner",
    status: "authored",
    prerequisites: [],
    outcome: "Read token probabilities",
  };
  e.context.plan = { tracks: [{ id: "llm-theory", lessons: [row] }] };
  e.run("index=plan;trackId='llm-theory';current=null;");
  const opened = e.run("openLesson('llm-002',false)");
  await settle();
  e.resolve(e.next("module-lesson"), {
    ...row,
    language: "python",
    runtime_profile: "python-core",
    learning_mode: "practice",
    source: "original code",
    guide_html: "chapter",
    session: {},
    history: [],
    capability: { profile: "python-core", ready: true, detail: "Fixture" },
  });
  await opened;
  assert.match(e.element("authored").className, /reading-focus/);
  assert.equal(e.element("prediction").hidden, false);
  assert.equal(e.element("solution-section").hidden, false);
  await e.event("reading-toggle");
  assert.equal(e.element("authored").className, "panes");
  assert.equal(e.element("source").value, "original code");
  assert.equal(e.storage.get("ds60.classroom.reading.llm-theory"), "false");
});
await test("reading preferences stay specific to a journey and survive chapter navigation", async () => {
  const e = environment();
  e.run("trackId='llm-theory'");
  assert.equal(e.run("preferredReadingView(false)"), true);
  e.storage.set("ds60.module.reading-view.llm-theory", "practice");
  assert.equal(e.run("preferredReadingView(false)"), false);
  e.run("trackId='llm-applied'");
  assert.equal(e.run("preferredReadingView(false)"), true);
  e.run("trackId='cpp'");
  assert.equal(e.run("preferredReadingView(false)"), false);
  e.storage.set("ds60.module.reading-view.cpp", "reading");
  assert.equal(e.run("preferredReadingView(false)"), true);
  e.run("trackId='statistics-ml'");
  assert.equal(e.run("preferredReadingView(true)"), true);
});
function legacyCurrent(e, id = "py-001", language = "python", mode = null) {
  e.current(id, language);
  e.run(
    "current.engine='legacy';current.runner={id:current.language,executor:current.language};current.effective={allowed_timeout_seconds:[15,60,120],timeout_seconds:60};",
  );
  e.context.chosenMode = mode;
  e.run(
    'current.mode=chosenMode;phaseNotes={read:"read note",attempt:"attempt note",compare:"compare note"};phase="read";',
  );
  e.element("phase-note").value = "read note";
  e.element("prediction").value = "my prediction";
  e.element("explanation").value = "my explanation";
}
async function resolveLegacySave(e, pending) {
  await settle();
  const pad = e.next("save-pad");
  if (pad) e.resolve(pad, { ok: true });
  for (let i = 0; i < 5; i++) {
    await settle();
    e.resolve(e.next("save"), {});
  }
  await pending;
}
function legacyData(id = "sql-001") {
  const sql = {
    id: "sql",
    title: "SQL",
    executor: "sql",
    kind: "code",
    file_suffix: ".sql",
    available: true,
    can_run: true,
    default_mode: "snippet",
    allowed_timeout_seconds: [15, 60, 120],
    timeout_seconds: 60,
    modes: [
      { id: "snippet", title: "SQL snippet", available: true, can_run: true },
      {
        id: "lesson",
        title: "Whole SQL lesson",
        available: true,
        can_run: true,
      },
    ],
  };
  const python = {
    id: "python",
    title: "Python",
    executor: "python",
    kind: "code",
    file_suffix: ".py",
    available: true,
    can_run: true,
    allowed_timeout_seconds: [15, 60, 120],
    timeout_seconds: 60,
  };
  return {
    id,
    title: "Shared lesson",
    level: "beginner",
    prerequisites: [],
    session: {
      read: "reading",
      predict: "prediction",
      attempt: "attempt",
      compare: "comparison",
      explain: "explanation",
    },
    lesson_path: "sql/lesson.sql",
    learner_code: "SELECT 1;",
    guide_html: "guide",
    capabilities: { default_runner: "sql", runners: [sql, python] },
  };
}
await test("legacy saves capture their language mode source and all five evidence phases", async () => {
  const e = environment();
  legacyCurrent(e, "bridge-001", "sql", "snippet");
  e.element("source").value = "SELECT 42;";
  const saving = e.run("queueSave()");
  await settle();
  assert.deepEqual(e.next("save-pad").body, {
    action: "save-pad",
    lesson_id: "bridge-001",
    language: "sql",
    mode: "snippet",
    code: "SELECT 42;",
  });
  e.current("java-001", "java");
  e.element("source").value = "new Java source";
  await resolveLegacySave(e, saving);
  assert.deepEqual(
    e.requests
      .filter((r) => r.body.action === "save")
      .map((r) => [r.body.phase, r.body.note]),
    [
      ["read", "read note"],
      ["predict", "my prediction"],
      ["attempt", "attempt note"],
      ["compare", "compare note"],
      ["explain", "my explanation"],
    ],
  );
  assert.ok(
    e.requests
      .filter((r) => r.body.action === "save")
      .every((r) => r.body.lesson_id === "bridge-001"),
  );
  assert.equal(e.element("source").value, "new Java source");
});
await test("SQL snippet whole-lesson and alternate language drafts have distinct identities", async () => {
  const e = environment();
  legacyCurrent(e, "bridge-001", "sql", "snippet");
  assert.equal(e.run("workspaceKey()"), "bridge-001:sql:snippet");
  e.element("source").value = "SELECT 42;";
  await e.event("source", "input");
  e.run("current.mode='lesson';");
  e.element("source").value = "\\i setup.sql\nSELECT 7;";
  await e.event("source", "input");
  e.run("current.mode=null;current.runner.id='python';");
  e.element("source").value = "print(1)";
  await e.event("source", "input");
  assert.equal(
    JSON.parse(e.storage.get("ds60.classroom.unsaved.bridge-001:sql:snippet"))
      .source,
    "SELECT 42;",
  );
  assert.equal(
    JSON.parse(e.storage.get("ds60.classroom.unsaved.bridge-001:sql:lesson"))
      .source,
    "\\i setup.sql\nSELECT 7;",
  );
  assert.equal(
    JSON.parse(
      e.storage.get("ds60.classroom.unsaved.bridge-001:python:snippet"),
    ).source,
    "print(1)",
  );
});
await test("whole-lesson selection reads its own working copy and preserves intentionally empty pads", async () => {
  const e = environment();
  e.context.subject = { id: "sql", engine: "legacy" };
  const loading = e.run(
    "fetchLesson('sql-001',subject,{language:'sql',mode:'lesson'})",
  );
  e.resolve(e.next("lesson"), legacyData());
  await settle();
  assert.deepEqual(e.next("read-pad").body, {
    action: "read-pad",
    lesson_id: "sql-001",
    language: "sql",
    mode: "lesson",
  });
  e.resolve(e.next("read-pad"), { code: "", saved: true, mode: "lesson" });
  const loaded = await loading;
  assert.equal(loaded.source, "");
  assert.equal(loaded.mode, "lesson");
});
await test("failed cross-subject saves keep the visible source and stop lesson fetches", async () => {
  const e = environment();
  e.current("a");
  e.element("source").value = "important draft";
  e.context.plan = {
    tracks: [
      {
        id: "t",
        engine: "module",
        lessons: [
          { id: "a", title: "A" },
          { id: "b", title: "B" },
        ],
      },
    ],
  };
  e.run("index=plan;trackId='t';");
  const opening = e.run("openLesson('b')");
  await settle();
  e.reject(e.next("module-save"));
  await assert.rejects(opening, /fixture failure/);
  assert.equal(e.next("module-lesson"), undefined);
  assert.equal(e.run("current.id"), "a");
  assert.equal(e.element("source").value, "important draft");
  assert.equal(
    JSON.parse(e.storage.get("ds60.classroom.unsaved.a")).source,
    "important draft",
  );
});
await test("typing during a lesson load preserves the newer source instead of replacing it", async () => {
  const e = environment();
  e.current("a");
  e.element("source").value = "first";
  e.context.plan = {
    tracks: [
      {
        id: "t",
        engine: "module",
        lessons: [
          { id: "a", title: "A" },
          { id: "b", title: "B" },
        ],
      },
    ],
  };
  e.run("index=plan;trackId='t';");
  const opening = e.run("openLesson('b')");
  await settle();
  e.resolve(e.next("module-save"), { session: {} });
  await settle();
  e.element("source").value = "newer while loading";
  await e.event("source", "input");
  e.resolve(e.next("module-lesson"), moduleData({ id: "b", title: "B" }));
  await opening;
  assert.equal(e.run("current.id"), "a");
  assert.equal(e.element("source").value, "newer while loading");
  assert.match(e.element("status").textContent, /edited.*loading/);
});
await test("old module browser drafts recover in the unified workspace without losing notes", async () => {
  const e = environment(),
    row = {
      id: "llm-002",
      title: "Tokens",
      level: "beginner",
      status: "authored",
      prerequisites: [],
    };
  e.context.plan = {
    tracks: [{ id: "llm-theory", engine: "module", lessons: [row] }],
  };
  e.run("index=plan;");
  e.storage.set(
    "ds60.module.unsaved.llm-002",
    JSON.stringify({
      source: "old retained source",
      prediction: "old prediction",
      explanation: "old explanation",
    }),
  );
  const loading = e.run("openLesson('llm-002',false)");
  e.resolve(e.next("module-lesson"), moduleData(row));
  await loading;
  assert.equal(e.element("source").value, "old retained source");
  assert.equal(e.element("explanation").value, "old explanation");
  assert.match(e.element("save-state").textContent, /Recovered/);
});
await test("partial legacy save failures preserve complete browser evidence for retry", async () => {
  const e = environment();
  legacyCurrent(e);
  e.element("source").value = "print(42)";
  const saving = e.run("queueSave()");
  await settle();
  e.resolve(e.next("save-pad"), { ok: true });
  await settle();
  e.resolve(e.next("save"), {});
  await settle();
  e.reject(e.next("save"), "evidence disk failure");
  await assert.rejects(saving, /disk failure/);
  const backup = JSON.parse(
    e.storage.get("ds60.classroom.unsaved.py-001:python:snippet"),
  );
  assert.equal(backup.source, "print(42)");
  assert.equal(backup.evidence.attempt, "attempt note");
  assert.match(e.element("save-state").textContent, /Server save failed/);
});
await test("late syntax preview responses never paint a newer draft", async () => {
  const e = environment();
  e.current();
  e.element("source").value = "first";
  e.run("previewVisible=true;");
  const first = e.run("renderSyntaxPreview()");
  const old = e.next("classroom-highlight");
  e.element("source").value = "second";
  const second = e.run("renderSyntaxPreview()");
  const latest = e.next("classroom-highlight");
  const coloredSource =
    '<span class="syntax-keyword">print</span>("second")\n    <span class="syntax-number">2</span>\n';
  e.resolve(latest, { html: coloredSource });
  await second;
  e.resolve(old, { html: "FIRST" });
  await first;
  const block = e.element("syntax-code").children[0];
  assert.equal(block.tagName, "PRE");
  assert.equal(block.className, "highlighted-code");
  assert.equal(block.children[0].tagName, "CODE");
  assert.equal(block.children[0].innerHTML, coloredSource);
  assert.equal(e.element("source").value, "second");
});
await test("syntax previews reject responses belonging to another language workspace", async () => {
  const e = environment();
  legacyCurrent(e, "bridge-001", "sql", "snippet");
  e.element("source").value = "SELECT 42;";
  e.run("previewVisible=true;");
  const preview = e.run("renderSyntaxPreview()");
  const pending = e.next("classroom-highlight");
  e.run("current.runner.id='python';current.language='python';");
  e.resolve(pending, { html: "STALE SQL" });
  await preview;
  assert.equal(e.element("syntax-code").innerHTML, "");
});
await test("late legacy output stays attached to its submitted lesson and pad", async () => {
  const e = environment();
  legacyCurrent(e, "sql-001", "sql", "snippet");
  e.context.receiptContext = e.run("contextOf()");
  e.current("java-001", "java");
  e.element("output").textContent = "Java workspace unchanged";
  e.context.result = {
    returncode: 0,
    output: "SQL output",
    elapsed_seconds: 1,
    language: "sql",
  };
  e.run("showLegacyResult(result,receiptContext,'SELECT 42;')");
  assert.equal(e.element("output").textContent, "Java workspace unchanged");
  assert.equal(
    e.run("legacyReceipts.get('sql-001:sql:snippet').source"),
    "SELECT 42;",
  );
});
await test("browser back waits for saves and restores the current route on failure", async () => {
  const e = environment();
  e.current("a");
  e.element("source").value = "precious draft";
  e.context.plan = {
    tracks: [{ id: "t", engine: "module", lessons: [{ id: "a", title: "A" }] }],
  };
  e.run("index=plan;visibleRoute='/classroom#lesson=a';");
  e.location.hash = "";
  const back = e.windowHandlers.get("popstate")();
  await settle();
  e.reject(e.next("module-save"), "disk unavailable");
  await back;
  assert.equal(e.location.hash, "#lesson=a");
  assert.equal(e.element("source").value, "precious draft");
  assert.match(e.element("status").textContent, /Navigation paused/);
});
await test("home navigation saves before hiding the active workspace", async () => {
  const e = environment();
  e.current("a");
  e.element("workspace-view").hidden = false;
  e.element("home-view").hidden = true;
  e.context.plan = {
    tracks: [
      {
        id: "t",
        engine: "module",
        title: "Track",
        lessons: [{ id: "a", title: "A" }],
      },
    ],
  };
  e.run("index=plan;trackId='t';");
  const home = e.run("showHome()");
  await settle();
  assert.equal(e.element("workspace-view").hidden, false);
  e.resolve(e.next("module-save"), { session: {} });
  await home;
  assert.equal(e.element("workspace-view").hidden, true);
  assert.equal(e.element("home-view").hidden, false);
});
await test("phase switching keeps separate reading attempt and comparison evidence", async () => {
  const e = environment();
  legacyCurrent(e);
  e.element("phase-note").value = "new read notes";
  e.element("phase").value = "attempt";
  await e.event("phase", "change");
  assert.equal(e.element("phase-note").value, "attempt note");
  e.element("phase-note").value = "new attempt notes";
  e.element("phase").value = "compare";
  await e.event("phase", "change");
  assert.equal(e.element("phase-note").value, "compare note");
  const fields = e.run("values()");
  assert.equal(fields.evidence.read, "new read notes");
  assert.equal(fields.evidence.attempt, "new attempt notes");
  assert.equal(fields.evidence.predict, "my prediction");
});
await test("runtime refresh never replaces source or notes with server copies", async () => {
  const e = environment();
  e.current();
  e.element("source").value = "unsaved source";
  e.element("explanation").value = "unsaved notes";
  const checking = e.event("refresh");
  await settle();
  e.resolve(e.next("module-lesson"), {
    id: "llm-009",
    source: "server source",
    session: { explanation: "server note" },
    capability: { ready: true, profile: "python-core" },
    history: [],
  });
  await checking;
  assert.equal(e.element("source").value, "unsaved source");
  assert.equal(e.element("explanation").value, "unsaved notes");
});
await test("unavailable browser storage reports that the learner must retain a local copy", async () => {
  const e = environment();
  e.current();
  e.context.localStorage.setItem = () => {
    throw new Error("quota");
  };
  e.element("source").value = "important";
  await e.event("source", "input");
  assert.match(e.element("save-state").textContent, /storage is unavailable/);
  const saving = e.run("queueSave()");
  await settle();
  e.reject(e.next("module-save"));
  await assert.rejects(saving);
  assert.match(e.element("save-state").textContent, /copy your work/);
});
await test("editor Escape allows keyboard users to leave the Tab-indenting pad", async () => {
  const e = environment();
  const handler = e.element("source").handlers.keydown[0];
  let prevented = false;
  handler({ key: "Escape" });
  handler({
    key: "Tab",
    target: e.element("source"),
    preventDefault() {
      prevented = true;
    },
  });
  assert.equal(prevented, false);
  handler({
    key: "Tab",
    shiftKey: true,
    target: e.element("source"),
    preventDefault() {
      prevented = true;
    },
  });
  assert.equal(prevented, false);
});
await test("all fourteen subject accents meet text contrast in both appearances", async () => {
  const e = environment();
  const palette = e.run("themes");
  assert.equal(Object.keys(palette).length, 14);
  const luminance = (hex) => {
    const rgb = hex
      .slice(1)
      .match(/../g)
      .map((v) => parseInt(v, 16) / 255)
      .map((v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];
  };
  const contrast = (a, b) => {
    const pair = [luminance(a), luminance(b)].sort((a, b) => b - a);
    return (pair[0] + 0.05) / (pair[1] + 0.05);
  };
  for (const [id, [light, tint, dark, darkTint]] of Object.entries(palette)) {
    assert.ok(contrast(light, "#ffffff") >= 4.5, id + " light text");
    assert.ok(contrast(light, tint) >= 4.5, id + " light tinted text");
    assert.ok(contrast(dark, "#20232b") >= 4.5, id + " dark text");
    assert.ok(contrast(dark, darkTint) >= 4.5, id + " dark tinted text");
  }
});

await test("reading-only module worksheets remain editable without inventing a runtime", async () => {
  const e = environment(),
    row = {
      id: "llm-001",
      title: "Reasoning",
      level: "beginner",
      status: "authored",
      prerequisites: [],
    };
  e.context.plan = {
    tracks: [{ id: "llm-theory", engine: "module", lessons: [row] }],
  };
  e.run("index=plan;");
  const loading = e.run("openLesson('llm-001',false)");
  e.resolve(e.next("module-lesson"), {
    ...moduleData(row, "# Written reasoning\n"),
    language: "markdown",
    runtime_profile: "reading",
    capability: { ready: true, profile: "reading" },
  });
  await loading;
  assert.equal(e.element("source-section").hidden, false);
  assert.equal(e.element("run").disabled, true);
  assert.equal(e.element("source").value, "# Written reasoning\n");
});
await test("console stdout and stderr explicitly use readable code colors in both appearances", async () => {
  const css = fs.readFileSync(filename.replace(/\.js$/, ".css"), "utf8");
  const declarations = (text) =>
    Object.fromEntries(
      [...text.matchAll(/(--[a-z-]+)\s*:\s*([^;]+);/g)].map((match) => [
        match[1],
        match[2].trim(),
      ]),
    );
  const light = declarations(css.match(/:root\s*\{([^}]+)\}/)[1]);
  const dark = {
    ...light,
    ...declarations(css.match(/body\[data-mode="dark"\]\s*\{([^}]+)\}/)[1]),
  };
  const consoleRule = css.match(/\.result-log\s*\{([^}]+)\}/)[1];
  assert.match(consoleRule, /background:\s*var\(--code-bg\)/);
  assert.match(consoleRule, /(?:^|;)\s*color:\s*var\(--code-text\)/);
  const luminance = (hex) => {
    const values = hex
      .slice(1)
      .match(/../g)
      .map((value) => parseInt(value, 16) / 255)
      .map((value) =>
        value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4,
      );
    return 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2];
  };
  for (const [appearance, tokens] of Object.entries({ light, dark })) {
    const values = [
      luminance(tokens["--code-text"]),
      luminance(tokens["--code-bg"]),
    ].sort((a, b) => b - a);
    assert.ok(
      (values[0] + 0.05) / (values[1] + 0.05) >= 7,
      appearance + " console contrast meets 7:1",
    );
  }
});
function guideLink(e, href, modifiers = {}) {
  const anchor = {
    getAttribute: (name) =>
      name === "href" ? href : (modifiers.attributes?.[name] ?? null),
  };
  let prevented = false;
  const event = {
    target: { closest: () => anchor },
    button: 0,
    preventDefault() {
      prevented = true;
    },
    ...modifiers,
  };
  e.context.linkEvent = event;
  return {
    event,
    prevented: () => prevented,
    follow: () => e.run("followGuideLink(linkEvent)"),
  };
}
function linkedPlan(e) {
  const a = {
    id: "llm-001",
    title: "First",
    status: "authored",
    level: "beginner",
    prerequisites: [],
  };
  const b = { ...a, id: "llm-002", title: "Second" };
  e.context.plan = {
    tracks: [
      {
        id: "llm-theory",
        engine: "module",
        title: "LLM theory",
        lessons: [a, b],
      },
    ],
    lesson_links: {
      "/reference-pages/courses/llm-theory/guides/002.md.html": "llm-002",
    },
  };
  e.run("index=plan;trackId='llm-theory';");
  return { a, b };
}
await test("mapped cross-lesson links wait for the current draft save and remain in the classroom", async () => {
  const e = environment(),
    { b } = linkedPlan(e);
  e.current("llm-001");
  e.element("source").value = "retained draft";
  const heading = e.element("module-guide--attention");
  heading.id = "module-guide--attention";
  e.element("guide").querySelectorAll = (selector) =>
    selector === "[id]" ? [heading] : [];
  const link = guideLink(
    e,
    "/reference-pages/courses/llm-theory/guides/002.md.html#attention",
  );
  const following = link.follow();
  await settle();
  assert.equal(link.prevented(), true);
  assert.equal(e.next("module-lesson"), undefined);
  assert.equal(e.next("module-save").body.fields.source, "retained draft");
  e.resolve(e.next("module-save"), { session: {} });
  await settle();
  assert.equal(e.next("module-lesson").body.lesson_id, "llm-002");
  e.resolve(e.next("module-lesson"), moduleData(b));
  await following;
  assert.equal(e.run("current.id"), "llm-002");
  assert.equal(e.location.pathname, "/classroom");
  assert.equal(heading.focused, true);
});
await test("mapped links preserve the old lesson and URL when its save fails", async () => {
  const e = environment();
  linkedPlan(e);
  e.current("llm-001");
  e.element("source").value = "important";
  const link = guideLink(
    e,
    "/reference-pages/courses/llm-theory/guides/002.md.html",
  );
  const following = link.follow();
  await settle();
  e.reject(e.next("module-save"), "disk unavailable");
  await following;
  assert.equal(e.run("current.id"), "llm-001");
  assert.equal(e.next("module-lesson"), undefined);
  assert.equal(e.element("source").value, "important");
  assert.match(e.element("status").textContent, /Navigation paused/);
});
await test("external modified and new-tab guide clicks keep normal browser behavior", async () => {
  for (const [href, modifiers] of [
    [
      "https://example.org/reference-pages/courses/llm-theory/guides/002.md.html",
      {},
    ],
    [
      "/reference-pages/courses/llm-theory/guides/002.md.html",
      { ctrlKey: true },
    ],
    [
      "/reference-pages/courses/llm-theory/guides/002.md.html",
      { metaKey: true },
    ],
    [
      "/reference-pages/courses/llm-theory/guides/002.md.html",
      { shiftKey: true },
    ],
    [
      "/reference-pages/courses/llm-theory/guides/002.md.html",
      { altKey: true },
    ],
    ["/reference-pages/courses/llm-theory/guides/002.md.html", { button: 1 }],
    [
      "/reference-pages/courses/llm-theory/guides/002.md.html",
      { attributes: { target: "_blank" } },
    ],
    [
      "/reference-pages/courses/llm-theory/guides/002.md.html",
      { attributes: { download: "" } },
    ],
  ]) {
    const e = environment();
    linkedPlan(e);
    const link = guideLink(e, href, modifiers);
    await link.follow();
    assert.equal(link.prevented(), false);
    assert.equal(e.next("module-lesson"), undefined);
    assert.equal(e.next("module-save"), undefined);
  }
});
await test("unmapped references and solution artifacts never cause implicit solution reveal", async () => {
  for (const path of [
    "/reference-pages/docs/guide.md.html",
    "/reference-pages/courses/llm-theory/solutions/002.md.html",
  ]) {
    const e = environment();
    linkedPlan(e);
    const link = guideLink(e, path);
    await link.follow();
    assert.equal(link.prevented(), false);
    assert.equal(e.next("module-lesson"), undefined);
    assert.equal(e.next("classroom-solutions"), undefined);
    assert.equal(e.next("module-solutions"), undefined);
  }
});
await test("a missing lesson link map leaves references safe while known reader links still resolve", async () => {
  const e = environment(),
    { b } = linkedPlan(e);
  e.run("delete index.lesson_links;");
  const reference = guideLink(
    e,
    "/reference-pages/courses/llm-theory/guides/002.md.html",
  );
  await reference.follow();
  assert.equal(reference.prevented(), false);
  const reader = guideLink(e, "/lesson-pages/llm-002.html#guide--attention");
  const heading = e.element("module-guide--attention");
  heading.id = "module-guide--attention";
  e.element("guide").querySelectorAll = (selector) =>
    selector === "[id]" ? [heading] : [];
  const following = reader.follow();
  await settle();
  e.resolve(e.next("module-lesson"), moduleData(b));
  await following;
  assert.equal(reader.prevented(), true);
  assert.equal(heading.focused, true);
});
await test("late mapped-link results cannot scroll an unrelated newer lesson", async () => {
  const e = environment(),
    { b } = linkedPlan(e);
  const heading = e.element("module-guide--attention");
  heading.id = "module-guide--attention";
  e.element("guide").querySelectorAll = (selector) =>
    selector === "[id]" ? [heading] : [];
  const link = guideLink(
    e,
    "/reference-pages/courses/llm-theory/guides/002.md.html#attention",
  );
  const following = link.follow();
  await settle();
  const pending = e.next("module-lesson");
  e.current("java-001", "java");
  e.run("intentVersion++;");
  e.resolve(pending, moduleData(b));
  await following;
  assert.equal(e.run("current.id"), "java-001");
  assert.notEqual(heading.focused, true);
});
function receiptFixture(
  context,
  id = "saved-1",
  source = 'print("earlier")\n',
) {
  return {
    id,
    saved_at: "2026-10-23T21:10:00+00:00",
    lesson_id: context.id,
    language: context.language,
    mode: context.mode || "snippet",
    source,
    source_sha256: "a".repeat(64),
    result: {
      returncode: 0,
      elapsed_seconds: 0.1,
      language: context.language,
      mode: context.mode || "snippet",
      output: "earlier output",
    },
  };
}
function receiptMetadata(receipt) {
  return {
    id: receipt.id,
    saved_at: receipt.saved_at,
    lesson_id: receipt.lesson_id,
    language: receipt.language,
    mode: receipt.mode,
    source_sha256: receipt.source_sha256,
    returncode: 0,
    status: "succeeded",
  };
}
await test("saved run history restores the latest durable output without replaying or changing the pad", async () => {
  const e = environment();
  legacyCurrent(e);
  e.element("source").value = "my current draft";
  e.element("explanation").value = "current notes";
  const context = e.run("contextOf()"),
    receipt = receiptFixture(context);
  const loading = e.run("refreshRunHistory({showLatest:true})");
  await settle();
  assert.deepEqual(e.next("classroom-history").body, {
    action: "classroom-history",
    lesson_id: "py-001",
    language: "python",
    mode: "snippet",
  });
  e.resolve(e.next("classroom-history"), {
    history: [receiptMetadata(receipt)],
  });
  await settle();
  assert.equal(e.next("classroom-run-result").body.receipt_id, "saved-1");
  e.resolve(e.next("classroom-run-result"), { receipt });
  await loading;
  assert.equal(e.element("output").textContent, "earlier output");
  assert.equal(e.element("source").value, "my current draft");
  assert.equal(e.element("explanation").value, "current notes");
  assert.match(e.element("run-storage-status").textContent, /Saved run/);
  assert.equal(e.element("error-line").hidden, true);
  assert.equal(
    e.requests.some((request) =>
      ["run", "run-lesson", "module-run", "save-pad"].includes(
        request.body.action,
      ),
    ),
    false,
  );
});
await test("late saved history cannot start receipt loading after a language or SQL mode switch", async () => {
  const e = environment();
  legacyCurrent(e, "sql-001", "sql", "snippet");
  const context = e.run("contextOf()"),
    receipt = receiptFixture(context);
  const loading = e.run("refreshRunHistory({showLatest:true})");
  await settle();
  e.run("current.mode='lesson';");
  e.element("output").textContent = "whole lesson output";
  e.resolve(e.next("classroom-history"), {
    history: [receiptMetadata(receipt)],
  });
  await loading;
  assert.equal(e.next("classroom-run-result"), undefined);
  assert.equal(e.element("output").textContent, "whole lesson output");
});
await test("late saved receipt results cannot appear in another lesson", async () => {
  const e = environment();
  legacyCurrent(e);
  e.context.receiptContext = e.run("contextOf()");
  const receipt = receiptFixture(e.context.receiptContext);
  const loading = e.run("openRunReceipt(receiptContext,'saved-1')");
  await settle();
  e.current("java-001", "java");
  e.element("output").textContent = "Java output";
  e.element("receipt-source-details").hidden = true;
  e.resolve(e.next("classroom-run-result"), { receipt });
  await loading;
  assert.equal(e.element("output").textContent, "Java output");
  assert.equal(e.element("receipt-source-details").hidden, true);
  assert.equal(e.next("classroom-highlight"), undefined);
});
await test("choosing an earlier receipt shows its recorded source without replacing newer code", async () => {
  const e = environment();
  legacyCurrent(e);
  e.element("source").value = "newer code";
  const context = e.run("contextOf()"),
    receipt = receiptFixture(context, "older", 'print("old code")\n');
  const loading = e.run("refreshRunHistory()");
  e.resolve(e.next("classroom-history"), {
    history: [receiptMetadata(receipt)],
  });
  await loading;
  const clicked = e.element("history").children[0].handlers.click[0]();
  await settle();
  e.resolve(e.next("classroom-run-result"), { receipt });
  await clicked;
  assert.equal(e.element("source").value, "newer code");
  assert.equal(
    e.element("receipt-source").children[0].children[0].textContent,
    'print("old code")\n',
  );
  assert.equal(e.element("output").textContent, "earlier output");
  const sourceBlock = e.element("receipt-source").children[0];
  const coloredSource =
    '<span class="syntax-builtin">print</span>("old code")\n';
  e.resolve(e.next("classroom-highlight"), { html: coloredSource });
  await settle();
  assert.equal(e.element("receipt-source").children[0], sourceBlock);
  assert.equal(sourceBlock.tagName, "PRE");
  assert.equal(sourceBlock.className, "highlighted-code");
  assert.equal(sourceBlock.children[0].tagName, "CODE");
  assert.equal(sourceBlock.children[0].innerHTML, coloredSource);
  assert.equal(e.element("source").value, "newer code");
  assert.equal(
    e.requests.some((request) =>
      ["run", "run-lesson", "module-run", "save-pad"].includes(
        request.body.action,
      ),
    ),
    false,
  );
});
await test("receipt save failures preserve actual output and explicitly avoid claiming persistence or retry", async () => {
  const e = environment();
  legacyCurrent(e);
  e.context.receiptContext = e.run("contextOf()");
  e.context.result = {
    returncode: 0,
    elapsed_seconds: 1,
    output: "actual completed result",
    language: "python",
    receipt_saved: false,
    receipt_error: "Disk full",
  };
  e.run("showLegacyResult(result,receiptContext,'print(42)')");
  assert.equal(e.element("output").textContent, "actual completed result");
  assert.match(
    e.element("run-storage-status").textContent,
    /could not be saved/,
  );
  assert.match(e.element("run-storage-status").textContent, /Disk full/);
  assert.match(
    e.element("run-storage-status").textContent,
    /No automatic retry/,
  );
  assert.equal(
    e.requests.some((request) =>
      ["run", "run-lesson", "module-run"].includes(request.body.action),
    ),
    false,
  );
});
await test("new live output cannot be replaced by an older pending history result", async () => {
  const e = environment();
  legacyCurrent(e);
  e.context.receiptContext = e.run("contextOf()");
  const receipt = receiptFixture(e.context.receiptContext);
  const loading = e.run("openRunReceipt(receiptContext,'saved-1')");
  await settle();
  e.context.latest = {
    returncode: 0,
    elapsed_seconds: 1,
    language: "python",
    output: "new live output",
    receipt_saved: true,
  };
  e.run("showLegacyResult(latest,receiptContext,'print(2)')");
  e.resolve(e.next("classroom-run-result"), { receipt });
  await loading;
  assert.equal(e.element("output").textContent, "new live output");
});
await test("saved receipt diagnostics require the exact currently edited source", async () => {
  const e = environment();
  legacyCurrent(e);
  e.context.receiptContext = e.run("contextOf()");
  const receipt = receiptFixture(e.context.receiptContext, "bad", "one\ntwo");
  receipt.result.output = '  File "practice.py", line 2\nValueError';
  receipt.result.returncode = 1;
  e.element("source").value = "one\ntwo";
  const loading = e.run("openRunReceipt(receiptContext,'bad')");
  e.resolve(e.next("classroom-run-result"), { receipt });
  await loading;
  assert.equal(e.element("error-line").hidden, false);
  e.element("source").value = "changed";
  await e.event("source", "input");
  assert.equal(e.element("error-line").hidden, true);
});
await test("mapped solution anchors focus the explicit reveal control without opening answers", async () => {
  const e = environment(),
    { b } = linkedPlan(e);
  const link = guideLink(e, "/lesson-pages/llm-002.html#solution-1");
  const following = link.follow();
  await settle();
  e.resolve(e.next("module-lesson"), moduleData(b));
  await following;
  assert.equal(e.element("reveal").focused, true);
  assert.match(e.element("status").textContent, /Choose Reveal solutions/);
  assert.equal(e.next("classroom-solutions"), undefined);
  assert.equal(e.next("module-solutions"), undefined);
  assert.equal(e.location.pathname, "/classroom");
});
console.log(JSON.stringify({ checks, passed: true, final: true }));
