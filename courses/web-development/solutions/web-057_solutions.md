# web-057: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-057.md`.

## Exercise 1: Draw the lifecycle from browser cookie to server session to stored note.

**Expected answer:** The cookie identifies session state; the session supplies an owner key and CSRF token; the database stores the owned note.

**Why:** The cookie selects the server session, the session provides the owner key and CSRF token, and the database stores the note under that owner.

## Exercise 2: Inspect the real Content-Type and redirect status.

**Expected evidence:** Record actual response headers instead of inferring them from PHP source.

**Why:** Observed headers show what the server really sent, which can differ from what the source suggests.

## Exercise 3: Run the owned lab and create one synthetic note through the browser.

**Expected evidence:** The note survives a page reload and appears after a successful POST-redirect-GET sequence.

**Why:** POST/redirect/GET makes the reload repeat a safe GET, so the note appears once and is not submitted twice.

## Exercise 4: Submit a request with a missing or wrong CSRF token.

**Expected evidence:** The server returns a rejection and inserts no note.

**Why:** The server compares the submitted token with the session token and rejects mismatches before writing.

## Exercise 5: Stop and resume the lab without deleting volumes.

**Expected evidence:** The same browser session can recover its notes while the named data and session volumes remain.

**Why:** Named volumes keep the database and session files, so the same browser session can see its notes after resume.

## Exercise 6: Explain which properties this local server has not qualified.

**Expected answer:** It does not establish production TLS, verified accounts, multi-instance concurrency, internet hardening or high availability.

**Why:** Production needs TLS, verified accounts, horizontal scaling, hardening and monitored availability, none of which a loopback lab provides.

## Comparing your worksheet

This lesson has no executable reference. Compare your worksheet with the answers above. The optional lab in `courses/web-development/fixtures/php-http-lab/` gives real request evidence only when you deliberately run it.
