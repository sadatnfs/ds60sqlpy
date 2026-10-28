## Calendar time is not one uniform integer

A date identifies a calendar day, while a datetime adds a clock value. A calendar month does not have a fixed number of days. Adding a month and adding thirty days can therefore produce different results. The difference is meaningful for billing periods, cohorts and scientific observation windows.

Julia's standard Dates types do not automatically attach an IANA time zone or resolve daylight-saving ambiguity. The fixture datetimes in this unit are explicitly interpreted as UTC by the application contract. They are not a demonstration of timezone conversion. A real local-time workflow needs a separately prepared timezone-aware approach and a policy for ambiguous or nonexistent local times.

Historical data also has more than one relevant timestamp. Event time records when something happened. Availability time records when a decision-maker could use that information. A later correction can describe an earlier event without having been available to the original decision.

## Worked case A: month arithmetic and clamping

The first program contrasts a calendar month with a fixed day count. It also shows how clamping an end-of-month date can make two successive month additions differ from adding two months at once. The intermediate February result is stored explicitly. A chained `start + Month(1) + Month(1)` is an n-argument addition in Julia and combines the periods before applying them, so it gives March 31. This is calendar behavior, not a floating-point error. A business or scientific window must state its intended rule.

{{WORKED_A}}

## Worked case B: choose an available historical value

The feature ledger contains a measurement and two later versions. The lookup requires both event and availability time to be no later than the request. It then chooses the latest eligible version using an explicit event/availability/version ordering. A request before the correction is published receives the earlier information, even though the correction refers to a past event.

{{WORKED_B}}

## Define boundaries and tie rules

Specify whether a cutoff is inclusive. A value published exactly at a decision timestamp may or may not be usable under a real ingestion process, but the policy must be consistent. The small reference uses inclusive comparisons and an explicit version number to resolve ties. A real pipeline may need transaction or ingestion sequence information as well.

Use stable entity identifiers in addition to timestamps. A latest-row lookup without an entity restriction can mix unrelated subjects. A duplicate or contradictory version should be diagnosed rather than hidden by whichever row happens to sort last.

## Diagnose leakage

If a historical model performs suspiciously well, inspect whether features or labels were reconstructed from their current corrected state. Event-time filtering alone can admit information published after the decision. Preserve source versions and availability evidence so the historical feature table can be audited.

A correct point-in-time lookup does not by itself establish that a feature is causal, valid or appropriate for the target. It establishes an information boundary under the recorded timestamps and policy. Delayed labels and incomplete event feeds still require their own treatment.

The examples use literal dates and a tiny authored ledger. They do not connect to a live feature store or certify the accuracy of real timestamps. They provide an executable contract that later modeling and capstone units can preserve when building a reproducible data workflow.
