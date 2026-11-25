# docker-027: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-027.md).

## Exercise 1: Predict which resources are durable.

**Expected answer:** Only the intended named volume and explicit backup files.

**Why:** Containers, peer client instances and project networks are replaceable. Do not accidentally rely on writable-layer state when describing recovery.

**Approach:** List each resource and ask whether recreating it loses anything: study-data and the backup files hold state, while app, client and the network are rebuilt.

**Why this is correct:** server.py keeps its counter only in /data and the root is read-only, so the writable layer holds nothing worth recovering.

**A plausible wrong approach:** Describing a container restart as preserving data because the container kept its name confuses the container with the volume.

**How to verify:** Run down without -v and up again; the counter remains, while the container ID and network ID change.

## Exercise 2: Change only the peer target port in a scratch copy.

**Expected evidence:** The request fails within its timeout while app remains healthy.

**Why:** The controlled fault separates internal routing from application readiness. Preserve the error rather than changing multiple network settings at once.

**Approach:** In a scratch copy, change only the client's URL from `app:8080` to another port and run the client once.

**Why this is correct:** Nothing listens on the new port, so the request fails within its 3 second timeout while app stays healthy.

**A plausible wrong approach:** Also editing the app's ports and network to see what happens loses track of which change caused the failure.

**How to verify:** docker compose ps still shows app healthy, and the client error names the port it tried.

## Exercise 3: Build an independent restore demonstration.

**Expected evidence:** New target state equals the exported counter while source remains intact.

**Why:** Recovery evidence requires use of the restored data. A copied file existing at a path is not enough without parsing and an application-level check.

**Approach:** Export counter.json from study-data, restore it into a new volume, and start a reader on that volume.

**Why this is correct:** Reading GET /counter through server.py runs read_counter's checks, proving the restored data is usable.

**A plausible wrong approach:** Checking only that the restored file exists skips parsing and would pass a truncated or invalid file.

**How to verify:** The reader returns the same counter as the export, and the source volume's counter is unchanged.

## Exercise 4: Diagnose a passing host request with failing peer request.

**Expected answer:** Inspect service DNS, network attachment and internal target port.

**Why:** The two paths share an application but have different discovery and routing. Their disagreement localizes the fault.

**Approach:** Compare the two paths: the host uses `127.0.0.1:18080` through a port mapping, the client uses `app:8080` through project DNS.

**Why this is correct:** Since the host request works, the app is serving; the fault is in the client's name, network or port.

**A plausible wrong approach:** Restarting the app because something is down ignores the passing host request.

**How to verify:** Check that client joins the project network, resolves app, and targets 8080; one of these shows the mismatch.

## Exercise 5: Explain the limits of this single-engine design.

**Expected answer:** No multi-host failover or database consistency guarantee is claimed.

**Why:** A small lab teaches the mechanisms honestly. Production requirements need additional architecture and qualification rather than a larger marketing claim.

**Approach:** List what the lab does not cover: other hosts, failover, replicated storage, and consistency for real databases.

**Why this is correct:** One engine with one volume teaches the mechanics without claiming a production-grade guarantee.

**A plausible wrong approach:** Presenting the capstone as a highly available design invites someone to rely on it for production.

**How to verify:** The handoff names these limits next to the parts that were tested.

## Exercise 6: Write a beginner operator handoff.

**Expected evidence:** Setup, evidence, failure diagnosis, backup/restore and scoped cleanup.

**Why:** A good handoff is executable by a reader with the documented prerequisites. It names state retention explicitly and avoids ambient context assumptions.

**Approach:** Write the handoff in operating order: prerequisites, start, health evidence, common failures, backup and restore, and scoped cleanup.

**Why this is correct:** A reader with only the listed prerequisites can follow it, and it names which volumes keep state after cleanup.

**A plausible wrong approach:** Writing steps that rely on your shell history or already-built images fails for the next operator.

**How to verify:** Someone new follows the handoff on a clean engine and reaches the same health and restore results.

## Check your transfer

Not necessarily. The restore volume holds the snapshot taken at export time, while the source keeps accepting increments, so a later increment through `exec` or the browser explains a higher source value. Compare the restored value with the counter in `counter-backup.json`: if both say 4, export and restore are correct and the source simply moved on, which `docker compose logs app` confirms with a later `POST /increment` line. If the backup says 5 and the restore says 4, the restore step wrote something other than the export.
