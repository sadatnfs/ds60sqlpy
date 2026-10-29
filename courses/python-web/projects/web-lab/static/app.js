"use strict";
let csrf = null;
let configuration = null;
let stream = null;
let currentJob = null;
const seen = new Set();
const output = document.querySelector("#output");
const show = (value) => {
  output.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
};
async function call(path, method = "GET", body = undefined) {
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (csrf) {
    headers["X-CSRF-Token"] = csrf;
    headers["X-CSRFToken"] = csrf;
  }
  const response = await fetch(path, {
    method,
    headers,
    credentials: "same-origin",
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await response.text();
  let result;
  try {
    result = JSON.parse(text);
  } catch {
    result = { error: text.slice(0, 600) };
  }
  if (!response.ok) throw new Error(`HTTP ${response.status}: ${JSON.stringify(result)}`);
  return result;
}
async function refresh() {
  const result = await call("/api/notes");
  const list = document.querySelector("#notes");
  list.replaceChildren();
  for (const note of result.notes) {
    const item = document.createElement("li");
    item.textContent = `${note.id}: ${note.title} (version ${note.version})`;
    list.append(item);
  }
  show(result);
}
function watchJob() {
  if (!currentJob) return;
  if (stream) stream.close();
  stream = new EventSource(`/api/jobs/${encodeURIComponent(currentJob)}/events`);
  stream.addEventListener("progress", (event) => {
    const value = JSON.parse(event.data);
    if (!seen.has(event.lastEventId)) {
      seen.add(event.lastEventId);
      const item = document.createElement("li");
      item.textContent = `Event ${event.lastEventId}: ${value.state}${value.result === null ? "" : `, result ${value.result}`}`;
      document.querySelector("#events").append(item);
    }
    document.querySelector("#job-state").textContent = `Job ${currentJob}: ${value.state}`;
    show(value);
    if (value.state === "finished") {
      stream.close();
      stream = null;
    }
  });
  stream.onerror = () => {
    document.querySelector("#job-state").textContent =
      `Job ${currentJob}: stream interrupted; browser reconnects unless disconnected.`;
  };
  for (const selector of ["#release-job", "#disconnect", "#reconnect"])
    document.querySelector(selector).disabled = false;
}
function guarded(operation) {
  return async (event) => {
    event.preventDefault();
    try {
      await operation(event);
    } catch (error) {
      show(error.message);
    }
  };
}
document.querySelector("#login-form").addEventListener(
  "submit",
  guarded(async (event) => {
    const values = new FormData(event.currentTarget);
    const result = await call("/api/login", "POST", {
      username: values.get("username"),
      password: values.get("password"),
    });
    csrf = result.csrf;
    document.querySelector("#identity").textContent = `Signed in as ${result.username}.`;
    if (stream) {
      stream.close();
      stream = null;
    }
    currentJob = null;
    seen.clear();
    document.querySelector("#events").replaceChildren();
    await refresh();
  }),
);
document.querySelector("#logout").addEventListener(
  "click",
  guarded(async () => {
    await call("/api/logout", "POST");
    csrf = null;
    if (stream) stream.close();
    stream = null;
    document.querySelector("#identity").textContent = "Signed out.";
    document.querySelector("#notes").replaceChildren();
    if (configuration.framework === "Django") csrf = (await call("/api/csrf")).csrf;
    show({ logged_out: true });
  }),
);
document.querySelector("#note-form").addEventListener(
  "submit",
  guarded(async (event) => {
    const form = event.currentTarget;
    await call("/api/notes", "POST", { title: new FormData(form).get("title") });
    form.reset();
    await refresh();
  }),
);
document.querySelector("#refresh").addEventListener("click", guarded(refresh));
document.querySelector("#create-job").addEventListener(
  "click",
  guarded(async () => {
    const result = await call("/api/jobs", "POST", { values: [2, 3, 5] });
    currentJob = result.id;
    localStorage.setItem("python-web-last-job", currentJob);
    seen.clear();
    document.querySelector("#events").replaceChildren();
    watchJob();
  }),
);
document.querySelector("#release-job").addEventListener(
  "click",
  guarded(async () => {
    if (currentJob) show(await call(`/api/jobs/${encodeURIComponent(currentJob)}/release`, "POST"));
  }),
);
document.querySelector("#disconnect").addEventListener("click", () => {
  if (stream) stream.close();
  stream = null;
  document.querySelector("#job-state").textContent =
    `Job ${currentJob}: stream deliberately disconnected; stored job retained.`;
});
document.querySelector("#reconnect").addEventListener(
  "click",
  guarded(async () => {
    if (currentJob) {
      await call(`/api/jobs/${encodeURIComponent(currentJob)}`);
      watchJob();
    }
  }),
);
document.querySelector("#socket").addEventListener("click", () => {
  const socket = new WebSocket(
    `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/socket`,
  );
  socket.onopen = () => socket.send(JSON.stringify({ message: "Local WebSocket" }));
  socket.onmessage = (event) => show(JSON.parse(event.data));
  socket.onerror = () => show("WebSocket failed. Check the session and server logs.");
});
(async () => {
  try {
    configuration = await call("/config");
    document.querySelector("#framework").textContent =
      `${configuration.framework} web engineering lab`;
    document.querySelector("#jobs").hidden = !configuration.jobs;
    document.querySelector("#docs").hidden = configuration.framework !== "FastAPI";
    document.querySelector("#admin").hidden = configuration.framework !== "Django";
    try {
      const result = await call("/api/me");
      csrf = result.csrf;
      document.querySelector("#identity").textContent = `Signed in as ${result.username}.`;
      await refresh();
    } catch {
      document.querySelector("#identity").textContent = "Sign in to inspect your notes.";
      if (configuration.framework === "Django") csrf = (await call("/api/csrf")).csrf;
    }
    const saved = localStorage.getItem("python-web-last-job");
    if (configuration.jobs && csrf && saved && /^[a-f0-9-]{36}$/.test(saved)) {
      try {
        const result = await call(`/api/jobs/${saved}`);
        currentJob = saved;
        show(result);
        watchJob();
      } catch {
        localStorage.removeItem("python-web-last-job");
      }
    }
  } catch (error) {
    show(error.message);
  }
})();
window.addEventListener("pagehide", () => {
  if (stream) stream.close();
});
