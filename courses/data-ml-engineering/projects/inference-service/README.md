# Inference lifecycle workshop

Run a real tiny causal Transformer through a local browser and authenticated HTTP/SSE API. Preparation trains original synthetic text locally. The server loads its byte-BPE tokenizer and safe numerical weights once at startup, performs prefill and cached decoding, and retains exact completed event records. The model demonstrates systems mechanics; it is not a pretrained assistant or evidence of general language capability.

This is an optional complete project for Data and ML Engineering chapters dme-057 through dme-072. It is separate from the classroom's bounded code pads. The default uses Linux CPU containers on macOS, Linux and Windows through WSL 2. No host Python, compiler, provider account or downloaded model is required.

## Prepare an owned copy

From the classroom repository root, prepare the ordinary CPU Torch image if it is missing:

```sh
./classroom build --profile llm-torch-cpu --local-build --tag 1.1.0
```

If you installed the classroom from Docker Hub, use the exact corresponding pulled Torch image as WORKSHOP_BASE_IMAGE below. The workshop never silently pulls or builds a missing base image. The initial HTTP image build installs only the seven small, hash-locked packages listed in requirements.lock, using network access during this explicit preparation step. Training and service startup perform no package or model downloads.

Copy this project outside the repository's maintained source tree:

```sh
mkdir -p "$HOME/inference-workshop"
cp -R courses/data-ml-engineering/projects/inference-service/. "$HOME/inference-workshop/"
cd "$HOME/inference-workshop"
./workshop prepare
./workshop start
```

Open [the local workshop](http://127.0.0.1:8892). Docker must be running. On Windows, run these commands in WSL 2 with Docker integration enabled. Keep the copy in the Linux home directory for predictable file ownership. The image is CPU-based on both AMD64 and ARM64; no NVIDIA dependency is pulled by this project.

The first preparation performs 256 actual gradient updates on the checked-in corpus, validates cached/full logits and writes .workshop/model/. Later preparation verifies existing model assets instead of overwriting or retraining them. A corrupted or incompatible checkpoint fails explicitly. Retain it for diagnosis and use a new owned copy for a deliberately new preparation.

To choose another port, project name or compatible already-pulled base image, set initial values before the first preparation:

```sh
WORKSHOP_PORT=8893 WORKSHOP_PROJECT=ds60-inference-two ./workshop prepare
# A Hub-installed base can be supplied explicitly:
# WORKSHOP_BASE_IMAGE=YOUR_ACCOUNT/ds60sqlpy:1.1.0-worker-llm-torch-cpu ./workshop prepare
```

Check the actual catalog suffix/tag in the classroom Docker Hub instructions before selecting a base. Do not invent a tag or use an incompatible architecture. Initial values are saved in .workshop/settings.env. Later commands use that saved selection; they do not silently change projects or ports from environment overrides.

Optional WORKSHOP_PACING=0.02 adds a visible delay between tokens for teaching. The default is zero. Pacing is bounded to at most 0.2 seconds and reported separately from model compute time. It is not a performance benchmark.

## Stop, resume and replace

```sh
./workshop stop
./workshop resume
./workshop status
./workshop logs
```

Resume starts the exact existing containers without building or pulling. If the containers no longer exist, use ./workshop start to create from the existing image and files. To apply a deliberately rebuilt project image:

```sh
./workshop build
./workshop replace
```

Replacement retains model assets, the private token and request records. A completed record stays byte-for-byte unchanged. An unfinished request becomes an explicit interrupted error on startup; it is never automatically generated again. No helper action deletes state, prunes images or uploads to a registry.

The service owns only the selected Compose project and the .workshop/ directory in this copy. Do not share that state directory between two running servers. A one-writer lock rejects accidental concurrent ownership. Do not delete .workshop/ to perform an ordinary restart.

## Follow one request

Enter a short synthetic prompt, choose generation settings and select Create and stream. The page shows model/tokenizer identity, readiness, context, actual device, queue reservations, text output, token events and terminal metrics. Temperature zero is greedy. Positive temperature uses a request-local seeded top-k sampler. EOS, stop-string matching and the maximum new-token budget are distinct finish reasons.

The model has a 96-token context under the supplied preparation. Prompt tokens include BOS, and prompt plus requested continuation must fit. A Unicode character is not necessarily one token. The tokenizer uses original byte BPE with no implicit Unicode normalization. Generated invalid byte sequences use an explicit replacement-character display policy; raw token IDs and bytes remain in the event trace.

A creation response means admitted work, not completed inference. The service has one compute slot and at most two waiting reservations. It rejects excess capacity and a full 128-record history explicitly. It does not silently evict earlier work. The only active subscriber must attach within 30 seconds. The subscriber queue holds four events; a five-second application backpressure timeout requests cancellation.

Cancellation is cooperative between model steps. An in-flight kernel must return before its reservation is released. Disconnecting an active stream requests cancellation under this project's policy. Reconnecting reads the retained events; it does not resume model generation. Completed history and exact JSON downloads never call the model.

The browser keeps an unknown creation's original idempotency key and parameters for explicit reconciliation. It does not automatically resubmit on reload. Reusing a key with changed parameters is rejected. Output uses text nodes, not HTML interpretation, and all browser assets are local.

## API contract

The UI obtains its private header token from the local page. Operator scripts may read the dedicated token file without printing it. Do not place tokens in URLs, command logs or reports. Host and Origin must match the saved loopback URL; POST calls require that exact Origin and all API calls require X-Workshop-Token.

| Operation | Endpoint | Behavior |
| --- | --- | --- |
| Create or reconcile | POST /api/requests | Strict JSON with prompt, max_new_tokens, temperature, top_k, seed, stops, idempotency_key |
| Inspect readiness/model | GET /api/status | Actual loaded identity, device and process counters |
| List retained identities | GET /api/requests | Source-bound statuses; no inference |
| Download record | GET /api/requests/ID | Exact bounded JSON envelope and checksum |
| Read events | GET /api/requests/ID/events | SSE with sequential IDs and explicit terminal event |
| Read suffix | Same path with ?after=N or Last-Event-ID | One validated cursor; never creates new work |
| Request cancellation | POST /api/requests/ID/cancel | Idempotent control; resource release follows cleanup |

A model token, SSE event and network chunk are separate units. A network chunk may contain part of one event or several complete events. The client parses event boundaries before checking each frame. Ordinary events allow 8,000 JSON bytes; terminal events allow 32,768 bytes to preserve Unicode output and JSON escaping within the 160,000-byte record limit. Transport chunks do not change those event limits. A closed connection without a terminal event is an unknown outcome. Read retained state rather than issuing a new generation with a new key. Record-save failure preserves actual in-memory output with a durability warning and explicit download; it does not rewrite the execution outcome as though nothing ran.

## Verification

The maintained API checker requires an explicitly disposable service and a contributor Python 3 interpreter. It creates only bounded synthetic requests, verifies admission/cancellation/source identity, streams actual output and saves exact receipt hashes:

```sh
python3 check_api.py --url http://127.0.0.1:8892 --token-file .workshop/token --report api-report.json
./workshop stop
./workshop resume
python3 check_api.py --url http://127.0.0.1:8892 --token-file .workshop/token --verify-persisted api-report.json --report resume-report.json
./workshop replace
python3 check_api.py --url http://127.0.0.1:8892 --token-file .workshop/token --verify-persisted api-report.json --report replacement-report.json
```

A prepared contributor Playwright environment can run the maintained real browser gate:

```sh
python3 check_browser.py --url http://127.0.0.1:8892 --output browser-report
# After replacement, open a fresh document and read the original identity only:
python3 check_browser.py --url http://127.0.0.1:8892 --verify-persisted browser-report/browser.json --output browser-replacement
```

Install Chromium deliberately in that contributor environment before running this optional gate. Learners only need their ordinary browser. The gate retains desktop/dark/mobile screenshots, exact downloads and a report; it does not weaken the service's CSP or follow external requests.

Readback mode submits no jobs and checks that generation-call counters remain unchanged. Preserve the original report, model identity and record bytes. A fresh process has a fresh process counter; that does not mean old requests were lost. Repository tests/test_llm_serving* contains independent tokenizer, schema, queue, failure, storage and numerical-mechanism regressions. Actual browser observations additionally qualify rendering, streaming, responsive layout and download bytes.

## Maintainer lifecycle gate

From the repository root, an explicitly disposable gate can prepare a separate
workshop copy, train its small original model, exercise the real API, verify
exact-container resume, replace the service and read the original records:

```sh
python scripts/check_inference_project.py --project ds60-infer-ci-local100 --image ds60sqlpy-worker-llm-torch-cpu:1.1.0 --confirm-disposable --report work/inference-project-receipts.json
```

The versioned CPU image must already exist and match the native Linux engine.
Add `--browser-python /path/to/prepared/browser-env/bin/python` to include the
actual Chromium streaming, unknown-outcome reconciliation and exact-download
gates. Prepare Playwright and Chromium deliberately first. The gate rejects an
existing project or evidence directory, removes only its newly owned containers
and retains its synthetic model and records under the ignored `work/` directory.
It never publishes an image or removes classroom volumes. Native PyTorch CI
requires this gate with the browser checks on both supported architectures.

## Limits and extensions

The live implementation uses whole-request FIFO and contiguous per-request KV caches. Continuous batching, chunked prefill, paged attention, prefix sharing, quantized kernels and speculative multi-token serving are explained with separate bounded examples. They are not silently claimed as live features.

The service accepts only a local loopback origin and uses one ASGI worker. It is not a public multi-tenant service. Do not expose its port publicly or mount a Docker socket. Images exclude the private token, model and history through an allowlisted build context. Files are mounted with read-only model/token paths and a separate writable state directory; processes have bounded CPU, memory and PID limits.

An explicit cuda:0 engine configuration is available only to separately prepared compatible environments and performs allocation/kernel/readback before readiness. The supplied Compose project remains CPU-only and does not install an accelerator stack. A Mac GPU is not CUDA, and CPU measurements do not qualify GPU kernels. See the existing CUDA/PyTorch routes for deliberate NVIDIA preparation and hardware-specific evidence.
