# Systems teaching content status

> Support boundary: this file retains historical implementation evidence. The
> supported product runs in Linux Docker containers, with Windows through WSL 2.
> Native Windows ACLs/backends and native executable builds are not supported
> targets or release gates. Current checks are defined in [validation](../validation.md).

## Current checkpoint,23 October2026

C++ and Kubernetes each have all42 planned IDs authored with exact direct prerequisites. C++ has38 added chapters plus the four preserved pilots. Kubernetes has38 added chapters plus its four preserved pilots. Canonical per-course lessons.json files remain the actual inventories. Scala/Spark completion remains coordinated separately by the integration owner.

## C++ depth and executable examples

The38 added C++ guides now contain76 independent copy-runnable worked programs,each with its own explicit standard headers,one main,checks and recorded expected output. Fragment-only examples are replaced. Topic-specific expansions explain mechanisms,lifetime/state traces,wrong approaches,edge cases and diagnostic evidence;the repeated generic Verify/hint wording and repeated syntax-as-pitfall paragraphs were removed. Internal publication labels are kept out of the learner-facing openings. The original pilots retain their substantive teaching bodies,with stale future-workspace/source claims corrected.

All42 guides currently contain47,259 prose words excluding fenced blocks,54,719 total words. Counts describe the snapshot,not a quality proof. cpp-007 now covers size versus capacity,reserve versus resize,reallocation and iterator invalidation,half-open ranges,accumulator type,multiplicity and the two-phase unique/erase contract,with safe complete programs. Concurrent chapters distinguish startup,publication,cancellation,joining,queue closure,atomic ordering,future errors and accepted/completed/cancelled/failed accounting.

Portable inputs live under courses/cpp/authoring/depth/. build_depth.py regenerates the38 updated guides/explanations and76 examples without changing official executable references or learner pads. A repeated build produced zero changed artifacts. expected_outputs.json remains an independently recorded execution oracle. Historical scratch reference generators should not be rerun for prose changes because the official parsers/capstones contain subsequent reviewed corrections.

The shared compile-and-run.md covers main.cpp,text/object/executable/data distinctions,compiler flags,exit status,stale binaries,relative paths,compile versus link failures and the one-translation-unit browser boundary. Its new Docker-only CMake route uses the prepared image,an explicitly new learner-owned project copy,a narrowly scoped durable bind mount,nonroot execution,no network,and separate configure/build/CTest/install phases in POSIX and PowerShell. No host compiler,CMake or Ninja is required for that route. Both multifile and record-library fixtures have genuine local install/export rules. Those exact Docker commands are now qualified by this author under the explicit bounded-container authorization described below.

Focused C++ guide/reference/system regression: **218 passed in39.50seconds**. All76 worked programs compiled and ran on the existing Apple Clang host. The suite also retained41 official references,parser/boundary mutation controls,real missing/duplicate-definition link failures,CLI budgets/errors and independent library consumption. The NDEBUG worked case was compiled separately and produced its distinct expected observation. Ruff passed both new content test files,and strict MyPy found no issues in them. git diff --check passed the owned paths.

The integration owner separately rebuilt the C++ image and reported all41 executable references passing through its baked current adapter. Receipt:work/cpp-final-image-acceptance.jsonl. That is actual image execution evidence,distinct from the native worked-program tests and the separately qualified Docker project commands. Other platforms/architectures and optional sanitizers/debuggers remain separate rows.

## Actual Docker project and worked-program qualification

On2026-10-23 the exact documented configure/build/CTest/install phases passed for fresh copies of both multifile and record-library. The copies live only under the task-owned work/cpp-project-proof directory,with spaces in their mount paths. Actual host UID503/GID20 was used;durable CMake output remains owned by UID503. Containers used no network,no image pulls,a read-only root,nonroot identity,dropped capabilities,no-new-privileges and only their fresh project bind mount. Every task-owned container was removed;final readback found zero remaining proof containers.

Prepared image:ds60sqlpy-worker-cpp20:0.3.0,immutable ID sha256:8849555fc0dd4c18131f8baaaef55e33ad3efbdf9562609ecd324bf62fdb7026,Linux arm64. Actual tools:GCC14.3.0,CMake3.28.4,Ninja1.11.1. Receipt:work/cpp-project-current-acceptance.json includes tutorial/source hashes,each phase command/output/status,installed artifact hashes and cleanup. The installed math_check ran inside Docker and printed add=5 subtract=2. A fresh consumer also imported the installed record-library exported target,passed its own CTest,was installed,and ran inside Docker with accepted=2 rejected=2. Native host compiler/CMake were not used for these workflows.

All76 new complete worked programs then compiled and ran inside the same image with C++20,debug flags,warnings and pthread support. Every stdout matched its independent recorded expectation;all exit statuses were0,with no compiler warnings or runtime stderr. The bounded batch took14.383seconds. Receipt:work/cpp-worked-programs-docker-acceptance.json records every source hash,compiler command and output comparison. Current repository source hashes still match both receipts.

The first proof harness expected an extra total field from the installed record consumer,although its documented output contains only accepted/rejected counts. That assertion was corrected and fresh project copies were fully rerun. No course binary or source behavior was changed to make the proof pass. Windows PowerShell/native Windows file sharing and non-arm64 runtime rows remain unqualified by this macOS-hosted Linux-container result.

## Kubernetes completion and runtime boundary

See [the detailed Kubernetes status](kubernetes-content-status.md). All42 lesson bodies are complete,with12 bounded YAML sources and30 explicit reading/host-lab worksheets. The38 new offline references pass with socket access denied. Real manifests cover configuration,Jobs,probes,RBAC,storage,network policy,Gateway,Kustomize,Helm,CRDs,admission,disruption,autoscaling,traffic,concurrency,recovery and capstones. The normal adapter remains intentionally closed;advanced host capabilities are stated rather than simulated as working browser operations.

The dedicated completion/runtime regression passed186 tests in3.91seconds. A post-regeneration content/system subset passed99 tests in3.56seconds,and portable regeneration changed zero artifacts. Actual local Kustomize rendering matched both overlays. Actual offline signature verification accepted a synthetic original and rejected a tampered copy. Helm is not installed on this host,so no actual Helm render is claimed.

The integration owner's fresh Linux aarch64 contract-2 runtime qualification passed12 expected-outcome cases,including ConfigMap environment/file checks,finite tasks and startup probes. Classroom API execution succeeded in14.493seconds. SIGTERM during an active operation reduced five owned resources to zero in5.078seconds with worker exit0. The exact owned cluster was released and broker stopped. These receipts do not qualify advanced storage/CNI/controller/Node/backup operations or every host platform. The beginner guide explains preparing immediately before Run because the private lease lasts15minutes,and releasing/repreparing after expiry.

## Focused instructional review after qualification

Corrected C++23 prose to identify its platform-int ABI rather than imply a fixed-width wire representation,and to explain status0 success,status1 null-output rejection and status2 overflow with output preservation. Executable C++ sources are unchanged and match the Docker receipt hashes. Corrected NLP16's teacher-forcing explanation:parallel target-position training applies to masked-attention decoders;teacher forcing does not remove an RNN's sequential hidden-state dependency. Its executable references are unchanged. The NLP README still had an in-progress introduction and was reported to its owner for shared entry-point cleanup.

Remaining concrete limitations are visible to learners:the Docker project proof covers POSIX invocation on a macOS-hosted Linux arm64 engine,not native Windows PowerShell/file-sharing behavior;Kubernetes advanced live exercises require separate qualified capabilities;Kubernetes19 supplies a dummy Secret and reload trace but still relies on a teacher-provided consuming workload for an actual projected Secret update experiment;and NLP15/16 teach exact small mechanisms without pretrained-model quality claims. These are not silently counted as live acceptance. Some C++ concurrency examples remain densely formatted despite complete compile/run coverage;an additional readability-only pass would improve scanning without adding behavior.

## Remaining coordination

The integration owner handles generated catalogs,readers,dashboard discovery and broad acceptance. C++ Docker project-command and76 worked-program qualification are complete,with receipts below. Scala/Spark remaining lesson bodies are not silently counted complete here. No tool installation,image build,engine configuration change,cluster mutation,learner-volume access,Git staging,commit or push was performed by this content author. The explicitly authorized C++ qualification used only task-owned short-lived offline containers. The historical records below describe earlier snapshots only and are superseded by this checkpoint for current content counts and fixture version.

## Earlier qualification history

Authored beta content covers cpp001-003 plus cpp009, spark001-003 plus spark013, and k8s001-003 plus k8s008. The IDs retain their hyphenated form in each course lessons.json. Each guide and explanatory solution carries six bounded exercises, two worked examples, concrete expected observations, hints and retrieval. Language learner sources use explicit numbered exercise comments; reading learners use response worksheets.

C++ and Scala pilots preserve direct prerequisites that may still be unpublished. C++004-008, Kubernetes004-007 and Scala004-012 are not silently treated as completed. Course metadata is separate from active catalog publication. Verification IDs remain null until a reviewed checker and actual qualification receipt exist.

Spark013 includes paired Scala/PySpark source and reference, one explicit seven-row JSON fixture, a runnable standard-library oracle and independent typed checker sources. The canonical paid metrics are6 rows,4 observed amounts and250 cents. Scala/PySpark compilation/execution has not been performed by content authoring. Version tuples remain subject to the actual prepared profile receipt.

C++ references can be checked with an existing native compiler; the trusted ownership harness tests14 independent value contracts after the worked-example entry point. No compiler is installed by these lessons. CMake/CTest is a separate optional manual path and is not inferred from a direct compiler invocation.

Kubernetes files use only ds60sqlpy-k8s-fixture:0.1.0, imagePullPolicy Never and workload token mounting disabled. The host operation owns the fixed hello resource identity, scoped credentials, target binding and cleanup. Static YAML authoring is not cluster acceptance. The Service client checks /version independently from the /ready probe. No ambient context, cluster creation or image build occurred during content authoring.

Remaining implementation gates include full prerequisite bridge authoring, additional host/platform qualification and publication review. The scoped Kubernetes adapter/host preparation and the limited live proof below are implemented. Test results and exact runtime claims must be appended only after their real checks complete.

## Executed content checks

On2026-10-22, the original repository's systems-content and shared link checks passed26 tests in2.51 seconds using4 grouped workers, with zero skips. AppleClang21.0.0 on Darwin arm64 compiled/reran the cpp002 and cpp003 references and the cpp009 trusted14-check harness. The learner stubs and a deliberately zero-dropping filter were rejected. The independent Spark standard-library oracle, Python syntax and static YAML fixture contracts passed. This does not qualify JVM/Spark execution, CMake/CTest, Windows/Linux native compilation or a Kubernetes cluster.

The first Kubernetes app adapter is one-shot: fixed hello Deployment plus optional Service, bounded controller/backend/client checks, then cleanup of only recorded matching UIDs. The cluster lease remains for explicit host release. Pilot rolling-update, Pod-deletion and second-Service tasks remain scoped manual/teacher exercises until typed stateful operations exist. The initial app Run does not claim to grade every task or its explanation.

Root runtime qualification subsequently confirmed actual Docker typed positive and bad-starter rejection for the C++ ownership and both Scala/PySpark row pilots. The canonical cpp009 and spark013 metadata now selects their registered verifiers. Spark013 exposes a PySpark variant with a separate saved pad identity; it does not create another lesson ID. Foundation lessons retain null verification IDs, so process success alone is not automatic grading. The design's4.2.0 compatibility candidate must not be confused with a prepared worker's actual version receipt.

## Scoped Kubernetes implementation checkpoint

The source now includes the strict one-shot handler, explicit pinned host preparation/release, separate fixed HTTP fixture and optional Compose companion. See the [preparation guide](../../docker/kubernetes/README.md). The final focused content/Kubernetes/link suite passed62 tests in4.10 seconds with zero skips; Ruff and the handler/host-companion type checks passed. An independent agent reproduced the repaired parent-alias, create-commit cancellation, create-commit timeout and foreign-nonce cases. No actual engine/cluster mutation occurred in these checks. Live Linux node/worker qualification remains required for the owned adapter; native Windows ACL execution is outside the support contract.

## First live Kubernetes boundary

A root-owned Linux aarch64 kind session subsequently passed the actual k8s008 Deployment plus Service operation: two Ready Pod identities matched EndpointSlice backends, the in-cluster version client passed and owned cleanup was confirmed in42.48 seconds. Deployment-only k8s003 passed in35.97 seconds. The pilot metadata now selects `k8s-readiness-v1`; the six-task course's stateful/manual activities remain outside that one-shot checker. The initial unready15-second rehearsal exposed an exhausted cleanup deadline, which was repaired with a fresh independent15-second cleanup reserve, a20-second shutdown wait and30-second Compose stop grace. Final rebuilt-image negative/cancellation acceptance is recorded separately by the root. The source regression suite passed58 Kubernetes/content tests in3.93 seconds, including a real child SIGTERM protocol and simulated deadline exhaustion. Strict MyPy covered the handler and both owned test files. No native Windows or other architecture qualification is inferred.


The rebuilt final Kubernetes worker subsequently passed all seven live Linux aarch64 acceptance cases: healthy Service/client, Deployment-only, unready bounded timeout, wrong-selector bounded timeout, namespace escape rejection, privileged-source rejection and cancellation. Every applicable case confirmed owned cleanup. During an actual SIGTERM while verifying, four observed owned resources became zero, the worker exited zero and shutdown took 6.837 seconds. The immutable-ID host release is a separate final rehearsal; native Windows, other host architectures and stateful manual lesson tasks remain separate acceptance rows. Exact image/resource IDs are retained in the root's private qualification receipts.
