"""Generate the networking/operations extension without contacting any cluster."""

from pathlib import Path
import json
import runpy
import sys
from urllib.parse import urlsplit

BASE = Path(__file__).resolve().parents[2]
ROOT = BASE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BASE / "authoring"))

from key_terms import render as key_terms_block  # noqa: E402
from reasoning import render as reasoning_block  # noqa: E402

from scripts.format_inline_code import canonical_markdown, ownership  # noqa: E402
from scripts.format_repo import load_policy  # noqa: E402

SPECS = runpy.run_path(str(Path(__file__).with_name("chapters.py")))["CHAPTERS"]
TEACH = runpy.run_path(str(Path(__file__).with_name("teaching.py")))["TEACHING"]
LAB_READ = (
    'kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" --namespace "$LAB_NAMESPACE" '
)

SITES = {
    "kubernetes.io": "Kubernetes documentation",
    "gateway-api.sigs.k8s.io": "Gateway API documentation",
    "docs.python.org": "Python documentation",
    "www.cni.dev": "CNI documentation",
    "kind.sigs.k8s.io": "kind documentation",
    "doc.traefik.io": "Traefik documentation",
    "opentelemetry.io": "OpenTelemetry documentation",
    "istio.io": "Istio documentation",
    "nginx.org": "nginx documentation",
}
LEAVES = {
    "ipaddress": "ipaddress module",
    "ngx_http_proxy_module": "ngx_http_proxy_module",
    "type-nodeport": "Type NodePort",
    "loadbalancer": "Type LoadBalancer",
    "virtual-ips": "Virtual IPs and service proxies",
    "endpoint-slice-v1": "EndpointSlice API reference",
    "nodelocaldns": "NodeLocal DNSCache",
    "dns-pod-service": "DNS for Services and Pods",
    "httproute": "HTTPRoute",
    "referencegrant": "ReferenceGrant",
    "tls": "TLS",
    "docs": "Overview",
    "services-networking": "Services, load balancing and networking",
    "cluster-ip-allocation": "ClusterIP allocation",
    "dns-debugging-resolution": "Debugging DNS resolution",
    "endpoint-slices": "EndpointSlices",
    "source-ip": "Source IP",
    "headless-services": "Headless Services",
    "statefulset": "StatefulSets",
    "dual-stack": "IPv4/IPv6 dual-stack",
    "topology-aware-routing": "Topology-aware routing",
    "liveness-readiness-startup-probes": "Liveness, readiness and startup probes",
    "debug-service": "Debug Services",
    "debug-running-pod": "Debug running Pods",
}


def reference_label(url):
    """Readable link text from a documentation URL, keeping the site name."""
    parts = urlsplit(url)
    leaf = parts.fragment or parts.path.rstrip("/").rsplit("/", 1)[-1]
    leaf = leaf.removesuffix(".html")
    words = LEAVES.get(leaf, leaf.replace("-", " "))
    site = SITES.get(parts.netloc, parts.netloc)
    return f"{site}: {words[:1].upper()}{words[1:]}" if words else site


def write(path, text):
    if path.suffix == ".md":
        relative = path.relative_to(ROOT).as_posix()
        if ".." in Path(relative).parts or "\\" in relative:
            raise ValueError("Generator Markdown path must stay inside its owned root")
        for component in (path, *path.parents):
            if component.is_symlink():
                raise ValueError("Generator Markdown output cannot use symlinks")
            if component == ROOT:
                break
        generated, protected = ownership(relative, load_policy(ROOT))
        if protected is not None:
            raise ValueError("Generator Markdown output is protected: " + relative)
        if generated:
            text = canonical_markdown(text, root=ROOT, path=relative)
        else:
            print(
                "GENERATION-DIRECT " + relative + ": layout owned by format-repo", file=sys.stderr
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def build():
    plan_path = ROOT / "docs/expansion/plans/kubernetes.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    manifest = json.loads((BASE / "lessons.json").read_text(encoding="utf-8"))
    plan["lessons"] = [r for r in plan["lessons"] if int(r["id"].split("-")[-1]) <= 42]
    manifest["lessons"] = [r for r in manifest["lessons"] if int(r["id"].split("-")[-1]) <= 42]
    inventory = []
    for n, spec in enumerate(SPECS, 43):
        title, concepts, mental, mechanism, diagram, examples, tasks, refs = spec
        key = f"k8s-{n:03d}"
        t = TEACH[key]
        reads = "\n".join(LAB_READ + read for read in t["reads"])
        checklist = "".join(f"\n- {item}" for item in t.get("checklist", []))
        if checklist:
            checklist = f"\nBefore concluding, record:\n{checklist}\n"
        vocabulary = "\n\n".join(part for part in (mental, key_terms_block(key)) if part)
        prereq = ["k8s-008", "k8s-020"] if n == 43 else [f"k8s-{n - 1:03d}"]
        prerequisites = ", ".join(f"`{p}`" for p in prereq)
        level = "intermediate" if n <= 52 else "advanced"
        guide = f"courses/kubernetes/guides/{key}.md"
        source = f"courses/kubernetes/lessons/{key}.md"
        solution = f"courses/kubernetes/solutions/{key}_solutions.md"
        text = f"""# {key}: {title}

## Level and prerequisites

{level.capitalize()}; about 120 minutes. Direct prerequisites: {prerequisites}. Shared workflow: [study guide](../STUDY-GUIDE.md#networking-extension-boundary).

## Learning objectives

- {tasks[2][0]}
- {tasks[-1][0]}

## Purpose, vocabulary and mental model

{vocabulary}

## Mechanism and field-by-field reasoning

{mechanism}

## Trace the request or control path

```text
{diagram}
```

{t["trace"]}

## Worked example / walkthrough
"""
        for i, (heading, body, lang, code, expected) in enumerate(examples, 1):
            text += f"\n### Worked example {i}: {heading}\n\n{body}\n\n```{lang}\n{code}\n```\n\n**Expected observation:** {expected}\n"
        text += f"""
## Run boundary and the owned host lab

{t["run"]}

The [fixture checker](../fixtures/networking/README.md) makes no API calls; on Windows use WSL 2.

```sh
: "${{LAB_KUBECONFIG:?Use the private path from the owned receipt}}"
: "${{LAB_CONTEXT:?Use the exact context from the owned receipt}}"
: "${{LAB_NAMESPACE:?Use the namespace from the owned receipt}}"
{reads}
```

{t["read_note"]} Read rules: [owned live reads](../STUDY-GUIDE.md#owned-live-reads).

## Six progressive exercises
"""
        worksheet = f"# {key}: learner evidence worksheet\n\nThe default examples are synthetic. Record actual cluster evidence only after a separately prepared owned host lab. Never copy credentials into this file.\n"
        answer = f"# {key}: explanatory solutions\n\nAttempt each exercise first, then compare ([study guide](../STUDY-GUIDE.md#solutions-and-the-ai-tutor)).\n\n## Mechanism review\n\n{mental}\n\n{mechanism}\n"
        ledger = []
        for i, (prompt, expected, why) in enumerate(tasks, 1):
            text += f"\n### Exercise {i}: {prompt}\n\n**Expected evidence:** {expected}\n\n**Progressive hint:** {t['hints'][i - 1]}\n"
            worksheet += f"\n## Exercise {i}: {prompt}\n\nMy prediction:\n\nSynthetic facts used:\n\nActual owned observation, if performed:\n\nInterpretation and remaining uncertainty:\n"
            answer += f"\n## Exercise {i}: {prompt}\n\n{why}\n\n**Expected:** {expected}\n"
            if reasoning_block(key, i):
                answer += f"\n{reasoning_block(key, i)}\n"
            ledger.append(dict(exercise=i, task=prompt, expected=expected))
        text += (
            f"""
## Diagnosis, failure boundaries and common mistakes

{t["mistakes"]}
{checklist}
General evidence rules: [diagnosis rules](../STUDY-GUIDE.md#diagnosis-rules).

## Retrieval and transfer

{t["retrieval"]}

Score your answer with the [retrieval loop](../STUDY-GUIDE.md#retrieval-loop).

## Primary references

"""
            + "\n".join(f"- [{reference_label(url)}]({url})" for url in refs)
            + f"""

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for {key}: {title}.
Read {guide} and {source}. Direct prerequisites: {prerequisites}.
Ask me to trace the request, predict the changed case and identify the smallest useful observation.
Keep courses/kubernetes/solutions/ closed until I attempt or explicitly request comparison.
Distinguish synthetic facts, API configuration, controller state, actual traffic and cleanup.
Use only an explicitly owned host receipt and named capability; never select an ambient cluster.
Do not install controllers, change networking, broaden RBAC or run destructive cleanup for me.
Finish with a fresh packet-path or failure-diagnosis case.
```
"""
        )
        write(ROOT / guide, text)
        write(ROOT / source, worksheet)
        write(ROOT / solution, answer)
        write(
            BASE / f"fixtures/{key}-cases.json",
            json.dumps(
                dict(
                    lesson_id=key,
                    provenance="synthetic teaching cases; no runtime observations",
                    cases=ledger,
                ),
                indent=2,
            ),
        )
        plan["lessons"].append(
            dict(
                id=key,
                title=title,
                level=level,
                minutes=120,
                prerequisites=prereq,
                runtime="reading",
                concepts=concepts,
                outcome=tasks[-1][0],
                lab=tasks[2][0],
                verification=tasks[-1][1],
            )
        )
        manifest["lessons"].append(
            dict(
                id=key,
                status="authored",
                language="markdown",
                runtime_profile="reading",
                guide_path=guide,
                source_path=source,
                solution_paths=[solution],
                verification_id=None,
            )
        )
        inventory.append(
            dict(
                id=key,
                runtime="reading",
                capability=(
                    "separately prepared owned dual-stack cluster and dual-stack application/client fixture"
                    if n == 60
                    else "separately prepared owned advanced host lab"
                ),
                fixture="courses/kubernetes/fixtures/networking",
                expected=tasks[-1][1],
            )
        )
    plan["summary"] = (
        "66 detailed Kubernetes lessons, including a dedicated 24-lesson networking and operations sequence covering Pod/Service/node addresses, CNI, DNS, routing, external load balancing, Gateway API, TLS, policy, dual-stack, topology and end-to-end diagnosis. Advanced host capabilities remain explicit."
    )
    write(plan_path, json.dumps(plan, indent=2))
    write(BASE / "lessons.json", json.dumps(manifest, indent=2))
    write(
        BASE / "fixtures/networking/lesson-inventory.json",
        json.dumps(
            dict(
                schema_version=1,
                lessons=inventory,
                qualification="static teaching fixtures only until actual owned runtime evidence is recorded",
            ),
            indent=2,
        ),
    )
    supplement_path = Path(__file__).with_name("supplements.json")
    if supplement_path.exists():
        for key, body in json.loads(supplement_path.read_text()).items():
            path = BASE / f"guides/{key}.md"
            s = path.read_text(encoding="utf-8")
            start = "## Networking depth supplement\n"
            end = "<!-- networking-depth-end -->"
            if start in s:
                s = s[: s.index(start)] + s[s.index(end) + len(end) :].lstrip("\n")
            block = start + "\n" + body + "\n\n" + end + "\n\n"
            marker = "## Ask an AI tutor about this lesson"
            s = s.replace(marker, block + marker) if marker in s else s + "\n" + block
            write(path, s)
    print(
        f"Authored {len(SPECS)} Kubernetes networking lessons; original 42 IDs and admission unchanged."
    )


if __name__ == "__main__":
    build()
