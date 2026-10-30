"""Generate the networking/operations extension without contacting any cluster."""

from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parents[2]
ROOT = BASE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.format_inline_code import canonical_markdown, ownership  # noqa: E402
from scripts.format_repo import load_policy  # noqa: E402

SPECS = runpy.run_path(str(Path(__file__).with_name("chapters.py")))["CHAPTERS"]


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
        prereq = ["k8s-008", "k8s-020"] if n == 43 else [f"k8s-{n - 1:03d}"]
        prerequisites = ", ".join(f"`{p}`" for p in prereq)
        level = "intermediate" if n <= 52 else "advanced"
        guide = f"courses/kubernetes/guides/{key}.md"
        source = f"courses/kubernetes/lessons/{key}.md"
        solution = f"courses/kubernetes/solutions/{key}_solutions.md"
        text = f"""# {key}: {title}

## Level and prerequisites

{level.capitalize()}; about 120 minutes plus optional supervised host observations. Direct prerequisites: {prerequisites}. This is the deep networking and operations extension; it preserves the original Kubernetes sequence and its separately qualified browser operations.

## Learning objectives

{tasks[2][0]} {tasks[-1][0]} Trace the exact caller, destination, control-plane object and data-plane behavior that would support your conclusion.

## Purpose, vocabulary and mental model

{mental}

## Mechanism and field-by-field reasoning

{mechanism}

## Trace the request or control path

```text
{diagram}
```

Read this diagram as a sequence of responsibilities. A controller can successfully create desired state while a later traffic or application step still fails. Identify the component that makes each decision and the concrete observation that would prove it. The addresses in these lessons are synthetic examples, never instructions to contact a shared or public system.

## Worked example / walkthrough
"""
        for i, (heading, body, lang, code, expected) in enumerate(examples, 1):
            text += f"\n### Worked example {i}: {heading}\n\n{body}\n\n```{lang}\n{code}\n```\n\n**Expected observation:** {expected}\n"
        text += """
## Run boundary and the owned host lab

The classroom saves a reading worksheet for this lesson. It does not provide the full advanced networking or controller operation in the ordinary Run adapter. The original admitted Kubernetes reference cases keep their existing contracts. A manifest being valid YAML does not mean it is admitted by that adapter, supported by your cluster, or successfully routed at runtime.

Start with the original synthetic topology and manifests in [the networking fixture](../fixtures/networking/README.md). Its static checker makes no API calls. It checks internal consistency of the teaching inputs and cannot establish a live CNI, DNS, load balancer, controller or NetworkPolicy result. The fixture inventory names the extra capability required for each optional live observation.

Optional live work requires a separately prepared, explicitly owned disposable target and the capability named by the fixture. Use the receipt's private kubeconfig, exact context and namespace. On Windows run Bash inside WSL 2. Do not use an ambient current-context, install a controller automatically or broaden RBAC after a Forbidden error. A completed one-shot browser Run has already cleaned its resources, so the host observation must belong to a separately retained owned session.

```sh
: "${LAB_KUBECONFIG:?Use the private path from the owned receipt}"
: "${LAB_CONTEXT:?Use the exact context from the owned receipt}"
: "${LAB_NAMESPACE:?Use the namespace from the owned receipt}"
kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" --namespace "$LAB_NAMESPACE" get services -o wide
```

This is a scoped read, not permission to create resources or change cluster networking. Keep credentials out of worksheets and portable exports. A host lab must record created resource UIDs and clean only those identities through its reviewed ownership procedure. Never delete a namespace merely because its name resembles the example.

## Six progressive exercises
"""
        worksheet = f"# {key}: learner evidence worksheet\n\nThe default examples are synthetic. Record actual cluster evidence only after a separately prepared owned host lab. Never copy credentials into this file.\n"
        answer = f"# {key}: explanatory solutions\n\nCompare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.\n\n## Mechanism review\n\n{mental}\n\n{mechanism}\n"
        ledger = []
        for i, (prompt, expected, why) in enumerate(tasks, 1):
            text += f"\n### Exercise {i}: {prompt}\n\n**Expected evidence:** {expected}\n\n**Progressive hint:** Name the caller and the first layer that can distinguish the possible causes. Compare the relevant object fields before changing a route, policy or workload.\n"
            worksheet += f"\n## Exercise {i}: {prompt}\n\nMy prediction:\n\nSynthetic facts used:\n\nActual owned observation, if performed:\n\nInterpretation and remaining uncertainty:\n"
            answer += f"\n## Exercise {i}: {prompt}\n\n{why}\n\n**Expected:** {expected}\n"
            ledger.append(dict(exercise=i, task=prompt, expected=expected))
        text += (
            f"""
## Diagnosis, failure boundaries and common mistakes

The controlled failure in this chapter is: {tasks[3][0]} Its distinguishing result is {tasks[3][1]} Keep that observation separate from guesses about adjacent layers. A DNS answer is not proof of a listening process. A Ready Pod is not proof of an externally reachable listener. A load-balancer address is not proof of TLS identity, path routing or a correct application response.

Use bounded observations from the actual caller's network namespace. Preserve timestamps, object UIDs, generation or resource versions where relevant, and the intended image identity. A stale healthy result from another namespace or an earlier revision cannot qualify the current path. Avoid broad packet captures, all-namespace dumps and secret output when a smaller field-level observation answers the question.

Do not repair a failed example by disabling NetworkPolicy, making a workload privileged, publishing every port or selecting another cluster. Those changes alter the contract rather than explain the failure. An unavailable capability is a valid boundary to report. Rehearse its mechanism with the synthetic fixture until the owned target is deliberately provisioned.

## Retrieval and transfer

Close the solution and reconstruct the diagram with different synthetic addresses and one changed failure condition. Explain which identities are stable, which can change after replacement, and how a client discovers the current destination. State one observation that would falsify your diagnosis.

Complete the six evidence records before advancing. For optional live work, review the owned resource ledger and UID-aware cleanup result. Keep source validation, API acceptance, controller status, actual traffic, application output and cleanup as distinct evidence. No local exercise establishes every cloud provider, CNI implementation, Kubernetes version or public production deployment.

## Primary references

"""
            + "\n".join(f"- [Official reference {i}]({url})" for i, url in enumerate(refs, 1))
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
