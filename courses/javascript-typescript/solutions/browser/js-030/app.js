const KEY = "ds60-js030-draft-v1";
const form = document.querySelector("#form");
const status = document.querySelector("#status");
const accepted = document.querySelector("#accepted");
if (
  !(form instanceof HTMLFormElement) ||
  !(status instanceof HTMLElement) ||
  !(accepted instanceof HTMLElement)
)
  throw new Error("required form nodes missing");
let state = null;
function validate(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value))
    throw new Error("Saved draft must be an object");
  if (Object.keys(value).sort().join(",") !== "name,quantity,version" || value.version !== 1)
    throw new Error("Unsupported saved draft version or fields");
  if (typeof value.name !== "string" || value.name.trim() === "" || value.name.length > 40)
    throw new Error("Name must contain 1 to 40 characters");
  if (!Number.isInteger(value.quantity) || value.quantity < 1 || value.quantity > 20)
    throw new Error("Quantity must be an integer from 1 to 20");
  return { version: 1, name: value.name.trim(), quantity: value.quantity };
}
function render(next) {
  state = next;
  accepted.textContent = JSON.stringify(state, null, 2);
}
function load() {
  try {
    const text = localStorage.getItem(KEY);
    if (text === null) {
      status.textContent = "No saved lesson draft";
      return;
    }
    const next = validate(JSON.parse(text));
    render(next);
    form.elements.namedItem("name").value = next.name;
    form.elements.namedItem("quantity").value = String(next.quantity);
    status.textContent = "Loaded validated saved draft";
  } catch (error) {
    status.textContent = `Cannot load saved draft: ${error.message}`;
  }
}
form.addEventListener("submit", (event) => {
  event.preventDefault();
  try {
    const fields = new FormData(form);
    const next = validate({
      version: 1,
      name: String(fields.get("name") ?? ""),
      quantity: Number(fields.get("quantity")),
    });
    render(next);
    try {
      localStorage.setItem(KEY, JSON.stringify(next));
      status.textContent = "Accepted and saved";
    } catch {
      status.textContent = "Accepted in memory; storage unavailable and not saved";
    }
  } catch (error) {
    status.textContent = `Rejected: ${error.message}`;
  }
});
document.querySelector("#reload").addEventListener("click", load);
document.querySelector("#corrupt").addEventListener("click", () => {
  try {
    localStorage.setItem(KEY, "{broken");
    status.textContent = "Stored malformed data in lesson key; try loading";
  } catch {
    status.textContent = "Storage unavailable; malformed fixture was not stored";
  }
});
document.querySelector("#reset").addEventListener("click", () => {
  try {
    localStorage.removeItem(KEY);
    status.textContent = "Removed only lesson draft";
  } catch {
    status.textContent = "Storage unavailable; removal not confirmed";
  }
});
window.addEventListener("storage", (event) => {
  if (event.key === KEY)
    document.querySelector("#external").textContent =
      "Saved draft changed in another tab; load when ready";
});
load();
