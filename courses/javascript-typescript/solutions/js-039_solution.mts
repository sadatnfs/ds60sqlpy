import { strict as assert } from "node:assert";

type Base = { readonly id: string; readonly attempt: number };
type State = Base &
  (
    | { readonly kind: "queued" }
    | { readonly kind: "running" }
    | { readonly kind: "succeeded"; readonly value: number }
    | { readonly kind: "failed"; readonly reason: string }
    | { readonly kind: "cancelled"; readonly reason: string }
  );
type Event =
  | { type: "start" }
  | { type: "complete"; value: number }
  | { type: "fail"; reason: string }
  | { type: "retry" }
  | { type: "cancel"; reason: string };
function initial(): State {
  return { id: "A", attempt: 0, kind: "queued" };
}
function assertNever(value: never): never {
  throw new Error("unknown event: " + JSON.stringify(value));
}
function transition(state: State, event: Event): State {
  if (state.kind === "succeeded" || state.kind === "cancelled") throw new Error("terminal state");
  switch (event.type) {
    case "start":
      if (state.kind !== "queued") throw new Error("invalid transition to running");
      return { id: state.id, attempt: state.attempt + 1, kind: "running" };
    case "complete":
      if (state.kind !== "running") throw new Error("invalid transition to succeeded");
      if (!Number.isFinite(event.value)) throw new RangeError("finite result required");
      return { ...state, kind: "succeeded", value: event.value };
    case "fail":
      if (state.kind !== "running") throw new Error("invalid transition to failed");
      return { ...state, kind: "failed", reason: event.reason };
    case "retry":
      if (state.kind !== "failed") throw new Error("invalid transition to queued");
      if (state.attempt >= 3) throw new Error("retry budget exhausted");
      return { id: state.id, attempt: state.attempt, kind: "queued" };
    case "cancel":
      return { id: state.id, attempt: state.attempt, kind: "cancelled", reason: event.reason };
    default:
      return assertNever(event);
  }
}
function replay(state: State, events: readonly Event[]): State {
  return events.reduce(transition, state);
}

export async function verify(): Promise<{ checks: number; status: string }> {
  // Exercise 1: Complete one valid job lifecycle
  {
    const started = transition(initial(), { type: "start" });
    const completed = transition(started, { type: "complete", value: 7 });
    assert.deepEqual(completed, { id: "A", attempt: 1, kind: "succeeded", value: 7 });
  }

  // Exercise 2: Reject a result arriving before start
  {
    const queued = initial();
    assert.throws(() => transition(queued, { type: "complete", value: 7 }), /invalid transition/u);
    assert.deepEqual(queued, { id: "A", attempt: 0, kind: "queued" });
  }

  // Exercise 3: Enforce the retry budget
  {
    let state: State = initial();
    for (let attempt = 1; attempt <= 3; attempt += 1) {
      state = transition(state, { type: "start" });
      state = transition(state, { type: "fail", reason: "temporary" });
      if (attempt < 3) state = transition(state, { type: "retry" });
    }
    assert.equal(state.attempt, 3);
    assert.throws(() => transition(state, { type: "retry" }), /retry budget/u);
  }

  // Exercise 4: Keep cancellation terminal
  {
    const cancelled = transition(transition(initial(), { type: "start" }), {
      type: "cancel",
      reason: "user request",
    });
    assert.equal(cancelled.kind, "cancelled");
    assert.throws(() => transition(cancelled, { type: "complete", value: 2 }), /terminal/u);
  }

  // Exercise 5: Replay deterministically from the same history
  {
    const events: Event[] = [
      { type: "start" },
      { type: "fail", reason: "retryable" },
      { type: "retry" },
      { type: "start" },
      { type: "complete", value: 3 },
    ];
    const first = replay(initial(), events);
    const second = replay(initial(), events);
    assert.deepEqual(first, second);
    assert.deepEqual(first, { id: "A", attempt: 2, kind: "succeeded", value: 3 });
  }

  // Exercise 6: Preserve input state and validate success values
  {
    const queued = initial();
    const before = structuredClone(queued);
    const running = transition(queued, { type: "start" });
    assert.deepEqual(queued, before);
    assert.notEqual(running, queued);
    assert.throws(() => transition(running, { type: "complete", value: NaN }), RangeError);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
