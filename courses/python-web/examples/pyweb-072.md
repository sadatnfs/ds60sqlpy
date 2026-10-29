Compare the [Flask/FastAPI/Django web-lab source](../projects/web-lab/README.md)
against the completed finite reference programs.

| Claim | Required evidence |
| --- | --- |
| Request/schema rule | Real finite framework client and rejected/accepted cases |
| Database invariant | Actual transaction/constraint result and side-effect inspection |
| HTTP/WS/SSE delivery | Owned server acceptance with actual socket observations |
| Offline UI/docs | Browser asset requests and visible interaction |
| Durable notes/jobs | Prior identity readback after stop/resume and replacement |
| Public TLS/multi-host scale | Separate deployment evidence, not supplied by this local lab |

Run `./workshop check` once to create synthetic acceptance records. After stopping,
resuming or replacing the owned services, run `./workshop verify` to read those
same records. Explain which component owns each request, connection, transaction,
job and durable state item, and identify the test that would expose a lost effect.
