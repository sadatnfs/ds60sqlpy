# Spark035-042 authoring and qualification handoff

Updated2026-10-23. All eight assigned IDs are authored and frozen:seven paired Scala/PySpark lessons plus reading-only spark-040. The private registration handoff is work/spark_advanced_records.json with schema_version,track_id and lessons fields. The lead owns merging canonical lessons.json,shared tests/status and the shared authoring helper. This author did not edit those shared surfaces.

The eight guides total16,478 words;explained solutions total7,704 words. Each has two worked examples,six distinct inspectable tasks,learner artifacts,separate complete references where runnable,and immutable case fixtures. Fourteen Python programs pass AST parsing. Manual checks passed exact IDs,direct prerequisites,all referenced files/local links,no em dashes,task/fixture structure and separate source/reference paths. The local pure-Python sink checks rejected float/bool batch IDs,changed payloads and extra fields. The capstone pure policy,after-publication replay,full literal oracle and corrupted-state negative passed.

## Exact lesson contracts

- spark-035: finite files and same-checkpoint recovery process2,2,0 rows;fresh checkpoint with a separate sink replays4. Final bag1:100,2:200,2:200,3:300 preserves business-ID multiplicity. Query ID persists;run ID changes.
- spark-036: actual foreachBatch failure after staging before publication,restart with attempts0,0,and next batch1. Stable query namespace is bound to source/checkpoint/schema. Local single-writer atomic batch payload/receipt files compare exact content. A separate unsafe append duplicates2 rows into4.
- spark-037: actual finite restart,deduplication,event-time-policy and invalid-row cases. JSON scan progress is printed as observed and compared with independently measured raw-source counts;predicate pushdown can reduce progress numInputRows. Exact output bags remain the oracle. The late cutoff is an explicit business rule,not a fabricated native-watermark claim.
- spark-038: actual progress/state observations2 to3 across restart and a separate empty finite query. Synthetic skew,growing-state and input-starvation incidents are clearly separated from measured counters. Unknown metrics remain unavailable.
- spark-039: actual2/4-partition comparison over20000 generated rows with100-key golden output,persisted readback,classic SQL metric maps,statusTracker stage counters,partition-row work imbalance,file counts and elapsed time. Missing metrics remain unavailable;hypothetical cost arithmetic is separate. No forced spill or per-task-duration measurement is invented.
- spark-040: JDBC reading contract with bigint/decimal/instant/NULL mapping,stride-bounds counterexample,connection/snapshot limits,fake-secret allowlisting and explicit unavailable live connector.
- spark-041: actual version tuple and semantic goldens;application preflight refuses changed state keys on the existing checkpoint,a separate candidate query exposes changed output,and the preserved baseline is resumed. This is same-runtime query-shape rehearsal,not an unprovisioned version upgrade.
- spark-042: actual foreachBatch failure after atomic publication followed by replay. Application-managed frozen event cutoffs95/110,duplicate/conflict policy and zero retention yield acceptedA/B/D/E/F,total75,duplicate2,late1,invalid2 across10 logical occurrences. Callback attempts0,0,1,2 examine4,4,4,2 rows. The committed chain validates input,derived state and predecessor hashes. It is explicitly bounded local application state,not native watermark eviction or distributed durability.

## Runtime evidence and repairs

The root integration owner reported actual Docker success for both languages of035,036,037,038 and039. Early036 Scala failed because Jackson LongNode and parsed IntNode were unequal despite representing the same batch ID. The repair validates integral numeric value,exact field set and exact textual identity/digest/payload;Python received equivalent strict-type checks. Changed-content rejection remains active.

Early037 asserted raw input count against a scan progress metric that reflected JSON predicate pushdown. The repaired reference separately measures raw immutable-source rows,prints actual progress and keeps exact output bags. Root confirmed both repaired languages. Scala039's equality expression was corrected from host-language == to Spark Column ===. Root confirmed that repair. Receipts include work/spark-streaming-final-{scala,python}-acceptance.jsonl and work/spark-metrics-repair-{scala,python}-acceptance.jsonl,with earlier035/036 runs in the root streaming receipts.

Actual041/042 qualification remains with the root owner at this handoff. No success is inferred from the local syntax/pure-policy checks. Any reported defect should be repaired in the owning scratch authoring inputs and regenerated before a fresh actual receipt.

## Lifecycle and reproducibility

Every file/checkpoint/sink is beneath a fresh current-job root. Per-query await is45seconds and stop timeout5seconds. Each program tracks only the queries it created,stops them before cleanup,and removes only its own root after they are inactive. Sources remain immutable files,AvailableNow bounds input,and no sleep is used to guess arrival. The root worker budget should be120seconds for streaming references.

Scratch inputs are task work/spark_advanced_common.py,spark_sink_support.py,spark_product_support.py,and spark_advanced35.py through spark_advanced42.py. The shared spark_author.py is imported without editing;its register function is privately overridden to write only the handoff records. These scratch files are not runtime dependencies:each learner/reference is a complete single-file program. The lead may package authoring inputs centrally after integration. Do not rerun a frozen batch while another agent is qualifying its current source.

No Docker,cluster,dependency or shared-runtime action was performed by this author for Spark. Root owns actual worker qualification and final shared integration. This author next reviews PyTorch019-036 depth in a separate data module while the lead retains001-018 and shared rendering/tests.
