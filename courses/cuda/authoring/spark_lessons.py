"""Original GPU Spark specialization with portable semantic reference models."""

from python_lessons import LESSONS, add

START = len(LESSONS)

add(
    49,
    "RAPIDS, cuDF and the Spark execution boundary",
    """RAPIDS is an ecosystem of GPU data-science components. cuDF is a columnar dataframe library; the NVIDIA cuDF plugin for Apache Spark, formerly named RAPIDS Accelerator for Apache Spark, integrates with Spark's execution engine. Scala and PySpark SQL/DataFrame expressions can reach the same optimized physical plan. The plugin targets supported SQL/DataFrame operators, not every line of Python or Scala in an application.

A Python loop inside an ordinary UDF does not become a CUDA kernel because the plugin is enabled. Separate GPU-aware UDF and machine-learning integrations have their own package and execution contracts. The first decision is therefore about where the work lives: a single-process dataframe, Spark's distributed SQL engine, a UDF process or a framework training job. This course keeps the existing CPU Spark workers usable and treats GPU Spark as an explicitly prepared external environment.""",
    "A DataFrame filter followed by groupBy sum is visible to Catalyst as declarative relational operations. A Python UDF that performs an opaque operation may require a CPU boundary or a separate supported integration.",
    "Grouping values [2,4,6,8] by accompanying labels A,A,B,B is the same relational objective in Scala and PySpark. Equivalent output is necessary, but GPU operator evidence still comes from the executed plan.",
    "Classify four execution layers;Explain cuDF versus plugin;Identify an opaque UDF;Write equivalent Scala and PySpark expressions;Define CPU-only progress;List real GPU evidence",
    "Separate local dataframe Spark operators UDF processes and training;The plugin integrates cuDF with Spark planning and execution;Arbitrary host code is not automatically accelerated;Use the same schema null policy and aggregation;Run semantic references and inspect teaching plans;Require compatible GPU runtime executed operator plan metrics and equal results",
    """rows=[("A",2),("A",4),("B",6),("B",8)]
totals={}
for key,value in rows:
    totals[key]=totals.get(key,0)+value
assert totals=={"A":6,"B":14}
print("CPU Spark semantic oracle:",sorted(totals.items()))""",
    "Grouped totals A 6 and B 14; no GPU execution claimed.",
)

add(
    50,
    "Compatibility is a tested matrix, not a jar name",
    """A working GPU Spark installation matches Spark patch line, Scala binary version, Java runtime, plugin release, CUDA native-library variant, host CPU architecture, Linux userspace, NVIDIA driver and GPU architecture. Spark distributions can carry vendor patches, so a nominal Spark version alone may not establish binary compatibility. The published support matrix and release notes must be checked for the exact selected release.

Record artifacts by version and checksum and keep a known CPU baseline. Do not copy a development SNAPSHOT from a documentation example into a beginner setup. The Scala suffix selects a binary ecosystem; the CUDA classifier selects native-library packaging and is not a substitute for a compatible host driver. A local ARM Mac image architecture and an NVIDIA Linux host architecture are separate concerns. This lesson's compatibility worksheet deliberately does not invent a universally supported version combination.""",
    "A jar built for Scala 2.12 should not be assumed compatible with a Scala 2.13 Spark distribution. A NoSuchMethodError can indicate binary integration trouble before useful GPU work starts.",
    "A package can load on one Linux host but fail to initialize native libraries on another architecture. Version ledger completeness and actual smoke execution are both required.",
    "List matrix axes;Identify a Scala mismatch;Distinguish toolkit and driver;Record artifact provenance;Design a CPU rollback;Define compatibility acceptance",
    "Include Spark Scala Java plugin CUDA architecture driver GPU and OS;Match the declared binary line;The driver is a host/runtime capability;Use release version checksum and primary source;Keep ordinary Spark environment and query;Require import startup bounded query and expected result on the selected host",
    """def compatible(spark_scala,jar_scala,host_arch,jar_arch):
    return spark_scala==jar_scala and host_arch==jar_arch
assert compatible("2.13","2.13","x86_64","x86_64")
assert not compatible("2.13","2.12","x86_64","x86_64")
print("CPU compatibility worksheet: mismatched Scala binary line rejected")""",
    "Illustrative Scala/host-architecture predicate rejects mismatch; not a full compatibility probe.",
)

add(
    51,
    "From Catalyst plans to actual GPU operators",
    """Catalyst represents a query as logical operations, applies transformations and selects physical implementations. Explain output shows what Spark planned, while an executed SQL plan and metrics show what happened for an action. Adaptive Query Execution can change a physical plan using runtime statistics, so the initial plan may differ from the final executed plan.

The plugin replaces supported physical operators with GPU-capable implementations and inserts transitions where needed. Use the release's explain diagnostics to understand why an operation stayed on CPU. Seeing one GPU node does not establish that the entire job is accelerated. Conversely, a CPU metadata or coordination node can coexist with useful GPU computation. Interpret the plan by operation and stage, then compare measured completed work.""",
    "A synthetic plan Scan -> Filter -> Aggregate can contain a GPU filter and aggregate with a CPU-side source boundary. Count transfers and conversions rather than labeling the whole query GPU-only.",
    "A count action triggers execution; constructing a DataFrame alone is lazy. A plan printed before an action does not contain the same runtime evidence as the completed SQL execution view.",
    "Draw logical versus physical plan;Mark GPU candidate nodes;Locate transitions;Explain lazy evaluation;Compare initial and final AQE plan;Choose operator metrics",
    "Logical nodes describe intent and physical nodes choose execution;Use actual plugin names from the selected release;Each transition may copy or change representation;An action is required for work;Inspect the final executed plan;Use rows batches time spill and device observations together",
    """plan=[("scan","CPU"),("filter","GPU"),("aggregate","GPU"),("collect","CPU")]
transitions=sum(plan[i][1]!=plan[i-1][1] for i in range(1,len(plan)))
assert transitions==2
assert sum(device=="GPU" for _,device in plan)==2
print("Synthetic plan worksheet:",transitions,"CPU/GPU transitions")""",
    "Synthetic plan has two GPU nodes and two backend transitions.",
)

add(
    52,
    "Supported operations, fallback and semantic boundaries",
    """Support depends on operator, expression, dtype and configuration. A supported aggregate on one type may fall back on another expression or precision requirement. CPU fallback means a compatible plugin environment selects CPU execution for an unsupported part of a query. It does not mean a missing NVIDIA GPU can always initialize the enabled plugin and run normally.

For CPU-only study, use ordinary Spark with the GPU plugin disabled or absent. For GPU study, inspect supported-operator documentation for the chosen release and capture reasons such as NOT_ON_GPU diagnostics. A mixed plan may pay row/columnar conversions and device transfers repeatedly. Do not force an incompatible operator merely to increase GPU coverage; preserve semantics and measure the whole query.""",
    "GPU aggregate -> CPU UDF -> GPU projection crosses the boundary twice around the UDF. Replacing the UDF with an equivalent supported expression might reduce transitions after parity tests.",
    "A machine with no GPU should use the CPU baseline configuration. This differs from a GPU machine where one unsupported expression falls back inside an otherwise valid plugin job.",
    "Classify fallback versus unavailable device;Find an unsupported expression;Count boundary costs;Rewrite an opaque function declaratively;Preserve edge semantics;Design a mixed-plan report",
    "Fallback is per supported execution environment;Consult operator type and expression rules;Include representation and transfer costs;Use built-in expressions only when equivalent;Test nulls overflow strings and timestamps;List each reason and observed transition",
    """states=[{"gpu_visible":False,"plugin_enabled":False},{"gpu_visible":True,"plugin_enabled":True,"cpu_operator":True}]
assert states[0]["plugin_enabled"] is False
assert states[1]["cpu_operator"] is True
print("CPU configuration worksheet: CPU baseline and GPU mixed plan are distinct")""",
    "CPU-only baseline and per-operator fallback are modeled separately.",
)

add(
    53,
    "Nulls, decimals, timestamps and equality contracts",
    """SQL semantics include null propagation, three-valued predicates, decimal precision/scale, overflow policy, timezone interpretation and string ordering. GPU and CPU results should be compared under the query's declared semantics, not by assuming every numeric column is a floating array. An empty aggregate and an aggregate of only null values can differ from a sum initialized to zero in Python.

Use explicit schemas and deterministic ordering for comparison. Floating aggregates may require a justified tolerance because reduction order can change; decimal and integer outputs often require exact equality under the selected SQL mode. Timestamp tests should name the session timezone and include boundary cases. Never hide a semantic mismatch by relaxing tolerance until the test passes.""",
    "COUNT (*) over [2, null,5] is 3 while COUNT (value) is 2. SUM (value) is 7 under skip-null semantics. The two counts answer different questions.",
    "Decimal 1.10 plus 2.20 should preserve the chosen decimal contract. A binary floating approximation is not a substitute for testing a decimal expression.",
    "Calculate both counts;Handle all-null aggregate;Compare decimal values;Name timestamp timezone;Choose float tolerances;Design ordered result comparison",
    "Row count 3 and non-null count 2;Follow Spark SQL null-result semantics;Use exact decimal type and scale;Set and record session timezone;Tie tolerance to dtype algorithm and scale;Sort by stable keys without erasing duplicate rows",
    """from decimal import Decimal
values=[2,None,5]
assert len(values)==3
assert sum(v is not None for v in values)==2
assert sum(v for v in values if v is not None)==7
assert Decimal("1.10")+Decimal("2.20")==Decimal("3.30")
print("CPU SQL-semantics oracle: rows 3, nonnull 2, sum 7, decimal 3.30")""",
    "Rows 3, non-null 2, sum 7 and exact decimal 3.30.",
)

add(
    54,
    "Columnar batches, Arrow and data movement",
    """Columnar execution groups values by column with accompanying validity and offset structures. Arrow defines interoperable columnar formats; it is not itself a guarantee of GPU residency or zero-copy across every process and device boundary. Variable-width strings need offsets and character storage, while nullable columns need validity information. A batch's byte size can vary greatly with its schema.

Spark's row-to-columnar and columnar-to-row transitions can add work around unsupported operators. Host-to-device and device-to-host transfers are further boundaries. Plan batches by bytes as well as row counts and include temporary decoded representations. Increasing batch size can improve amortization while raising peak memory and spill risk. Preserve schema and null behavior through every conversion.""",
    "One thousand float64 values occupy 8000 payload bytes, plus any null mask and metadata. One thousand strings can occupy widely different storage depending on lengths.",
    "A validity mask for nine rows needs at least two bytes at one bit per row. Treating null as numeric zero would erase information rather than merely change representation.",
    "Count fixed-width payload;Count validity bytes;Explain string offsets;Locate row-column transitions;Budget transfer payload;Design a conversion parity test",
    "Rows times element width;Ceiling rows divided by eight;Offsets identify boundaries in character data;Inspect the physical plan;Include values masks offsets and temporary copies;Compare schema row identity nulls and values",
    """rows,itemsize=1000,8
payload=rows*itemsize
mask=(9+7)//8
assert payload==8000 and mask==2
strings=["a","longer",""]
assert sum(len(s.encode("utf-8")) for s in strings)==7
print("CPU columnar ledger:",payload,mask,7)""",
    "Fixed payload 8000 bytes, nine-row mask 2 bytes, string characters 7 bytes.",
)

add(
    55,
    "GPU resources, executor ownership and task concurrency",
    """Spark schedules executor and task resources, while the plugin manages how many tasks may actively use an executor's GPU. CPU task slots, fractional GPU resource requests and GPU admission concurrency are related but distinct controls. A fractional task resource amount is a scheduling share; it does not physically partition VRAM or make each task own an isolated fraction of the device.

Follow the selected plugin release's executor-to-GPU mapping and Spark resource discovery requirements. Use an explicitly prepared GPU discovery mechanism and verify assigned addresses. Raising concurrent GPU tasks may improve overlap but multiply live batches and memory pressure. A controlled experiment changes one concurrency setting, records resource allocation and observes actual completed-query throughput and memory.""",
    "With an executor assigned one GPU and tasks requesting 0.25 GPU, resource accounting can admit up to four such tasks, subject to CPU slots and other limits. This is not four VRAM partitions.",
    "A plugin concurrency limit of two can restrict active GPU work even when Spark has four runnable task slots. The two controls answer different scheduling questions.",
    "Compute resource-share slots;Compare CPU and GPU limits;Explain VRAM nonpartitioning;Verify device addresses;Design a concurrency experiment;Describe oversubscription failure",
    "One divided by 0.25 gives four accounting slots;The effective bound includes all constraints;Scheduling fractions do not reserve fixed memory slices;Inspect explicit discovery and assignment;Hold query partitions and data fixed;Too many live tasks can spill or fail without any syntax error",
    """from fractions import Fraction
gpu=Fraction(1)
request=Fraction(1,4)
slots=int(gpu/request)
plugin_limit=2
active=min(slots,plugin_limit)
assert slots==4 and active==2
print("CPU resource model:",slots,"scheduled shares;",active,"GPU-active bound")""",
    "Four scheduling shares with a two-task plugin admission bound.",
)

add(
    56,
    "Memory pools, batch sizing and bounded spills",
    """GPU Spark uses device allocations for columnar batches, intermediate operators and workspaces, with host memory and disk potentially involved in spill behavior. The JVM heap is only one memory category. Reducing executor heap does not directly create VRAM, and increasing GPU task concurrency can raise simultaneous live memory even when each task fits alone.

A spill moves data to a slower tier to preserve progress under pressure. It is an operational behavior to measure, not an automatic failure or a free capacity extension. Record device, pinned host, pageable host and spill-disk budgets separately. Use small deterministic datasets for semantics and bounded representative data for performance; never deliberately fill a shared device or disk. Check plugin-specific memory settings against the pinned release.""",
    "Three active tasks each needing 2 GiB plus 1 GiB shared workspace require an illustrative 7 GiB live budget. Four tasks require 9 GiB and exceed an 8 GiB budget.",
    "A spill can allow completion while adding serialization and I/O cost. Comparing only kernel time misses the resulting end-to-end slowdown.",
    "Compute concurrent live memory;Lower concurrency;Separate JVM and device pools;Budget spill disk;Design safe batch changes;Interpret successful but spilling execution",
    "Add per-task live sets and shared state;Reduce simultaneous live demand;They are separate allocators and resources;Use explicit disposable paths and capacity;Bound rows and bytes before launch;Completion is valid but performance and storage behavior need reporting",
    """per_task,shared,capacity=2,1,8
assert 3*per_task+shared==7
assert 4*per_task+shared==9
safe=[tasks for tasks in range(1,5) if tasks*per_task+shared<=capacity]
assert safe==[1,2,3]
print("CPU memory budget:",safe,"safe task counts in the model")""",
    "One through three tasks fit the simplified budget; four do not.",
)

add(
    57,
    "Joins, skew and broadcast decisions",
    """A join matches keys across relations; duplicate keys multiply output rows. GPU acceleration cannot remove that semantic expansion. A broadcast join replicates a small side to workers, while a shuffle join redistributes records by key. Choice depends on estimated sizes, runtime statistics, supported operators and memory. Broadcasting a relation that only appears small in stale statistics can cause pressure.

Skew concentrates rows on a few keys, creating large partitions and long tasks. Salting or repartitioning is not automatically correct: a transformation must preserve intended join multiplicity and outer-join behavior. Inspect partition sizes, output cardinality and the final adaptive plan. Keep one simple CPU oracle with duplicate and missing keys to prevent a fast but incorrect rewrite.""",
    "Left keys [A, A, B] and right keys [A, A, C] produce four matches for A in an inner join. Expected cardinality is not the minimum of input lengths.",
    "If one partition holds 900 rows and nine others hold roughly 11, the maximum task dominates the barrier despite a small average partition size.",
    "Calculate duplicate join output;Add unmatched keys;Identify skew;Compare broadcast and shuffle;Design a safe rewrite;Inspect final AQE decision",
    "Multiply key multiplicities;Inner joins exclude unmatched keys while outer joins preserve defined null rows;Compare maximum and distribution not average alone;Broadcast replicates one side and shuffle redistributes both as needed;Preserve duplicates and null-key semantics;Capture executed plan after action",
    """left=[("A",1),("A",2),("B",3)]
right=[("A",10),("A",20),("C",30)]
joined=[(k,a,b) for k,a in left for r,b in right if k==r]
assert len(joined)==4
assert {k for k,_,_ in joined}=={"A"}
print("CPU join oracle:",joined)""",
    "Four A matches from two-by-two duplicate keys.",
)

add(
    58,
    "Shuffle, transport and network bottlenecks",
    """A shuffle redistributes records between tasks, often crossing executor and host boundaries. Its cost includes serialization or columnar handling, buffering, transport, disk and downstream processing. A GPU can accelerate supported local operators while the job remains limited by network or storage. Specialized shuffle managers and transports have their own compatibility, startup configuration and failure behavior.

Do not infer RDMA, peer-to-peer or GPUDirect capability from an installed library. Those paths require actual hardware, topology and runtime support. Establish an ordinary supported shuffle baseline, then qualify an optional accelerated path. Record bytes, partitions, transfer time, retries and spill. Preserve query semantics and avoid exposing network services or changing cluster-wide settings from an ordinary lesson pad.""",
    "Moving 10 GiB over an effective 1 GiB/s path has a 10-second payload lower bound before other costs. Halving a 100 ms local kernel cannot remove that bottleneck.",
    "Reducing shuffle volume through an equivalent pre-aggregation may help more than changing transport. The rewrite must preserve aggregate semantics, especially for nonassociative or stateful operations.",
    "Compute transfer lower bound;Identify local versus network time;Explain pre-aggregation;List transport qualification;Separate startup settings;Design a bounded shuffle comparison",
    "Bytes divided by effective bandwidth;Measure the complete stage;Combine only when mathematical semantics allow;Verify devices topology libraries and real traffic;Some shuffle choices require fresh executors;Use identical partitioned fixtures and capture bytes spills and output",
    """gib=1024**3
payload=10*gib
bandwidth=gib
seconds=payload/bandwidth
assert seconds==10
kernel_saving=0.05
assert kernel_saving/seconds<0.01
print("CPU shuffle bound:",seconds,"seconds before additional overhead")""",
    "Ten-second payload lower bound;50 ms kernel saving is below 1 percent of it.",
)

add(
    59,
    "AQE, partition sizes and a fair benchmark",
    """Adaptive Query Execution can coalesce partitions, change join strategy and respond to skew using runtime information. A GPU comparison must record the final executed plan, not only the initial configuration. Partition count changes task granularity, scheduler overhead, memory per task and available concurrency. There is no universal best count for every dataset and device.

Separate semantic smoke fixtures from performance datasets. Tiny data is excellent for correctness but often dominated by startup. Use the same input snapshots, query, output materialization, cache state and warmup policy for CPU and GPU comparisons. Report cold and warm runs, sample distributions and resource cost. Qualification estimates help select workloads; they are not measured speedups on the learner's hardware.""",
    "One million rows split into 100 equal partitions averages 10000 rows each. Reducing to 10 partitions raises the average to 100000 and may increase per-task memory.",
    "A warm GPU run reading cached data cannot fairly be compared with a cold CPU run downloading inputs. Label cache state or repeat under matched conditions.",
    "Calculate partition averages;Explain skew beyond averages;Capture final AQE plan;Define cache policy;Choose semantic and performance fixtures;Separate estimated and observed speedup",
    "Divide rows by partitions;Report tails and maximum sizes;Inspect after the action;Use equivalent cold or warm states;Tiny bounded correctness data and representative measured data serve different purposes;Predictions remain predictions until executed",
    """rows=1_000_000
assert rows//100==10000 and rows//10==100000
runs=[{"backend":"CPU","cache":"cold"},{"backend":"GPU","cache":"warm"}]
assert runs[0]["cache"]!=runs[1]["cache"]
print("CPU benchmark worksheet: unmatched cache comparison rejected")""",
    "Partition averages 10000 and 100000; unmatched cache states rejected.",
)

add(
    60,
    "Python UDFs, pandas APIs and GPU-aware ML boundaries",
    """Spark SQL expressions, Python UDFs, pandas UDFs, pandas API on Spark and GPU dataframe libraries are different execution surfaces. Arrow can improve interchange for vectorized UDFs without making their body GPU code. A GPU-aware UDF must explicitly manage supported packages, device assignment, batch size and transfers under a reviewed contract. Ordinary plugin enablement does not rewrite arbitrary Python algorithms.

GPU-accelerated machine-learning integrations such as Spark RAPIDS ML are separate from SQL operator acceleration. Estimator support, semantics and release compatibility need their own validation. A training job inside each partition can duplicate work or oversubscribe a device if resource ownership is unclear. Keep preprocessing, distributed SQL and training responsibilities explicit, and compare model quality as well as elapsed time.""",
    "A built-in multiplication expression is visible in the relational plan. A Python UDF returning x*2 may hide the same algebra behind a process boundary and block equivalent optimization.",
    "Calling a GPU library from every partition does not automatically coordinate multi-GPU training. Each task needs a defined device share and bounded memory contract.",
    "Classify four APIs;Replace an equivalent simple UDF;Explain Arrow limits;Define GPU-aware UDF ownership;Distinguish SQL and ML acceleration;Design quality parity tests",
    "Name SQL UDF pandas-style and local GPU dataframe surfaces;Use a built-in expression if null/type semantics match;Interchange format is not an execution device;Record assigned device batches and cleanup;They are separate integrations;Use same split target metric and preprocessing",
    """values=[1,None,3]
def expression(x):
    return None if x is None else x*2
expected=[2,None,6]
assert [expression(x) for x in values]==expected
print("CPU expression parity oracle:",expected)""",
    "Null-preserving expression produces [2, None,6].",
)

add(
    61,
    "GPU Spark on an explicitly owned Kubernetes cluster",
    """Kubernetes schedules pods onto nodes; an installed and configured device plugin advertises GPU resources to that scheduler. Spark's driver requests executors, and Spark's own resource discovery must agree with what each executor container can access. These are different layers. A pod resource limit alone does not prove the selected image, driver and native libraries can execute the Spark GPU plugin.

This is a manual external lab for a named disposable cluster and namespace. Never use ambient kubeconfig or expose a driver service publicly by convenience. Define service accounts, image provenance, node selection, resource limits, storage and cleanup before creating workloads. Docker Desktop on a Mac is useful for the CPU classroom, but it does not manufacture an NVIDIA GPU for Kubernetes. Observe pod placement and actual device visibility before a bounded query.""",
    "A cluster can have three nodes but only one advertising a compatible GPU. A GPU executor must land on the eligible node and see the assigned resource inside its container.",
    "A driver pod running successfully while executors remain Pending proves control-plane submission only. Inspect resource requests, events and image/runtime constraints before changing code.",
    "Draw scheduler layers;Name ownership boundaries;Diagnose Pending executors;Verify device visibility;Design private networking;Write scoped cleanup",
    "Kubernetes allocates pods and Spark allocates tasks;Use exact cluster namespace labels and job identity;Read events and resource availability;Run a bounded owned executor probe;Keep internal services private;Delete only resources created for this named lab and preserve requested logs",
    """nodes=[{"name":"cpu-node","gpu":0},{"name":"gpu-node","gpu":1}]
eligible=[node["name"] for node in nodes if node["gpu"]>=1]
assert eligible==["gpu-node"]
print("CPU scheduling worksheet:",eligible)""",
    "Only the illustrative GPU node is eligible; no cluster operation occurs.",
)

add(
    62,
    "Operational diagnosis, metrics and recovery",
    """GPU Spark failures can originate in query semantics, JVM integration, native library loading, device memory, host memory, spill disk, network or scheduler state. Preserve the first relevant error and correlate it with executor, task and SQL execution identity. A later generic task retry may hide the original native failure. Repeatedly increasing memory without a budget can move the problem between tiers.

Recovery should preserve input snapshots, output commit semantics and event logs. Retrying a task is safe only under the application's side-effect contract; external writes inside a UDF can be duplicated. A poisoned device context may require a fresh owned process, while device-wide reset is an administrator operation that can affect unrelated jobs. The classroom must never reset a shared GPU automatically.""",
    "An executor fails with device OOM while JVM heap is below its limit. Increasing heap does not address the measured GPU live-set problem.",
    "A task writes an external message then fails before Spark commits its output. Retrying may send the message twice unless an idempotency or transactional design handles it.",
    "Classify failure layers;Correlate job identities;Budget before changing settings;Analyze retry side effects;Define process cleanup;Preserve an incident packet",
    "Use first evidence rather than guessing;Link app executor stage task and SQL IDs;Count actual live and spill categories;At-least-once execution can duplicate writes;Terminate only owned job processes;Keep sanitized config plans logs metrics and input identity",
    """events=[("task1","write","key-7"),("task1-retry","write","key-7")]
raw=len(events)
idempotent=len({key for _,_,key in events})
assert raw==2 and idempotent==1
print("CPU retry model:",raw,"attempts;",idempotent,"logical keys")""",
    "Two attempts can target one logical output key.",
)

add(
    63,
    "Capstone: the same analytical pipeline in Scala and PySpark",
    """Build a bounded ETL pipeline with an explicit schema, null handling, a join, a derived column and a grouped metric. Provide Scala and PySpark implementations using equivalent declarative expressions. Use a CPU oracle for exact expected output, then run both ordinary Spark implementations. Only after semantic agreement should a separately prepared GPU Spark environment be compared.

The GPU report includes exact compatibility matrix, initial and executed plans, unsupported-operation reasons, resource assignment, task concurrency, memory/spill observations and complete timing. Keep query text and input identity unchanged across backends unless a rewrite is separately named and revalidated. A result table alone does not prove the plugin accelerated any operator. A plan alone does not prove the final result is correct.""",
    "Sales (A,2),(A,4),(B,3) joined to prices (A,10),(B,20) yield revenue A 60 and B 60. The fixture has deterministic exact integer output.",
    "Adding a duplicate A price row intentionally doubles A matches. A defensive uniqueness check should reject that input if the business contract requires one price per product.",
    "Derive expected revenue;Write Scala expressions;Write PySpark expressions;Test duplicate dimension keys;Capture executed GPU evidence;Prepare a balanced capstone report",
    "A revenue is \\((2+4)\\times10=60\\), and B revenue is \\(3\\times20=60\\);Use explicit schema join and groupBy;Match those operations and sort output;Reject or explicitly accept multiplicity;Require plans metrics and equality on actual hardware;Include CPU functionality and pending GPU limitations separately",
    """sales=[("A",2),("A",4),("B",3)]
prices={"A":10,"B":20}
revenue={}
for product,quantity in sales:
    revenue[product]=revenue.get(product,0)+quantity*prices[product]
assert sorted(revenue.items())==[("A",60),("B",60)]
print("CPU ETL oracle:",sorted(revenue.items()))""",
    "Sorted revenue [(A,60),(B,60)].",
)

add(
    64,
    "When GPU Spark is the wrong tool",
    """A good acceleration decision includes a credible no-change outcome. Tiny data, unsupported expressions, expensive transfers, external I/O, severe skew or a memory-constrained device can make CPU Spark or a single-process dataframe the better choice. Distributed scheduling overhead can dominate a workload that fits comfortably in one local process. GPU capability is one input to architecture, not a requirement to use it.

Compare total completion time, resource cost, operational complexity and output quality under actual constraints. Maintain a CPU fallback installation separately from plugin operator fallback. Revisit the decision when data size, workload mix or hardware changes. The final review should identify the smallest supported system that solves the problem and the evidence that would justify expanding it.""",
    "A local CPU dataframe finishes a tiny analysis in 0.1 seconds while Spark startup takes several seconds. No kernel speedup can erase startup for a one-off job without changing the execution model.",
    "A GPU query saves 30 seconds of compute but adds 40 seconds of transfers and conversions. The complete application loses 10 seconds despite faster arithmetic.",
    "Compute end-to-end tradeoff;Choose a tiny-data tool;Separate setup and steady state;Include operational cost;Define a reevaluation trigger;Write an evidence-based recommendation",
    "Sum all changed costs;A local CPU tool may be sufficient;Both boundaries matter for user workflow;Count maintenance compatibility and resource ownership;Name data growth or changed workload support;Recommend the simplest qualified option and state missing evidence",
    """saved_compute,added_transfer=30,40
net=added_transfer-saved_compute
assert net==10
candidates={"local_cpu":0.1,"spark_startup_only":3.0}
assert candidates["local_cpu"]<candidates["spark_startup_only"]
print("CPU architecture decision: GPU candidate adds",net,"seconds")""",
    "GPU candidate adds 10 modeled seconds end to end.",
)

SPARK_LESSONS = LESSONS[START:]
