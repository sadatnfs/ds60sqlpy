# Disposable Docker study application

This is an optional host lab, not an engine operation inside a classroom coding pad. Run Bash in Linux, macOS Terminal, or Ubuntu under WSL 2. Use a local Docker-compatible engine with Linux containers and Compose. Initial build needs internet access for the Python base image; prepared runs use the local image. No command here publishes an image.

The fixture is a standard-library Python HTTP server. GET `/` reads the public message, GET `/healthz` reports readiness, GET `/counter` reads data, and POST `/increment` performs one intentional increment. GET requests do not mutate the counter. The server is for local teaching only. Its in-process lock is not a multi-container database transaction.

## Prepare an owned copy

From the repository root, choose a new directory that does not already contain learner work:

```sh
if [ -e .learning/docker-study ]; then
  echo 'Learner directory already exists; choose a new name.'
  exit 1
fi
mkdir -p .learning/docker-study
cp -R courses/docker/fixtures/compose-lab/. .learning/docker-study/
cd .learning/docker-study
docker context show
docker context inspect "$(docker context show)"
docker info --format '{{.OSType}}'
docker compose version
```

Stop if the guard says the directory exists; choose a different new directory instead of overwriting it. Confirm the selected endpoint is your intended local engine and OSType is `linux`. The commands below use project `ds60-docker-study` and host port 18080. If those belong to existing unrelated work, choose a distinct project name and unused loopback port consistently in your copy. Do not stop the unrelated service.

## Validate, build with visible logs and start

```sh
docker compose -p ds60-docker-study config --quiet
docker compose --progress plain -p ds60-docker-study build
docker compose -p ds60-docker-study up -d --wait
docker compose -p ds60-docker-study ps
```

If your network requires the documented Docker Hub mirror, keep TLS verification
enabled and deliberately replace only the base-image build input:

```sh
docker compose --progress plain -p ds60-docker-study build --build-arg DS60_PYTHON_IMAGE=mirror.gcr.io/library/python:3.12-slim
```

This build-only argument does not change runtime commands or publish an image.
Use only a registry you deliberately trust, and record the resolved base identity.

Open `http://127.0.0.1:18080/` in your host browser. Expected JSON includes `message: hello from Docker study`. Open `/counter` and expect a nonnegative integer. A fresh volume starts at 0. A retained volume can have a larger value. The image runs as UID 10001, root is read-only, and only its named data volume and bounded temporary storage are writable.

## Compare host and peer networking

```sh
docker compose -p ds60-docker-study --profile tools run --rm client
```

The peer resolves `app` through the project network and requests container port 8080. It does not use the host port. Expected output is the same public message as the browser. A failure must be diagnosed from its own caller namespace; changing to host networking is not part of this lab.

## Increment explicitly and prove replacement persistence

```sh
docker compose -p ds60-docker-study exec app python -c "import urllib.request; r=urllib.request.Request('http://127.0.0.1:8080/increment', data=b'', method='POST'); print(urllib.request.urlopen(r, timeout=3).read().decode())"
docker compose -p ds60-docker-study ps -q app
docker compose -p ds60-docker-study up -d --force-recreate --wait app
docker compose -p ds60-docker-study ps -q app
```

Record the counter and the two container IDs. The IDs differ. GET `/counter` after replacement returns the retained value. A browser refresh or image rebuild alone is not this replacement test. Concurrent requests within this one server are serialized by a process-local lock. Do not scale the writer to multiple containers and assume that lock coordinates them.

## Export a consistent counter without touching other volumes

Stop the writer before exporting. The command writes a new local backup file and refuses to overwrite an existing one through shell noclobber:

```sh
docker compose -p ds60-docker-study stop app
(
  set -C
  docker compose -p ds60-docker-study run --rm --no-deps app python -c "from pathlib import Path; import json; p=Path('/data/counter.json'); v=json.loads(p.read_text()) if p.exists() else {'schema_version':1,'counter':0}; assert type(v) is dict and type(v.get('schema_version')) is int and v['schema_version']==1 and type(v['counter']) is int and v['counter']>=0; print(json.dumps(v,sort_keys=True))" >counter-backup.json
)
```

Expected file is a small JSON object with schema_version 1 and the recorded counter. If export fails, keep the error and do not treat an empty or partial file as a backup. Verify the file before use. This procedure is valid for this stopped single-file teaching app. It is not a live PostgreSQL backup recipe.

## Independently restore into a new volume

These commands create only a clearly named disposable restore target. Stop if that name already exists. The original project volume is never modified by this restore experiment.

```sh
if docker volume inspect ds60-docker-study-restore >/dev/null 2>&1; then
  echo 'Restore target already exists; choose a new owned name.'
  exit 1
fi
docker volume create --label ds60.study=restore ds60-docker-study-restore
docker run --rm --pull never --user 0:0 --network none -v ds60-docker-study-restore:/restore ds60-docker-study:local python -c "import os; os.chown('/restore',10001,10001)"
docker run --rm -i --pull never --network none -v ds60-docker-study-restore:/data ds60-docker-study:local python -c "import sys,json; from pathlib import Path; v=json.load(sys.stdin); assert type(v) is dict and type(v.get('schema_version')) is int and v['schema_version']==1 and type(v.get('counter')) is int and v['counter']>=0; p=Path('/data/counter.json'); f=p.open('x'); f.write(json.dumps(v)+'\\n'); f.close(); print('restored',v['counter'])" <counter-backup.json
docker run --rm --pull never --network none --read-only -v ds60-docker-study-restore:/data:ro ds60-docker-study:local python -c "from pathlib import Path; import json; v=json.loads(Path('/data/counter.json').read_text()); print('verified',v['counter'])"
```

The first temporary root process changes ownership only inside the newly created restore volume. It receives no host bind mount or network. The restore refuses to overwrite an existing counter. Compare restored and verified values with the backup and original record. This proves an independent reader can use the exported data. It does not prove recovery of a general database or a multi-writer service.

After reviewing the restore evidence, remove only this explicit temporary restore volume:

```sh
docker volume rm ds60-docker-study-restore
docker compose -p ds60-docker-study up -d --wait app
```

## Stop and retain progress

```sh
docker compose -p ds60-docker-study logs --tail 30 app
docker compose -p ds60-docker-study down
```

Named study data remains. To deliberately reset only this disposable study project after exporting anything you want to retain, run `docker compose -p ds60-docker-study down --volumes` from this copy. That deletes the study counter. Do not apply it to the main classroom project. Do not run global prune commands as part of this lesson.

## Evidence boundaries

Model parsing, Python checks, image builds, real engine execution and a browser observation are separate checks. `../inventory.json` lists the intended qualification cases. It does not claim they have run on your engine. Archive the actual outputs and platform information in your ignored learner copy.
