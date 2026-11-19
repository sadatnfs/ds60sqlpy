# web-053: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-053.md`.

## Exercise 1: Explain why knowing a record id is not sufficient permission.

**Expected answer:** Ids identify objects; a policy must authorize access for the current actor.

**Why:** Ids are guessable or discoverable, so each access needs a policy check against the current actor.

## Exercise 2: Add owner scoping to a prepared read query.

**Expected evidence:** The query can return only the requested actor's matching record.

**Why:** Scoping the query by owner means another actor's record can never be returned, even by mistake.

## Exercise 3: Build an object-access function with separate trusted actor and requested id inputs.

**Expected evidence:** The owner can read the record and a different actor receives no record.

**Why:** Keeping trusted and untrusted inputs separate makes it obvious which value decides permission.

## Exercise 4: Diagnose trusting owner_id from a submitted form.

**Expected answer:** A caller can forge it; derive ownership from the verified server-side identity.

**Why:** The browser can send any value, so ownership must come from the verified session identity.

## Exercise 5: Test own, other and missing records.

**Expected evidence:** Each follows a deliberate policy without leaking another actor's title.

**Why:** Returning the same no-record result for other and missing ids avoids revealing which ids exist.

## Exercise 6: Explain why hiding an edit button is only a user-interface convenience.

**Expected answer:** The server endpoint must enforce the same permission even when called directly.

**Why:** Hiding a control changes only the page; the endpoint must check permission on every request.

## Reference comparison

Open `courses/web-development/solutions/web-053_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
