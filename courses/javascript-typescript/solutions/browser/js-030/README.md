# js-030 browser reference

Copy this whole folder into a new learner-owned ignored directory, for example `.learning/expansion/js-030/`. Preserve an existing attempt by choosing a new directory name instead of overwriting it. The starter contains the accessible controls and TODO comments; the separate completed reference contains the handlers. Use the guide before revealing the reference.

## Main route: Docker-only static server

Use Explorer, Finder or your native file-copy tool to make a **new learner-owned copy** of this whole folder under `.learning/expansion/js-030-browser/`. Preserve an existing copy by choosing a new name. Open a terminal in that copied folder. Mount only this copy, not the repository, its parent directory or the authenticated classroom files.

The already prepared `ds60sqlpy-lab:0.4.1` image supplies Python inside Docker, so no host Python installation is required. Use a separate origin for each lesson. From the copied directory, POSIX shells use:

```bash
docker run --pull never --rm --name ds60-js-030-static --read-only --user 65534:65534 --cap-drop ALL --security-opt no-new-privileges --memory 128m --cpus 1 --pids-limit 64 --publish 127.0.0.1:8730:8000 --mount "type=bind,source=$PWD,target=/site,readonly" --entrypoint python ds60sqlpy-lab:0.4.1 -m http.server 8000 --bind 0.0.0.0 --directory /site
```

Windows users run the same Bash command inside their Docker-integrated WSL 2 terminal.

Open `http://127.0.0.1:8730/` in a real browser. The host publish address is loopback only; the 0.0.0.0 bind is inside the container namespace so the published port can reach it. The source mount is read-only and the server only reads this copied fixture. Edit your copy on the host and reload the page. If this specific port is occupied, choose a different unused loopback port and keep it consistent for storage checks. Never reuse the authenticated classroom origin for these scripts.

Stop this foreground server with Ctrl+C. If needed, stop only the named `ds60-js-030-static` container from another terminal. The --rm option removes that container after it stops; the learner copy remains. The image must already be prepared through the course Docker setup; this command does not install packages or intentionally acquire external assets.

An optional already-prepared contributor Python environment can instead run `python -m http.server 8730 --bind 127.0.0.1 --directory .` from the same copy. This alternative is not required for the Docker route.

## Checks

1. Validate named form fields before accepting state.
2. Report actual persistence success or failure.
3. Validate stored version and fields before loading.
4. Distinguish unsaved draft from persisted state.
5. Observe external-tab storage notification without overwriting unsaved input.
6. Reset only the owned storage key.

Record visible results, relevant DOM properties, browser version and any console errors. For keyboard behavior, use actual Tab and activation keys. For storage, keep the same scheme/host/port and use two actual tabs for the cross-document notification. Storage may be unavailable under browser policy; report that outcome honestly. The reference never clears unrelated localStorage keys. For CSP, inspect the actual browser policy and resource behavior; a static source check alone is not execution evidence.

No screen-reader compatibility claim follows solely from ARIA attributes. A separate assistive-technology session is needed for that evidence. No exercise requires external navigation or a paid API.
