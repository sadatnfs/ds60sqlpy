# docker-037: TLS, reverse proxies and publishing responsibly

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-036`

## Learning objectives

Draw proxy and upstream trust boundaries. State what would be required before public exposure. Use TLS, reverse proxy and certificate accurately when you explain what you observed.

## Purpose, vocabulary and mental model

TLS authenticates a server identity and encrypts traffic in transit under its certificate trust model. A reverse proxy receives client requests and forwards them to an upstream application. It can terminate TLS, route hostnames and paths, apply limits and emit access logs. It does not automatically make the upstream application authorized or safe for public use.

The study app is intentionally host-loopback only and uses HTTP for local teaching. Publishing it to the internet would create new requirements: identity, access control, TLS certificates, input limits, abuse handling, patching and operational ownership. This chapter designs that boundary without exposing your machine.

Proxy headers such as a forwarded client address are claims from the proxy chain. An application should trust them only from known proxies under an explicit configuration. Accepting arbitrary client-supplied forwarding headers can break rate limits or audit attribution.

### Key terms

- **TLS:** A protocol that authenticates the server identity and encrypts traffic in transit under a certificate trust model.
- **Certificate:** A signed document binding a server name to a public key, which clients verify through trusted issuers.
- **Reverse proxy:** A server that receives client requests and forwards them to an upstream application, often terminating TLS.
- **Public exposure:** Making a service reachable from the internet, which adds identity, access control, patching and abuse handling duties.
- **Forwarded header:** A proxy-added claim about the original client, which an application should trust only from known proxies.

## Anatomy and a trace you can follow

Draw the full request path before configuring a proxy: client name resolution, public endpoint, TLS handshake, proxy routing, upstream connection and application response. Each hop has its own timeout and identity. A certificate for one hostname does not validate a different name merely because both resolve to the same IP.

Use a synthetic configuration review and diagrams here. The course does not register a domain, request certificates or open firewall ports. A production configuration must use the chosen proxy’s actual documentation and a separate deployment review.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-037.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Distinguish TLS and application authorization.

**Hint:** Ask what TLS proves about the server and what it says about the user.

### Exercise 2: Predict the effect of a certificate name mismatch.

**Hint:** Compare the requested host name with the names in the certificate.

### Exercise 3: Draw proxy and upstream trust boundaries.

**Hint:** Mark where TLS ends and which identity each hop trusts.

### Exercise 4: Diagnose a proxy 502 separately from an app 404.

**Hint:** Check whether the response came from the proxy or from the app.

### Exercise 5: Explain forwarded-header spoofing.

**Hint:** Ask who can set an X-Forwarded-For header.

### Exercise 6: State what would be required before public exposure.

**Expected evidence:** A separate deployment design covering access, TLS, limits, operations and data.

**Hint:** List the access, TLS, limits, operations and data requirements for public use.

## Common mistakes and diagnosis

Treating HTTPS as authorization. Trusting forwarded headers from any client. Publishing the learning server to the internet.

Exercise 4 is this chapter's boundary case: Diagnose a proxy 502 separately from an app 404. Read the proxy log for the upstream it contacted and request the app route directly from an owned vantage point before changing either side. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Match a certificate mismatch, a proxy 502 and an app 401 to the layer that failed. Then reconstruct worked example 2 (Compare identity and routing failures) with one different value, predict what changes, and name which of TLS, reverse proxy, certificate and public exposure the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Port publishing and mapping](https://docs.docker.com/engine/network/port-publishing/)
- [nginx proxy module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)

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
