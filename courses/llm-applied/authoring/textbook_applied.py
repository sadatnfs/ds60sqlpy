"""Connected applied-LLM textbook chapters, separate from frozen worked programs."""

from __future__ import annotations

from typing import Any

CHAPTERS: dict[str, dict[str, str]] = {}


def chapter(number: int, overview: str, narrative: str) -> None:
    identifier = f"llm-applied-{number:03d}"
    assert identifier not in CHAPTERS
    CHAPTERS[identifier] = {"overview": overview.strip(), "narrative": narrative.strip()}


def apply_textbook(specs: dict[str, dict[str, Any]]) -> None:
    for identifier, body in CHAPTERS.items():
        specs[identifier]["textbook_overview"] = body["overview"]
        specs[identifier]["textbook_chapter"] = body["narrative"]
        if "mental_from" in body:
            specs[identifier]["textbook_mental"] = specs[identifier]["mental"].replace(
                body["mental_from"], body["mental_to"]
            )


chapter(
    1,
    """A useful subject-matter assistant must connect a question to the right knowledge, computation and evidence. This chapter develops that architecture from an analyst's concrete request, then explains how prompting, retrieval and fine-tuning change different parts of the system.""",
    """## A question that requires more than a plausible sentence

Imagine an analyst asking a Methods Desk assistant: “What was conversion yesterday, and should we conclude that the checkout change worked?” The assistant has access to a metric handbook and, through a reviewed tool, a small table of events. This is an illustrative design case rather than a recorded model experiment. Its purpose is to expose the decisions hidden inside an apparently simple question.

There are12 recorded visits and four recorded purchases. Two visits belong to test accounts, and one of those visits contains a purchase. The handbook defines conversion using eligible visits and excludes test accounts. The descriptive calculation is therefore(4-1)/(12-2)=3/10=0.3. Dividing the raw totals gives4/12, about0.3333. Both expressions are easy to calculate; only one matches the stated eligibility policy. An arithmetic-capable model can still give the wrong answer if it selects the wrong definition or fails to apply the exclusion.

The second half of the question asks for a stronger conclusion. A comparison with an earlier day can reflect changes in traffic, measurement, user composition or the checkout itself. The assistant must know whether there was random assignment, which unit was assigned, which outcomes were observed and which analysis was planned. The number0.3 is a descriptive result. It does not contain that design information. A helpful answer can report the value, identify the definition and computation, and explain what evidence is missing before interpreting the checkout change.

This decomposition gives the assistant a practical purpose: shorten the path from an analyst's question to a reviewable evidence chain. It should help find the applicable definition, preserve units, prepare a bounded tool request and explain the resulting artifact. The assistant's most valuable behavior may sometimes be noticing that the requested conclusion is stronger than the available evidence.

## What changes when a prompt, context or model changes

A causal language model represents a conditional distribution over continuations. For a generated answer y, one conceptual description is p_theta(y given I,q,C), where theta denotes learned parameters, I the instructions, q the question and C the supplied context. The actual model receives a serialized token sequence rather than these mathematical labels. The separation is useful for system design because it identifies what an intervention changes.

Prompt engineering changes how the task, examples and requested output are expressed in I and sometimes q. Retrieval chooses evidence to place in C. Fine-tuning changes theta using a training objective over examples. A single application can use all three: retrieve the current handbook paragraph, ask for a structured analysis request, and use an adapted model that has learned the organization's response format.

These mechanisms do not provide equivalent update paths. If the handbook changes tomorrow, replacing a versioned document and rebuilding the appropriate index can make the new evidence available without retraining the answer model. If the model repeatedly confuses assignment_unit with analysis_unit even when the correct source is present, the problem may concern interpretation or output behavior rather than missing knowledge. Better instructions, examples or supervised adaptation could then be useful. If the model invents a sum after receiving the right counts, the application can move that calculation into a deterministic tool.

A retrieval-augmented system can itself contain trained retrievers and trained generators. The distinction here is between supplying evidence during a particular inference and updating learned parameters. Saying that retrieval supplies context does not imply that every component in a RAG architecture is permanently untrained. Conversely, an adapted model can still require retrieval because learned response behavior does not eliminate the need for current, attributable evidence.

## Diagnose a failure before selecting a training method

Suppose the Methods Desk produces four failures. In the first, it cites an obsolete denominator definition. In the second, it reads the current definition correctly but emits a string where the required count is an integer. In the third, it receives valid counts but reports0.33 after the tool returned0.3. In the fourth, it describes an observational difference as a proven treatment effect.

These failures suggest different interventions. The stale definition points toward corpus/version selection. The type mismatch points toward output contracts and validation, with prompting or adaptation considered after observing the pattern. The changed numeric result points toward the interface between the computed artifact and its explanation. The causal overclaim points toward the interpretation rubric and the evidence supplied about study design. Training one model on a handful of corrected answers might reduce all four visible examples while leaving their underlying causes intact.

A controlled diagnosis starts with the least ambiguous experiment. Supply the correct definition directly and see whether the answer stage can use it. Supply already validated counts and check the calculation/explanation boundary. Give a counterexample with no randomized assignment and inspect the claim. Each intervention holds other conditions as stable as possible. The result is a reason to change a particular component, not a generic preference for a more complex architecture.

Fine-tuning becomes a defensible candidate when the desired behavior is stable, examples can teach it, and a measured baseline repeatedly fails. Examples should represent the variation that matters: different wording, missing information, ambiguous units, relevant distractors and legitimate unknowns. A hundred copies of one template do not provide the same information as a smaller set of independently informative cases. The admission count in the runnable fixture is a pedagogical rule, not a statistical sample-size calculation.

## Build a comparison that answers the engineering question

To decide whether retrieval helps, compare candidates on the same question families with a declared evidence policy. To decide whether adaptation helps, keep the evaluation questions and source access fixed and use real outputs from both parameter states. To decide whether a hybrid is worth its cost, include work, latency and failure categories alongside answer quality. A candidate should not win merely because it receives a larger context or is evaluated on easier questions.

The unit of evaluation is also part of the claim. If ten questions are paraphrases of one metric definition, they provide useful robustness checks but limited evidence about transfer to ten independent domains. A held-out handbook family or a new type of analytical request asks a harder question. The experiment should distinguish success on the training behavior from success on the intended deployment population.

This chapter's route selector does not run a language model. It makes the design decision visible through named inputs and reasons. The later adaptation chapters perform real updates, and the optional pretrained recipe records a revealing failure: training and reload succeeded, but a generated formula was wrong despite supplied evidence. That result belongs in the same engineering story. The model, retrieval, tool and evaluation contracts must each earn their part of the answer.

The next chapter takes the first concrete interface in that story: turning a source statement into a typed analytical record without losing its units, provenance or missingness.""",
)

chapter(
    2,
    """Structured extraction is the bridge between language and analysis. This chapter follows an analyst's source note through parsing, validation, provenance and aggregation, showing why a well-formed record can still be scientifically misleading.""",
    """## From a source note to a defensible data row

The Methods Desk receives a study note containing counts, a description of eligibility and a statement about account-level randomization. A language model may be useful because the note is not always written in a fixed template. Before that flexibility can help, the application must decide what an accepted row means. Otherwise the model can produce neat JSON that downstream code interprets incorrectly.

Consider the sentence “Three purchases were observed in ten eligible visits; assignment was by account.” There are at least three distinct pieces of information: a numerator count, a denominator count and a study-design unit. The phrase eligible visits depends on an eligibility definition. The phrase assignment by account identifies where treatment was assigned, not necessarily how a reported descriptive ratio was weighted. Preserving those distinctions is part of extraction, even before any statistical model is fitted.

A useful interface separates the source observation from the proposed interpretation. The raw source and its version remain available. The proposal names fields and supporting spans. A validator checks the schema and domain constraints. A validated record can then be admitted to a particular calculation. The result is another artifact with its own inputs and method. If a reviewer later disputes the eligibility rule, the system can revisit that decision without pretending the original text contained a different fact.

## A schema expresses analytical commitments

The runnable example's counts assume at most one counted purchase per eligible visit. That is why purchases cannot exceed visits. In another application, a visit can contain multiple item purchases, so the same inequality would reject valid data. The correct repair would be to change the metric definition and schema deliberately, perhaps to items_per_visit, rather than loosening a validator while continuing to call the result a conversion probability.

Units need similar care. A value of12 can mean12 visits,12 accounts,12 dollars or12 percentage points. A schema that stores only value=12 cannot recover the distinction from the number. Dates can identify event time, reporting time or an effective policy date. Identifiers can contain leading zeros that must survive serialization. The choice of primitive type is therefore a modeling decision, not merely a programming convenience.

Some ambiguity should remain explicit. If a source says “about ten visits,” converting it into an exact integer10 may be inappropriate. If it says “no purchases were reported,” that can mean an observed zero or an absence of reporting. A production extraction schema may need separate value,status,unit and support fields. The narrow fixture intentionally rejects missing counts so the reader can see that unknown is not silently replaced by zero. Expanding the schema should preserve that distinction.

Validation cannot prove that a plausible value was stated in the source. An invented count of three still satisfies0<=3<=10. Provenance is therefore a second contract: each accepted field needs a source span or another recorded evidence link. The span proves where the proposed value came from; interpreting that phrase correctly remains a semantic responsibility.

## When individually correct rows produce a wrong aggregate

Suppose account A has one eligible visit and one purchase, while account B has nine eligible visits and two purchases. The visit-weighted rate is3/10=0.3. The equally weighted account mean is(1+2/9)/2=11/18, about0.6111. Neither number is an arithmetic error. The first weights each visit equally; the second weights each account equally and averages its within-account ratio.

An assistant asked for “average account conversion” must resolve which quantity is intended. It cannot infer the estimand solely from the existence of an assignment_unit field. If randomization is by account, a treatment-effect analysis also needs the assignment and account identities, not just a pooled count ratio. Repeated visits from the same account can share behavior and treatment. Treating every visit as an independently randomized unit would create an unjustified uncertainty calculation.

The distinction becomes especially important after extraction. A source may report one row per account, one row per visit or one summary row per study. Joining those rows to another table can duplicate observations. A correct extractor does not protect a later analysis from grain changes. Carry identifiers, counts and aggregation rules through the pipeline so the final statistic can be reconstructed from its actual observational units.

## Rejection changes the analyzed population

Imagine100 source notes. The extractor accepts80 and rejects20 because their outcome language is ambiguous. Among accepted notes, field accuracy is excellent. That result does not establish that the accepted80 represent all100. Perhaps unsuccessful studies describe outcomes less consistently, or older reports use a different format. Excluding them can change the estimated result even when every retained value is correct.

The evaluation should therefore keep separate counts for all eligible sources, accepted records, rejected records and unsupported accepted fields. If72 of80 accepted records are entirely correct, accepted-record accuracy is0.9 and acceptance coverage is0.8. The count of fully correct accepted records per all eligible sources is72/100=0.72. These describe different properties of the system. The intended workflow determines whether a rejected record goes to human review, a second parser, an explicit unknown state or a separately reported exclusion.

Repeated correction can create its own leakage. If every final assessment error is turned into another prompt example, the assessment is now influencing system selection. Keep document families and annotation revisions traceable so a new model version is not evaluated only on patterns that motivated its development. Agreement with a schema is easy to score; trustworthy extraction requires representative sources and a support rubric.

## Connect the record back to the analyst's question

The practical result is a chain of named quantities. The source supplies a count claim. The extractor proposes a typed value and span. The validator admits it under declared units and rules. The calculation produces a ratio. The explanation can then say what the ratio describes and which stronger conclusions remain unsupported. This chain lets a data scientist localize a disagreement to extraction, eligibility, weighting or interpretation.

The reference parser is deliberately narrower than an LLM. Its exact grammar supplies a reliable arithmetic and provenance baseline before a more flexible proposal stage is introduced. A language model earns value when it correctly handles useful variation while preserving the same acceptance contract. Flexibility that merely hides unsupported fields is not an improvement in the analytical system.""",
)
chapter(
    3,
    """Prompt and context design determine what task the model sees and what evidence it can use. This chapter develops a prompt as a testable interface, works through a complete context allocation, and explains how to diagnose failures without confusing clearer instructions with enforced permissions.""",
    """## Write the task before writing a persuasive instruction

The Methods Desk now has a validated source record and a handbook definition. An analyst asks for yesterday's conversion rate. A prompt saying “You are an excellent data scientist; answer accurately” expresses a preference but leaves several decisions unresolved. Which definition applies? Should excluded visits be removed? Must the answer provide a source? What should happen if the required count is absent? Should a numerical tool be used, or may the model infer a value from prose?

A more useful prompt describes the interface. It identifies the question, supplies admitted evidence with stable IDs, asks for the applicable definition and eligibility rule, and requires the answer to use the tool result for any numerical claim. It also names an incomplete-evidence outcome. The aim is to make the intended task unambiguous enough to evaluate. The model can still fail, but the application now has a concrete criterion for recognizing that failure.

The output design should serve the analyst rather than the implementation. A useful response can state the metric, period, eligibility rule, computed value and supporting evidence in ordinary language. Internally, the application may represent those as typed fields so it can check that the quoted value equals the calculation artifact. The user need not see every internal schema key. Structured internal records and readable external explanations can coexist.

## Context is a selected dataset for one prediction

A prompt's evidence is a small dataset assembled for one request. Selection changes which facts are available, and ordering can change how the model encounters them. Long context capacity does not remove the need for selection: irrelevant documents, contradictory versions and repeated chunks can consume attention and make the requested evidence harder to locate. A larger context should be evaluated as a system change, not treated as an automatic quality improvement.

Suppose the intended tokenizer measures a256-token total allowance for an illustrative request. Instructions use120 tokens, the question20, template/tool overhead20 and reserved answer capacity40. That leaves56 for evidence. A definition costs20, its exclusion rule12 and a validated-count artifact24, exactly filling the allowance. The arithmetic is256-120-20-20-40=56. These are hypothetical measured costs for the example, not claims about the whitespace-counting helper below.

Adding a30-token general FAQ now forces a tradeoff. If the FAQ displaces the exclusion rule, the model may produce a correctly formatted answer using the wrong population. Selecting the most individually relevant chunks is not always sufficient because some facts are useful together. The definition and exclusion can form one required evidence group. The count artifact becomes meaningful only when its eligibility matches that group.

One way to express the design is to choose a set S of evidence items that maximizes a task utility f(S), subject to total cost at most the evidence allowance. If utility were additive, f(S) would be the sum of individual values and the problem would resemble knapsack selection. For evidence, utility can have complementarity and redundancy: two items may jointly establish a claim, while two overlapping passages may add little beyond one. The simple ordered allocator is intentionally easier to inspect, but it should not be mistaken for a general optimum under those dependencies.

## Make an unknown result specific enough to be useful

An unknown answer can identify a missing dependency. If the definition is present but the eligible-visit count is absent, the assistant can explain the formula and say that it cannot calculate the requested value. If counts are present but two applicable policies disagree, it can surface the conflict. If the user lacks access to required evidence, the outward response should respect the application's disclosure policy while an internal trace records the appropriate failure category.

These are different states. Collapsing them into “I am not confident” loses information that could guide the next action. A repair may require a different data query, a policy-owner clarification or an authorized source. Asking the model to be more confident does not fill any of those gaps. A good prompt names the expected incomplete-evidence behavior, and the application checks whether the response follows it.

Few-shot examples can demonstrate that distinction. One example can answer a supported definition, another can return a numerical result linked to a tool artifact, and another can decline to infer a causal effect from an observational difference. The examples should vary the evidence pattern rather than merely rephrase one easy success. They become part of the system configuration and therefore part of the evaluation's exposure history.

## Test the interface with controlled changes

A useful prompt test changes one dependency at a time. Remove the exclusion rule while keeping the question and counts fixed. Replace the policy version with an obsolete one. Give the model a tool result of0.3 and an irrelevant passage containing0.33. Ask for a causal conclusion while supplying only descriptive counts. These probes ask whether the response tracks the evidence contract rather than a familiar phrase or the most convenient number.

The runnable examples in this chapter do not execute a model; they test prompt assembly, identity and budgeting. An actual response evaluation must save the rendered prompt and generated artifact, then apply the task rubric. Passing a JSON serialization check is useful preparation, but it cannot establish how a model behaves when it reads the resulting string.

The same distinction applies to prompt injection. Separating instructions from evidence in the application makes the intended roles inspectable. It does not physically prevent a model from interpreting an imperative sentence inside a document. A retrieved instruction cannot legitimately expand the application's operation catalog or its access scope, regardless of what the model proposes. The trusted dispatcher enforces that boundary after validating a proposal.

## Revise prompts without consuming the final assessment

Prompt development is a form of system selection. If a failing question causes a new instruction or demonstration to be added, that question has influenced the configuration even though no gradient was computed. Retain a development ledger that connects revisions to observed failure classes. Evaluate a frozen candidate on questions that did not determine its wording before making a fresh generalization claim.

A prompt hash helps identify which version was used, but reproducing a result also needs the evidence snapshot, model/tokenizer, decoding settings and relevant runtime state. That broader record becomes the basis for the corpus and version-management work in the next chapter. An answer is only as traceable as the identities retained along its path.""",
)

chapter(
    4,
    """A retrieval corpus is an analytical dataset with lineage, time semantics and evaluation roles. This chapter follows a policy revision through ingestion, chunking, indexing and answering, explaining how a system can reproduce both current and historical results without confusing integrity with authority.""",
    """## A policy revision changes more than a paragraph

The Methods Desk serves a handbook containing a conversion definition, an eligibility rule and an experiment-analysis note. On October10, a revised policy is published with an effective date of October5. An analyst reviewing an October7 experiment now asks two different questions: “Which rule should apply retrospectively?” and “Which rule did the team know when it made its October8 decision?” A single latest-version flag cannot answer both.

The first question concerns effective time: the interval during which the policy is meant to apply. The second concerns the evidence available at a particular knowledge or ingestion time. A system may legitimately return different source versions for these questions. It should make the temporal interpretation explicit instead of treating historical disagreement as an inexplicable model inconsistency.

This is why corpus metadata belongs beside the text. A source identity, version, effective interval, publication or ingestion time and supersession relationship can determine whether a passage is admissible for the requested claim. The exact required fields depend on the task. The small fixture's maximum-version policy is a clear starting point for current-only questions, but it is not a substitute for those richer time semantics.

## Preserve the original and name each transformation

Documents often pass through extraction, normalization, chunking and indexing before a model sees them. A PDF may become extracted text; repeated headers may be removed; tables may be represented as rows with labels; chunks may receive contextual titles; an encoder may turn those chunks into vectors. Each representation has a purpose, but each can also change the evidence available to a later answer.

Keep the original admitted content and a record of transformations. A content hash identifies exact bytes under a stated representation. A hash of extracted text is not the same identity as a hash of the original file, and a normalized string may need a mapping back to original citation coordinates. If whitespace or Unicode normalization changes character positions, the old offsets cannot be applied blindly to the new string.

A useful lineage chain links a retrieved item to its chunk, the chunk to a document version, and that version to an admitted source artifact. The index build records the chunking and encoding policy. An answer record identifies the evidence actually supplied, not merely a current corpus label that might later change. This lets an analyst distinguish “the model ignored the right source” from “the right source never reached the model.”

Integrity remains only one part of admission. Text and digest can agree while the document is stale, false or outside the permitted audience. A permission field in a fixture is a declared teaching input; it does not authenticate a real publisher. Source authority, access policy and applicability need their own evidence. Keeping them separate also makes failures actionable: a hash mismatch calls for artifact repair, while an unresolved permission basis calls for a different admission decision.

## Release the corpus and index as a compatible pair

Suppose corpus release R contains policy version1 and index release I was built from its chunks. A maintainer prepares version2 in a new corpus release but has not yet rebuilt I. If the answer trace records only “current corpus,” a user can receive version1 from the old index while believing the answer used version2. The system has mixed two valid artifacts into an invalid identity claim.

A coherent release process prepares the new source snapshot and derived index under separate identities, checks their relationship, and changes the served reference only when the pair is ready. Requests can remain pinned to one complete release during that transition. The exact atomicity mechanism depends on the storage and serving system; the local manifest example does not implement a distributed publication protocol. The design requirement is that a response can name one internally consistent evidence snapshot.

Rollback needs the same care. Reverting the encoder while keeping vectors produced by a newer encoder can preserve vector width and still destroy semantic compatibility. Reverting a source document while keeping chunks with newer offsets can produce broken citations. A rollback artifact should describe the compatible collection of sources, transformations, indexes and policies rather than a model file alone.

## Define what evaluation is allowed to see

Evaluation isolation is more subtle for retrieval than “never include the test document anywhere.” A RAG task may intentionally ask whether the system can answer questions using documents present in its retrieval corpus. In that setting, making the supporting document available at inference is part of the task, not automatically leakage. What must remain separate is the use of assessment questions, labels or outcomes to select prompts, tune retrieval or train a model when claiming independent performance.

The relevant split follows the generalization claim. To test a new-document workflow, hold out document families from the development process and then admit them through the intended inference path. To test paraphrase robustness on a fixed knowledge base, the corpus may remain fixed while question families are separated. To test an adapted extractor on new source formats, annotation examples from the same template family may be inappropriate training exposure. These are different experiments and should not share a vague label such as “unseen data.”

Hash disjointness is too weak to establish semantic independence. A revised paragraph, translated page or lightly edited report can retain the same answer structure with a different digest. Family identities help preserve those relationships. At the same time, ordinary shared boilerplate does not necessarily make two datasets dependent in the way that matters. The family rule should be justified by the task and data-generation process.

## Use the corpus record to explain a disagreement

When two answers disagree, compare the question's time interpretation, admitted source versions, index build, selected chunks and supplied context before blaming the language model. A changed result may be a correct response to a changed policy. A stable result may be wrong if it came from an obsolete cache. The corpus record gives the analyst a way to tell.

The next chapter moves from whole documents to the units actually retrieved. Chunking should preserve the relationships established here: a chunk is a versioned source span with a transformation history, not an anonymous bag of text whose origin can be reconstructed later by guesswork.""",
)
chapter(
    5,
    """Chunking determines the unit that retrieval can find and the context an answer can inspect. This chapter follows a handbook definition through competing splitting policies, connecting boundary choices to evidence sufficiency, citation coordinates and the budget available for other facts.""",
    """## Retrieve a complete meaning, not merely a matching sentence

The Methods Desk handbook defines conversion in one paragraph, lists exclusions in a table and explains the assignment unit in the next section. A question about the formula may need only the first paragraph. A question about yesterday's reported value also needs the exclusions. A question about uncertainty needs the assignment and observation structure. The appropriate retrieval unit therefore depends on the claims the answer must support.

A fixed-length chunker cannot know all of those dependencies from token positions alone. It can provide a predictable storage and retrieval unit, but a boundary can separate a term from its definition, a table value from its header or an exception from the rule it qualifies. The design task is to preserve enough local structure that relevant context can be recovered under a finite budget.

Consider a two-sentence policy: “Count purchases over eligible visits. Test accounts are excluded from the eligible population.” A split after the first sentence creates a concise formula chunk and a separate exclusion chunk. That may work well if the query retrieves both. If only the formula enters the answer context, the model can produce a complete-looking calculation while omitting the eligibility rule. Increasing overlap can reduce some boundary failures, but it does not guarantee that every required relationship stays together.

## Separate indexing units, evidence units and answer context

Three units are useful to distinguish. The indexing unit is what the retriever scores. The evidence unit is the smallest source material that establishes a required fact or relationship. The answer context is the assembled set of material supplied to the model. These units can differ without being inconsistent.

For example, a short paragraph can be an effective indexing unit because its vector or lexical score focuses on one topic. Once selected, the application might also include the section heading and a linked eligibility table in the answer context. That expansion must remain versioned and budgeted. It should not silently fetch unauthorized material or add unrelated neighboring text merely because it is nearby.

A long chunk offers more surrounding information but can make retrieval less discriminating. If a passage covers conversion, retention, experiment design and logging together, a similarity score may be influenced by several topics. A short chunk can isolate the intended topic but lose the qualifications that make its statements valid. There is no universal boundary size that resolves both tensions for every question.

This suggests evaluating chunking at the claim level. For a formula question, label the formula span. For an eligibility question, label the rule and its scope. For a multi-part analytical question, record the set of required evidence and whether alternatives are interchangeable or jointly necessary. A single document-level relevance label can hide the fact that the returned chunk omitted the useful part of that document.

## Tables and headings need an explicit representation

Suppose a table contains columns account_type,eligible andreason. A row containing “test,false,internal traffic” is hard to interpret if retrieved without its column labels. A structure-aware representation can attach those labels to the row or preserve a small table region. If the representation repeats labels for retrieval, keep a separate link to the original source span so the generated text is not falsely presented as a verbatim quote.

Headings have a similar role. The sentence “Use account-level resampling” under “Repeated visits within accounts” has a more specific meaning than the same sentence in isolation. A chunk can carry the heading as metadata or expanded context. Repeating the heading into every indexed chunk also changes lexical frequencies and embedding inputs, so it becomes part of the retrieval policy rather than a neutral display choice.

Preserving meaning does not mean inventing it. A missing table header should not be guessed from a plausible neighboring section. An extracted PDF row with damaged column order may need quarantine or a source-specific parser. The assistant can be fluent about a malformed representation, which is precisely why source-format failures need independent checks before answer generation.

## Overlap changes both cost and apparent support

The window calculation later in this chapter makes duplication measurable. With size3 and overlap1, seven source tokens occupy nine stored token positions. At larger scales, overlapping chunks can cause several high-ranked candidates to repeat the same fact. Returning three such chunks may look like three supporting sources while actually supplying one piece of evidence three times.

Deduplication should preserve evidence identity. Removing every repeated phrase blindly can discard a phrase that has different scope in two sources. Keeping every repeated chunk wastes context and can overstate corroboration. Source version, offsets and semantic role help distinguish exact overlap from independent evidence.

The context budget introduces an opportunity cost. If redundant chunks consume the space needed for an exclusion rule or an independent contradictory source, higher raw retrieval recall can produce worse answers. A meaningful comparison records the unique evidence covered, the number of repeated positions, context cost and supported-answer outcome. It should not reward a splitter solely for producing many candidates that contain an answer keyword.

## Rebuilding chunks changes the experiment

A splitter update can alter chunk identities, offsets, document frequencies, vectors and cached answers even when the original handbook is unchanged. The new index is therefore a new system configuration. Preserve the old policy long enough to reproduce a prior answer, and evaluate the new one on frozen questions before attributing an improvement to another component.

Boundary tests should include negation, exceptions, units, table headers and references such as “the rule above.” Short-source and empty-source behavior also matters: a source should not acquire invented padding text merely to satisfy a window size. The literal splitter below provides a transparent baseline for those coordinate and termination checks. Structure-aware splitting can then be judged by whether it improves the actual evidence path, rather than by whether its chunks look more natural to the author.

Once chunks have stable identities and meaningful boundaries, the next problem is ranking them. The lexical chapter begins with a method whose terms and scores can be calculated directly, giving the assistant a baseline that can be inspected before introducing learned geometry.""",
)

chapter(
    6,
    """Lexical retrieval provides a transparent first ranking of the corpus. This chapter explains how term evidence becomes a score, why an inverted index is useful, and how exact terminology, tokenization and negation affect a data-science assistant's retrieval decisions.""",
    """## Start with the words an analyst can name

An analyst asks the Methods Desk where the handbook discusses account randomization. The phrase contains an unusually useful term: randomization is more specific than account in this small corpus. A lexical retriever can use that distinction without training a language model. It looks for observed terms and ranks documents according to a declared weighting rule.

This transparency makes lexical retrieval a valuable baseline for technical domains. Analysts often know a metric name, an experiment identifier, a column name or an error message. Those strings can be more diagnostic than a broad semantic similarity. A learned retriever may add value for paraphrases, but it should be compared against the exact-match behavior that the task already supports.

The first step is tokenization. The fixture lowercases text and extracts ASCII letter/digit runs. That policy makes “Account” and “account” match, but it does not equate randomization with randomized or purchase with buy. It also chooses how punctuation-separated identifiers are split. A retrieval miss caused by that transformation should be diagnosed before changing the ranking formula.

## From documents to an inverted index

The reference implementation scans small dictionaries so the arithmetic remains visible. A larger lexical index commonly organizes postings by term: each term points to the documents containing it, together with information such as frequency. Document lengths and corpus-level counts provide the remaining statistics. A query then looks up its terms instead of rereading every source string from scratch.

This organization separates two jobs. Index construction records what terms occur under a particular tokenizer and source snapshot. Query scoring uses those recorded facts to rank candidates. If the source changes but the index does not, the scorer can be perfectly implemented and still rank stale content. If the tokenizer changes, the postings and their statistics must be rebuilt consistently.

Term frequency tells how often a term appears within a document. Document frequency tells in how many indexed documents it appears. The first can distinguish a passing mention from a repeated topic; the second estimates how discriminating the term is in the corpus. Counting occurrences when document presence was intended confuses these roles. Repeated text in one source is not equivalent to the term appearing across many sources.

BM25 combines rarity with diminishing returns from repetition and a document-length adjustment. The detailed calculation below derives each factor on the literal corpus. The important modeling idea is that a long document should not win merely because it has more opportunities to contain a term, and a document should not obtain unlimited advantage by repeating that term. The chosen parameters control those tradeoffs; they do not turn the score into a calibrated probability of correctness.

## A high lexical score can preserve an unresolved contradiction

Consider three equal-length documents: “exclude test accounts,” “include test accounts,” and “record eligible visits.” For the query “test accounts,” the first two have the same matching term frequencies and the same lengths. Each query term appears in two of three documents, so each contributes log(1.6) under the fixture's IDF convention. Both documents score2*log(1.6), about0.940007.

The tie is correct for the stated lexical evidence. The two documents make opposite claims, but the query terms alone do not distinguish their policy meaning. A deterministic ID tie-break makes the output reproducible; it does not resolve which source is applicable. Version, authority and scope must be considered before an answer adopts either statement.

Adding more query words can help without solving entailment generally. A passage saying “Do not exclude test accounts” still contains exclude,test andaccounts. A bag of terms does not represent the full effect of negation or the scope of an exception. Lexical retrieval is choosing candidates for inspection, not proving that their propositions answer the question correctly.

Technical quantities create another mismatch. “100 milliseconds” and “0.1 seconds” may describe the same duration while sharing little lexical form. A domain-aware normalization step could make the equivalence available, but it must preserve units and context. Blind text substitution can create false matches. The same caution applies to abbreviations, SQL identifiers and method names whose common-language meanings differ from their technical use.

## Diagnose the baseline before adding a learned model

For each missed question, inspect the emitted query tokens, the relevant source tokens and the scoring statistics. A zero score can mean no shared vocabulary, a tokenizer mismatch or evidence that is genuinely absent. Returning the first zero-score document by ID does not make the question answerable. A low score can also reflect a long chunk whose relevant sentence was diluted by unrelated material.

For a false positive, inspect why its terms matched. Was the query broad? Did a repeated header inflate document frequency? Did the source discuss a rejected method rather than recommend it? Did an old policy contain the same terminology as the current rule? These explanations point toward different changes: query formulation, chunking, metadata filtering or a richer relevance model.

Corpus changes affect the score distribution. Rechunking one long handbook into many passages changes document count, average length and term frequencies across indexed units. A threshold chosen before that change may not retain its earlier meaning. The score belongs to a particular corpus and analysis policy, so the evaluation trace should identify both.

A learned embedding branch is justified when failures show useful semantic relationships that lexical terms miss. A reranker is justified when candidates contain the needed evidence but ordering remains poor. The baseline is not a disposable stepping stone. It remains a comparison tool and can continue to supply strong candidates for exact identifiers and rare terminology in a hybrid system.""",
)
chapter(
    7,
    """Embedding retrieval replaces exact vocabulary overlap with learned or authored geometry. This chapter explains how that geometry is produced and used, how to separate representation errors from search errors, and why a nearby passage is still only a candidate for a supported answer.""",
    """## A synonym miss suggests a new representation

The Methods Desk lexical baseline misses a purchase question when the relevant passage uses buy. One possible intervention is a curated synonym rule. Another is an encoder trained to place useful paraphrases near each other. The second approach can handle relationships beyond a small dictionary, but it introduces a learned representation whose successes and failures must be measured.

An embedding is a vector produced by a specified mapping. For text, the mapping may tokenize the input, compute contextual hidden states and pool them into a fixed-width representation. Those transformations can retain useful task information while discarding other details. The vector's coordinates are not generally named concepts such as purchases or geometry. The literal table below gives its axes explicit meanings only so the arithmetic can be inspected.

A learned encoder's training objective influences what similarity means. A model trained on paraphrase pairs may behave differently from one trained to match questions with answer passages. A sentence that restates a question can be semantically similar without containing its answer. A long policy page can be relevant to the topic while failing to establish the requested exception. Retrieval evaluation must therefore use the intended query-to-evidence relationship, not a vague notion that the texts sound related.

## Queries and documents can have different roles

A query is often short and underspecified; a document passage can contain the explanation needed to answer it. A dual-encoder system can use a query encoder and a document encoder trained as a compatible pair. They need not have identical parameters or identical input formatting. What matters is that the resulting vectors are intended to be compared under the declared scoring function. Dense Passage Retrieval is one example of learning such query-passage representations. [Dense Passage Retrieval](https://arxiv.org/abs/2004.04906).

This refines the metadata lesson. Requiring a compatible encoder pair is stronger and more accurate than blindly requiring the same model-name string on both sides. An intentionally asymmetric pair can be valid; an unrelated query encoder and document encoder of the same width can be invalid. An index record should identify the document encoder and its compatible query-side configuration, including preprocessing, pooling and normalization policies.

Once document vectors are computed, they can be reused for many queries. A new question needs its own encoding and a search over those stored vectors. This is the efficiency advantage of separate encoding. It also creates a consistency obligation: changing the document encoder without rebuilding its vectors, or changing the query encoder outside the declared pair, can silently invalidate comparisons that remain dimensionally legal.

## Similarity is a geometric measurement with a task interpretation

Cosine similarity measures directional agreement after normalization. A dot product also responds to vector magnitude. The worked table calculates both and demonstrates positive-scale invariance for cosine. Neither score becomes a relevance probability merely because it lies in a familiar numeric range.

Consider an ambiguous question: “How should we handle variance?” A nearby passage about feature scaling may share vocabulary and topic associations with a passage about sampling uncertainty. Both may be legitimate candidates, but the analyst's intended task is unresolved. A strong similarity score cannot supply the missing context. The assistant may need the surrounding analytical question or an explicit clarification before selecting a method.

Negation, scope and exact quantities can be difficult in a different way. Two passages about including and excluding test accounts may have very similar overall topic representations. A passage with the wrong experiment identifier may also be close to the correct one. These are reasons to retain exact-match tests and claim-level support evaluation, not reasons to assume that all embeddings ignore such distinctions. The relevant question is how the particular encoder performs on those cases.

A threshold should be evaluated on labeled requests under the intended corpus and encoder. A score of0.85 can have different implications across domains or after adaptation. Even a well-calibrated relevance estimate would not by itself establish source authority, freshness or entitlement to use the document. Those are separate parts of the evidence path.

## Localize the error before changing the encoder

There are at least three places a dense retrieval system can lose the answer. The encoder may assign poor geometry to the relevant passage. An approximate search index may miss a vector that exact search would have found. A later top-k or context-budget stage may discard a good candidate. Inspecting only the final answer hides these distinctions.

For a frozen set of vectors, exact search provides a useful search-mechanics reference. Approximate-index recall can then be measured against that ranking. Semantic relevance recall is a different comparison against authored or reviewed evidence labels. An index can perfectly reproduce an encoder's wrong ranking, while an excellent encoder can be undermined by an overly aggressive search approximation.

The literal implementation below performs exact scoring over a tiny table and rejects obvious shape and norm failures. It does not evaluate a learned text encoder or an approximate index. Its role is to make the geometry and numerical boundary visible before those components are introduced. A real retrieval-model training example later in the route changes a small projection through gradients, while still keeping its literal-feature scope explicit.

## Decide whether adaptation addresses the observed gap

If errors cluster around domain-specific meanings, a governed adaptation dataset may help. It should include positive query-passage pairs and negatives that are truly unsuitable under the task. A passage can be a hard negative because it is topically close, but it may also be another correct answer. Training against a false negative teaches the wrong geometry.

A useful evaluation includes exact identifiers, paraphrases, ambiguity, negation, numerical units and unseen document families. Keep a lexical baseline and measure the effects of any normalization or query-prefix convention. The goal is not to prove that vectors are generally more intelligent than words. It is to find which representation supplies the evidence the analyst needs under a stated cost and quality contract.

The next chapter combines those complementary sources of candidates. Fusion can help when their errors differ, but agreement between two rankers is still evidence about ranking behavior rather than a proof that the selected passage supports the answer.""",
)

chapter(
    8,
    """Hybrid retrieval and reranking allocate different amounts of computation to different stages. This chapter develops a complete candidate-to-context pipeline, explains when combining rankers helps, and shows how to preserve the evidence needed to diagnose a failure at the correct stage.""",
    """## Two rankers can contribute different useful evidence

The Methods Desk now has a lexical branch that finds exact metric names and a dense branch that can recover paraphrases. Combining them is attractive when one finds a relevant passage the other misses. It adds little when they repeatedly return the same stale or incomplete chunk. Before choosing a fusion rule, inspect the overlap in their useful and harmful results.

For an eligibility question, the lexical branch might rank the metric definition first and an older definition second. The dense branch might rank the same current definition first and the exclusion rule second. Their union contains the two facts required for the answer, but a final context budget of two items can still be wasted on the two definitions. Candidate diversity is useful only if the later selection preserves complementary evidence.

Authorization and applicability should already restrict the candidate universe. Fusion is not the place to let an inaccessible or superseded document earn its way into the answer by receiving a high score. The next chapter examines that admission boundary in detail. Here the ranking methods operate on candidates already eligible for the request.

## Why rank fusion is an attractive baseline

Lexical and dense scores often have different scales. Adding them directly can let one branch dominate because of numerical units rather than useful evidence. Reciprocal-rank fusion replaces raw scores with contributions determined by position. The exact worked example below shows how one document's strong positions across both lists can overcome another's single high position.

The convenience has a cost. Rank fusion discards the magnitude of a lead. A ranker that barely prefers its first document and one that strongly separates it from all others contribute the same top-rank value. The fusion constant also changes how strongly position matters relative to appearing in several lists. Those are design choices that should be evaluated against the task, not hidden behind the claim that rank fusion is scale-free and therefore universally reliable.

Consensus can reinforce a shared error. Two encoders trained on related data, or two retrieval branches built from the same repeated headings, may both prefer the same misleading passage. Their agreement is not independent corroboration of the document's claim. A document also does not become more authoritative because it was returned by two algorithms. Source support and ranking consensus answer different questions.

Duplicate handling must distinguish those levels. Repeated IDs within one result list should not create extra votes. The same source returned by different branches can intentionally accumulate rank contributions, but the answer stage should still recognize that it is one source. Overlapping chunks from that source may need additional deduplication so they do not consume the entire context budget.

## Spend expensive reasoning on a bounded candidate set

A common second stage is a cross-encoder that reads the query and a candidate together. In a transformer implementation, tokens from both sides can interact inside the model, allowing finer comparisons than a single precomputed document vector. That flexibility is often useful for distinctions such as whether a passage answers a question, discusses an exception or merely mentions the same topic.

The extra interaction has a work cost. A standard dense self-attention layer over a combined sequence of length Q+D forms a score matrix proportional to(Q+D)^2. A bi-encoder can compute document representations in advance and encode a new query separately. These operation counts explain a design tradeoff; they are not measured latency or memory claims for every architecture, kernel or batch size.

A reranker is therefore usually applied to a smaller admitted candidate set. Its budget includes candidate count and passage length, not only the number of model calls. Increasing the candidate pool may improve recall while increasing latency and context-processing work. Compare quality at a declared budget, and record whether truncation removed the part of a candidate that made it relevant.

The runnable reranker here sorts authored features. It demonstrates the second-stage boundary without pretending to be a trained cross-encoder. The distinction matters because an observed order from a literal feature table says nothing about how a learned model interprets arbitrary query-passage pairs.

## Read a failure as a pipeline trace

Consider an illustrative evaluation of ten questions. The first-stage candidates contain sufficient evidence for eight. The final context retains sufficient evidence for six of those eight. The answer stage produces a correct supported answer for five of those six. The observed end-to-end success count is five, while the conditional stage rates are8/10,6/8 and5/6. Their product is5/10. This arithmetic is a diagnostic worksheet, not a recorded benchmark.

The two candidate misses and two context-selection losses require different interventions. If the required passage is absent from the candidate set, a better reranking order cannot recover it. If the passage is present but displaced by redundant chunks, the final selector needs attention. If sufficient evidence reaches the model but its answer is wrong, improving candidate recall alone may leave the error unchanged.

A reranker can also optimize the wrong target. Document-level relevance may be too broad when the answer needs a specific source span. A long passage can contain both relevant and contradictory material. A score that places the passage first does not determine which statement the generator will use. Retain claim-level evidence requirements when moving from ranking evaluation to answer evaluation.

## Compare a hybrid with the baseline fairly

Hold the authorized corpus, query families and final context budget fixed. Report the work used by each branch and the reranker. A hybrid supplied100 candidates should not be compared with a five-candidate baseline and credited entirely for a better model. It may still be the better system, but the reason includes the additional retrieval budget.

Use ablations to identify what each component contributes: lexical only, dense only, their union/fusion and fusion with reranking. Preserve examples where the added component hurts as well as where it helps. This makes the result useful for deciding whether the complexity is justified and gives the analyst a way to diagnose future changes in corpus or query distribution.""",
)
chapter(
    9,
    """A domain assistant answers within a principal's permitted evidence, not within everything its infrastructure can store. This chapter follows a request through admission, ranking, conversation state and caching, making the access boundary precise enough to test.""",
    """## The same question can have two legitimate evidence sets

Two analysts ask the Methods Desk for a project threshold. One is permitted to read only the public handbook; the other also has access to a restricted project note. The question text is identical, but the admissible evidence is different. A retrieval system that keys only on the question can therefore return an answer produced under the wrong authority.

The model should not decide that authority from a claim in the question such as “I am the project owner.” Trusted application state identifies the principal and computes the effective policy. Retrieval then operates on the admitted corpus. The fixture uses explicit scope sets to make that step visible, but it does not authenticate users or prove integration with a real identity provider.

This separation is as important for quality as for confidentiality. A source outside the request's scope is not a valid candidate even if its content would make the answer easy. Conversely, a permitted source can be irrelevant or obsolete. Admission, relevance and applicability are distinct decisions that must agree before the source supports an answer.

## Define the observable boundary

A useful thought experiment compares two corpora that differ only in material the public analyst is not allowed to see. Under a policy that hides that material's existence, the public answer and public diagnostic trace should not change merely because the restricted text changed. In the deterministic fixture, filtering the restricted record out before selection makes this property directly inspectable.

The observable result includes more than the final sentence. A candidate list, document title, score explanation, citation preview or debug trace can expose restricted information. A response saying “I found the confidential threshold but cannot show it” may reveal more than the application's policy permits. Internal failure categories can remain detailed while outward behavior uses a disclosure-safe unknown response.

A learned model adds another scope distinction. Filtering the current retrieval corpus prevents unauthorized retrieved content from entering that request. It does not prove that a model trained earlier on sensitive examples cannot reproduce remembered material. The training-data policy and the runtime retrieval policy therefore address different paths by which information can enter an answer. Fine-tuning is not a record-level permission mechanism.

## Put admission before every component that consumes content

Filtering the final answer is too late if an unauthorized passage was already supplied to a reranker or generator. The intermediate model may incorporate it into a paraphrase or a later tool proposal, and a cache may retain its effect. The admission boundary should therefore precede content consumption, with any additional fetch checked under the same effective policy.

The top-k counterexample below also shows a retrieval-quality consequence. If an inaccessible document occupies one of the global top positions, removing it afterward leaves fewer useful candidates. Ranking the admitted set first can return a full public result list. A system can therefore leak less and answer more usefully by placing the policy at the correct stage.

Links and model-generated plans do not grant permission. A public paragraph may point to a restricted appendix. A proposed follow-up query may name a project that the caller cannot access. Those are data for an admission decision, not new authority. The application should resolve the target under its policy before retrieving text or metadata that would cross the boundary.

## A cache needs the same evidence contract as a fresh answer

Caching reuses a result, so its validity depends on the conditions under which that result was produced. The fixture includes question, scope set, corpus version and retriever version in the key. That is sufficient to illustrate policy partitioning within its simple shared corpus. A multi-tenant or personalized service may need tenant identity, per-record grants, prompt/model versions and other fields that affect the permitted answer.

The correct equivalence class is “requests for which this stored result remains valid,” not merely “requests with similar wording.” Two principals with the same effective policy may safely share some results; two principals with the same role label may still have different grants. A hash does not resolve that distinction. It only identifies the supplied key material.

Conversation history is another form of reuse. A prior privileged turn can contain restricted evidence even if the current retrieval step filters correctly. Changing the principal or effective scope without revisiting retained context can reintroduce information through history. The application needs a defined policy for which earlier turns and artifacts remain admissible for the current request.

## Revocation introduces a time boundary

Suppose an answer was cached while access was valid and the permission is then revoked. A time-to-live limits how long the cache may persist, but it does not implement an immediate-revocation contract by itself. A policy generation or effective-permission identity can invalidate reuse, and the serving layer may need to recheck authorization before releasing the stored answer.

The exact timing guarantee must be stated. A service may define authorization at request admission, at each content fetch or at final response release, with additional rules for long-running operations. Distributed policy changes can race with work already in progress. The local scope filter does not solve that coordination problem; it supplies a small invariant that a larger implementation should preserve under its chosen timing semantics.

Testing should exercise transitions, not only isolated requests. Ask as a privileged principal, then as a public principal with the same wording. Change a policy version while keeping the question fixed. Revoke a source after a cache entry exists. Inspect both returned text and trace fields. These cases reveal whether the system's state boundaries match its access claim.

The next chapter allows retrieval to continue across several steps. Its central requirement follows directly from this one: every rewrite, graph edge and follow-up request remains inside the original request's effective authority unless trusted application policy explicitly changes it.""",
)

chapter(
    10,
    """Some analytical questions need vocabulary translation or several linked sources. This chapter develops a bounded retrieval plan from a missing-evidence question, explains the meaning of each hop, and shows how to preserve intent, scope and termination while the evidence set grows.""",
    """## Ask what evidence is missing before asking another question

An analyst asks: “Our experiment randomized accounts, but outcomes are recorded as repeated visits. What should be resampled for an uncertainty estimate?” The Methods Desk may need an assignment-design source and a source describing the dependence of repeated observations. Finding only a generic bootstrap paragraph is insufficient because the resampling unit is the substantive issue.

A useful retrieval plan names that dependency. The first search locates the experiment's assignment and observation structure. The next search locates the method guidance relevant to independent accounts with repeated visits. The answer can then explain why treating all visits as independent would require an assumption not established by the design. It still needs the actual data and a justified analysis plan before producing an uncertainty estimate.

This is different from adding searches until the model feels confident. Each additional step should have a reason tied to an unresolved claim: a missing definition, an eligibility exception, a linked method or a conflicting source. Without that reason, more context can add noise and contradictions while consuming the budget intended for useful evidence.

## A rewrite is an interpretation that can be wrong

The controlled synonym rule below replaces buy with purchase. That can repair a simple vocabulary mismatch. A realistic rewrite may be more ambitious, expanding an abbreviation or translating a user's informal question into the corpus's terminology. The expansion can help retrieval while also changing the task.

For example, rewriting “Should test accounts be excluded?” into “conversion-rate definition” can lose the user's focus on an exception. Rewriting “Why did variance increase?” into “how to normalize feature variance” assumes that variance refers to preprocessing rather than sampling uncertainty. A good system retains the original question and treats the rewrite as a proposal that can be compared with it.

Important constraints should survive the transformation: entity, time period, units, negation, requested comparison and access scope. A rewrite that removes “not,” changes accounts to visits or substitutes a broader project identifier may retrieve plausible but unsuitable evidence. Preserving an original-query branch can protect exact terms while another branch explores paraphrases, but the combined work and final context must remain bounded.

## A link is a route to inspect, not a proof to adopt

The graph fixture represents a chain from a metric definition to exclusions and then to test-account details. Breadth-first traversal makes the edge-count meaning of a hop explicit. Starting at depth zero, the two-hop result includes nodes at distances zero, one and two. The visited set prevents a cycle from repeatedly emitting the same identity.

A real document link can have several meanings: an authoritative dependency, a related-topic suggestion, an obsolete reference or a navigation convenience. The existence of a path does not establish the logical relationship needed for the answer. If a metric page links to a general experimentation guide, the assistant still must determine whether the cited section applies to the experiment being analyzed.

This distinction is especially important in generated plans. A language model can propose a bridge that sounds plausible without source support. The application should retain why the bridge was followed and which admitted passage established the connection. A missing bridge is an incomplete-evidence state, not permission to synthesize a confident relationship between unrelated sources.

## Bound depth, breadth and actual work separately

The fixed graph walk has a depth limit and a visited set. Those controls prevent particular forms of repeated or over-deep traversal, but they do not bound every resource. A single node may have hundreds of outgoing links. A shallow search can therefore examine many candidates, and one remote request can take a long time even when the call count is small.

A complete retrieval loop may need separate budgets for hops, candidate IDs examined, documents fetched, model calls, context tokens and elapsed time. Each budget should specify what is charged when an operation fails or is retried. The local helper performs no network fetch, so its successful cycle test does not establish cancellation or timeout behavior for a remote service.

The integer validation also has a conceptual purpose. A hop count is discrete. Accepting1.5 and comparing it with integer depths would not define a meaningful stopping boundary. The already-qualified implementation rejects that configuration before traversal. Input types can be part of the algorithm's termination proof, not merely a style preference.

## Stop when the contract is satisfied or cannot be satisfied

A useful stopping rule can depend on evidence sufficiency rather than the first positive score. If the answer requires a definition and an exclusion rule, finding only the definition does not finish the task. If an additional authorized source supplies the exclusion and both versions are applicable, the evidence requirement may be complete. If the work budget expires first, the response should identify the remaining limitation rather than treat partial retrieval as a complete answer.

Sufficiency labels are themselves part of the evaluation design. Some questions can be answered by any one of several equivalent passages; others require several facts jointly. A planner that stops after the first relevant hit may work on the former and fail systematically on the latter. Preserve that distinction in the held-out question set.

Measure each retrieval step's contribution. Did it add a required fact, repeat an existing source, introduce a contradiction or merely produce more text? Keep the original query, proposed rewrites, admitted candidates and termination reason in the trace. This record allows a reviewer to improve the plan without attributing every failure to the final generator.

The following chapter turns the selected evidence into claims. The boundary becomes stricter: a retrieved passage is a candidate source, while a grounded answer must explain exactly what that source supports and which requested claims remain unresolved.""",
)
chapter(
    11,
    """A grounded answer is a set of claims connected to the evidence appropriate for each claim. This chapter builds that connection for a data-science request, distinguishing quotations, computations, interpretations and useful abstention instead of treating citations as decoration.""",
    """## Decompose the answer the analyst will read

The Methods Desk is ready to respond to the conversion question. A concise answer might say: “For the selected reporting period, conversion was30% after excluding test accounts. This descriptive result alone does not establish that the checkout change caused an improvement.” That paragraph contains several claims, each requiring a different supporting artifact.

The metric definition supplies the numerator and denominator rule. The eligibility source establishes the exclusion. The validated data artifact supplies three purchases and ten eligible visits for the stated period. The calculation artifact supplies3/10=0.3. The interpretation statement concerns the absence of a sufficient causal design in the supplied evidence. One citation at the paragraph's end does not automatically support all of those components.

A claim-level representation makes the dependencies visible. The formula claim points to the applicable policy span. The numeric claim points to the accepted inputs and deterministic calculation. The period claim points to the data selection. A causal-effect claim would need additional design and analysis evidence. This representation need not be exposed as raw JSON to the user, but it gives the application something more precise to validate than the answer's overall fluency.

## Quotation, paraphrase and inference have different obligations

An exact quotation has a strong integrity check: the cited source slice should reproduce the quoted text. A paraphrase adds a semantic question: does the new wording preserve the source's scope, conditions and uncertainty? An inference adds another question: do the premises and method justify the conclusion? These obligations build on one another rather than replacing each other.

For example, “test accounts are excluded from this experiment's eligible population” does not establish that every company metric excludes them. A paraphrase that drops “this experiment” broadens the claim. A passage recommending account-level resampling under independent accounts does not establish that such resampling resolves missing outcomes or confounding. Retaining the source's conditions is part of grounding.

Source truth and source attribution also differ. A policy document can establish what the policy states, while an empirical claim may require data beyond that document. When two applicable sources conflict, accurately quoting each can establish that a conflict exists without establishing which one is correct. A useful assistant should expose that state and the declared precedence rule instead of inventing a smooth reconciliation.

The extractive baseline below deliberately makes only a narrow construction: it creates a source-span record or returns unknown when no document is supplied. Its separate support examples show why record construction is not a general entailment validator. Adding a generative stage should preserve that distinction rather than labeling any answer with a valid document ID as grounded.

## Keep the computed artifact as the numerical authority

Numerical explanations are especially easy to corrupt through paraphrase. The tool can return0.3 while the prose rounds it incorrectly, changes the denominator, describes it as a30-percentage-point improvement or treats it as a treatment effect. Those are different statements even though they share the number30.

A report interface can bind a numerical claim to a result field and its units. The percentage representation of0.3 is30%; a difference of0.03 between two rates is three percentage points; a relative change from0.3 to0.33 is10%. The requested comparison determines which expression is appropriate. A language model should not choose among them solely because one sounds more persuasive.

The underlying data selection remains part of the claim. “Yesterday” needs a resolved date, timezone and availability cutoff. A late-arriving event may change a revised report without implying that an earlier calculation was arithmetically wrong. Preserve the period and snapshot identity so the explanation describes the result that was actually computed.

For statistical interpretation, retain the method and assumptions alongside the numeric output. A p-value, confidence interval or posterior quantity has a specific meaning under its model and design. A generated description should be checked against that computed artifact and the relevant statistical definition. The [statistics book](../../statistics-ml/README.md) develops those distinctions; a citation-bearing language model response is not a substitute for them.

## Abstention is a task outcome, not an apology

The assistant can be useful while declining a stronger claim. It may explain a known formula while saying that the required count is missing, report a descriptive difference while withholding a causal conclusion, or identify a source conflict that requires a policy decision. A specific limitation tells the analyst what would make the next step possible.

Coverage prevents selective answering from hiding the cost of refusal. In an illustrative set of100 requests, suppose the system answers80 and72 satisfy the full correctness-and-support contract. Its coverage is0.8 and conditional accuracy is0.9. The remaining20 refusals and eight failed answers still matter. A report that presents only90% accuracy omits how often the system helped and what kinds of errors it made.

The appropriate tradeoff depends on the task. If an accepted answer earns one unit of benefit and a failed answer costs nine, those72 successes and eight failures have net utility72-9*8=0 before considering refusal costs. This is an illustrative utility calculation, not a universal deployment threshold. It shows why a seemingly high average accuracy can be insufficient for a particular use. Any score used to select answers must be evaluated for the relevant event and population; cosine similarity is not automatically that probability.

## Evaluate support with deliberate corruptions

Useful negative cases alter one claim while leaving the rest plausible. Swap eligible visits for all visits. Preserve a citation but replace its quote. Remove a condition such as “under independent accounts.” Attach a current version label to old text. Quote the correct formula but invent the count. Each corruption probes a different link in the evidence chain.

A support evaluator should also accept legitimate paraphrases and calculations, so it does not reward only copied wording. Human review, deterministic checks and a model-based judge can contribute different observations. If a judge is used, measure its failures on these controlled cases and on representative real requests before treating its score as a trusted acceptance decision.

The next chapter turns these observations into an evaluation dataset. The aim is to know not only whether a candidate improved, but which stage improved, which cases remain unresolved and what the result can support about the intended assistant.""",
)

chapter(
    12,
    """An evaluation should answer the engineering question that motivated the system change. This chapter builds a question-and-evidence benchmark, separates retrieval and answer metrics, and develops oracle controls that identify useful interventions without overstating what a single score proves.""",
    """## Begin with the work the assistant is supposed to help perform

The Methods Desk needs to answer current definitions, explain eligibility rules, calculate validated descriptive quantities and recognize when a requested conclusion exceeds the evidence. An evaluation containing only easy definition lookups would miss much of that job. The test set should represent the tasks and failure boundaries that determine usefulness.

Useful case families include a supported definition, an eligibility exception, a historical-version question, missing evidence, an access-restricted question, a deterministic calculation, an unsupported causal request and an ambiguous term. These are categories for designing evaluation, not a claim that eight examples suffice for a production decision. Each needs representative variation and a clear expected behavior under the request's access and time policy.

Answerability is conditional on that policy. A restricted document may contain an answer, but the public caller's admissible evidence set may not. A historical question may be answerable only when older versions remain available. An ambiguous question may require clarification rather than a guessed interpretation. Labels should describe the intended behavior, not merely whether a string appears somewhere in the global corpus.

## Store enough information to score the right thing

A case should retain a stable question ID, family, requested scope and period, relevant evidence identities, required claims, allowed alternatives and scoring decisions. Some questions need any one of several equivalent sources; others require a set of facts jointly. A flat list of relevant documents does not express that distinction automatically.

Candidate recall asks whether useful evidence entered an early pool. Final-context recall asks whether it survived ranking, deduplication and the token budget. Answer correctness asks whether the returned response satisfies the question. Support asks whether the response's substantive claims are established by its admitted evidence and calculations. Appropriate abstention asks whether the system declined the cases it should decline while still answering useful cases.

These measurements can disagree for meaningful reasons. A generator may guess a correct answer despite a retrieval miss, which fails a source-grounded contract. A correct citation can accompany an irrelevant answer. A perfectly supported quotation can omit the requested computation. Keeping the metrics separate allows the report to identify those outcomes instead of averaging them into an opaque score.

The runnable metric helper below operates on explicit IDs and relevance sets. The saved answer labels are authored examples showing how a result table would be processed. They are not evidence that a named model generated those answers. An actual benchmark run needs the rendered inputs, model outputs and rubric decisions that connect the computation to observed behavior.

## Compare candidates on the same identified cases

Suppose an illustrative eight-question evaluation finds that candidate A answers seven, with five accepted answers and two unsupported failures. Candidate B answers five, all accepted, and refuses three. Both produce five accepted answers overall, but their coverage and error profiles differ. A headline accuracy among answered cases would favor B; a task that strongly values coverage may need to inspect which questions B refused. The acceptance policy determines the relevant tradeoff.

Pairing by question ID preserves that comparison. If one candidate is evaluated on a different mix of questions, a score difference can reflect difficulty rather than system quality. Family labels matter too: many paraphrases of one question can dominate a row average without adding independent evidence about new domains. The next chapter develops the corresponding paired and family-level uncertainty calculations.

Freeze the rubric before using results to select a candidate. A new interpretation of correctness that appears only after inspecting a favored system can turn evaluation into another tuning step. Annotation disagreements should remain visible, especially for paraphrases, partial answers and legitimate abstentions. A deterministic answer key is useful where the task permits one, but a rubric is still needed for semantic scope and support.

## Use oracle context as a controlled diagnostic

An oracle-context run supplies known sufficient evidence to the answer stage. If the response improves, the intervention was useful under that protocol. To attribute the improvement specifically to a missing passage, hold other context properties as stable as possible. Replacing a long noisy context with one short perfect paragraph changes both evidence presence and distraction, and may expose a context-use failure as well as a retrieval miss.

A useful sequence can compare the observed context, observed context plus the missing required source, and a minimal sufficient context. The first change probes whether supplying the missing fact helps under the original distractions. The second probes whether the answerer struggles with competing or irrelevant material. These controls are not always equally realistic serving options, but they help locate the failure.

If the oracle result still fails, inspect the answer model, prompt, source interpretation and rubric. The source may not actually be sufficient, or the required computation may be absent. Calling every oracle failure “generation error” would hide those alternatives. The purpose of the control is to make a narrower investigation possible, not to assign blame automatically.

## Evaluate a judge before using it to evaluate the assistant

A model-based judge can help triage large numbers of responses, but it is another measurement system. Test it on known corruptions such as a swapped denominator, an unsupported universal claim, a valid citation attached to the wrong proposition and a legitimate paraphrase with little word overlap. Compare its decisions with deterministic checks and reviewed labels, and preserve cases of disagreement.

Judge prompts, versions and evidence access affect the measurement. A judge shown the answer key may answer a different question from one asked to determine support using only supplied context. A judge that knows which system produced an answer may introduce another source of bias. Record those conditions so the resulting scores can be interpreted and reproduced.

The final report should connect metrics to decisions. If candidate recall is the main limitation, investigate retrieval or corpus coverage. If evidence arrives but the formula changes in prose, repair the calculation-to-explanation interface. If unsupported claims are concentrated in causal requests, improve the task contract and assessment for those requests. The evaluation is most useful when it tells the team what evidence would justify the next change.""",
)
CHAPTERS["llm-applied-012"]["mental_from"] = "If the answer improves, retrieval was a bottleneck."
CHAPTERS["llm-applied-012"]["mental_to"] = (
    "An improvement shows that the context intervention helped under that protocol; narrower controls are needed to attribute it to a particular retrieval failure."
)
chapter(
    13,
    """A reliability study must define what varies and what population the comparison represents. This chapter connects paired question results, family dependence, stochastic model behavior and selective answering to an interpretable decision about an assistant.""",
    """## Decide which improvement the study is meant to estimate

The Methods Desk team has two candidate configurations and a fixed question set. Candidate A may answer exact definitions well while candidate B handles ambiguous analytical requests better. A single average can conceal that pattern, especially if the benchmark contains many paraphrases of the easy definition questions and only a few examples of the harder task.

The estimand is the quantity the study is trying to learn about. It might be the difference in error across all incoming requests, the average difference across equally weighted subject families, or the change in supported-answer coverage under a fixed abstention policy. Those targets imply different weights. Choosing the weighting rule after seeing which candidate wins turns the reported result into another selection decision.

The small fixture below makes this visible without a complex model. Repeating a favorable family changes the row-weighted mean but not the equally weighted family mean. Both calculations are mathematically valid. Their scientific usefulness depends on whether the weighting matches the population the assistant is intended to serve.

## Pair the cases before estimating variability

A difficult question tends to affect both candidates. Comparing their results on the same identified case preserves that shared difficulty. The difference for question i can be defined as error_A_i minus error_B_i, with a negative value favoring A. The study then analyzes those paired differences rather than pretending the two error tables are unrelated samples.

Pairing requires more than equal row counts. The question, source snapshot, policy, rubric and relevant evaluation conditions must correspond. If one candidate sees an updated policy or a different context budget, the comparison may still be useful as a system comparison, but it no longer isolates the same component change. Preserve those conditions alongside the question ID.

The variance identity for a paired difference explains the role of correlation. Var(A-B)=Var(A)+Var(B)-2Cov(A,B). If the candidates tend to succeed and fail on the same questions, that covariance can materially affect uncertainty. Independently resampling A and B destroys the correspondence that the study deliberately created.

## Preserve the dependence among related questions

Paraphrases, document revisions and questions derived from the same source can share errors. Treating every variant as an independent observation may make uncertainty look smaller than the evidence warrants. A family-level analysis first summarizes the paired results within each family and then treats families as the resampling units under its stated assumptions.

That choice does not magically make families independent. The family definition should reflect the dependence relevant to the study. Several families may still share a template, authoring process or narrow knowledge source. With very few independent groups, a bootstrap can describe the empirical sample's coarse variability but cannot create broad domain coverage.

The exact two-family distribution later in the chapter is useful for this reason. Its outcomes remain-1,0 and1 regardless of how many bootstrap draws are generated. Increasing the number of resamples approximates that distribution more precisely; it does not add new study families. A reported interval should therefore be accompanied by the number and nature of the underlying units.

## Separate question variation from model variation

A language-model system can vary because of which questions are sampled, which training seed produced the model, or which stochastic decoding draws were used. These are different sources of variation. Repeating generation many times for one question estimates behavior conditional on that question and model; it does not create many independent questions.

Similarly, evaluating one trained checkpoint on many cases does not quantify how much the training procedure varies across independently trained checkpoints. If that variation matters to the decision, the experiment needs a design that includes it. A single bootstrap over question rows cannot recover an unobserved distribution of training outcomes.

A practical report can state what is held fixed and what is varied. For example: the model checkpoint and decoding policy are fixed, while question families are resampled. Or: several independently initialized adapters are trained under the same protocol, each evaluated on the same families. The analysis should follow that design rather than applying one uncertainty calculation to every situation.

## Measure refusal and severe failures beside average quality

An assistant can reduce its error among answered questions by refusing more requests. Coverage shows the consequence. Appropriate refusals on unanswerable or unauthorized questions are valuable, while refusals on well-supported routine questions can reduce utility. Keep those categories separate so a candidate cannot appear universally reliable by avoiding difficult work.

Some failures also have decision rules that are not interchangeable with average quality. A required access boundary can be violated once even while a mean task score improves. The acceptance policy may treat that violation as a blocking condition. That is a declared engineering constraint, not a contradiction of the average's arithmetic.

Statistical uncertainty does not automatically cover measurement error. If a rubric systematically rewards confident unsupported explanations, a narrow confidence interval can precisely describe performance on the wrong target. Review disagreement cases, source-support labels and task coverage before interpreting precision as trustworthiness.

## Keep the final assessment outside development

Trying many prompt, retrieval and adapter configurations gives the team more opportunities to fit the development set. The best observed validation score can partly reflect selection noise. A final assessment that also guides later changes has joined the development process. The appropriate response is to record that use and obtain new independent evidence for a fresh final claim, rather than preserve the old test label while continuing to tune against it.

The output of the study should be a reproducible analytical artifact: paired case IDs, family definitions, weights, metrics, uncertainty method, failure categories and configuration identities. A generated narrative can explain that artifact, but it should not invent significance, change denominators or convert a system comparison into a causal claim about one component. This discipline becomes especially important when the next chapters begin updating model parameters.""",
)

chapter(
    14,
    """Supervised fine-tuning teaches the behavior represented by its examples and loss. This chapter develops a domain-training dataset from the assistant's task contract, then connects annotation quality, token masks, weighting and data splits to the behavior an optimizer is actually encouraged to learn.""",
    """## Turn an observed behavior gap into training examples

Suppose the Methods Desk consistently finds the right evidence but struggles to produce a stable analysis record. It sometimes mixes assignment_unit with analysis_unit, omits an unknown status or adds a causal conclusion to a descriptive result. Those are candidate behavior gaps for supervised adaptation after prompt and validation baselines have been measured.

A training record should show the intended response to a particular admitted input. It needs the question, relevant context, desired answer, source or annotation provenance and a family identity. For the assistant's factual statements, the target should be supported by the supplied evidence. For its numerical statements, the target should agree with the validated calculation artifact. A polished but unsupported target teaches the model to reproduce the same failure more consistently.

The dataset should include the decisions the system is expected to make. Supported requests need useful answers. Missing-information cases need a specific unknown result. Conflicting applicable sources need an explicit conflict or the declared precedence behavior. Unsupported causal requests need an explanation of the missing design evidence. If every example is an easy success, the model receives little supervision for the boundaries that make the assistant reliable.

## Teach dependence on evidence rather than a memorized answer

A domain model can learn a shortcut from repeated templates. If every conversion question in training has the answer0.3, success on a similarly worded evaluation question may not show that the model used the supplied counts. Vary the relevant inputs deliberately and check whether the target changes according to the rule. Preserve legitimate cases where the right answer remains unchanged as well, so the model is not rewarded for reacting to irrelevant differences.

For example, changing three purchases to four while holding ten eligible visits fixed changes the descriptive rate from0.3 to0.4. Changing an irrelevant source title should not change it. Removing the denominator should produce an incomplete-evidence outcome under the contract. These counterfactual pairs make the intended input-output dependency more explicit than repeated demonstrations of one final sentence.

The same principle applies to policy versions and units. A target should not use an old eligibility rule when the admitted context supplies a new applicable rule. A response about visits should not silently become an account-weighted estimate because a familiar phrase appears nearby. Annotation review must inspect those semantics before treating the records as a larger training corpus.

## The loss defines which parts of the record are learned directly

In causal language modeling, the model predicts the next token from the preceding sequence. The answer-only mask selects which prediction events contribute to the supervised objective. Prompt tokens still provide context, and answer loss can backpropagate through their representations. Excluding a prompt-prediction loss is different from making the prompt irrelevant to learning.

The indexed table later in this chapter shows why the first answer token is predicted at the final prompt position. That off-by-one detail matters: a mask based only on whether an input token belongs to the answer can remove the first answer target. A model may then learn later continuation patterns while receiving no direct supervised signal for how the answer should begin.

Formatting is part of that sequence. Role markers, separators and end-of-turn tokens depend on the intended tokenizer and template. A label mask should be checked against actual tokenized records and a collated batch. Character counts from the source text cannot reliably replace that inspection. The optional pretrained recipe later uses a different division of shifting responsibility from the manual helper, which is why its labels must be interpreted under its own trainer/model contract.

## Choose the weighting rule, not just the loss name

Let record i have m_i active answer tokens and mean token loss l_i. A global token mean is the sum of m_i*l_i divided by the sum of m_i. An equally weighted mean of record losses is the sum of l_i divided by the number of records. These objectives differ when answer lengths differ.

For an illustrative pair, one answer has ten active tokens with mean loss0.2 and another has100 active tokens with mean loss1.0. The token-weighted mean is(10*0.2+100*1.0)/110=102/110, about0.9273. The equally weighted record mean is(0.2+1.0)/2=0.6. The first gives the longer answer more influence. Neither is automatically correct for every assistant task; the intended population and behavior should determine the weighting.

Batching and gradient accumulation must preserve that choice. Averaging microbatch means equally can change a token-weighted objective when active-token counts differ. Report those counts so the effective denominator is visible. A record with no active target cannot contribute a defined mean supervised loss, while a truncated record with some active targets may still have lost a necessary ending or qualification.

## Separate semantic admission, splitting and token processing

Data splitting should occur at the unit relevant to transfer before examples are selected or rewritten for training. Related document versions and template variants can leak the same answer structure across nominally different rows. If the goal is to generalize to new source families, a split that leaves near-duplicates on both sides does not test that goal.

Packing several records into one sequence creates another boundary. An answer-only loss mask does not by itself prevent later records from attending to earlier records. The attention and position policy must match the intended independence between examples. Likewise, truncation should be evaluated after rendering the real template, because overhead can consume the space the answer was expected to occupy.

A useful data audit follows each accepted record through these transformations: source-supported target, family assignment, rendered tokens, active-label positions, truncation result and final batch representation. The audit identifies whether a failure is semantic, structural or numerical. More optimizer steps cannot repair a target that is wrong or a mask that supervises the wrong event.

The next chapter runs the complete update loop on a small decoder. Its literal tokens make those mechanics observable, while the dataset principles here explain what would be required for the same machinery to support a meaningful domain-assistant experiment.""",
)
chapter(
    15,
    """Full supervised fine-tuning makes the complete model available to the optimizer. This chapter follows one update from token inputs to parameter state, explains the role of Adam and teacher forcing, and shows how to read a tiny training result without turning it into a claim of domain expertise.""",
    """## Treat training as a state transition that can be inspected

The Methods Desk dataset now defines a behavior worth testing. Before using a pretrained model, the course reduces the machinery to a small causal decoder with literal token IDs. The reduction keeps the computation real: embeddings, attention, normalization, a feed-forward block, logits, loss, backward propagation and optimizer updates all execute. It removes the temptation to explain a successful run as natural-language understanding when the visible task can be examined directly.

Let theta_t denote the model state after t optimizer updates. A training iteration first evaluates the objective at theta_t, computes its gradient and then constructs theta_(t+1). The recorded loss belongs to the state at which it was evaluated. This is why the last value in a20-iteration pre-update curve describes theta_19, while a final post-training evaluation describes theta_20.

The qualified reference preserves that distinction. It recomputes final training loss from the frozen final state, alongside held-out loss. A report should identify which state produced each number. Otherwise a seemingly minor logging label can make two candidates or two datasets appear to have been evaluated at the same checkpoint when they were not.

## Follow the supervised signal through the decoder

The two training rows contain prompt and answer symbols. After shifting, the model receives three input positions per row and predicts a16-way vocabulary distribution at each position. Only four target positions contribute to the answer objective. The shape ledger later in the chapter shows how a[2,3] token matrix becomes[2,3,32] hidden states, two attention heads and finally[2,3,16] logits.

At an active target position, cross entropy encourages the target logit relative to the other vocabulary logits. Its derivative contains the predicted class probabilities minus the target indicator, scaled by the active-event denominator. This local derivative then flows through the output projection, feed-forward and attention paths into earlier parameters. The independent zero-logit probe isolates that first step without relying on the randomly initialized decoder's output.

The ignored prompt-prediction positions have no direct loss term. Their representations can still influence later answer positions through causal attention, so prompt embeddings can receive gradients from the answer objective. That is the desired conditioning relationship. A mask that removed the prompt from the forward graph would define a different learning problem.

Full SFT describes the parameter set available for optimization. It does not require every scalar to change on every batch. An embedding row for a token never used as an input can have zero input-embedding gradient in this untied model. Unused position rows can likewise remain unchanged. The reference checks that all parameters are trainable and that an embedding tensor actually changes; it does not falsely require every entry to move.

## Adam adds optimizer state to model state

Ordinary gradient descent uses the current gradient directly. Adam also maintains moving estimates of its first and second moments. In a coordinatewise description, m_t=beta1*m_(t-1)+(1-beta1)*g_t and v_t=beta2*v_(t-1)+(1-beta2)*g_t². Bias-corrected versions divide by1-beta1^t and1-beta2^t. The update then scales the first-moment estimate by the square root of the second-moment estimate plus epsilon. The versioned PyTorch documentation specifies the concrete implementation options. [PyTorch2.9 Adam](https://docs.pytorch.org/docs/2.9/generated/torch.optim.Adam.html).

Those moments are part of a training restart, even though they are not needed for ordinary model inference. Restoring only model weights and restarting Adam from empty state can produce a different trajectory. Learning-rate scheduling, random state and data order can add further restart requirements. The tiny exercise starts from a declared initial state and uses a fixed update count; it does not claim to implement a complete resumable training service.

Adaptive scaling also does not guarantee that every step lowers the objective or that the chosen learning rate is appropriate. The fixture requires finite logged values and an improvement over its initial loss. A realistic experiment should inspect unstable updates, parameter changes, gradients and validation behavior rather than treating the optimizer's name as a convergence certificate.

## Teacher-forced loss and generated answers are different observations

During training, each answer position sees the earlier correct answer tokens supplied by the dataset. During autoregressive generation, it sees its own earlier outputs. An early generation mistake can therefore change later inputs in a way that teacher-forced evaluation did not exercise. A lower token loss is useful evidence about the declared predictive objective, but it does not by itself establish exact-match generation or correct stopping.

The literal held-out row changes the first prompt token while retaining a familiar second prompt token and answer. A model could succeed by using the latter token as a shortcut and largely ignoring the changed prefix. That makes the row a small transfer probe, not a demonstration of reasoning about an unseen domain. More informative cases would vary the dependencies that the intended task requires and include changes that should and should not alter the answer.

A domain-assistant evaluation must also inspect the content of generated responses: unsupported fields, wrong units, invented citations, inappropriate refusals and regression on previously useful tasks. Those outcomes cannot be recovered from training loss alone. If the model learned an unsupported target from the dataset, successful optimization can make the error more consistent.

## Read a training receipt as evidence, not endorsement

A useful receipt identifies the data, model configuration, target mask, optimizer settings, update count and the state used for evaluation. It preserves both successes and failures. In this course, actual parameter changes and finite losses establish that the training machinery ran. The literal vocabulary, two training rows and one visible transfer row limit the task claim.

Forgetting and overfitting require separate observations. A candidate may improve the supervised task while worsening another capability, or may memorize the training templates without transferring. Keep baseline-retention tasks and untouched evaluation families when the experiment moves to a realistic domain dataset. The next chapter constrains the update through low-rank factors, but the need for those measurements remains.""",
)
CHAPTERS["llm-applied-015"]["mental_from"] = "We update every parameter for exactly20 steps"
CHAPTERS["llm-applied-015"]["mental_to"] = (
    "All model parameters are eligible for the20 optimizer steps"
)

chapter(
    16,
    """LoRA constrains a model update to a factorized subspace while retaining the frozen base computation. This chapter connects the matrix derivation to a domain-adaptation decision, explains why placement and scaling matter, and follows the adapter from initialization through evaluation and inference merging.""",
    """## Constrain the update without changing the task definition

The Methods Desk team has a stable extraction-format gap and a reviewed dataset. Full SFT makes all model parameters available to the optimizer. LoRA offers another hypothesis: perhaps the required behavior can be learned through a smaller additive update at selected linear transformations. This is a restriction on the adaptation mechanism, not a change in what counts as a correct supported answer.

In the row-vector convention used here, the effective map is X(W+sAB). W is the frozen base, A maps the input features into r intermediate directions, B maps those directions to the output, and s=alpha/r controls their scale. The trainable factors contain r*(Din+Dout) entries instead of Din*Dout entries for a free full matrix update. The product AB has rank at most r.

That bound is a capacity statement about one update matrix. It does not prove that the task needs only r directions, that training uses all of them or that a small rank is universally sufficient. The original LoRA work provides empirical evidence for the method on particular models and tasks; the small fixture below supplies an independently checkable instance of its mechanics. [LoRA](https://arxiv.org/abs/2106.09685).

## Initialization creates a useful controlled starting point

Starting B at zero makes the initial additive update zero, so the adapter preserves the base function before training. A is nonzero so B can receive a useful first gradient. If both factors were zero, the ordinary factor gradients would also be zero in this branch and that update rule would remain stuck at the initial product.

The apparently asymmetric first step is therefore expected. The derivative for A contains B, so A's first gradient can be a connected zero while B's gradient is nonzero. That is different from a missing gradient caused by detach, an absent parameter or an optimizer that does not own the factor. The exact example derives every B-gradient entry as0.5 and the first updated output as0.8, giving a concrete anchor for that reasoning.

The example's symmetric factors produce a rank-one update within a rank-two parameterization. This is useful evidence about the realized product. It prevents a common interpretive mistake: treating configured rank as a guarantee that every direction became independently useful. Factor columns also do not have uniquely identified semantic meanings, because multiple factorizations can represent the same product.

## Placement determines what the adapter can change

An output-head adapter changes how existing hidden representations are mapped to vocabulary scores. An adapter in attention projections can affect another part of the computation, while feed-forward or embedding adaptations reach still different transformations. The same rank number at different target modules therefore describes different hypothesis classes and parameter budgets.

For the Methods Desk, a formatting failure and a failure to distinguish two domain concepts may respond differently to those choices. If the hidden representation already separates the relevant cases, a narrow output adaptation might be enough. If the model does not represent the distinction needed by the task, a final projection alone may be limited. Those are testable hypotheses, not guarantees based on module names.

Rank and scale should be considered together. Increasing rank while keeping alpha fixed changes the alpha/r multiplier, as well as the number and initialization of the factors. Comparing two configurations without recording those choices can attribute a difference to rank while several parts of the effective update changed. Learning rate, target modules, dropout and data weighting add further conditions to the comparison.

## Frozen weights can still carry gradients

Freezing W means its values are not updated by the optimizer. It does not generally mean that the forward operation involving W should run outside autograd. Suppose an earlier trainable stage produces h=f_phi(x), followed by y=hW. The derivative with respect to phi still depends on propagation through W, even when W is treated as a constant.

Putting the whole hW operation under no_grad would remove that path to the earlier trainable stage. This distinction matters when adapters appear at several depths in a model. The correct freezing policy controls parameter updates while preserving the computation graph needed by the trainable parts. The literal matrix fixture has a simpler dependency structure, but its derivative formulas make the principle visible.

Optimizer membership must match the intended trainable set. A factor with requires_grad=True is not updated unless the optimizer owns it and step is called. Conversely, a mistaken explicit assignment can alter a supposedly frozen base even when its gradient flag is False. Parameter counts, ownership checks and before/after base comparisons provide complementary evidence.

## Merge only under a declared inference contract

In exact arithmetic, the factorized expression XW+s(XA)B equals X(W+sAB). A merged matrix can therefore represent the same linear function for inference. In floating-point arithmetic, reassociation and quantization can change the result, so compare outputs in the intended dtype and model mode under a justified tolerance.

Keep the original base separate when it is shared among adapters. An in-place merge can change the starting point for another adapter and make the artifact identity misleading. The saved configuration should identify the base revision, factor shapes, rank, scale, target modules, tokenizer and relevant runtime conditions. Matching tensor shapes alone does not prove that an adapter belongs to a particular base checkpoint.

Trainable-parameter savings also need a precise interpretation. The frozen base still occupies storage and participates in forward computation. Activations and attention intermediates may dominate memory for long contexts. The factor-count ratio is useful arithmetic, while peak memory and latency require measurements on the actual backend. The next chapter examines how quantizing the frozen base changes those accounting and numerical questions without changing the need for independent task evaluation.""",
)
chapter(
    17,
    """Quantized adaptation changes both the stored representation of the base and the learning problem faced by an adapter. This chapter separates rounding, packing, computation and task fitting, then explains how to compare quality and resources without turning a byte count into a hardware claim.""",
    """## Quantization introduces an approximation before adaptation begins

The Methods Desk team wants to reduce the resources required by a larger base model. Quantization replaces floating weights with a smaller set of representable values, usually together with scale or codebook metadata. That substitution changes the function before any adapter is trained. A later improvement must therefore be interpreted relative to both the original base and the quantized base.

The literal example uses a uniform grid with a scale derived from the largest absolute value. It rounds a2-by-2 matrix into signed codes, packs them into bytes and reconstructs approximate float32 values for computation. Each step has a different property: rounding loses numerical information, packing preserves the chosen codes, and dequantization reconstructs the approximation encoded by those codes.

The exact arithmetic below shows that a successful code round trip does not imply unchanged model output. The packed bytes can be perfectly correct while the reconstructed matrix produces a different result. That difference is the expected approximation error to measure before attributing a later task change to adaptation.

## Outliers explain a basic quantization tradeoff

Consider an illustrative uniform quantizer for weights[0.01,0.02,0.03,10] using the range-7 through7. A single scale based on the maximum is10/7, about1.4286. The three small weights round to zero because the grid is too coarse to distinguish them, while the large value uses the extreme code.

If the first three weights were represented in a separate group, their maximum-based scale would be0.03/7, about0.004286. They could then be represented much more accurately, at the cost of additional group metadata and a different computation layout. This explains why granularity and scale policy matter. It is an example of uniform quantization reasoning, not an implementation of NF4 or a claim that a particular block size is optimal.

A nonuniform codebook makes another tradeoff by placing representable values more densely in some regions than others. The original QLoRA method uses specific mechanisms including NF4, double quantization and paged optimizers. The CPU fixture implements none of those particular backend features. Its value is that the simpler codes, packing and adapter gradients can be derived directly before reading a larger implementation.

## Weight reconstruction and task behavior are different objectives

Let W be the original matrix and W_q its reconstruction. An adapter gives W_q+AB under the chosen orientation and scale. If the training target were exact original-model parity on all inputs, the desired correction would relate to W-W_q. That difference need not be low rank. A constrained adapter may approximate it well on some input directions and poorly on others.

Task adaptation can have a different target entirely. The runnable example trains toward zero output on one input. Its falling loss establishes progress on that objective, not recovery of the original matrix. Many matrices agree on one input vector while behaving differently elsewhere. A tiny fit should therefore be accompanied by an explicit statement of which directions or tasks were evaluated.

Input magnitude also affects output error. Small weight errors can be amplified when multiplied by large or aligned input values. The layer-level bound derived later uses the input's absolute values to make that relationship visible. In a full network, nonlinearities and later layers add further dependencies, so a local reconstruction bound is not automatically a bound on generated-answer quality.

A useful comparison separates four conditions: original base, quantized base, adapted original base and adapted quantized base. Keeping the same held-out task contract across them helps identify the degradation introduced by quantization and the behavior learned by the adapter. Without the unadapted quantized control, an adapter's improvement may conceal how much quality was lost earlier.

## Gradients use the reconstructed computation

The frozen codes do not need to be differentiable for this adapter experiment. Their reconstruction acts as a constant in a computation that also contains trainable factors. Gradients can flow into those factors and, when required by the architecture, through the constant base computation to earlier trainable stages.

That is different from optimizing quantization decisions themselves. The fixture does not learn the integer codes, use a straight-through estimator for rounding or update the scale. Those would define additional algorithms with their own assumptions and tests. Keeping the base representation fixed makes it possible to verify that the observed changes come from the intended adapter parameters.

The first factor-gradient asymmetry remains the same as in the unquantized LoRA example: a zero B can give A a connected zero gradient while nonzero A allows B to learn. Quantizing W changes the forward values and therefore the loss gradient, but it does not remove the need to reason about factor orientation, denominator and optimizer membership.

## Account for what is stored and what is live

Packed payload size describes a serialization or storage representation. Peak training memory describes the largest simultaneous set of live allocations. The latter can include packed weights, scales, reconstructed blocks or matrices, adapter parameters, gradients, optimizer state, activations and temporary kernel buffers. Their lifetimes depend on the backend.

The tiny example explicitly materializes a float32 reconstruction. Its six-byte logical packed representation therefore cannot be reported as the total memory used by the calculation. A backend that dequantizes blocks transiently may behave differently, but that behavior must be observed rather than inferred from the word4-bit.

For a domain-assistant decision, report numerical error, held-out task quality and measured resources separately. Include unsupported answers, exact identifiers and relevant retention tasks, because a small average loss change can conceal a costly domain failure. The next chapter applies the same discipline to comparing full and adapter fine-tuning under fixed evaluation conditions.""",
)

chapter(
    18,
    """An adaptation comparison is an experiment over complete configurations. This chapter explains how to align starting states, data, objectives and budgets, then connects parameter-level checks to a defensible choice for a subject-matter assistant.""",
    """## State the decision the comparison is meant to support

The Methods Desk team is deciding whether a stable response-format gap justifies adaptation and, if so, which update strategy is useful. Full SFT and LoRA are candidate mechanisms, but the actual decision also depends on the dataset, target modules, optimizer policy, serving constraints and quality rubric. A comparison should name that decision before collecting a favorable score.

One question is whether a small output-head adapter can fit the literal token task. Another is whether a realistic adapter improves supported domain answers under a memory budget. A third is whether full SFT retains useful general behavior after specializing. These questions require different evidence. The runnable experiment answers a narrow version of the first while establishing state controls that transfer to larger studies.

The unadapted prompt and retrieval baselines remain relevant. If the task is already solved by supplying the correct current definition and validating the output, training may add cost without addressing a necessary gap. If adaptation helps formatting but factual support remains limited by missing evidence, the final architecture may still need retrieval and tools.

## Align what should be held fixed

Copying one base state into independent model objects establishes a common starting function. Merely constructing two models after setting one global seed can produce different initial values because construction consumes random draws. The explicit state copy in the fixture is therefore a meaningful experimental control.

The candidates also share training examples, shifted inputs, answer masks and held-out records. Those controls keep the supervised events comparable. Separate optimizer objects prevent one candidate's state from influencing the other. Frozen-base snapshots verify that the adapter candidate preserves the values that its design says should remain fixed.

Some conditions necessarily differ. The full candidate has10464 trainable parameters, while the output-head adapter has96. Their hypothesis spaces are different by design. The fixed learning rates also differ in the fixture. A result can compare those complete configurations, but it cannot isolate an abstract method effect from every associated choice.

## Equal steps are one budget, not every budget

Twenty optimizer updates for each candidate align update count. They do not guarantee equal wall time, memory, gradient computation or optimization difficulty. An adapter can reduce trainable state while still running the base forward computation. Longer sequences can shift the dominant cost toward activations and attention rather than parameter updates.

A practical study can choose a resource constraint that matches the decision: equal data exposure, equal update count, equal tuning budget or a fixed time/memory limit. It should report the resulting tradeoff rather than imply that one comparison is universally fair. If each method receives hyperparameter tuning, keep that selection on development data and record the budget used to choose its final configuration.

Serving adds another dimension. An unmerged adapter can support switching among task variants while retaining a shared base. A merged artifact can change inference structure and deployment handling. Those choices affect operational complexity and must be tested under the intended dtype, model mode and artifact identity. Training parameter count alone does not settle them.

## Evaluate the behavior that motivated adaptation

Teacher-forced token loss measures the probability assigned to target continuations under supplied prefixes. It is useful for optimization diagnosis, but the Methods Desk needs more: valid structured fields, source-supported claims, correct calculations, appropriate unknowns and retention of relevant baseline behavior. A model can improve one of those dimensions while worsening another.

The tiny held-out row changes a prefix token but preserves a familiar answer pattern. It is deliberately not required to favor either candidate. That is an important testing principle: a held-out result is an observation to report, not an assertion that must be made favorable by tuning against it. The fixed fixture can reveal a mechanics failure without pretending to establish broad generalization.

A larger study should preserve actual generated outputs and their evidence context. If an adapted model uses the right field names but invents a denominator, format accuracy and grounded correctness must remain separate. If it refuses more requests, coverage belongs beside conditional quality. If it improves the target task but loses another useful capability, that regression is part of the decision rather than an unrelated inconvenience.

## Interpret a difference at the correct level

A lower loss for one candidate can arise from capacity, optimization policy, data fit or a useful inductive restriction. One run cannot identify all of those mechanisms. Paired evaluation over the same questions and repeated training where relevant can make the conclusion more informative, but the analysis must still match the observed design.

The output-head-only adapter also limits the scope of a negative result. Failure at that placement does not show that every LoRA configuration would fail, because adapters in attention or feed-forward modules can change different computations. Conversely, success on the tiny head task does not establish that the same rank and placement suit a pretrained domain assistant.

The report should retain the base identity, trainable set, target modules, rank/scale, optimizer settings, data and mask identities, update budget, evaluation artifacts and failure cases. This is the bridge from a reproducible training exercise to an engineering decision. The following preference and retrieval-training chapters change the objective again, so they need the same discipline about what signal is being optimized and what useful behavior is actually measured.""",
)
chapter(
    19,
    """Preference learning optimizes a comparison supplied by its feedback data. This chapter develops that comparison for a domain assistant, derives what the relative-probability objective rewards, and separates improved preference fit from factual support and a complete RLHF workflow.""",
    """## A preference label needs a substantive reason

The Methods Desk can produce two responses to the same question. One is concise, cites the applicable definition and preserves the computed denominator. The other is more polished but substitutes an unsupported population. A preference dataset should record why one is chosen. If the rubric rewards presentation alone, the training signal can favor the less trustworthy answer.

Other pairs may involve two supported answers with different levels of detail, or an appropriate abstention compared with an unsupported confident claim. These are legitimate but different feedback dimensions. Mixing them without a clear rubric makes the meaning of a lower preference loss hard to interpret. Retain the question, evidence, response identities, annotation rationale and disagreement state.

A pair is also conditional on its context. An answer that is preferable under one policy version or access scope may be unsuitable under another. If the chosen response includes evidence the actual caller could not access, the pair teaches an invalid behavior for that request. Data admission from the earlier chapters remains relevant after changing the optimization objective.

## Compare the policy with a fixed reference

For responses y_plus and y_minus to the same input x, define the policy log-probability difference as log pi_theta(y_plus given x) minus log pi_theta(y_minus given x). Define the analogous difference under a fixed reference policy. A DPO-style margin scales the policy-minus-reference advantage by beta, then applies a logistic loss that becomes smaller when that adjusted advantage increases.

The worked scalar example isolates this arithmetic: at equal adjusted margins, loss is log2 and the derivative has a known sign and magnitude. It performs a real SGD step on that scalar. A full language model would obtain the two log probabilities from token-level predictions and backpropagate through its parameters. The scalar itself is not a complete normalized policy over possible responses.

The reference makes the comparison relative to an existing distribution. A response pair already strongly favored by the reference has a different adjusted margin from an equally scored pair, even if the policy's raw difference is the same. Changing the reference checkpoint therefore changes the training objective. It belongs in the experiment's identity alongside tokenizer, response masks and beta.

## Relative advantage does not determine absolute probability

An illustrative probability example makes the distinction concrete. Suppose the reference assigns probabilities0.4 to the chosen response and0.3 to the rejected response, leaving0.3 for other responses. A candidate assigns0.3 and0.1, leaving0.6 elsewhere. The chosen response became less probable in absolute terms, but its advantage over the rejected response increased from4/3 to3.

The adjusted log-ratio is log(3/(4/3))=log(9/4), about0.81093. At beta0.5, the margin is log(3/2), and the logistic loss is log(5/3), about0.51083, below log2. This is a hand calculation for valid illustrative distributions, not a measured model update. It shows why a preference-loss improvement should not be paraphrased as “every chosen answer became more likely” or as a task-accuracy improvement without examining the actual outputs.

Sequence scoring adds another assumption. A joint response log probability is a sum of conditional token log probabilities under the chosen mask and stopping convention. Averaging by response length defines a different score. Prompt positions, end markers and truncation must be handled consistently for policy and reference. A convenient normalization should not be introduced silently while retaining the interpretation of a different objective.

## Feedback can reward a shortcut

If preferred answers are consistently longer, the model may learn length-related behavior that correlates with the labels without improving evidence use. If a judge prefers confident language, a cautious supported answer can be penalized. If almost every chosen response contains a particular boilerplate phrase, that phrase can become a shortcut. Review such correlations before treating the feedback as an unambiguous quality signal.

Counterexamples help define the desired behavior. Include a fluent answer with a wrong denominator, a correct concise answer, a legitimate unknown, an irrelevant citation and a qualified explanation that preserves the source's assumptions. A model-based annotator can help produce proposals, but its labels need the same validation and disagreement analysis as any other measurement process.

The evaluation should retain the underlying domain contracts: source support, numerical fidelity, access boundaries, useful coverage and baseline retention. Preference agreement is another outcome. It does not replace them. A candidate can match training preferences more closely while making an unacceptable change on a rare but consequential question family.

## Place DPO within the broader feedback landscape

Many RLHF workflows train a reward model from feedback and then optimize a policy using generated rollouts and a regularization or reference relationship. Those stages introduce additional learned state, sampling and reward-model behavior. Offline preference objectives such as DPO use a different route from fixed preference pairs to parameter updates.

The distinction is about the executed mechanism, not a hierarchy of reassuring names. This chapter does not train a reward model or run online reinforcement learning. A larger workflow would need artifacts and measurements for each stage, including how its feedback relates to actual task utility. The original DPO paper supplies the method behind the simplified margin exercise; the local numerical proof does not inherit every result from that larger setting.

For the Methods Desk, preference learning is useful only if it improves the behaviors the application values under an independent assessment. The next chapter returns to another trainable component: the retriever and reranker that determine which evidence reaches the answer model in the first place.""",
)

chapter(
    20,
    """Retrieval adaptation learns which evidence should be nearby or highly ranked for a question. This chapter develops domain relevance labels, positive and negative construction, contrastive objectives and index consistency, connecting the tiny gradient example to a realistic retrieval-training study.""",
    """## Train the relationship the analyst actually needs

The Methods Desk repeatedly retrieves a general variance passage when the question concerns uncertainty for repeated visits within accounts. This may be a representation gap rather than an answer-model gap. A retrieval-training example can pair that question with the relevant account-level method passage and distinguish it from a topically similar but unsuitable passage.

Relevance is conditional on the query. A visit-level analysis page can be useful for a different experiment and a negative candidate for this account-level question. Labeling the whole document as globally bad would lose that distinction. Store the query, positive evidence, negative candidate, source identities and the reason the pair expresses the intended task.

The task may have several valid positive passages. One can state the rule directly, while another supplies an equivalent explanation under the same assumptions. Treating every nonselected passage as negative can push away useful evidence. Annotation should preserve alternatives and uncertainty rather than force all candidates into a single-positive classification merely because the loss interface makes that convenient.

## Understand what the contrastive denominator means

For a query q, a common single-positive contrastive objective is the negative log of exp(score(q,d_plus)/tau) divided by the sum of those exponentials over the candidate documents. The denominator defines the alternatives the model must distinguish. The temperature tau changes the scale of score differences and the gradient, so it is part of the objective rather than a display parameter.

With two identical scores, the positive probability is one-half and the loss is log2. With three identical scores and one designated positive, the loss is log3. A change in negative-set size can therefore change the initial loss scale even when the representation has not improved or worsened. Compare ranking and held-out relevance beside the optimization curve.

A false negative can make the task contradictory. If the positive and negative are the same document under the same representation, their scores cannot be separated by changing a shared encoder. With only those two identical candidates and a single-positive target, the probability remains one-half. A multi-positive formulation or corrected labels may be appropriate, depending on the actual evidence relationship. More training cannot resolve a contradiction created by the dataset definition.

The tiny reference uses two fixed identity-feature pairs, so the first gradient can be derived exactly. It establishes that the optimizer changes the projection in the direction implied by the labels. It does not establish a tokenizer, a pretrained semantic representation or a domain benchmark. The later held-out feature probe tests one point relative to the learned linear boundary.

## Mine difficult cases without turning them into wrong labels

Random negatives can be easy enough that the model learns only broad topic differences. Hard negatives are candidates a retriever currently ranks highly despite their being unsuitable under the task. They can expose the fine distinctions the assistant needs, such as account versus visit units, a superseded definition or a missing exception.

Hardness does not establish incorrectness. A highly ranked candidate may be another valid answer or may contain the relevant fact in a different span. Review those cases before using them as negative supervision. Exact IDs help detect direct collisions, while content and family relationships can reveal near-duplicates or alternative positives with different filenames.

Mining also belongs to the development history. Record which retriever and corpus snapshot produced the candidates. Keep final assessment labels out of training and selection. A retrieval corpus may legitimately contain documents used during evaluation, but using their held-out relevance judgments to construct training pairs changes the independence claim.

## A reranker learns a different interface

A bi-encoder supports reusable document vectors and relatively cheap candidate search. A reranker can jointly inspect a query-candidate pair and learn a more detailed ordering inside a bounded pool. A pairwise objective such as softplus of the negative positive-minus-negative score margin rewards the chosen candidate over the rejected candidate for that query.

That relative score does not automatically calibrate across queries. A high score for one easy query and a lower score for another can reflect different score distributions rather than different probabilities of relevance. If the application needs an answerability threshold, calibrate and evaluate that decision separately under the relevant request population.

The candidate ceiling remains. A well-trained reranker cannot recover evidence absent from its input unless the system explicitly performs another admitted retrieval step. Report candidate recall, reranked ordering and final-context sufficiency separately. Otherwise an answer-stage failure may be incorrectly attributed to the component that merely received an incomplete pool.

## Rebuild the serving representation after adaptation

Updating an encoder changes the coordinate system used for retrieval. Query and document representations must remain a compatible pair. If document vectors are produced by an old encoder while the query side uses a new incompatible one, dimensions can still match and the scores can still be finite. Those arithmetic facts do not establish meaningful similarity.

A release should bind encoder identity, tokenizer/preprocessing, pooling, normalization and index build. Evaluate exact vector search before attributing a miss to an approximate index. Retain lexical and unadapted baselines so a domain adaptation that helps paraphrases but harms exact identifiers is visible.

Finally, measure the effect on the assistant's answers. A retriever can improve its own ranking metric while supplying context the generator misuses. The complete task still requires supported claims, valid calculations and appropriate abstention. Retrieval training is one targeted intervention in that evidence path, not a replacement for its other contracts.""",
)
chapter(
    21,
    """A pretrained-model experiment connects the earlier concepts to real artifacts, tokenizers and training software. This chapter follows the qualified optional recipe from preparation through reload and generation, explaining exactly what its successes and its observed failure establish.""",
    """## Move from literal tokens to a model with a prior history

The tiny decoder began with randomly initialized weights and an authored vocabulary. A pretrained model arrives with a tokenizer, architecture, learned parameters, chat formatting and a history of training that this course does not reproduce. Those artifacts are part of the experiment's starting state. A model name alone is too imprecise to identify that state when a repository branch can change.

The optional recipe pins one SmolLM2-135M-Instruct revision and verifies the acquired local files. It also uses a separately prepared dependency environment with platform-specific locks. This makes the transition to a real model explicit without changing the ordinary classroom's offline fixtures. Reading the chapter does not acquire weights or start training; the separate recipe documents those deliberate actions.

The qualified run is evidence for a bounded path through that particular environment. Its source, manifests and receipts should be read together. A successful dependency resolution on another architecture is useful preparation, but it is not an executed result on that architecture. Likewise, a matching file hash proves identity relative to the recorded artifact, not answer quality.

## Inspect what the small dataset is actually teaching

The four training examples ask for only the assignment unit. They map statements about randomized accounts, racks and hosts to singular labels, and map an unspecified assignment description to unknown. The evaluation example uses clusters. The family labels are disjoint, but all examples share a narrow extraction task and a closely related prompt form.

That structure is valuable for testing formatting, masks and actual updates. It is much weaker evidence for a broad subject assistant. A model can improve this task by learning how to emit the requested short label without learning a new statistical concept or a general policy for causal interpretation. The held-out cluster label tests one small transfer beyond the training entities, not independent coverage of business questions.

A domain dataset intended to teach evidence use would need a broader range of supported and unsupported requests, units, source conflicts and counterfactual inputs. The earlier data-design chapter explains how to construct those cases. Scaling the number of optimizer steps on these four records cannot manufacture the missing diversity.

## Verify the model's actual token interface

The recipe renders the prompt with its generation marker and renders the prompt plus completion as a full conversation. It requires the prompt token IDs to be an exact prefix of the full sequence. That check establishes the boundary for this tokenizer/template pair. It is more reliable than inferring the boundary from character length or assuming that every chat template uses the same markers.

The trainer receives completion-only supervision and no packing in the documented recipe. Before training, the script inspects processed examples and an actual collated batch. Prompt labels are ignored, active labels match the corresponding input IDs, and the causal model performs the shift internally. This differs from the earlier manual helper that explicitly created shifted inputs and labels. Applying both shifts would optimize the wrong prediction events.

The length limit is also an admission rule. Overlong records are rejected rather than silently truncated into partial answers. That policy trades dataset coverage for a clear target contract. Another application might use a reviewed truncation or segmentation policy, but it would need to inspect which answer and stop tokens survive.

## Separate execution mechanics from the model's usefulness

The documented Linux arm64 recipe completed ten full-SFT updates and ten LoRA updates. The full path had134515008 trainable parameters; the adapter path had230400. Both produced saved artifacts and evaluation measurements. Those observations establish that the intended training and artifact operations executed in that environment.

The held-out token losses changed substantially differently for the two paths. The full model's recorded loss fell from6.721148 to0.008058, while the LoRA path's fell to6.474194. The narrow dataset and single evaluation record are essential context for those numbers. They do not establish a general ranking of adaptation methods, nor do they measure supported-answer quality on a representative domain workload.

Reload adds another evidence tier. A saved adapter must be combined with the intended base and tokenizer under the recorded configuration. The recipe performed that reload and generated a response offline. Two same-environment LoRA runs also matched artifact hashes and evaluation loss after the seed was placed before adapter construction. That is a concrete repeatability result under the tested conditions, not a promise of bitwise equivalence across every platform.

## Learn from the wrong formula that the model generated

The generation probe supplied the correct conversion definition as evidence. The saved adapter nevertheless described eligible visits divided by eligible visits, which is the wrong formula. The answer was fluent enough to appear plausible while failing the central domain claim. Its supplied evidence IDs also did not establish validated claim-level citations.

This result connects several earlier chapters. Retrieval can supply the right text without guaranteeing that generation uses it. A completed optimizer run can improve a narrow token objective without improving an unrelated analytical task. Saving and reloading an adapter proves an artifact path, while the returned answer still needs semantic and numerical evaluation.

The correct response to that failure is to preserve the generated artifact and classify the error. It may motivate a better prompt, a more appropriate dataset, a constrained calculation interface, or an evidence-use evaluation. It does not justify rewriting the expected answer after the fact or describing the model as a domain expert because training completed successfully.

## Reproduce a bounded experiment before expanding it

A learner reproducing the recipe should identify the exact environment, asset snapshot, dataset, masks, optimizer configuration and output directory, then retain the resulting receipt. Existing artifacts should not be silently overwritten by a retry. A failed preparation or training step remains a failed step until repaired and rerun; a success receipt should follow actual execution.

The [optional recipe](../fixtures/pretrained/README.md) contains the concrete Docker-first commands and current execution record. They are separate from the written cases below. The next chapter focuses on a complementary way to improve the Methods Desk: let a model propose a bounded analytical operation, while trusted code computes and records the result that the final explanation must use.""",
)

chapter(
    22,
    """Tools connect language proposals to explicit analytical operations. This chapter follows a request through validation, data admission, computation and explanation, showing how typed interfaces and stable arithmetic support a data scientist without turning a model's wording into execution authority.""",
    """## Treat a tool call as a proposal with a defined meaning

An analyst asks the Methods Desk to compare average outcomes by group. The model can help identify a suitable operation and fill a structured request, but the application must decide whether that request is allowed and whether its inputs satisfy the operation's assumptions. The model's output is data presented to that decision, not an arbitrary program to execute.

The fixture exposes one operation: group_mean over named group and value fields. Extra keys and unsupported operations are rejected. This small interface makes the computation easy to inspect and gives the learner a concrete baseline before considering a larger tool catalog. A real database-backed operation would additionally need authenticated data access, a reviewed query shape and a snapshot or consistency policy.

The operation catalog should correspond to useful analytical tasks. A count, a grouped mean, a validated join or a predeclared confidence-interval calculation can each have a clear input and output contract. Exposing unrestricted text execution because it is flexible moves many unresolved decisions into the model proposal. The narrower interface lets the application preserve units, grain and resource bounds explicitly.

## Trace the data as carefully as the requested operation

The accepted request does not establish that the rows are appropriate. The application must know which observations the principal may use, which reporting period they belong to and what one row represents. The fixture uses one uniquely identified observation per row and rejects duplicate IDs. A join that duplicates a row would otherwise change the weight it receives in the mean.

For group A with values1 and3 and group B with value10, the tool returns counts and means: A has count2 and mean2; B has count1 and mean10. The difference of means is eight. Retaining counts makes the result interpretable and allows the overall observation mean to be reconstructed as14/3. Averaging the two group means instead yields six and defines a different weighting rule.

Missingness is another part of the contract. Replacing a missing measurement with zero or dropping it silently changes the denominator and possibly the population. The fixture rejects missing values under its strict policy. Another operation could support missingness explicitly, but should then report which observations contributed and which policy was applied.

## Validate the numerical output, not only the primitive types

Finite numeric inputs can still lead to an unstable implementation. Two values of1e308 have a finite mean of1e308, but a naive intermediate sum can overflow. The qualified tool uses scaled summation and checks its result. This is an example of why typed input admission and computational correctness are independent obligations.

Different tasks require different numerical representations. Integer cents can preserve exact monetary totals under an appropriate domain contract; floating-point means introduce rounding. A statistical procedure may need conditioning checks or a meaningful tolerance. The tool's output should state the method and units rather than presenting every numeric value as exact in the same sense.

The current example is deterministic over its accepted in-memory rows. A remote query can observe changing data between two calls, so repeating the same request text does not necessarily reproduce the same result. A larger analytical artifact should retain a data snapshot or equivalent source identity, the operation/code version and the relevant policy. Those identities let the analyst distinguish changed input from changed implementation.

## Keep execution and explanation as separate stages

After the dispatcher returns a structured result, the language model can explain it. That second stage must preserve the values, units and scope of the artifact. A response saying group A's mean is20 when the tool returned2 is an output-validation failure, even if the prose is otherwise clear. A response calling the difference a causal effect adds a claim the grouped mean did not establish.

A structured report can refer directly to result fields and render reviewed phrases around them. More flexible prose can be checked through a separate claim-extraction and validation process. Either way, the calculation artifact remains the numerical source. Asking the generator to recompute the number from memory creates another opportunity for divergence.

The analyst's requested interpretation may require additional work. A mean difference can reflect selection, confounding, measurement or random variation. A tool that calculates it correctly does not establish random assignment, independence or a suitable uncertainty model. The assistant should identify the missing design evidence and, when appropriate, propose a separate reviewed analysis rather than claim that the arithmetic already answered the causal question.

## Bound the operation through its lifecycle

The fixture's row limit controls one dimension of work. A serving tool also needs a duration limit, cancellation behavior and explicit handling of partial failure. A retry policy should distinguish whether the previous operation merely failed to return a result or may already have produced a side effect. The pure grouped-mean example has no external mutation; operations that write data need a separately defined authorization and recovery contract.

Tool results and errors are also untrusted inputs to a later model stage. An error message should not be allowed to redefine the operation catalog or request broader access merely because it appears in a tool-output field. The application retains control of which next actions are admissible, while the model can propose a useful explanation or recovery step within that boundary.

The next chapter combines these lifecycle concerns with freshness, caching and observability. Together they make a domain assistant reviewable as a system: a question leads to admitted evidence and data, a bounded computation produces an artifact, and the final answer is checked against what actually happened.""",
)
chapter(
    23,
    """A useful assistant must preserve its evidence contract while time, permissions and runtime conditions change. This chapter follows failures through a request lifecycle and explains how freshness, work budgets, cancellation and observability support reliable behavior beyond a successful model call.""",
    """## Follow one request through changing system state

Consider a serving design for the Methods Desk. A request is admitted under a principal's policy, retrieves an applicable handbook version, obtains a validated calculation, checks the proposed answer and returns it. Each transition should produce enough information to explain what happened. The local code below exercises only a few of those boundaries: time admission, a call counter and selected trace fields.

A failure should remain attached to its stage. Missing evidence is different from a retriever timeout. A denied source is different from an empty public corpus. A valid tool request whose computation failed is different from an unsupported operation. These distinctions help an operator repair the system and help the analyst understand what can be concluded from a partial result.

The outward explanation may be less detailed than the internal trace when disclosure policy requires it. A public response should not reveal restricted document identities simply to explain why it could not answer. The system can preserve a precise internal category without copying sensitive content into a broadly visible log or user message.

## Freshness is a policy over the relevant kind of time

The chapter's age rule compares a source publication time with an injected UTC now. It is useful because the exact boundary can be tested: at the maximum permitted age, a source is admitted; just beyond it, it is not. Future timestamps fail rather than becoming evidence that is indefinitely fresh.

A real question may need a different temporal interpretation. Publication, effective date, ingestion, last verification and data-event time describe different facts. A recently downloaded old policy is not necessarily current. A historical question may legitimately require an old source. The application should identify which time field its freshness or applicability rule uses.

Requests also take time to execute. A source can change between retrieval and response release. One policy may pin a consistent snapshot for the duration of a request; another may require revalidation before answering a current-policy question. Neither behavior is supplied automatically by a timestamp comparison. The serving contract must state how it handles such changes and keep the relevant versions in the result.

## A resource budget has several dimensions

The local Budget counter limits admitted operations. It cannot bound the time taken by one operation, the size of its result or the amount of model context it creates. A fuller design may track tool calls, retrieved documents, tokens, bytes and elapsed time separately. Those budgets should be charged at the points where resources are committed, with clear behavior for failure and retry.

For a serial pipeline, stage latencies add. Two independent retrieval branches that truly run in parallel can instead contribute approximately the larger branch latency plus coordination overhead, while still consuming the work of both branches. This distinction explains why latency and total resource cost can move differently. Actual scheduling, contention and backend behavior require measurement; the arithmetic is a planning model.

A deadline should propagate through the stages that can consume it. Starting a long model call when almost no request budget remains may guarantee a timeout after expensive work has already begun. Cancellation also needs an observed lifecycle: a request that is no longer useful should not leave unbounded background work merely because the caller stopped waiting.

The call-counter example intentionally counts an admitted attempt before the operation. If that operation fails, the attempt has consumed budget. A retry policy that refunds every failure can create an unbounded loop; a policy that never retries can reduce completion unnecessarily. Decide which failures are retryable and whether the previous attempt may have produced a side effect. A pure in-memory calculation is simpler than a remote mutating operation, so their recovery contracts should not be conflated.

## Make traces useful without turning them into another corpus

A diagnostic record can identify request, policy, corpus/index/model versions, admitted source IDs, operation counts, durations and a named result. Those fields help locate whether an incident came from stale data, a policy change, a timeout, a numerical failure or an unsupported answer. Raw private queries and unrestricted source bodies are not always needed to make that diagnosis.

A field-name allowlist is only a beginning. If the allowed request_id value contains a private query, the key is approved while the content still violates the intended trace contract. Values need their own types, length bounds and permitted categories, and the trace store needs an access and retention policy. The tiny helper demonstrates omission of certain keys, not a complete privacy-preserving logging service.

Quality monitoring also needs labels appropriate to the claim. A rising average retrieval score does not establish that answers became more correct. A lower refusal rate can indicate improved evidence coverage or more unsupported answering. A model or corpus fingerprint change can identify when behavior shifted, but it does not explain the cause without representative failure examples and evaluation.

## Repair incidents through the evidence chain

If a current-definition answer uses an old policy, compare the source snapshot, index build and cache identity. If a valid calculation is misquoted, inspect the result-to-explanation interface. If a request exceeds its budget, inspect retries and cancellation rather than only the final timeout message. If a model follows an instruction embedded in evidence, inspect both model behavior and whether the application allowed any unauthorized operation to proceed.

An incident can become a useful development case, but doing so changes the evaluation history. If its answer or failure label is used to revise a prompt or training dataset, it belongs to development from then on. Preserve independent cases for a fresh assessment. The final chapter brings these ideas together into a reviewable assistant design while keeping the course's actual executed baseline distinct from the larger system it motivates.""",
)

chapter(
    24,
    """The capstone assembles the reasoning developed across the route into one evidence-based assistant design. This chapter walks a realistic analytical request through the required interfaces, then compares that design with the exact local baseline and the separately executed pretrained experiment.""",
    """## Return to the analyst's original question

The Methods Desk began with a request for conversion and an interpretation of a checkout change. The course has now supplied the concepts needed to answer that request carefully: applicable source versions, structured extraction, retrieval, support checks, deterministic tools, adaptation objectives and operational boundaries. The final task is to connect them without claiming that a list of components is already an integrated system.

Use the illustrative event case from the opening chapter. There are12 recorded visits and four purchases, including two visits and one purchase from test accounts. Under the stated exclusion policy, the descriptive rate is3/10=0.3. A useful answer identifies the reporting period, the applicable definition and exclusion, the calculation artifact and the limits of the interpretation.

Notice that both4/12 and3/10 satisfy a simple count schema with purchases no greater than visits. A numerical validator cannot decide which population was intended from those values alone. Eligibility and provenance must be established before the calculation. This is why the evidence chain matters even when the arithmetic is elementary.

The causal question needs more. A handbook instruction saying “Randomize by account” establishes a recommended design, not proof that a particular experiment actually followed it. The assistant needs the experiment's assignment and analysis evidence before claiming a treatment effect. A source can be authoritative about a method while not being evidence that the method was executed.

## Specify the interfaces that would carry the answer

A complete design starts by resolving the request's meaning: metric, period, population, desired comparison and effective access policy. It then admits the relevant corpus and data snapshot. Retrieval selects candidate evidence; context assembly preserves the facts needed for the requested claims. A proposal stage can extract fields or request a reviewed tool operation, but trusted validation controls admission to execution.

The calculation returns a structured artifact with inputs, units, method and relevant identities. The answer stage uses that artifact rather than inventing a second calculation. Claim validation checks whether the response's substantive statements are supported by the admitted sources and computed results. An unresolved definition, missing denominator, source conflict or unsupported causal claim produces an appropriately bounded answer.

These interfaces should make failures localizable. If the output is wrong, a reviewer can inspect the selected policy, accepted rows, computation and final claims separately. Without those artifacts, the entire investigation becomes a debate about whether the generated paragraph sounds reasonable.

A request can also succeed partially. The assistant may explain the current formula while lacking the data required to calculate it, or report a descriptive rate while declining a causal interpretation. The useful boundary is the set of claims supported by the available evidence, not a requirement to return either a complete confident answer or no information at all.

## Identify what the executable capstone actually connects

The local Assistant is intentionally smaller than that design. At construction it copies documents permitted by a supplied scope set. Its answer method maps fixed question keys to admitted document IDs and returns the first sentence with a versioned span. Unsupported or excluded targets return unknown without revealing the restricted identity. A separate conversion helper validates integer counts and a positive denominator.

That is an actual tested lookup-and-extraction path. It does not run the lexical or embedding retrievers, the trained tiny decoder, the optional pretrained adapter, a live identity provider or a dynamic freshness service. Those mechanisms were studied separately. Their existence elsewhere in the course does not make them part of this method's call path.

The fixed question map is a useful baseline because its evidence behavior can be inspected exactly. It also limits the natural-language task. A future interface must determine how a user's phrasing maps to the intended operation and evidence. That mapping needs its own evaluation, especially when a question is ambiguous, historical or asks for several claims together.

The first-sentence extraction has a similarly visible limit. It returns the formula sentence from the metric document, while the exclusion appears in the next sentence. A question requiring eligibility details needs that additional evidence. A precise citation to an incomplete span does not turn the response into a complete policy explanation.

## Compare candidate systems without merging their claims

A sensible progression retains the transparent extractive baseline, then evaluates a generative answer stage under the same question and evidence contract. An adapted generator is another candidate parameter state, and a changed retriever is another intervention. Compare them on identified cases and retain actual output artifacts, rather than filling a report with the answers the system was expected to produce.

Keep context and work budgets explicit. A candidate receiving more documents or a larger token allowance may be a better complete system, but that comparison does not isolate a model improvement. Likewise, a fine-tuned model evaluated on the templates that drove its training does not establish transfer to independent request families.

The course contains two distinct kinds of real evidence. The local capstone passes its fixed source, status, access and arithmetic checks. The separate pretrained recipe completed preparation, training, reload and generation, but its adapter produced an incorrect conversion formula despite supplied evidence. Both observations matter. They should not be combined into a fictional run in which the trained model automatically inherited the baseline's correct answer.

The capstone's local receipt therefore correctly records that pretrained generation was not executed within that baseline run. That does not deny the separate recipe's execution. It preserves the identity of each experiment so the reader can judge what was actually connected and tested.

## Evaluate the complete request, including useful refusal

The three fixed status cases contain one answered definition and two correct unknowns. Status accuracy is3/3, while answer coverage is1/3. That is an appropriate result for those authored cases, not a general assistant benchmark. A useful broader assessment needs representative supported questions, missing-evidence cases, access constraints, source revisions, calculations and interpretation requests.

Score numerical fidelity and support independently. Corrupt a citation span while keeping the answer text plausible. Change an eligibility rule while keeping raw counts fixed. Provide a correct tool result and check whether the explanation preserves it. Ask for a causal conclusion without assignment evidence. These controlled cases reveal which interface fails and prevent a broad average from concealing an important boundary.

Use paired case identities and justified family groupings when comparing candidates. Report coverage, accepted-answer quality, unsupported claims, severe boundary failures and resource use. A low loss or high preference score is one measurement, not a substitute for the task outcome. The analysis should retain enough counts and assumptions that another reviewer can reconstruct the conclusion.

## Make the final decision proportional to the evidence

A local no-go can be a successful capstone result. It means the learner can distinguish a functioning mechanism from evidence sufficient for a larger claim. The next experiment should address a named missing requirement: natural-language intent mapping, representative domain evaluation, actual integrated generation, authenticated access, freshness/revocation behavior or bounded serving under failure.

The same discipline applies when a candidate does improve. Preserve the baseline and the failed cases, identify the configuration that earned the result, and state the population and conditions under which it was measured. A subject-matter assistant becomes useful through that sequence of explicit improvements, with retrieval supplying evidence, adaptation learning justified behavior and tools producing reproducible analytical artifacts.

The lasting skill is the ability to follow an answer backward: from its claim to its calculation or source, from that artifact to admitted inputs and versions, and from an observed result to the experiment that produced it. That makes the assistant's help something a data scientist can examine and improve rather than merely trust.""",
)
