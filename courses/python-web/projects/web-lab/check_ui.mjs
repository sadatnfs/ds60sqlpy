// Browser event lifetime regression, without a server or a fake framework execution claim.
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const elements = new Map();
const element = (name) => {
  if (!elements.has(name)) {
    elements.set(name, {
      listeners: {},
      children: [],
      textContent: "",
      resetCount: 0,
      addEventListener(event, callback) {
        this.listeners[event] = callback;
      },
      append(child) {
        this.children.push(child);
      },
      replaceChildren() {
        this.children = [];
      },
      reset() {
        this.resetCount += 1;
      },
    });
  }
  return elements.get(name);
};
const requests = [];
const context = vm.createContext({
  document: { querySelector: element, createElement: () => ({ textContent: "" }) },
  window: { addEventListener() {} },
  FormData: class {
    constructor(form) {
      assert.equal(form, element("#note-form"));
    }
    get(name) {
      assert.equal(name, "title");
      return "Event lifetime";
    }
  },
  fetch: async (path, options) => {
    if (path === "/config") return new Promise(() => {});
    requests.push([path, options.method]);
    const value =
      options.method === "POST"
        ? { id: 1, title: "Event lifetime" }
        : { notes: [{ id: 1, title: "Event lifetime", version: 1 }] };
    return {
      ok: true,
      status: options.method === "POST" ? 201 : 200,
      text: async () => JSON.stringify(value),
    };
  },
});
vm.runInContext(fs.readFileSync(new URL("./static/app.js", import.meta.url), "utf8"), context);
const form = element("#note-form");
const event = { currentTarget: form, preventDefault() {} };
const pending = form.listeners.submit(event);
// Real Event.currentTarget is cleared after the dispatch callback yields.
event.currentTarget = null;
await pending;
assert.equal(form.resetCount, 1);
assert.deepEqual(requests, [
  ["/api/notes", "POST"],
  ["/api/notes", "GET"],
]);
assert.equal(element("#notes").children.length, 1);
assert.match(element("#notes").children[0].textContent, /Event lifetime/);
console.log(
  "Web note form retains its dispatch target across awaits and refreshes committed data.",
);
