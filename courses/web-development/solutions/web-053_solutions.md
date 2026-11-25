# web-053: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-053.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Explain why knowing a record id is not sufficient permission.

**Expected answer:** Ids identify objects; a policy must authorize access for the current actor.

**Approach:** Separate identification from permission: an id locates a record, while a policy decides whether this actor may see it.

**Why:** Ids are guessable or discoverable, so each access needs a policy check against the current actor.

**Plausible wrong approach:** Making ids long and random and calling that access control fails because ids leak through links, logs and shared screens.

**How to verify:** Your explanation shows a valid id requested by the wrong actor and the check that rejects it.

## Exercise 2: Add owner scoping to a prepared read query.

**Expected evidence:** The query can return only the requested actor's matching record.

**Approach:** Add `AND owner_id = :actor_id` to the WHERE clause and bind the trusted actor value alongside the id.

**Why:** Scoping the query by owner means another actor's record can never be returned, even by mistake.

**Plausible wrong approach:** Fetching by id and comparing owner in PHP later fails when a code path forgets the comparison and returns the row.

**How to verify:** Running the query for another actor's note returns false from `fetch()`. The same query with the owner's id returns the title, which shows the scope is not blocking everyone.

## Exercise 3: Build an object-access function with separate trusted actor and requested id inputs.

**Expected evidence:** The owner can read the record and a different actor receives no record.

**Approach:** Write `loadOwnedNote(PDO $db, int $actorId, int $noteId)` that returns the title or null, with actor first and named separately.

**Why:** Keeping trusted and untrusted inputs separate makes it obvious which value decides permission.

**Plausible wrong approach:** Taking one array of request fields that includes owner_id fails because the caller can set any owner it likes.

**How to verify:** The owner gets the title, a different actor gets null, and the function never reads request data. Swapping the two arguments by mistake becomes visible in review because the parameter names differ.

## Exercise 4: Diagnose trusting owner_id from a submitted form.

**Expected answer:** A caller can forge it; derive ownership from the verified server-side identity.

**Approach:** Remove owner_id from form handling and set it from the verified session identity in the adapter.

**Why:** The browser can send any value, so ownership must come from the verified session identity.

**Plausible wrong approach:** Validating that the submitted owner_id is an integer fails because a forged integer is still well formed.

**How to verify:** A request carrying another user's owner_id still stores the note under the session's actor.

## Exercise 5: Test own, other and missing records.

**Expected evidence:** Each follows a deliberate policy without leaking another actor's title.

**Approach:** Request an owned id, another actor's id and a missing id, and compare the three responses.

**Why:** Returning the same no-record result for other and missing ids avoids revealing which ids exist.

**Plausible wrong approach:** Returning Forbidden for other actors and Not found for missing ids fails because the difference reveals which ids exist.

**How to verify:** The other actor case and the missing case return the same result, and neither includes a title. Logs for the denied request record the actor and id but not the title.

## Exercise 6: Explain why hiding an edit button is only a user-interface convenience.

**Expected answer:** The server endpoint must enforce the same permission even when called directly.

**Approach:** Note that anyone can send a request directly with curl or browser tools, bypassing the page that hides the button.

**Why:** Hiding a control changes only the page; the endpoint must check permission on every request.

**Plausible wrong approach:** Hiding the delete button for non owners and calling it protected fails because the endpoint still deletes when called directly.

**How to verify:** Your answer describes a direct request test that the server rejects for a non owner. The same direct request succeeds for the owner, so the rule targets permission rather than the endpoint.

## Reference comparison

The reference requires owner 7 to read note 1, owner 8 to get null for it and a missing id to return null. That catches id-only lookups and leaks. It does not cover update or delete paths, so check that they apply the same owner scoping as reads.

Open `courses/web-development/solutions/web-053_solution.php` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
