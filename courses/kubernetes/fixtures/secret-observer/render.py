"""Regenerate the reviewed synthetic Kubernetes fixture without cluster access."""

from __future__ import annotations

import json
from pathlib import Path


def manifest(folder: Path) -> dict[str, object]:
    labels = {"app": "synthetic-secret-observer", "ds60-lesson": "k8s-019"}
    secret = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {"name": "synthetic-message", "labels": labels},
        "type": "Opaque",
        "stringData": {"lesson-message": "DUMMY_LESSON_ONLY"},
    }
    program = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": "synthetic-secret-observer-program", "labels": labels},
        "data": {"app.py": (folder / "app.py").read_text()},
    }
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": "synthetic-secret-observer", "labels": labels},
        "spec": {
            "replicas": 1,
            "revisionHistoryLimit": 0,
            "progressDeadlineSeconds": 60,
            "selector": {"matchLabels": {"app": labels["app"]}},
            "template": {
                "metadata": {"labels": labels},
                "spec": {
                    "automountServiceAccountToken": False,
                    "terminationGracePeriodSeconds": 1,
                    "securityContext": {
                        "runAsNonRoot": True,
                        "runAsUser": 65532,
                        "runAsGroup": 65532,
                        "fsGroup": 65532,
                        "seccompProfile": {"type": "RuntimeDefault"},
                    },
                    "containers": [
                        {
                            "name": "observer",
                            "image": "ds60sqlpy-k8s-fixture:0.2.0",
                            "imagePullPolicy": "Never",
                            "command": ["python", "-u", "/lesson/app.py"],
                            "env": [
                                {
                                    "name": "SYNTHETIC_MARKER",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": "synthetic-message",
                                            "key": "lesson-message",
                                        }
                                    },
                                },
                                {
                                    "name": "POD_UID",
                                    "valueFrom": {"fieldRef": {"fieldPath": "metadata.uid"}},
                                },
                            ],
                            "ports": [{"containerPort": 8080}],
                            "resources": {
                                "requests": {"cpu": "25m", "memory": "32Mi"},
                                "limits": {"cpu": "100m", "memory": "96Mi"},
                            },
                            "securityContext": {
                                "allowPrivilegeEscalation": False,
                                "readOnlyRootFilesystem": True,
                                "capabilities": {"drop": ["ALL"]},
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/ready", "port": 8080},
                                "periodSeconds": 2,
                                "timeoutSeconds": 1,
                            },
                            "volumeMounts": [
                                {
                                    "name": "program",
                                    "mountPath": "/lesson",
                                    "readOnly": True,
                                },
                                {
                                    "name": "marker",
                                    "mountPath": "/synthetic",
                                    "readOnly": True,
                                },
                            ],
                        }
                    ],
                    "volumes": [
                        {
                            "name": "program",
                            "configMap": {"name": "synthetic-secret-observer-program"},
                        },
                        {
                            "name": "marker",
                            "secret": {
                                "secretName": "synthetic-message",
                                "defaultMode": 288,
                                "items": [{"key": "lesson-message", "path": "message"}],
                            },
                        },
                    ],
                },
            },
        },
    }
    return {"apiVersion": "v1", "kind": "List", "items": [secret, program, deployment]}


if __name__ == "__main__":
    folder = Path(__file__).resolve().parent
    (folder / "manifest.json").write_text(json.dumps(manifest(folder), indent=2) + "\n")
    (folder / "rotate.json").write_text(
        json.dumps({"stringData": {"lesson-message": "DUMMY_LESSON_ROTATED"}}, indent=2) + "\n"
    )
