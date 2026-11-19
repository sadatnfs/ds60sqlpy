# web-050: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-050.md`.

## Exercise 1: Explain hashing versus reversible encryption for passwords.

**Expected answer:** A password verifier needs a one-way verification representation, not recovery of the original secret.

**Why:** Verification only needs to recompute and compare, so a one-way slow hash avoids storing anything that can be decrypted.

## Exercise 2: Verify both a correct and incorrect synthetic phrase.

**Expected evidence:** The library accepts only the correct candidate.

**Why:** password_verify recomputes the hash using the algorithm, salt and parameters stored in the encoded string.

## Exercise 3: Build a password-verification demonstration without printing the hash or secret.

**Expected evidence:** The output reports the test result while keeping credential-shaped values out of logs.

**Why:** Hashes and passwords in logs give attackers offline guessing material.

## Exercise 4: Diagnose using a general fast hash such as SHA-256 for password storage.

**Expected answer:** Fast general hashes do not provide a suitable password-guessing cost by themselves.

**Why:** General-purpose hashes are designed to be fast, so attackers can test billions of guesses; password hashes add memory and time cost per guess.

## Exercise 5: Explain an algorithm-specific input-length boundary and a hash that needs an upgrade.

**Expected answer:** bcrypt uses only the first 72 bytes, so the input policy must reject or document longer passphrases; password_needs_rehash returns true for a cost-10 bcrypt hash checked against the Argon2id options.

**Why:** bcrypt ignores bytes after the 72nd, and password_needs_rehash detects any algorithm or parameter change, so old hashes can be upgraded at the next login.

## Exercise 6: List the additional controls required around a real login.

**Expected answer:** TLS, rate limits, session rotation, recovery, safe errors and authorization remain separate requirements.

**Why:** Credential stuffing, interception, session theft and account-recovery abuse need rate limits, TLS, session rotation and careful recovery design.

## Reference comparison

Open `courses/web-development/solutions/web-050_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
