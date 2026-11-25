# Kubernetes study guide: shared workflow for every lesson

Each lesson guide teaches one mechanism. This page holds the workflow, run boundary and evidence rules that are the same for all 66 lessons, so the guides can spend their words on the lesson itself. Read it once before k8s-001 and return to the section a guide links when you need it.

## How a lesson works

1. Read the guide's mental model and both worked examples before opening the learner file.
2. Write a prediction for each exercise in the learner artifact before you look at any evidence. A worksheet line that says "My prediction:" exists so the guess is recorded before the answer is known.
3. Open one progressive hint at a time. A hint names where to look; it never states the expected value.
4. Gather the evidence the exercise asks for, then compare it with the **Expected** line.
5. Only then open the matching file under `solutions/`. If your reasoning differed, write down which assumption failed.
6. Finish with the guide's retrieval prompt from memory and carry the next step forward.

A successful process exit or a manual "read" marker is not proof of understanding. The checked-in learner file is a starter; your real edits live in the app-owned workspace.

## Running lessons: worksheets, checks and the browser Run

Lessons come in two kinds.

- **Reading lessons** save a Markdown worksheet. Saving stores your text; it does not contact a cluster, grade an explanation or create a runtime receipt.
- **Browser Run lessons** use the allowlisted `k8s-kind` source. The worker binds one owned namespace, creates the fixed resources, waits within a deadline, records bounded checks and cleans the recorded UIDs. A one-shot Run is not a persistent session, so stateful steps such as a rollout, a Pod replacement or a live ConfigMap edit are separate host-lab work.

Each lesson also ships an offline reference check under `solutions/k8s-NNN_checks.py`. Run it from the repository root with `python courses/kubernetes/solutions/k8s-NNN_checks.py`. It evaluates synthetic facts and makes no API calls, so a pass proves the reasoning about the supplied case, not cluster behavior. The case ledgers under `fixtures/` are immutable teaching input.

The precise browser operation, its image and its deadlines are described in [the host-lab guide](host-labs.md#the-current-bounded-browser-operation).

## Owned live reads

Live reads are optional and only valid after a teacher or operator has prepared an owned, disposable target and the lesson's named capability actually exists there. The receipt names three values that every command must pass explicitly:

```sh
: "${LAB_KUBECONFIG:?Use the private path from the owned receipt}"
: "${LAB_CONTEXT:?Use the exact context from the owned receipt}"
: "${LAB_NAMESPACE:?Use the namespace from the owned receipt}"
kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" --namespace "$LAB_NAMESPACE" get pods -o wide
```

Rules that apply to every guide's read block:

- Never rely on an ambient current-context, a default kubeconfig or a workplace, shared or production cluster.
- Windows readers run the same Bash commands inside WSL 2. The lab adapter refuses native Windows credential handling, so do not run kubectl against the receipt from PowerShell. From PowerShell only open the distribution (`wsl.exe --distribution Ubuntu`), change to the checkout's Linux path and run the Bash block unchanged.
- A completed one-shot browser Run has already cleaned its objects, so NotFound can be the correct answer.
- Forbidden can mean the capability was deliberately not granted. Neither result authorizes switching credentials, installing a controller or falling back to another context.
- Keep only the fields the exercise needs. Record UIDs, resource versions and timestamps so a later reader can tell which object you saw.

[host-labs.md](host-labs.md) explains receipts, lease expiry, apply and cleanup in full.

## Networking extension boundary

Lessons k8s-043 through k8s-066 share one synthetic topology and manifest set in [the networking fixtures](fixtures/networking/README.md). Its addresses are examples, not allocations, and you should never contact them. The fixture checker makes no API calls, network requests, installations or Docker operations:

```sh
python courses/kubernetes/fixtures/networking/check_fixtures.py
```

A pass proves the files agree with each other: CIDRs separate, selectors match, the named target port resolves, the AND policy peer cases hold. It does not prove that a CNI enforces policy, that a controller serves a route or that a client can reach anything. Ingress, Gateway API, enforcing NetworkPolicy, dual-stack and multi-zone topology each need a separately prepared capability; a missing one is reported as unavailable, never installed from a lesson.

## Diagnosis rules

These rules hold in every diagnosis section:

- Observe from the caller's namespace and node first, then move one hop toward the backend. Name the hop where evidence stops.
- Use bounded reads (`get`, `describe`, a field selector, a short timeout). Preserve UIDs, timestamps and `metadata.generation` against `status.observedGeneration` before you change anything.
- Do not repair a failed example by disabling NetworkPolicy, running a privileged Pod, publishing every port or switching clusters. Those changes destroy the evidence and widen access.
- Accepted is not working. A DNS answer is not a listener, Ready is not reachability, an assigned load balancer address is not TLS or routing, and a controller can create desired state while traffic still fails.
- An unavailable capability is a valid, recordable boundary.

## Retrieval loop

Close the guide and the solutions, then reconstruct the lesson's argument from memory. Sort each claim by the evidence level that supports it:

| Level | What it shows |
| --- | --- |
| Source | The manifest or worksheet states an intent |
| API acceptance | The server admitted the object and assigned an identity |
| Controller status | A controller observed the generation and reported conditions |
| Traffic | A named caller reached a named endpoint |
| Application output | The app returned the exact expected bytes |
| Cleanup | The recorded UIDs were removed by the owning operation |

A claim supported only by a higher row than you actually observed is the usual mistake. Each guide's retrieval prompt asks you to apply the lesson to a changed case; answer it in your learner file.

## Solutions and the AI tutor

Solutions under `solutions/` are separate from the learner artifact. Open them after an attempt, or ask for a comparison explicitly. Each guide ends with a tutor prompt that names `$guide-ds60sqlpy-learning`, the guide path and the source path. The tutor follows the same order: explain, ask for a prediction, let you attempt, give one hint, inspect evidence, then ask for retrieval. It must use only an explicit owned lease and never select an ambient cluster for you. The [course README](README.md) lists the lesson sequence.
