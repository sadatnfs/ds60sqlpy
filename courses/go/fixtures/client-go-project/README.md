# Prepared client-go project: bounded Pod reader

This is a real multi-file Go project for lessons go-041 and go-047. It uses
client-go v0.35.0 and the matching Kubernetes library release line. The dependency
requires Go 1.25 or newer. The ordinary one-file classroom pad does not install
or execute this project.

## What is demonstrated

- A typed CoreV1 client lists Pods with context cancellation.
- Pagination is handled explicitly, with at most three pages and sixty objects.
- Every request has a transport timeout and the operation has an overall deadline.
- The command requires an explicit kubeconfig path, context, namespace and expected
  HTTPS API endpoint.
- Ambient context discovery, insecure TLS, userinfo in endpoint strings,
  authentication plugins, configured proxies and impersonation are rejected. Host
  HTTP proxy environment variables are not inherited.
- Local HTTP tests exercise real typed-client serialization and pagination.
  They do not claim that a live Kubernetes API server or cluster was tested.

The command is read-only. It does not create, modify or delete cluster objects.
A Pod list still reveals resource metadata, so use only an explicitly owned
disposable teaching namespace and the intended minimal identity.

## Prepare dependencies and run offline tests

From this project directory in a prepared Linux or WSL 2 Go environment:

```sh
go mod download
go mod verify
CGO_ENABLED=0 GOPROXY=off GOSUMDB=off go test ./...
CGO_ENABLED=0 GOPROXY=off GOSUMDB=off go build -o owned-pod-reader .
```

The first command is deliberate network preparation. The checked-in go.mod and
go.sum pin the reviewed module graph. The following commands use the prepared
cache and fail instead of fetching a missing dependency. Do not change the
Kubernetes modules independently to unrelated minor versions.

The tests start only temporary loopback HTTP servers. They verify two-page
continuation, rejection of an endless continuation stream, cancellation before
a request and refusal of ambient configuration. These tests are safe to run
without kubeconfig or cluster credentials.

## Deliberate live read

Prepare an owned disposable cluster and a namespace-scoped identity with only
the required Pod list permission. Record the intended context, exact API server
URL and namespace. Inspect the selected configuration privately; do not paste
credentials into notes, source or command arguments.

Then supply your own actual values:

```sh
./owned-pod-reader \
  -execute \
  -kubeconfig "$LESSON_KUBECONFIG" \
  -context "$LESSON_CONTEXT" \
  -namespace "$LESSON_NAMESPACE" \
  -expected-server "$LESSON_API_SERVER"
```

These variables are placeholders that you must set to the deliberately prepared
target. Running the command without them fails before API client creation.
No token, password or client private key belongs in the command line. The
explicit configuration file supplies the selected disposable credentials.

Expected output is one Pod name per returned object followed by a total. An empty
namespace legitimately prints a zero total. Forbidden access, cancellation and
pagination-budget exhaustion produce an error and a nonzero exit. Do not replace
a forbidden response with cluster-admin credentials just to make the example pass.

## Reason about the remaining boundaries

The endpoint and context checks reduce accidental target selection, but they do
not establish resource ownership by themselves. The learner must prepare and
verify the disposable target through the repository owned-cluster workflow.
Static credentials need a private file and an appropriate lifetime. The example
does not implement a general kubeconfig security scanner or multi-tenant sandbox.

A list can change between requests; use the server continuation contract and
resource versions rather than assuming a client-side count is a permanent truth.
For a controller, move from this bounded reader to informer caches, keyed work
queues, idempotent reconciliation and exact UID-bound cleanup. The later lessons
explain why fake-client success alone cannot establish rollout or networking
behavior.

Sources: [client-go project and compatibility guidance](https://github.com/kubernetes/client-go),
[API pagination](https://kubernetes.io/docs/reference/using-api/api-concepts/#retrieving-large-results-sets-in-chunks),
and [client-go v0.35.0 module requirements](https://github.com/kubernetes/client-go/blob/v0.35.0/go.mod).
Reviewed 2026-10-23.
