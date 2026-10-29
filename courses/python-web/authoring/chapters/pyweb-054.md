## Starting point and result

Django permissions and groups help express capabilities, while object visibility still needs a concrete data-access rule. This chapter grants one user a model-level permission through a group, compares another user without that permission and independently scopes a private note to its owner.

## Mechanism: model permission and object permission differ

Django creates standard model permissions through its content-types and authentication applications. A group can hold permissions, and users can belong to groups. Calling has_perm checks the configured authentication backend's policy for the requested permission.

The default model-permission backend does not automatically implement arbitrary object-level authorization. Passing an object to has_perm is not a declaration of how ownership works. A project needing object permissions must implement or select an appropriate backend and test it, or explicitly scope its queries and domain operations.

The example uses a real migrated auth database for users, groups and permissions. Its private-note fixture is a small mapping so the owner predicate is visible. The model permission is intentionally not treated as permission to read every note in the application.

## Worked case: grant a capability through a group

Alice joins an Editors group holding the auth.change_user permission. A freshly loaded Alice object reports that capability; Bob does not. Reloading is deliberate because user permission caches can make a previously evaluated object stale after permissions change.

The permission's app label and codename identify the intended capability. A similarly named string or an unrelated model permission is not interchangeable. Real administrative actions should request the exact permission they require and should not grant broad privileges merely to simplify a test.

Group membership is useful for managing capabilities, but the group name itself is not a security mechanism. The backend evaluates assigned permissions and policy. Hard-coding a string comparison against a display label can bypass that machinery and make later changes fragile.

## Worked case: scope a resource to its owner

Two clients are logged in through force_login so this case focuses on authorization rather than password verification. Alice can retrieve her note. Bob receives 404 for the same identifier. The view checks authentication and then the row's owner against request.user.pk.

The program also demonstrates that the default backend does not suddenly authorize a specific object merely because Alice has a related model permission. Object-level semantics require their own policy. The explicit predicate provides the fixture's visibility rule.

In a real database-backed route, include the owner or tenant condition in the lookup itself where practical. That reduces accidental exposure through intermediate data and ensures that list, detail, update and delete paths use the same scope. Background jobs and administrative tools need an equivalent rule when acting on behalf of a user.

## Failure diagnosis and discussion

**Why use force_login here after testing passwords earlier?** It isolates the authorization question. The test assumes a known authenticated principal and asks whether that principal can access the resource. It does not claim another password-verification result.

**Why can a permission change appear ineffective on an existing user object?** The backend may cache permission results. Refresh or invalidate deliberately, and test the application behavior at the relevant request boundary.

If an authenticated user sees another user's row, inspect object scoping before adjusting group membership. If every permission is false, inspect the backend, app label and codename. Continue with CSRF, which protects authenticated browser actions from a different class of unwanted request initiation.
