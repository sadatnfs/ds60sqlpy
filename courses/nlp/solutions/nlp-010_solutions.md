# nlp-010: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Trace the first column

The N partial path begins with .6*.6=.36 and the V path with .4*.1=.04. These scores include both starting plausibility and observation likelihood. Choosing only the largest emission would omit part of the model. Store one score per ending state rather than one global winner.

**Expected:** Exponentiated initial scores are [0.36,0.04].

## Exercise 2: Implement backpointers

The N,V path wins after accounting for the transition factor. Backpointers preserve which earlier state produced each final candidate. Returning only the final state loses the sequence. The reference checks the exact probability and alignment length, so a decoder with a correct final label but wrong history cannot pass.

**Expected:** Path [0,1], probability 0.0756 and two labels for two observations.

## Exercise 3: Compare an independent oracle

Exhaustive enumeration independently multiplies the factors for each path. It is feasible only because the fixture is tiny, but it provides a meaningful implementation oracle. The second example demonstrates that selecting each token's favored state independently does not respect sequence transitions.

**Expected:** First optimum N,V at 0.0756; second optimum V,V at 0.1386.

## Exercise 4: Handle boundaries

The empty product has probability one under the API convention. A zero likelihood for every state leaves no possible complete path and must not quietly produce state zero. Exact ties are different: several valid optima exist, and first-index argmax gives a deterministic documented choice.

**Expected:** Empty path/log score 0; impossible row raises ValueError; tied fixture chooses [0,0].

## Exercise 5: Validate BIO structure

The validator checks structural continuity. It does not know the words or whether the entity type is semantically correct. Keeping this boundary explicit avoids confusing a legal label sequence with a good named-entity recognizer. Other corpus conventions require a deliberate alternative policy.

**Expected:** Valid [B-ORG,I-ORG,O]; reject leading I-ORG and a PER-to-ORG continuation.

## Exercise 6: Compare token and entity evidence

The gold entity covers token positions [0,2), while the predicted entity covers [0,1). They overlap but are not equal typed spans. Exact entity scoring therefore counts a false positive and false negative despite two matching token labels. The evaluation unit must match the extraction use case.

**Expected:** Token accuracy 2/3 but zero exactly recovered two-token ORG entities.

## Transfer and limits

Sequence labeling assigns a label to every token while accounting for relationships among neighboring labels. Part-of-speech tagging, entity tagging and some segmentation tasks have this shape. A document classifier returns one label for a whole document; a sequence tagger returns an ordered label sequence aligned with tokens. Losing that alignment can make a numerically valid output unusable.

A hidden Markov model separates hidden label transitions from observed token emissions. For labels s_1,...,s_T and observations x_1,...,x_T, its joint probability is pi(s_1)*b_s1(x_1)*product_(t=2)^T a_(s_(t-1),s_t)*b_st(x_t). The initial distribution pi chooses the first state, a describes state transitions, and b describes token likelihood within a state. Conditional independence assumptions make this model tractable but limit its linguistic realism.

Viterbi decoding finds the single highest-probability complete path. It does not compute the marginal probability of each token's label, and choosing the most likely label at each position independently can produce a different sequence. This lesson implements the actual dynamic program on tiny authored probability tables, compares it with exhaustive enumeration and then examines BIO entity constraints.

## Mechanism review and counterexample

BIO labeling uses B-TYPE for the beginning of an entity, I-TYPE for a continuation and O outside an entity. Under the strict policy here, I-ORG cannot start a sequence or follow O, and I-ORG cannot continue a B-PER span. Some corpora use different repair or tagging conventions, so a decoder and evaluator must share the same policy.

Illegal transitions can be forbidden by a transition mask in a structured model, but doing so changes the model and its normalization choices. The reference provides a separate strict BIO validator so the constraint is visible without pretending the two-state noun/verb HMM is already a trained named-entity model. A real tagger also needs token-offset alignment, annotation conventions, training data and held-out evaluation.

Token accuracy can conceal entity failure. For gold tags [B-ORG,I-ORG,O] and predictions [B-ORG,O,O], two of three tokens match, yet the two-token entity is not recovered exactly. Entity-level precision/recall should compare complete typed spans, while token metrics can remain diagnostic. This distinction becomes central in the next lesson.
