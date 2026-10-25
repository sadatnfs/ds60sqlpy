# web-057: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

The earlier PHP pads isolated language and application logic. A real HTTP lab adds a browser, request headers, cookies, server process and persistent storage. Each boundary introduces behavior that a pure function cannot prove. The maintained optional fixture runs a local PHP development server in its own Linux container and binds its published port to host loopback. It is a learning server, not an internet deployment.

The fixture stores synthetic notes under an anonymous browser session. That demonstrates session continuity and separation, not verified user identity. A session cookie carries an identifier; the server stores the session and a random owner key. Prepared statements store notes in SQLite. A form includes a CSRF token, the server validates it before writing, and successful POST handling redirects to a GET page. Source, database and session state have distinct lifetimes.

Read the fixture README and copy the lab into an ignored learner directory before editing. Its Compose project name is ds60-web-study and its loopback port is 18088. Inspect whether those names belong to existing work before starting. The fixture builds only when you deliberately run the documented command. It does not mount the Docker socket, contact the classroom database or expose a public port. Named volumes retain notes and sessions across container replacement; removing those volumes is a separate reset.

## Exercise 1: Draw the lifecycle from browser cookie to server session to stored note.

The cookie identifies session state; the session supplies an owner key and CSRF token; the database stores the owned note.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Inspect the real Content-Type and redirect status.

Record actual response headers instead of inferring them from PHP source.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Run the owned lab and create one synthetic note through the browser.

The note survives a page reload and appears after a successful POST-redirect-GET sequence.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Submit a request with a missing or wrong CSRF token.

The server returns a rejection and inserts no note.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Stop and resume the lab without deleting volumes.

The same browser session can recover its notes while the named data and session volumes remain.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain which properties this local server has not qualified.

It does not establish production TLS, verified accounts, multi-instance concurrency, internet hardening or high availability.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
