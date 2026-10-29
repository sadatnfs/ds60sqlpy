## Starting point and result

Django's deployment checks inspect settings for known risky combinations. They are useful diagnostics, but a clean configuration report does not prove that TLS, proxies, static files or database recovery actually work. This chapter runs the real check framework against an intentionally incomplete configuration and a more deliberate one.

## Mechanism: static checks evaluate declared configuration

Run_checks with include_deployment_checks enables checks aimed at deployment settings. Debug mode, host configuration, secure cookie settings, redirect behavior and middleware choices can produce identified warnings. The identifiers are useful for stable assertions and for finding the framework's explanation.

The first configuration deliberately enables DEBUG and leaves ALLOWED_HOSTS empty. The program expects the corresponding warning IDs. The second context changes a reviewed set of settings and confirms that several specific warnings disappear.

These settings are not a universal deployment recipe. Enabling a secure redirect behind a proxy that reports the wrong scheme can cause loops. HSTS has consequences for future browser access and subdomains. A local HTTP workshop may deliberately use different settings from a public HTTPS service and should explain that boundary rather than copying production-looking flags blindly.

## Worked case: detect known unsafe declarations

The initial check run returns a set of issue IDs. The assertions require the debug-mode and empty-host warnings to be present. The program prints the full set so learners can see other findings from the pinned framework version.

A warning list should be investigated, not simply silenced until a command exits cleanly. Some findings may be deliberate in a local fixture; others indicate a missing protection. Record the reason for an exception and test the actual behavior it affects.

The fixture uses a synthetic secret string. Real deployments need secret generation, storage and rotation outside committed source. A string that satisfies a checker's length or character heuristic is not automatically a securely generated secret.

## Worked case: revise settings and inspect the changed findings

An override_settings context disables DEBUG, supplies an allowed host, enables secure cookies and redirect/HSTS declarations, adds clickjacking middleware and changes the fixture secret. The targeted warning IDs are absent in the second result.

This proves that the real framework checks recognized those declarations. It does not establish a TLS handshake, trusted proxy isolation or correct certificate management. Those require actual network tests and infrastructure configuration. The chapter intentionally reports the result as configuration diagnostics.

A production rollout should also check migration state, static-asset delivery, health/readiness semantics and persistent data. A web process can start successfully while its database schema is incompatible. A health endpoint can return 200 while the application cannot complete its principal workflow.

## Failure diagnosis and discussion

**Why can SECURE_SSL_REDIRECT cause a loop?** The application may see the proxy-to-app HTTP hop without a correctly trusted indication of the original HTTPS request. Trust only headers from the actual controlled proxy path.

**Should every local classroom server enable HSTS?** No. The local serving contract differs from a public HTTPS deployment. HSTS should be applied deliberately to the intended host and subdomain policy.

If checks change after a framework upgrade, read the new check semantics and assess the actual deployment. Do not merely replace expected IDs. Continue with the Django walkthrough to combine validated forms, authenticated ownership, CSRF and real database effects before moving into cross-framework operational design.
