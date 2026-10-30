from author import BASE, ROOT, canonical_markdown, hello
import copy, json

# These are host-only finite commands, never admitted by the normal worker.
marker = b"persistent-demo\n"
writer = "from pathlib import Path; import hashlib; p=Path('/data/marker'); value=b'persistent-demo\\n'; f=p.open('xb'); f.write(value); f.close(); print(hashlib.sha256(value).hexdigest())"
reader = "from pathlib import Path; import hashlib; value=Path('/data/marker').read_bytes(); assert value==b'persistent-demo\\n'; print(hashlib.sha256(value).hexdigest())"
for mode, code in (("writer", writer), ("reader", reader)):
    pod = copy.deepcopy(hello()[0]["spec"]["template"]["spec"])
    pod["restartPolicy"] = "Never"
    pod["securityContext"]["fsGroup"] = 65532
    container = pod["containers"][0]
    container.pop("ports", None)
    container.pop("readinessProbe", None)
    container["name"] = "marker"
    container["command"] = ["python", "-c", code]
    container["volumeMounts"] = [
        {"name": "data", "mountPath": "/data", "readOnly": mode == "reader"}
    ]
    pod["volumes"] = [
        {
            "name": "data",
            "persistentVolumeClaim": {"claimName": "data-store-0", "readOnly": mode == "reader"},
        }
    ]
    pod["affinity"] = {
        "podAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": [
                {
                    "labelSelector": {"matchLabels": {"app": "store"}},
                    "topologyKey": "kubernetes.io/hostname",
                }
            ]
        }
    }
    job = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {"name": "marker-" + mode},
        "spec": {
            "backoffLimit": 0,
            "activeDeadlineSeconds": 60,
            "completions": 1,
            "parallelism": 1,
            "template": {"metadata": {"labels": {"role": "marker-" + mode}}, "spec": pod},
        },
    }
    (BASE / f"fixtures/k8s-022-marker-{mode}.json").write_text(json.dumps(job, indent=2) + "\n")

objects = {
    4: "deployment hello",
    5: "pods -l app=hello",
    6: "deployment hello",
    7: "service hello",
    9: "configmap hello-config",
    10: "deployment hello",
    11: "job hello-task",
    12: "pods -l app=hello",
    13: "deployment hello",
    14: "endpointslices -l kubernetes.io/service-name=hello",
    15: "pods -l app=hello",
    16: "pod init-demo",
    17: "deployment hello",
    18: "rolebinding lesson-pod-reader",
    19: "secret synthetic-message",
    20: "service hello",
    21: "networkpolicy hello-allow-client",
    22: "pvc data-store-0",
    23: "httproute hello-route",
    24: "deployment hello",
    25: "deployment hello",
    26: "daemonset node-fixture",
    27: "pods -l app=hello",
    28: "statefulset store",
    29: "lessonreports hello-report",
    30: "lessonreports hello-report",
    31: "deployment hello",
    32: "pdb hello-budget",
    33: "hpa hello",
    34: "service hello",
    35: "configmap hello-config",
    36: "pvc data-store-0",
    37: "deployment hello",
    38: "deployment hello",
    39: "pods -l app=hello",
    40: "endpointslices -l kubernetes.io/service-name=hello",
    41: "pvc data-store-0",
    42: "lessonreports hello-report",
}
for n, resource in objects.items():
    output = "jsonpath='{.metadata.uid}'" if n == 19 else "json"
    path = BASE / f"guides/k8s-{n:03d}.md"
    text = path.read_text()
    block = f"""## Inspect the specific owned object

Only after the chapter's host capability is provisioned and its resources remain present, use the explicit receipt fields described in [host-labs.md](../host-labs.md). A completed one-shot browser Run has already cleaned its objects. The following read does not provision the missing capability and does not justify changing credentials after a Forbidden result.

POSIX:

```sh
: "${{LAB_KUBECONFIG:?Use the owned receipt path}}"
: "${{LAB_CONTEXT:?Use the owned receipt context}}"
: "${{LAB_NAMESPACE:?Use the owned receipt namespace}}"
kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" --namespace "$LAB_NAMESPACE" get {resource} -o {output}
```

PowerShell:

```powershell
if (-not $env:LAB_KUBECONFIG -or -not $env:LAB_CONTEXT -or -not $env:LAB_NAMESPACE) {{ throw 'Owned receipt fields are required.' }}
& kubectl --kubeconfig $env:LAB_KUBECONFIG --context $env:LAB_CONTEXT --namespace $env:LAB_NAMESPACE get {resource} -o {output}
if ($LASTEXITCODE -ne 0) {{ throw 'The scoped observation failed.' }}
```

Retain only the fields needed by this chapter's prediction. A NotFound result may be expected after one-shot cleanup; a Forbidden result may identify a deliberately absent advanced capability. Neither result authorizes an ambient-context fallback.

"""
    if n in (22, 28):
        block += """## Concrete finite marker operations

The separate [exclusive-create writer](../fixtures/k8s-022-marker-writer.json) and [read-only verifier](../fixtures/k8s-022-marker-reader.json) are host-only Job manifests. The writer opens `/data/marker` with mode `xb`, so an existing file causes failure instead of silently overwriting evidence. The reader requires the exact `persistent-demo` bytes followed by a newline and reports their SHA256. It never initializes data.

Both Jobs have one completion, no retry and a60-second deadline. They use the fixed preloaded image and restricted nonroot settings. Required Pod affinity places them on the node hosting app=store, which makes the single-node ReadWriteOnce attachment assumption explicit; it does not create a storage class or guarantee scheduling. The reader mounts the claim read-only. Run initialization once, replace only the application Pod through the host operation, then run the independent reader. A second writer failure is the intended overwrite guard.

These commands are more general than the normal hello-task contract and are rejected by the browser adapter. Only the separately reviewed storage lease may bind ownership,submit them and clean their recorded UIDs. Their local code checks establish exclusive-write/read semantics, not live persistence.

"""
    if "## Inspect the specific owned object" not in text:
        text = text.replace("## Run and bounded evidence", block + "## Run and bounded evidence")
    text = canonical_markdown(text, root=ROOT, path=path.relative_to(ROOT).as_posix())
    path.write_text(text)
