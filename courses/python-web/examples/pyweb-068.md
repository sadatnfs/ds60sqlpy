Read the [owned web-lab instructions](../projects/web-lab/README.md) from the course
source tree, then run its explicit lifecycle in a prepared Linux Docker engine:

```sh
cd courses/python-web/projects/web-lab
./workshop prepare
./workshop start
./workshop check
```

The actual test opens an SSE connection and receives a queued/running event while
the job is still unreleased. Only after receiving bytes does it release the job.
It disconnects, reconnects with Last-Event-ID and verifies the committed result10.
It also performs a real one-message WebSocket exchange. Inspect the source-bound
receipt under this owned project's `.workshop/acceptance.json`.

A prepared image or this command reference is not an execution receipt. Network
acceptance is separate from browser rendering and from public TLS/proxy behavior.
