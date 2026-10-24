const output = document.querySelector("#output");
const input = document.querySelector("#text");
const count = document.querySelector("#count");
if (
  !(output instanceof HTMLElement) ||
  !(input instanceof HTMLTextAreaElement) ||
  !(count instanceof HTMLElement)
)
  throw new Error("renderer nodes missing");
document.querySelector("#render").addEventListener("click", () => {
  output.textContent = input.value;
  count.textContent = `Child elements: ${output.childElementCount}; image elements: ${output.querySelectorAll("img").length}`;
});
function localLink(text) {
  const url = new URL(text, location.href);
  if (
    !["http:", "https:"].includes(url.protocol) ||
    url.origin !== location.origin ||
    url.username ||
    url.password
  )
    throw new Error("Only same-origin HTTP links without credentials are accepted");
  return url;
}
document.querySelector("#check").addEventListener("click", () => {
  const target = document.querySelector("#link");
  target.replaceChildren();
  try {
    const url = localLink(document.querySelector("#url").value);
    const link = document.createElement("a");
    link.href = url.href;
    link.textContent = "Open accepted local page";
    target.append(link);
    document.querySelector("#url-status").textContent = `Accepted: ${url.pathname}`;
  } catch (error) {
    document.querySelector("#url-status").textContent = `Rejected: ${error.message}`;
  }
});
document.querySelector("#origin").textContent = `This page origin: ${location.origin}`;
