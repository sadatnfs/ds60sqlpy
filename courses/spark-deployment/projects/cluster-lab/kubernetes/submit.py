"""Print a concrete cluster submit plan; execute only with explicit target options."""

import argparse
import re
import shlex
import subprocess
import urllib.parse
from pathlib import Path


def command(args):
    if not re.fullmatch(r"ds60-spark-[a-z0-9-]{1,40}", args.namespace):
        raise ValueError("Use an explicitly owned namespace beginning ds60-spark-")
    if not args.master.startswith("k8s://https://"):
        raise ValueError("Use the explicit Kubernetes HTTPS API URL")
    endpoint = urllib.parse.urlsplit(args.master.removeprefix("k8s://"))
    if (
        not endpoint.hostname
        or endpoint.username is not None
        or endpoint.password is not None
        or endpoint.query
        or endpoint.fragment
        or endpoint.path not in {"", "/"}
    ):
        raise ValueError("The API URL must not contain credentials, query or path data")
    if not re.fullmatch(r"[a-zA-Z0-9._/:-]+@sha256:[0-9a-f]{64}", args.image):
        raise ValueError("Select a prepared image by immutable registry digest")
    if not args.kubeconfig.is_file():
        raise ValueError("Pass an explicitly prepared kubeconfig file")
    return [
        args.spark_submit,
        "--master",
        args.master,
        "--deploy-mode",
        "cluster",
        "--name",
        "ds60-kubernetes-partition-proof",
        "--conf",
        "spark.kubernetes.context=" + args.context,
        "--conf",
        "spark.kubernetes.namespace=" + args.namespace,
        "--conf",
        "spark.kubernetes.container.image=" + args.image,
        "--conf",
        "spark.kubernetes.authenticate.driver.serviceAccountName=spark-driver",
        "--conf",
        "spark.kubernetes.authenticate.executor.serviceAccountName=spark-executor",
        "--conf",
        "spark.kubernetes.driver.label.ds60-workshop=spark-deployment",
        "--conf",
        "spark.kubernetes.executor.label.ds60-workshop=spark-deployment",
        "--conf",
        "spark.executor.instances=2",
        "--conf",
        "spark.executor.cores=1",
        "--conf",
        "spark.executor.memory=512m",
        "--conf",
        "spark.driver.memory=1g",
        "--conf",
        "spark.driver.maxResultSize=1m",
        "--conf",
        "spark.kubernetes.driver.limit.cores=1",
        "--conf",
        "spark.kubernetes.executor.limit.cores=1",
        "--conf",
        "spark.kubernetes.submission.waitAppCompletion=true",
        "local:///opt/spark/work-dir/kubernetes_job.py",
    ]


def verify_context_endpoint(args):
    result = subprocess.run(
        [
            "kubectl",
            "--kubeconfig",
            str(args.kubeconfig.resolve()),
            "--context",
            args.context,
            "config",
            "view",
            "--minify",
            "--output",
            "jsonpath={.clusters[0].cluster.server}",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    selected = result.stdout.strip().rstrip("/")
    requested = args.master.removeprefix("k8s://").rstrip("/")
    if not selected or selected != requested:
        raise ValueError("Requested API URL differs from the explicit kubeconfig context")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--kubeconfig", type=Path, required=True)
    parser.add_argument("--master", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--spark-submit", default="spark-submit")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    argv = command(args)
    print(shlex.join(argv))
    if args.execute:
        import os

        verify_context_endpoint(args)
        env = dict(os.environ, KUBECONFIG=str(args.kubeconfig.resolve()))
        subprocess.run(argv, env=env, check=True, timeout=600)
    else:
        print("Plan only. No Kubernetes request or registry operation was made.")


if __name__ == "__main__":
    main()
