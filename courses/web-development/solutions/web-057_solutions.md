# web-057: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-057.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Draw the lifecycle from browser cookie to server session to stored note.

**Expected answer:** The cookie identifies session state; the session supplies an owner key and CSRF token; the database stores the owned note.

**Approach:** Trace one note: the browser sends the session cookie, the server finds the session, reads its owner key and token, and stores the note under that owner.

**Why:** The cookie selects the server session, the session provides the owner key and CSRF token, and the database stores the note under that owner.

**Plausible wrong approach:** Drawing the note text inside the cookie fails because the lab keeps notes in its database and the cookie holds only an identifier.

**How to verify:** Your diagram has three boxes, cookie, session and database, with the note only in the database.

## Exercise 2: Inspect the real Content-Type and redirect status.

**Expected evidence:** Record actual response headers instead of inferring them from PHP source.

**Approach:** Run `curl --include` against the form page and against a valid POST, and copy the status line and Content-Type header.

**Why:** Observed headers show what the server really sent, which can differ from what the source suggests.

**Plausible wrong approach:** Writing down the header values from `header()` calls in the PHP source fails because proxies or errors can change what is actually sent.

**How to verify:** Your notes include the real status line and headers copied from the curl output.

## Exercise 3: Run the owned lab and create one synthetic note through the browser.

**Expected evidence:** The note survives a page reload and appears after a successful POST-redirect-GET sequence.

**Approach:** Start the lab with the documented command, open the page, submit one synthetic note, then reload and check it is still listed.

**Why:** POST/redirect/GET makes the reload repeat a safe GET, so the note appears once and is not submitted twice.

**Plausible wrong approach:** Starting a second copy on another port fails because it uses different volumes, so the notes you check are not the ones you created.

**How to verify:** The note appears after the 303 redirect, and still appears after a manual reload.

## Exercise 4: Submit a request with a missing or wrong CSRF token.

**Expected evidence:** The server returns a rejection and inserts no note.

**Approach:** Submit the form with the token field removed or changed in browser tools, then reload the list.

**Why:** The server compares the submitted token with the session token and rejects mismatches before writing.

**Plausible wrong approach:** Judging success by the absence of an error page fails because a broken check might accept the request silently.

**How to verify:** The server answers with a rejection status, and the note list has the same entries as before.

## Exercise 5: Stop and resume the lab without deleting volumes.

**Expected evidence:** The same browser session can recover its notes while the named data and session volumes remain.

**Approach:** Stop the containers with `docker compose stop` for the ds60-web-study project, start them again, and reload the page in the same browser.

**Why:** Named volumes keep the database and session files, so the same browser session can see its notes after resume.

**Plausible wrong approach:** Running `down --volumes` to restart fails because it deletes the named volumes that hold the notes and sessions.

**How to verify:** `docker volume ls` still lists the lab volumes, and the earlier note is still on the page.

## Exercise 6: Explain which properties this local server has not qualified.

**Expected answer:** It does not establish production TLS, verified accounts, multi-instance concurrency, internet hardening or high availability.

**Approach:** Compare the lab's setup with a production deployment and list what is absent, such as TLS, accounts and multiple instances.

**Why:** Production needs TLS, verified accounts, horizontal scaling, hardening and monitored availability, none of which a loopback lab provides.

**Plausible wrong approach:** Calling the lab production ready because notes persist fails because persistence on one machine says nothing about outages or attackers.

**How to verify:** Your list names at least four missing properties and the evidence each would need.

## Comparing your worksheet

Compare your lifecycle drawing with the solution's and check that each arrow names the request, the status and where state is stored. If you ran the optional lab, the health response, the 303 redirect and a rejected token are your evidence; record them with the exact command you ran.

This lesson has no executable reference ([worksheet rules](../STUDY-GUIDE.md#worksheets)).
