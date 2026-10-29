Use the [owned web-lab instructions](../../projects/web-lab/README.md). After a passed
check has written its exact note/job identities:

```sh
./workshop stop
./workshop resume
./workshop verify
./workshop replace
./workshop verify
```

Resume requires the existing five containers and verifies their identities.
Replace recreates the application/worker containers from the saved local image.
Both retain the project's PostgreSQL data and private `.workshop/` settings.
Verify reads the prior receipt's records instead of creating replacement data.

Record service, image, platform, source hashes and actual readback separately.
Never delete the project volume or use a global prune to simulate successful
recovery. The local loopback HTTP contract does not establish a public TLS edge.
