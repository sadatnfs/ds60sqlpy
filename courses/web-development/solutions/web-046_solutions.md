# web-046: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

HTTP separates a request from its response. A request includes a method, target and headers, and may contain a body. A response includes a status code, headers and body. The method expresses intended semantics: GET should retrieve a representation without requesting a state change, while POST commonly submits data for processing. The server must still enforce its own rules regardless of a client-supplied method or path.

Routing selects application behavior from the request method and path. Keep routing separate from the domain calculation so logic can be tested without a live server. A 404 means the requested resource or route is not found; a 405 means the resource exists but the method is unsupported. The application should not return 200 for every failure merely because it produced a page.

The CLI reference receives a synthetic request array and returns a response array. This is a model of an HTTP boundary, not an actual network exchange. A real adapter would read the server-provided environment, validate it, set status and headers before body output, and send the body. Content-Type should describe the response representation, and error bodies should match the declared format.

## Exercise 1: Identify status, headers and body in the response model.

They are separate fields with different protocol responsibilities.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a not-found response for an unknown path.

The unknown route returns 404 instead of pretending to be a successful page.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a pure router for health and lesson-summary requests.

Known GET routes return their declared representations and unsupported requests are rejected.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose headers sent after body output in a real adapter.

Response metadata must be established before output begins, subject to the runtime's buffering behavior.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test a known path with the wrong method.

The route returns 405 and identifies allowed methods where appropriate.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain what a CLI response model does not prove.

It does not qualify actual networking, server configuration, cookie handling or browser behavior.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
