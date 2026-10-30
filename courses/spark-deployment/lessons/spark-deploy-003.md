# spark-deploy-003: Own an isolated Compose topology

Tutorial mode. Stage: beginner. Direct prerequisites: `spark-deploy-002`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Own the topology and its saved state

The Compose project has a master, two workers, a separate driver and a History Server. The notebook is optional. All Spark compute services join a private internal network. A narrow UI relay connects that network to a separate ingress network and publishes only fixed HTTP destinations on host loopback with dynamically chosen ports. No service receives the Docker socket, host credentials or a learner volume. Spark application code is trusted local code in this single-user lab.

`lab.py` records a random project identity and checks ownership labels before operating on containers. State is a separate host directory containing event logs, bounded results, notebooks and a private login token. Container replacement and state deletion are different actions. The wrapper provides no state-destruction command.

## Worked case A: bring up the owned services

After initialization in the preceding chapter:

```sh
python3 lab.py up
python3 lab.py status
python3 lab.py urls
```

`up` explicitly disables builds and pulls. Compose creation order is not readiness: each worker waits for the master socket, while the application separately waits for its required executors. A listening master alone does not prove correct data processing. Expect the five Spark services plus their UI relay, two registered workers in the master UI and dynamic loopback URLs. Do not assume that the host's port is the container's port.

Each worker advertises one core and one GiB to the master. The container limit includes more than executor heap. The combined environment needs headroom for the driver, master, History Server, Java/Python processes, native memory and other active work. The declared limits are small teaching budgets, not production sizing guidance.

## Worked case B: stop, resume and replace without deleting evidence

```sh
python3 lab.py stop
python3 lab.py resume
python3 lab.py down
python3 lab.py up
```

Stop and resume use existing containers. Down removes only this project's containers and network, preserving the saved files. A subsequent up recreates containers using the saved image IDs. Event logs and JSON results should remain byte-identical if no new application has written to them. Container IDs may change after replacement and must not be used as persistent data identity.

Before a lifecycle comparison, record the filenames and hashes you intend to preserve. Afterward, compare those same files and read a completed report without submitting its application again. A fresh successful run is different evidence from retained-result readback.

## Diagnose and transfer

If an unrelated container shares the project label but lacks the workshop owner label, the wrapper refuses the operation. Investigate ownership rather than deleting it. If the saved image was removed, prepare the exact intended image deliberately or start a new owned lab; a silent tag substitution would invalidate the original receipt.

An internal Compose network prevents ordinary outbound routing but is not a sandbox for hostile code or a replacement for application authentication. Keep the lab on a trusted engine. The security chapters explain what changes when peers, machines or users cease to be trusted.

## Primary references

- [Compose networking and service names](https://docs.docker.com/compose/how-tos/networking/)
- [Compose startup ordering](https://docs.docker.com/compose/how-tos/startup-order/)
