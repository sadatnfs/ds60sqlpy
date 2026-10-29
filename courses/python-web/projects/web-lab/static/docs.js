"use strict";
const result = document.querySelector("#result");
function detail(label, data) {
  const element = document.createElement("details");
  const summary = document.createElement("summary");
  summary.textContent = label;
  const content = document.createElement("pre");
  content.textContent = JSON.stringify(data, null, 2);
  element.append(summary, content);
  return element;
}
(async () => {
  try {
    const response = await fetch("/openapi.json", { credentials: "same-origin" });
    if (!response.ok) throw new Error(`Schema HTTP ${response.status}`);
    const schema = await response.json();
    for (const [path, operations] of Object.entries(schema.paths)) {
      for (const [method, operation] of Object.entries(operations)) {
        const article = document.createElement("article");
        article.className = "operation";
        const heading = document.createElement("h3");
        heading.textContent = `${method.toUpperCase()} ${path}`;
        const summary = document.createElement("p");
        summary.textContent = operation.summary || operation.operationId || "Operation";
        article.append(heading, summary, detail("Request and response contract", operation));
        document.querySelector("#operations").append(article);
      }
    }
    for (const [name, value] of Object.entries(schema.components?.schemas || {}))
      document.querySelector("#schemas").append(detail(name, value));
  } catch (error) {
    result.textContent = error.message;
  }
})();
document.querySelector("#run").addEventListener("click", async () => {
  const selection = {
    health: ["GET", "/healthz"],
    list: ["GET", "/api/notes"],
    create: ["POST", "/api/notes"],
  }[document.querySelector("#operation").value];
  if (!selection) return;
  try {
    const [method, path] = selection;
    const headers = {};
    let body;
    if (method === "POST") {
      const text = document.querySelector("#body").value;
      if (text.length > 1000) throw new Error("Keep this example body below 1000 characters.");
      body = JSON.stringify(JSON.parse(text));
      headers["Content-Type"] = "application/json";
      const session = await fetch("/api/me", { credentials: "same-origin" });
      if (!session.ok) throw new Error("Sign in on the workshop page before creating a note.");
      headers["X-CSRF-Token"] = (await session.json()).csrf;
    }
    const response = await fetch(path, { method, headers, credentials: "same-origin", body });
    result.textContent = `HTTP ${response.status}\n${JSON.stringify(await response.json(), null, 2)}`;
  } catch (error) {
    result.textContent = error.message;
  }
});
