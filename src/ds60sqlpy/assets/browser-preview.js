"use strict";
// An opaque iframe executes local learner code. Its reports are client
// observations, never server-side verifier evidence or a hard CPU sandbox.
(() => {
  class BrowserPreview {
    constructor(container) {
      this.container = container;
      this.frame = null;
      this.port = null;
      this.sequence = 0;
      this.pending = null;
      this.timer = null;
      this.latest = null;
      this.startedAt = null;
    }
    get active() {
      return this.frame !== null;
    }
    snapshot() {
      return this.latest ? { ...this.latest } : null;
    }
    stop(reason = "Preview stopped.") {
      const stoppedAt = performance.now();
      this.sequence++;
      if (this.timer !== null) clearTimeout(this.timer);
      this.timer = null;
      this.port?.close();
      this.port = null;
      this.frame?.remove();
      this.frame = null;
      this.container.replaceChildren();
      if (this.pending) {
        const settle = this.pending;
        this.pending = null;
        this.latest = {
          ...this.latest,
          status: "cancelled",
          elapsed_seconds: Math.min(3600, Math.max(0, (stoppedAt - this.startedAt) / 1000)),
          output: (this.latest?.output || "") + "\n" + reason,
        };
        settle(this.snapshot());
      }
      this.startedAt = null;
    }
    start(source, onOutput = () => {}) {
      this.stop("Replaced by another preview.");
      const sequence = ++this.sequence;
      const began = performance.now();
      this.startedAt = began;
      this.latest = { source, output: "", status: "running", elapsed_seconds: 0 };
      const frame = document.createElement("iframe");
      this.frame = frame;
      frame.title = "Interactive D3 visualization preview";
      frame.setAttribute("sandbox", "allow-scripts");
      frame.setAttribute("referrerpolicy", "no-referrer");
      frame.src = "/browser-sandbox";
      const channel = new MessageChannel();
      this.port = channel.port1;
      const elapsed = () => Math.min(3600, Math.max(0, (performance.now() - began) / 1000));
      return new Promise((resolve, reject) => {
        this.pending = resolve;
        this.timer = setTimeout(() => {
          if (sequence !== this.sequence) return;
          this.stop(
            "Preview initialization or initial script completion exceeded its UI wait budget.",
          );
        }, 120000);
        channel.port1.onmessage = (event) => {
          if (sequence !== this.sequence || frame !== this.frame) return;
          const data = event.data;
          if (
            !data ||
            typeof data.output !== "string" ||
            new TextEncoder().encode(data.output).length > 32000 ||
            !["started", "output", "complete", "interaction-error"].includes(data.type)
          )
            return;
          this.latest = { ...this.latest, output: data.output, elapsed_seconds: elapsed() };
          if (data.type === "interaction-error") this.latest.status = "failed";
          onOutput(this.snapshot(), data.type);
          if (
            data.type === "complete" &&
            this.pending &&
            ["succeeded", "failed"].includes(data.status)
          ) {
            this.latest.status = data.status;
            if (this.timer !== null) clearTimeout(this.timer);
            this.timer = null;
            this.pending = null;
            resolve(this.snapshot());
          }
        };
        channel.port1.start();
        frame.addEventListener(
          "load",
          () => {
            if (sequence !== this.sequence || frame !== this.frame) return;
            try {
              frame.contentWindow.postMessage({ type: "ds60-browser-connect", source }, "*", [
                channel.port2,
              ]);
            } catch (error) {
              this.pending = null;
              this.stop("The preview could not initialize.");
              reject(error);
            }
          },
          { once: true },
        );
        this.container.replaceChildren(frame);
      });
    }
  }
  globalThis.DS60BrowserPreview = BrowserPreview;
})();
