from author import author,hello,BASE
import json

timeline=[{'seconds':0,'event':'baseline','service_uid':'svc-1','selector':'hello','ready_pods':1,'response':'expected'}, {'seconds':10,'event':'host_fault','service_uid':'svc-1','selector':'missing','ready_pods':1,'response':'timeout'}, {'seconds':15,'event':'observation','service_uid':'svc-1','selector':'missing','ready_pods':1,'endpoints':0}, {'seconds':25,'event':'conditional_repair','service_uid':'svc-1','selector':'hello','ready_pods':1}, {'seconds':30,'event':'verification','service_uid':'svc-1','selector':'hello','ready_pods':1,'response':'expected','endpoints':1}]
(BASE/'fixtures/k8s-040-timeline.json').write_text(json.dumps(timeline,indent=2)+'\n')
author(40,
'''An incident investigation turns a symptom into a testable explanation and a bounded repair. The first useful question is not which command might make the red status disappear, but which observation would distinguish the leading hypotheses. A Service timeout with healthy Pods can result from selectors, ports, network policy or the application path. Restarting every Pod changes evidence without necessarily testing any of those causes.

This chapter injects one synthetic fault: a host-controlled change to the selector of the exact owned Service. The workload remains Ready, but the Service no longer selects it. The investigator records a baseline, the symptom, endpoint/selector evidence, a conditional repair and a post-repair application check. A separate teacher may reveal the chosen fault only after the learner has formed a hypothesis.

The normal browser adapter can demonstrate bounded failures but does not offer an unrestricted fault-injection API or persistent arbitrary edits. The advanced exercise requires an exclusive lease and a fixed host action with a deadline, cancellation, exact target UID and restoration record. No unrelated namespace, Node or cluster setting is changed.''',
[
('Preserve a useful timeline','''[The synthetic timeline](../fixtures/k8s-040-timeline.json) uses elapsed seconds from one controlled start. It records Service UID, selector, Ready Pod count and application result. At second10 the application request times out while one Pod remains Ready. At second15 the selected endpoint count is zero. Those facts narrow the investigation toward the route rather than proving the application process crashed.

Record observation time separately from event time when logs arrive late. Keep the request path, timeout and relevant object generation/version so that two readers can compare the same operation. Avoid copying tokens or unbounded logs. A small exact field extract often explains the failure better than a large undifferentiated dump.

A good baseline includes a successful application response and the expected selection graph before the fault. Without that control, an after-fault timeout could be an old defect. The experiment should have one declared fault so the causal story is interpretable; if another failure appears, stop and report the confounding condition.'''),
('Test hypotheses with minimal observations','''Hypothesis1: the application crashed. Inspect Ready state, termination/restart evidence and the fixed application observation path. Hypothesis2: the Service selects no intended Pods. Compare its selector with Pod labels and observed EndpointSlices. Hypothesis3: the selected backend port is wrong. Compare Service port/targetPort with the container named port. These are distinct checks, not a generic restart ritual.

In the supplied trace, the selector became missing and endpoints fell to zero while Pod readiness remained healthy. Restoring the last verified selector is the minimal repair consistent with the evidence. Use the recorded UID and a current conditional update to avoid overwriting another actor's changes or mutating a replacement object.

After repair, observe endpoints and the ordinary Service response again. A successful API update only says the desired change was accepted. The end-to-end observation closes the incident, while the timeline supports the causal explanation. If the response remains wrong, preserve that result and continue from evidence instead of declaring victory from an update exit code.'''),
('Keep fault injection bounded','''The host operation must know how to restore its own change, including on cancellation or deadline. It should stop if the target UID changes or unrelated state would be affected. Do not broaden the fault into a node outage, policy deletion or credential change to make the lesson more dramatic.

The post-incident review explains contributing conditions and detection gaps without inventing a root cause unsupported by the trace. A finite recovery can validate this selector-repair path; it does not prove resilience to every outage or that the failure will never recur.''')],
[
('Diagnose healthy Pods with no endpoints','''Before: selector app=hello,one ready Pod labeled app=hello,one endpoint,expected response. During: selector app=missing,same ready Pod,zero endpoints,timeout. Only the selector changed in the controlled experiment.''','The evidence supports a selector mismatch; a Ready Pod does not guarantee Service reachability.'),
('Close the repair loop','''Restore app=hello on Service UID svc-1 with a current version precondition. Then observe one selected endpoint and the expected payload through the Service at second30. A replacement Service UID svc-2 would stop the operation instead.''','The same owned route recovers. Identity replacement is a stop condition, not permission to apply the old repair blindly.')],
[
('Record the baseline','Capture selector,Pod label,endpoint count and fixed response before the fault.','A connected selection graph and successful application control.','A later failure needs a known earlier working path.','The baseline makes the experiment interpretable. It should identify the exact Service and Pod identities rather than only their names, because replacement during the exercise changes the scope of the repair.'),
('Form competing hypotheses','List crash,selector mismatch and target-port mismatch with a distinguishing observation for each.','Three specific evidence checks rather than a generic restart.','Ask what would be different if each cause were true.','The hypotheses connect symptoms to mechanisms. A Ready Pod weakens some crash explanations, zero selected endpoints points toward selection, and a populated endpoint with a wrong port suggests another branch. No single symptom proves every detail.'),
('Interpret the supplied timeline','Find the field change and the earliest observation supporting its effect.','Selector changes at10;zero endpoints observed at15 while readiness remains1.','Separate event time from observation time.','The controlled one-fault trace supports a narrow causal explanation. In a real incident, the same correlation would require checking concurrent changes and alternative causes rather than assuming the teacher-supplied synthetic control conditions.'),
('Apply the minimal bounded repair','Restore the verified selector only if the Service UID and current update precondition match.','Owned svc-1 repaired;replacement UID causes refusal.','Read current state before writing.','The repair should preserve unrelated fields and respect optimistic concurrency. A stale whole-object replacement risks undoing another legitimate change, while a name-only update risks modifying an unrelated replacement.'),
('Verify application recovery','Read endpoint selection and the ordinary Service response after the repair.','One endpoint and expected payload,with actual timestamps if live.','API success is not the serving result.','This check demonstrates the route works again for the observed request path. If the response still fails, the incident remains open even when the update command succeeded or the Pods were Ready throughout.'),
('Write the review and stop conditions','Summarize cause,evidence,repair,unrelated-state preservation and remaining uncertainty.','A timestamped bounded incident packet with no unsupported broad resilience claim.','Include cancellation and restoration behavior.','The review should teach how the failure was detected and repaired, and where the experiment stops. It should preserve evidence of a failed or cancelled repair rather than converting every exercise into an assumed success story.')],
hello(True),
'''
import json
from pathlib import Path

def main():
    events=json.loads((Path(__file__).resolve().parents[1]/'fixtures/k8s-040-timeline.json').read_text())
    assert [e['seconds'] for e in events]==sorted(e['seconds'] for e in events)
    assert len({e['service_uid'] for e in events})==1
    assert events[0]['response']=='expected' and events[1]['response']=='timeout'
    assert events[2]['ready_pods']==1 and events[2]['endpoints']==0
    assert events[-1]['endpoints']==1 and events[-1]['response']=='expected'
    print('k8s-040 synthetic selector incident trace passed; no fault injected')

if __name__ == "__main__":
    main()
''',capability='one fixed host fault with UID-bound restoration and timestamped application evidence',refs=['[Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)','[Debug running Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/)'])

recovery={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'recovery-plan'},'data':{'start':'declared service interruption','finish':'application response and independent restored marker pass','rto_seconds':'120','rpo_seconds':'30','scope':'synthetic immutable marker rehearsal'}}
author(41,
'''A recovery objective is a target, and a recovery measurement is an observation. Recovery Time Objective, or RTO, sets an acceptable duration for restoring the defined service. Recovery Point Objective, or RPO, sets an acceptable data-loss window. A drill must define start, finish and data reference points before it can compare observations with those objectives.

For this synthetic drill, interruption begins at12:00:00Z. The application and independently restored marker both pass at12:01:30Z, giving90seconds of observed recovery time. The source's last durable marker was timestamped11:59:50Z, while the latest restored durable marker is11:59:30Z, giving a20-second loss boundary under this example's timestamp assumptions. With targets120seconds and30seconds, these observed measures meet the two targets.

These calculations do not establish database transaction consistency or prove that no record outside the markers was lost. The immutable marker fixture makes a narrow data contract measurable. A Ready Pod at12:00:40Z is an intermediate milestone, not the finish when the marker and ordinary service path are still unverified.''',
[
('Define clocks, milestones and units','''Use UTC timestamps with explicit offsets or a monotonic elapsed timer for duration measurements. Do not subtract mixed local time strings across a daylight-saving transition. Record whether the start is fault injection, detected impact or incident declaration; these choices produce different measures. The runbook must choose one definition and keep it consistent.

Finish means the declared application and data acceptance criteria have both passed. Pod scheduling, Ready state, successful restore command and open TCP port can be useful intermediate milestones, but none automatically satisfies the whole service contract. If data verification finishes after application reachability, the later required check determines the measured finish.

For the RPO example, compare the source last durable data point with the restored last durable point. The difference estimates the data-loss time boundary for the represented sequence. Backup completion time alone can be misleading: a backup finishing at noon may contain data only through an earlier point. Data lineage and durability semantics matter.'''),
('Write a runbook another person can execute','''A reviewable runbook names the exact owned target, required host capabilities, inputs, operation order, expected observations, stop conditions and rollback/cleanup. It distinguishes privileged host steps from learner observations. Each step should explain why it exists, so a missing prerequisite is diagnosed rather than bypassed.

The negative control deliberately omits the independent marker verification. The application responds and the Pod is Ready, but the finish gate remains false. This tests whether the runbook can reject an attractive incomplete result. A runbook that records success at the first green signal is measuring a narrower objective than it claims.

During a live drill, preserve actual timestamps and failed attempts. Do not replace observed durations with the planned schedule. If the host lease expires or a required backup is unavailable, stop and report the missing evidence. Renewing a lease or reprovisioning a destination is a new controlled operation, not an invisible continuation under stale credentials.'''),
('Interpret objectives without overstatement','''Meeting an objective once is a useful rehearsal result, not a guarantee that every future incident will recover within the same duration. Report the tested fault,data size,environment and operator procedure. Repeatability and broader failure coverage require additional independent drills.

Do not export private backups or credentials to make the evidence packet self-contained. The packet can include synthetic marker hashes,timestamps,operation receipts and protected backup references while leaving sensitive payloads under the host's access and retention policy.''')],
[
('Calculate the two measurements','''Start12:00:00Z;finish12:01:30Z gives90seconds. Source durable point11:59:50Z;restored durable point11:59:30Z gives20seconds. Targets are RTO120seconds and RPO30seconds.''','Observed90<=120 and20<=30 meet the stated synthetic targets,assuming the milestone and durability definitions are valid.'),
('Reject a missing verification step','''At second40 the Pod is Ready. At second60 the service responds. The marker hash has not been read. The finish predicate requires service_ok and data_ok,so the drill remains incomplete.''','No finish time is claimed until both required observations exist. Ready or service success alone cannot close the data recovery objective.')],
[
('Define start and finish','Write the exact interruption start and required final gates.','A fixed start definition and application+data finish predicate.','Choose definitions before measuring.','The duration has meaning only relative to its milestones. Changing start from failure to detection after the drill can make the reported recovery seem faster without changing the system behavior, so definitions must remain explicit.'),
('Compute observed recovery time','Subtract12:00:00Z from12:01:30Z in seconds.','90seconds,compared with target120seconds.','Use timezone-aware timestamps.','The elapsed time includes all required restoration and verification work in this definition. A Pod-ready milestone at40seconds is useful diagnostic detail but cannot substitute for the later complete acceptance time.'),
('Compute the data-loss boundary','Compare source11:59:50Z with restored11:59:30Z.','20seconds,compared with target30seconds.','Use durable data points rather than backup finish time.','This metric describes the represented marker timeline. It does not infer record counts or transactional consistency. The report must state how each timestamp relates to durable application data.'),
('Run the missing-step negative','Evaluate service_ok true,data_ok false,Pod_ready true.','Recovery finish remains false.','A conjunction requires both inputs.','The negative control catches a runbook that prematurely records success. It is especially important because a responding application can be serving empty,old or incorrect data while looking operationally healthy.'),
('Review clocks and evidence','Identify timezone,clock source,backup reference,marker hash and host receipt for each milestone.','Every measurement is traceable without exporting sensitive backup contents.','Separate observed timestamps from planned times.','The evidence packet should allow another person to recompute the result and understand uncertainty. Missing clock synchronization or ambiguous durability definitions should be reported rather than hidden behind precise-looking numbers.'),
('Write the objective conclusion','Report target,observed result,failed controls and untested conditions.','A bounded drill conclusion with no universal recovery guarantee.','One rehearsal is one observation.','A useful conclusion explains whether the stated objective was met under the tested conditions and what prevented broader claims. It also records cleanup and any retained synthetic backup material so the drill is operationally complete.')],
[recovery],
'''
from datetime import datetime

def seconds(later,earlier):
    a=datetime.fromisoformat(later.replace('Z','+00:00'));b=datetime.fromisoformat(earlier.replace('Z','+00:00'))
    if a.tzinfo is None or b.tzinfo is None:raise ValueError('timezone required')
    result=(a-b).total_seconds()
    if result<0:raise ValueError('reversed milestones')
    return result

def finished(service_ok,data_ok):return service_ok and data_ok

def main():
    elapsed=seconds('2026-01-01T12:01:30Z','2026-01-01T12:00:00Z')
    loss=seconds('2026-01-01T11:59:50Z','2026-01-01T11:59:30Z')
    assert elapsed==90 and loss==20 and elapsed<=120 and loss<=30
    assert not finished(True,False) and finished(True,True)
    print('k8s-041 synthetic RTO/RPO arithmetic and missing-step control passed')

if __name__ == "__main__":
    main()
''',capability='qualified synthetic recovery drill with independent service/data acceptance and source timestamps',refs=['[Kubernetes debugging overview](https://kubernetes.io/docs/tasks/debug/)','[etcd recovery considerations](https://etcd.io/docs/v3.6/op-guide/recovery/)'])

cr={'apiVersion':'learning.ds60sqlpy/v1','kind':'LessonReport','metadata':{'name':'hello-report'},'spec':{'message':'reviewer','replicas':2}}
author(42,
'''The final capstone is a reviewable release and recovery story. A policy-compliant custom resource expresses intent; a qualified controller creates owned child resources; the application responds correctly; the data contract holds; a bounded incident is diagnosed and repaired; and the owned environment is cleaned without disturbing unrelated resources. No single green status represents that entire chain.

Use the LessonReport API from k8s-029 and the reconciliation contract from k8s-030. The host must supply the exact CRD/controller,admission,metrics,traffic and storage/recovery capabilities used by the selected scenario. The normal browser adapter does not provide them. Begin with the complete offline evidence packet and explicitly mark live gates unavailable until their corresponding capability receipts exist.

The learner acts as both implementer and reviewer: first predict the expected observations,then compare actual evidence,then challenge the weakest conclusion. The capstone is not a license to install arbitrary operators,change cluster policy or choose another context. Privileged actions remain fixed host operations in an exclusive owned lease,with separate receipts and stop conditions.''',
[
('Design the release packet before execution','''The packet starts with desired manifests,rendered artifact hashes,qualified image identity,prerequisite capability receipts and exact cluster/namespace ownership. It states which source fields are learner-controlled and which host identities are fixed. A manifest accepted by a schema is only the first gate.

Next define controller convergence: expected parent UID/generation,owned child graph,observed generation and application marker. Define admission and authorization controls separately,including one policy-specific denial and one permitted request. Define finite release samples and the rollback selector or desired-state restoration point. Do not turn a read-only signature check into an assumed cluster enforcement guarantee.

For autoscaling or storage,include only the scenario's qualified capabilities. An HPA source without metrics is not a completed scaling activity. A PVC object without a verified marker is not durable-data acceptance. If a capability is missing,the packet should make that gap visible instead of silently substituting a toy model for live execution.'''),
('Connect incident response to recovery objectives','''Choose one teacher-selected,host-allowlisted fault with a known restoration procedure. Capture the pre-fault baseline and preserve a timestamped investigation. The learner must explain why the selected observation distinguishes hypotheses and why the repair is scoped to the observed cause.

If the scenario requires restoration,measure recovery using the definitions from k8s-041. Keep service acceptance,data hash and durability points distinct. A repaired route with wrong data fails;correct data behind a broken Service also fails. The negative control should omit one required gate and prove the final acceptance function rejects the incomplete packet.

After recovery,review authorization and ownership again. Operational pressure is a common reason to widen permissions or bypass policy. This capstone succeeds only if the recovery story preserves the declared boundary or explicitly records a controlled host action with its own authorization and receipt.'''),
('Close the lifecycle and defend the evidence','''Cleanup removes only resources owned by the lease and recorded operation,using UID-aware checks. Retained claims or backups need an explicit policy and protected location. The host releases its exclusive cluster only after finalizers,finite Jobs and data-retention decisions are resolved. A cleanup failure is an outcome to report,not a line to omit.

The final review distinguishes source correctness,offline examples,API acceptance,controller convergence,application/data behavior and lifecycle cleanup. It states the exact versions,architecture and finite observations. A small synthetic capstone does not prove production HA,arbitrary-code isolation,exactly-once external side effects or reliable recurring operation.

A reviewer should be able to point to the evidence for every claimed gate and identify every unavailable capability. That is the practical meaning of a defensible platform change: the conclusion is as specific as the measurements that support it.''')],
[
('Trace one intended release','''LessonReport hello-report requests reviewer and2 replicas. The packet records parent UID p1,generation3,child owner p1,observedGeneration3,two ready replicas and four reviewer responses. These are synthetic teaching values until read from the qualified runtime.''','The joined fields form a coherent convergence hypothesis. Copying them into a worksheet does not create a runtime receipt.'),
('Reject an attractive incomplete packet','''API pass,controller pass,application pass,authorization pass,recovery service pass,but data hash wrong and cleanup unknown. Even with every Pod Ready,the final gate fails. After independent data verification and owned cleanup receipts pass,the complete synthetic packet can be accepted.''','All required gates must have evidence. Missing or failed data/cleanup rows cannot be replaced by a successful application request.')],
[
('Prepare the capability and ownership packet','List exact runtime capabilities,versions,source hashes and owned identities for the selected scenario.','Every requested live action has a qualified capability or an explicit unavailable row.','Do not infer capabilities from manifests.','The packet prevents execution assumptions from being hidden in prose. A CRD,controller,policy,metrics path or storage driver must actually exist under the declared host contract before its live outcome can be claimed.'),
('Defend desired state and admission','Review the custom resource and capture permitted and policy-denied controls.','Schema,authorization and admission conclusions remain separate.','Keep the negative request valid except for the intended policy violation.','This makes each control interpretable. A local parser rejection is useful but cannot stand in for server policy enforcement,while an accepted custom resource still requires a functioning controller before it produces a workload.'),
('Prove owned convergence and release behavior','Join parent generation,child ownership,readiness and finite application samples.','Current-generation owned resources serve the expected marker through the intended route.','A status boolean without identity/generation is incomplete.','The joined evidence rules out several false positives,such as stale readiness or a response from the wrong backend. The finite sample remains bounded evidence and does not establish an exact traffic ratio or unlimited reliability.'),
('Investigate one bounded incident','Record baseline,fault,symptom,hypotheses,minimal repair and post-repair response.','Timestamped causal explanation with exact target and cancellation/restore behavior.','Use one controlled fault and preserve alternatives.','The investigation should show why the repair follows from observations. Restarting or deleting broadly would make it harder to distinguish the cause and could violate the owned scope even if the symptom temporarily disappeared.'),
('Measure service and data recovery','Apply the stated RTO/RPO definitions and missing-data negative control.','Independent service/data gates and recomputable source timestamps/hashes.','Ready alone is insufficient.','The recovery packet must reject a serving application with the wrong restored marker. It should also state the immutable synthetic-data assumptions so the reviewer does not mistake the exercise for a transactional database recovery proof.'),
('Complete cleanup and review limits','Collect UID-aware cleanup/release receipts and defend each remaining claim.','No unrelated resources removed;missing or failed gates remain visible.','An unknown cleanup row is not success.','The final handoff should make the environment lifecycle auditable and retain only permitted synthetic evidence. A concise limitation statement is part of technical accuracy,because the tested platform slice is smaller than a production Kubernetes reliability or security guarantee.')],
[cr],
'''
REQUIRED=('capability','api','authorization','admission','controller','application','data','recovery','cleanup')
def accept(packet):return all(packet.get(key)=='pass' for key in REQUIRED)

def main():
    complete={key:'pass' for key in REQUIRED}
    assert accept(complete)
    for key in REQUIRED:
        assert not accept({**complete,key:'unavailable'})
        assert not accept({k:v for k,v in complete.items() if k!=key})
    assert not accept({**complete,'data':'wrong-hash','cleanup':'unknown'})
    print('k8s-042 synthetic all-gates capstone passed; no advanced host operation executed')

if __name__ == "__main__":
    main()
''',capability='exclusive integrated platform/controller/policy/metrics/traffic/storage/recovery lease',refs=['[Kubernetes controllers](https://kubernetes.io/docs/concepts/architecture/controller/)','[Kubernetes security overview](https://kubernetes.io/docs/concepts/security/overview/)','[Kubernetes application troubleshooting](https://kubernetes.io/docs/tasks/debug/debug-application/)'])
