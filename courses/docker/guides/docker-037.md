# docker-037: TLS, reverse proxies and publishing responsibly

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-036`

## Learning objectives

Draw proxy and upstream trust boundaries. State what would be required before public exposure. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

TLS authenticates a server identity and encrypts traffic in transit under its certificate trust model. A reverse proxy receives client requests and forwards them to an upstream application. It can terminate TLS, route hostnames and paths, apply limits and emit access logs. It does not automatically make the upstream application authorized or safe for public use.

The study app is intentionally host-loopback only and uses HTTP for local teaching. Publishing it to the internet would create new requirements: identity, access control, TLS certificates, input limits, abuse handling, patching and operational ownership. This chapter designs that boundary without exposing your machine.

Proxy headers such as a forwarded client address are claims from the proxy chain. An application should trust them only from known proxies under an explicit configuration. Accepting arbitrary client-supplied forwarding headers can break rate limits or audit attribution.

## Anatomy and a trace you can follow

Draw the full request path before configuring a proxy: client name resolution, public endpoint, TLS handshake, proxy routing, upstream connection and application response. Each hop has its own timeout and identity. A certificate for one hostname does not validate a different name merely because both resolve to the same IP.

Use a synthetic configuration review and diagrams here. The course does not register a domain, request certificates or open firewall ports. A production configuration must use the chosen proxy’s actual documentation and a separate deployment review.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Trace a protected request

This is a conceptual public architecture.

```text
browser -> DNS name -> TLS proxy -> private app endpoint
          certificate name        bounded upstream timeout
```

**Expected observation:** TLS protects the client-to-proxy hop; upstream protection and trust are separate design choices.

### Worked example 2: Compare identity and routing failures

These synthetic symptoms occur at different stages.

```text
certificate name mismatch: TLS identity problem
HTTP 502 from proxy: upstream handling problem
HTTP 401 from app: application authentication requirement
```

**Expected observation:** Changing a container port does not repair an invalid certificate identity.

## Six progressive exercises

### Exercise 1: Distinguish TLS and application authorization.

**Expected evidence:** Encrypted authenticated transport versus permission for an action.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict the effect of a certificate name mismatch.

**Expected evidence:** The client cannot validate the requested server name normally.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Draw proxy and upstream trust boundaries.

**Expected evidence:** Explicit client-facing and internal hops with identities and timeouts.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a proxy 502 separately from an app 404.

**Expected evidence:** Upstream failure versus a completed app route response.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain forwarded-header spoofing.

**Expected evidence:** Untrusted clients can send headers unless the proxy boundary sanitizes them.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: State what would be required before public exposure.

**Expected evidence:** A separate deployment design covering access, TLS, limits, operations and data.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a proxy 502 separately from an app 404. Use its expected observation, Upstream failure versus a completed app route response., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/network/port-publishing/)
- [Official reference 2](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-037: TLS, reverse proxies and publishing responsibly.
Read courses/docker/guides/docker-037.md and courses/docker/lessons/docker-037.md. Direct prerequisites: `docker-036`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
