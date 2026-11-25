# web-050: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-050.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Explain hashing versus reversible encryption for passwords.

**Expected answer:** A password verifier needs a one-way verification representation, not recovery of the original secret.

**Approach:** Note that a login check only needs to confirm a candidate matches, so the stored form never needs to be turned back into the password.

**Why:** Verification only needs to recompute and compare, so a one-way slow hash avoids storing anything that can be decrypted.

**Plausible wrong approach:** Encrypting passwords with a reversible key fails because anyone who obtains the key can recover every stored password.

**How to verify:** Your explanation shows `password_verify` checking a candidate without any decryption step.

## Exercise 2: Verify both a correct and incorrect synthetic phrase.

**Expected evidence:** The library accepts only the correct candidate.

**Approach:** Call `password_verify` with the correct phrase and with a different one against the same stored hash.

**Why:** password_verify recomputes the hash using the algorithm, salt and parameters stored in the encoded string.

**Plausible wrong approach:** Comparing `password_hash($candidate)` with the stored string fails because each call uses a new salt and never matches.

**How to verify:** The correct phrase prints true and the different phrase prints false. Verifying against a second hash of the same phrase also prints true, despite the different salt.

## Exercise 3: Build a password-verification demonstration without printing the hash or secret.

**Expected evidence:** The output reports the test result while keeping credential-shaped values out of logs.

**Approach:** Hash a synthetic phrase, verify it, and print only labeled booleans such as verify correct: true.

**Why:** Hashes and passwords in logs give attackers offline guessing material.

**Plausible wrong approach:** Printing the hash for debugging fails because logs then hold material an attacker can try to crack offline.

**How to verify:** The program output contains no `$argon2id$` string and no passphrase text.

## Exercise 4: Diagnose using a general fast hash such as SHA-256 for password storage.

**Expected answer:** Fast general hashes do not provide a suitable password-guessing cost by themselves.

**Approach:** Replace `hash('sha256', ...)` with `password_hash` and plan to rehash each account at its next successful login.

**Why:** General-purpose hashes are designed to be fast, so attackers can test billions of guesses; password hashes add memory and time cost per guess.

**Plausible wrong approach:** Adding a single shared salt to SHA-256 fails because the hash stays fast, so guessing remains cheap.

**How to verify:** New records begin with `$argon2id$`, and old records are flagged by `password_needs_rehash`.

## Exercise 5: Explain an algorithm-specific input-length boundary and a hash that needs an upgrade.

**Expected answer:** bcrypt uses only the first 72 bytes, so the input policy must reject or document longer passphrases; password_needs_rehash returns true for a cost-10 bcrypt hash checked against the Argon2id options.

**Approach:** State the bcrypt limit of 72 bytes, define a policy for longer inputs, and call `password_needs_rehash` on a bcrypt hash.

**Why:** bcrypt ignores bytes after the 72nd, and password_needs_rehash detects any algorithm or parameter change, so old hashes can be upgraded at the next login.

**Plausible wrong approach:** Accepting a 100 byte passphrase under bcrypt without a note fails because bytes beyond 72 are silently ignored.

**How to verify:** A cost 10 bcrypt hash checked against the Argon2id options returns true from `password_needs_rehash`.

## Exercise 6: List the additional controls required around a real login.

**Expected answer:** TLS, rate limits, session rotation, recovery, safe errors and authorization remain separate requirements.

**Approach:** List controls outside hashing: TLS, rate limits, session rotation, recovery flow, generic errors and authorization after login.

**Why:** Credential stuffing, interception, session theft and account-recovery abuse need rate limits, TLS, session rotation and careful recovery design.

**Plausible wrong approach:** Raising Argon2 memory and calling the login secure fails because an unlimited guessing endpoint still lets attackers try many passwords.

**How to verify:** Your list names at least five controls, each with what it protects against. Rate limits appear first because they directly cap online guessing.

## Reference comparison

The reference requires an Argon2id hash prefix, accepts the correct phrase, rejects a different one and confirms current parameters need no rehash, then shows a legacy bcrypt hash verifying but needing an upgrade. It does not test login rate limits, so list them separately.

Open `courses/web-development/solutions/web-050_solution.php` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
