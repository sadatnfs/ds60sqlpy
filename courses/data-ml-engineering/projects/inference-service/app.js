"use strict";
const token = document.querySelector('meta[name="workshop-token"]').content;
const node = (id) => document.getElementById(id);
let activeId = null;
let selectedId = null;
let streaming = false;
let pending = null;
try {
  pending = JSON.parse(sessionStorage.getItem("inference-pending") || "null");
} catch {
  pending = null;
}
if (
  pending &&
  (typeof pending !== "object" ||
    !pending.parameters ||
    typeof pending.idempotency_key !== "string" ||
    !/^[A-Za-z0-9_-]{8,80}$/.test(pending.idempotency_key) ||
    typeof pending.parameters.prompt !== "string" ||
    !Array.isArray(pending.parameters.stops) ||
    !pending.parameters.stops.every((value) => typeof value === "string") ||
    !["max_new_tokens", "temperature", "top_k", "seed"].every((key) =>
      Number.isFinite(pending.parameters[key]),
    ))
) {
  pending = null;
  sessionStorage.removeItem("inference-pending");
}
const api = (path, options = {}) =>
  fetch(path, {
    ...options,
    cache: "no-store",
    headers: { "X-Workshop-Token": token, ...(options.headers || {}) },
  });
function message(text) {
  node("request-status").textContent = text;
}
function busy(value) {
  streaming = value;
  node("submit").disabled = value;
  node("cancel").disabled = !value;
  node("readback").disabled = value || !selectedId;
  node("download").disabled = value || !selectedId;
}
async function jsonResponse(response) {
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || `HTTP ${response.status}`);
  return result;
}
async function readiness() {
  const status = await jsonResponse(await api("/api/status"));
  node("readiness").textContent =
    `Ready on ${status.device}. ${status.waiting} waiting; ${status.reserved_tokens} tokens reserved. ${status.generation_calls} generation calls since startup.`;
  const facts = {
    Parameters: status.parameters.toLocaleString(),
    "Context / vocabulary": `${status.context} / ${status.vocabulary}`,
    "Model SHA-256": status.model_sha256,
    "Load / warm-up": `${status.load_seconds.toFixed(3)} s / ${status.warm_seconds.toFixed(3)} s`,
    "Demonstration pacing": `${status.pacing_seconds} seconds per token, outside compute timing`,
  };
  node("model-facts").replaceChildren();
  for (const [label, value] of Object.entries(facts)) {
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value;
    node("model-facts").append(dt, dd);
  }
}
function observe(event) {
  node("events").textContent += `${event.id} ${event.kind} ${JSON.stringify(event.data)}\n`;
  if (event.kind === "token") node("output").textContent += event.data.text;
  if (["completed", "cancelled", "error"].includes(event.kind)) {
    node("output").textContent = event.data.text;
    const values = Object.entries(event.data.metrics).map(
      ([key, value]) => `${key}: ${Number.isInteger(value) ? value : value.toFixed(5)}`,
    );
    node("metrics").textContent = `${values.join(" · ")} ${event.data.warning || ""}`;
    message(
      `${event.kind}: ${event.data.reason}. ${event.data.durable ? "Record saved." : "Download this result before leaving."}`,
    );
  }
}
async function streamEvents(identity) {
  const response = await api(`/api/requests/${identity}/events`);
  if (!response.ok) await jsonResponse(response);
  if (!response.body) throw new Error("Streaming response body is unavailable");
  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8", { fatal: true });
  let buffer = "";
  let last = 0;
  let terminal = false;
  let receivedBytes = 0;
  const frameByteLimit = 32768 + 128;
  const streamByteLimit = 262144;
  const encoder = new TextEncoder();
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (!done) {
        receivedBytes += value.byteLength;
        if (receivedBytes > streamByteLimit)
          throw new Error("SSE response exceeds the workshop limit");
      }
      buffer += done ? decoder.decode() : decoder.decode(value, { stream: true });
      let boundary;
      while ((boundary = buffer.indexOf("\n\n")) >= 0) {
        const frame = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        if (encoder.encode(frame).byteLength > frameByteLimit)
          throw new Error("SSE frame exceeds the workshop limit");
        let identityText = "";
        let kind = "message";
        const data = [];
        for (const line of frame.split("\n")) {
          if (line.startsWith("id: ")) identityText = line.slice(4);
          if (line.startsWith("event: ")) kind = line.slice(7);
          if (line.startsWith("data: ")) data.push(line.slice(6));
        }
        if (!data.length) continue;
        const id = Number(identityText);
        if (!Number.isSafeInteger(id) || id !== last + 1)
          throw new Error("SSE event identity is out of sequence");
        last = id;
        const parsed = JSON.parse(data.join("\n"));
        observe({ id, kind, data: parsed });
        terminal = ["completed", "cancelled", "error"].includes(kind);
      }
      if (encoder.encode(buffer).byteLength > frameByteLimit)
        throw new Error("SSE frame exceeds the workshop limit");
      if (done) {
        if (buffer || !terminal)
          throw new Error(
            "Stream ended without a terminal event. Read history to reconcile; no request was replayed.",
          );
        break;
      }
    }
  } finally {
    await reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}
function select(identity) {
  selectedId = identity;
  node("request-id").textContent = identity;
  node("output").textContent = "";
  node("events").textContent = "";
  node("metrics").textContent = "Waiting for terminal metrics.";
}
async function readback(identity) {
  if (streaming) return;
  select(identity);
  busy(true);
  try {
    await streamEvents(identity);
  } catch (error) {
    message(error.message);
  } finally {
    busy(false);
    await refresh().catch((error) => message(error.message));
  }
}
async function refresh() {
  await readiness();
  const result = await jsonResponse(await api("/api/requests"));
  node("history").replaceChildren();
  for (const entry of result.requests) {
    const row = document.createElement("div");
    row.className = "history-row";
    row.setAttribute("role", "listitem");
    const label = document.createElement("span");
    label.className = "mono";
    label.textContent = `${entry.id} · ${entry.status}`;
    const button = document.createElement("button");
    button.textContent = "Read events";
    button.disabled = streaming || !["completed", "cancelled", "error"].includes(entry.status);
    button.addEventListener("click", () => readback(entry.id));
    row.append(label, button);
    node("history").append(row);
  }
}
node("request-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (streaming) return;
  const parameters = {
    prompt: node("prompt").value,
    max_new_tokens: Number(node("max-tokens").value),
    temperature: Number(node("temperature").value),
    top_k: Number(node("top-k").value),
    seed: Number(node("seed").value),
    stops: node("stop-string").value ? [node("stop-string").value] : [],
  };
  if (pending && JSON.stringify(pending.parameters) !== JSON.stringify(parameters)) {
    message(
      "A previous creation response was unknown. Restore those inputs or reload its saved request before creating a different one.",
    );
    return;
  }
  if (!pending) pending = { parameters, idempotency_key: crypto.randomUUID() };
  sessionStorage.setItem("inference-pending", JSON.stringify(pending));
  busy(true);
  message("Submitting the explicitly requested source.");
  try {
    const response = await api("/api/requests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...pending.parameters,
        idempotency_key: pending.idempotency_key,
      }),
    });
    const result = await response.json();
    if (!response.ok) {
      if (response.status < 500) {
        pending = null;
        sessionStorage.removeItem("inference-pending");
      }
      throw new Error(result.error || `HTTP ${response.status}`);
    }
    activeId = result.id;
    select(result.id);
    pending = null;
    sessionStorage.removeItem("inference-pending");
    message(
      result.created
        ? "Admitted. Opening the explicit event stream."
        : "Original request found. Reading it without a second generation.",
    );
    await streamEvents(result.id);
  } catch (error) {
    message(
      `${error.message}${pending ? " The creation outcome is unknown. Submit the same inputs explicitly to reconcile with the same idempotency key." : ""}`,
    );
  } finally {
    activeId = null;
    busy(false);
    await refresh().catch((error) => message(error.message));
  }
});
node("cancel").addEventListener("click", async () => {
  if (!activeId) return;
  try {
    await jsonResponse(await api(`/api/requests/${activeId}/cancel`, { method: "POST" }));
    message(
      "Cancellation requested. An in-flight kernel must return before its reservation is released.",
    );
  } catch (error) {
    message(error.message);
  }
});
node("readback").addEventListener("click", () => selectedId && readback(selectedId));
node("download").addEventListener("click", async () => {
  if (!selectedId) return;
  try {
    const response = await api(`/api/requests/${selectedId}`);
    if (!response.ok) await jsonResponse(response);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `inference-${selectedId}.json`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (error) {
    message(error.message);
  }
});
node("refresh").addEventListener("click", () => refresh().catch((error) => message(error.message)));
if (pending) {
  for (const [field, key] of [
    ["prompt", "prompt"],
    ["max-tokens", "max_new_tokens"],
    ["temperature", "temperature"],
    ["top-k", "top_k"],
    ["seed", "seed"],
  ])
    node(field).value = pending.parameters[key];
  node("stop-string").value = pending.parameters.stops[0] || "";
  message(
    "A previous creation response was unknown. No request has been replayed. Submit these restored inputs explicitly to reconcile.",
  );
}
refresh().catch((error) => message(error.message));
