# ruff: noqa: E501
"""Transfer exercises and authored Verify text for the TensorFlow and LLM theory renderer.

A lesson listed in TRANSFER publishes its first two spec exercises only as worked
examples. Its practice list starts with these two transfer exercises, which change
the fixture, ask for a prediction or add a debugging step, followed by spec
exercises 3-6. Reading lessons cannot derive a Verify line from assertions, so
AUTHORED_VERIFY names the check for each written case.
"""

from render import ex

TRANSFER = {
    "tf-011": [
        ex(
            "Fit one epoch with the standard loop",
            "Build a fresh zero-initialized model, compile it with SGD(0.1) and loss='mse', then call fit(x, y, epochs=1, batch_size=3, shuffle=False, verbose=0).",
            "History loss 56/3 (the loss before the update); kernel 28/15, the same as train_on_batch.",
            """fitted=tf.keras.Sequential([tf.keras.Input(shape=(1,)),tf.keras.layers.Dense(1,use_bias=False,kernel_initializer='zeros')])
fitted.compile(optimizer=tf.keras.optimizers.SGD(.1),loss='mse')
history=fitted.fit(x,y,epochs=1,batch_size=3,shuffle=False,verbose=0)
assert len(history.history['loss'])==1
np.testing.assert_allclose(history.history['loss'][0],56/3,rtol=1e-6)
np.testing.assert_allclose(fitted.get_weights()[0],[[28/15]],atol=1e-6,rtol=0)""",
            "With batch_size equal to the three observations and shuffle=False, one epoch is exactly one full-batch step, so fit must reproduce the hand-derived kernel. The History entry is the mean loss computed during the epoch, before the step changed the weight, which is why it reports 56/3 rather than the post-update loss 56/675. The relative tolerance reflects float32 rounding of a value near 18.7.",
        ),
        ex(
            "Predict a halved learning rate",
            "Before running it, predict the kernel and post-update loss for a fresh model trained once with SGD(0.05); then check the prediction.",
            "kernel 14/15; post-update loss 3584/675, about 5.31.",
            """half=tf.keras.Sequential([tf.keras.Input(shape=(1,)),tf.keras.layers.Dense(1,use_bias=False,kernel_initializer='zeros')])
half.compile(optimizer=tf.keras.optimizers.SGD(.05),loss='mse')
half.train_on_batch(x,y)
np.testing.assert_allclose(half.get_weights()[0],[[14/15]],atol=1e-6,rtol=0)
np.testing.assert_allclose(np.mean((half(x).numpy()-y)**2),3584/675,atol=1e-5,rtol=0)""",
            "The gradient at zero is still -56/3, so half the rate moves the kernel half as far, to 14/15. The loss is \\((14/3)(w-2)^2\\); with \\(w-2=-16/15\\) it equals 3584/675. A loss near 5.3 has larger float32 rounding than 56/675, so the check uses 1e-5.",
        ),
    ],
    "tf-015": [
        ex(
            "Replay a seeded shuffle",
            "Shuffle the five records with shuffle(5, seed=7, reshuffle_each_iteration=False). Traverse it twice, rebuild the same pipeline from the literal arrays, and compare the ID orders.",
            "the same ID order on both passes and after rebuilding; IDs 0-4 each appear once; every value is still ID+1.",
            """replay=ds.shuffle(5,seed=7,reshuffle_each_iteration=False)
first=[int(i) for i,v in replay.as_numpy_iterator()]
assert [int(i) for i,v in replay.as_numpy_iterator()]==first
rebuilt=tf.data.Dataset.from_tensor_slices((np.arange(5),np.arange(1,6,dtype='float32'))).shuffle(5,seed=7,reshuffle_each_iteration=False)
assert [int(i) for i,v in rebuilt.as_numpy_iterator()]==first
assert sorted(first)==[0,1,2,3,4]
assert all(float(v)==int(i)+1 for i,v in replay.as_numpy_iterator())""",
            "A buffer of five holds the whole fixture, so any order is possible. The operation seed fixes the order and reshuffle_each_iteration=False repeats it on every pass; with the default True, each epoch would draw a new order. Shuffling the (ID, value) tuple keeps each pair together, which the ID+1 check confirms.",
        ),
        ex(
            "Predict a different batch size",
            "Predict the batch sizes for batch(3), then the surviving IDs when drop_remainder=True, before running the pipeline.",
            "sizes [3, 2]; with drop_remainder=True only IDs 0, 1, 2 remain.",
            """sizes=[len(i) for i,v in ds.batch(3).as_numpy_iterator()]
kept=np.concatenate([i for i,v in ds.batch(3,drop_remainder=True).as_numpy_iterator()])
assert sizes==[3,2]
assert kept.tolist()==[0,1,2]""",
            "Five records in batches of three leave a remainder of two. Dropping it removes 40 percent of this fixture, far more than the single record lost with batches of two, so the ledger of absent IDs matters more as the batch grows.",
        ),
    ],
    "llm-029": [
        ex(
            "Read a longer training run",
            "Compare row A with row F (P 1000, D 10000, S 400, C 4, L 1.7). Identify what changed and calculate the F/A loss ratio.",
            "steps and compute quadrupled; parameters and data fixed; ratio 0.85, a 15 percent decrease.",
            """Run P     D     S   C L
A   1000  10000 100 1 2.0
F   1000  10000 400 4 1.7
Controlled: P, D, evaluation protocol. Changed: S, C.
1.7 / 2.0 = 0.85; (2.0 - 1.7) / 2.0 = 0.15""",
            "Only the number of updates and the compute it consumes differ, so the comparison is controlled for parameters and data. The decrease is measured relative to A, the baseline row.",
            verify="Check that both rows keep P 1000 and D 10000, that only S and C are marked as changed, and that 1.7/2.0 reproduces the ratio 0.85.",
        ),
        ex(
            "Isolate a data change",
            "Row H uses P 1000, D 20000, S 100 with measured C 2 and L 1.95. State which factors changed relative to A and the percent decrease.",
            "data and compute changed; parameters and steps fixed; ratio 0.975, a 2.5 percent decrease.",
            """Run P     D     S   C L
A   1000  10000 100 1 2.0
H   1000  20000 100 2 1.95
Controlled: P, S, evaluation protocol. Changed: D, C.
1.95 / 2.0 = 0.975; (2.0 - 1.95) / 2.0 = 0.025""",
            "Compute is a measured consequence of the run, not an independent knob, so it changes with D here. The comparison isolates the data-size choice only because P, S and the evaluation protocol are held fixed.",
            verify="Check that the comparison holds P 1000 and S 100 fixed, lists D and C as the changed columns, and that 1.95/2.0 reproduces 0.975.",
        ),
    ],
    "llm-030": [
        ex(
            "Complete a validation row",
            "Document d6 is an authored practice question placed in validation, family F3. Write its manifest row and state which uses it may serve.",
            "row d6 | local author | course fixture permission | validation | F3 | hash-of-d6; model selection only, not gradients or final test reporting.",
            """d6 | local author | course fixture permission | validation | F3 | hash-of-d6
Gradient updates: not admitted
Model selection: admitted
Final test reporting: not admitted""",
            "Validation data may guide choices such as early stopping, which is why it must stay separate from the test family F2 used for the final report.",
            verify="Check that the d6 row fills all five required fields and that the use list admits model selection while refusing gradient updates and final test reporting.",
        ),
        ex(
            "Correct a mislabelled family",
            "A manifest records d3, the answer to test document d2, as family F1 in train because it came from a crawl labelled training. Identify the error and correct the row.",
            "d3 belongs to evaluation-derived family F2 and is blocked; a crawl label is neither provenance nor permission.",
            """Recorded: d3 | crawl | unknown | train | F1
Problem: d3 reproduces the answer to test document d2
Corrected: d3 | crawl | unresolved permission | blocked | F2 (evaluation-derived)""",
            "The family follows the evaluation relationship, not the folder where the bytes were found. Leaving d3 in F1 would let a test answer reach training while every manifest field looked complete.",
            verify="Check that the corrected row moves d3 from F1 to F2, blocks its training admission and keeps permission unresolved instead of inferring it from the crawl label.",
        ),
    ],
    "llm-039": [
        ex(
            "Compare uneven denominators",
            "Group D has 1 failure in 50 cases; group E has 0 failures in 5. Compare the observed rates and what each establishes.",
            "D observed 1/50 = 0.02; E observed 0/5; five cases do not show that E is safer than D.",
            """D: failures 1, count 50, observed rate 1/50 = 0.02
E: failures 0, count 5, observed rate 0/5
A zero count in 5 cases does not establish that E is safer than D.""",
            "A lower observed rate on a much smaller denominator is weak evidence. Report both counts so a reader can see how little E was tested.",
            verify="Check that 1/50 is written as 0.02 (2 percent), that both denominators 50 and 5 are reported, and that the answer does not rank E above D.",
        ),
        ex(
            "Recompute a gate with two severe failures",
            "Eighteen minor cases pass and two severe cases fail. Calculate the pass rate and the gate result.",
            "18/20 = 90 percent passes; 2 severe failures; the gate fails.",
            """Pass rate = 18/20 = 90 percent
Severe failures = 2
Required severe-failure gate = fail""",
            "The pass rate matches the earlier case, yet the decision depends on the severe-failure count, which is now two. An aggregate rate cannot replace the gate.",
            verify="Check that the pass rate is 18/20 = 0.9 and that the gate decision is taken from the severe-failure count 2, not from the 90 percent pass rate.",
        ),
    ],
    "llm-041": [
        ex(
            "Translate a second weight matrix",
            "Use row input [2, -1] and NumPy/Keras kernel [[1, 0, 2], [3, 1, 0]]. State the PyTorch Linear weight and the outputs.",
            "PyTorch weight [[1, 3], [0, 1], [2, 0]]; outputs [-1, -1, 4].",
            """X shape (1, 2): [2, -1]
NumPy/Keras W shape (2, 3): [[1, 0, 2], [3, 1, 0]]
PyTorch Linear.weight shape (3, 2): [[1, 3], [0, 1], [2, 0]]
Output: [2*1-1*3, 2*0-1*1, 2*2-1*0] = [-1, -1, 4]""",
            "PyTorch stores one row per output feature, so its weight is the transpose of the input-by-output kernel. A negative input entry makes a transposition mistake visible in the outputs.",
            verify="Check that the PyTorch weight has shape (3, 2) and equals the transpose, and that each output is the dot product of [2, -1] with one weight row: -1, -1 and 4.",
        ),
        ex(
            "Translate a padding mask",
            "Three keys are k0, k1 and a padding key k2. Write the course allowed mask, the PyTorch key_padding_mask and the Keras attention_mask row.",
            "allowed [1, 1, 0]; key_padding_mask [False, False, True]; Keras [True, True, False].",
            """Keys: k0 real, k1 real, k2 padding
Course allowed mask: 1 1 0
PyTorch key_padding_mask: False False True (True ignores the key)
Keras attention_mask row: True True False (True attends)""",
            "The same exclusion has opposite boolean polarity in the two PyTorch arguments and in Keras. Writing all three side by side prevents a negation error from attending to padding.",
            verify="Check that the PyTorch key_padding_mask is the logical negation of the Keras row and that k2 is the only key excluded in all three representations.",
        ),
    ],
}

TRANSFER.update(
    {
        "tf-010": [
            ex(
                "Partition a second account fixture",
                "Use groups E, E, F, F, G, G, H, H with values 2, 4, 6, 8, 10, 12, 40, 44; train on E, F and G, then center the held-out rows with the training mean.",
                "train mean 7; validation group H; centered values 33 and 37.",
                """groups2=np.array(list('EEFFGGHH')); x2=np.array([2.,4.,6.,8.,10.,12.,40.,44.])
train2=np.isin(groups2,['E','F','G']); mean2=x2[train2].mean()
assert mean2==7 and set(groups2[~train2])=={'H'}
np.testing.assert_array_equal(x2[~train2]-mean2,[33.,37.])""",
                "Three training accounts now contribute six rows, and the held-out account is centered with a statistic it did not influence. Its centered values are far from zero, which is information about the new account rather than an error.",
            ),
            ex(
                "Predict the effect of a training outlier",
                "Change the first training value from 2 to 200. Predict the new training mean and the centered validation values before running the check.",
                "training mean 40; centered H values 0 and 4.",
                """outlier=x2.copy(); outlier[0]=200
shifted=outlier[train2].mean()
assert shifted==40
np.testing.assert_array_equal(outlier[~train2]-shifted,[0.,4.])""",
                "Changing a validation value left the training mean alone in Example B; changing a training value moves the frozen statistic and every transformed validation row with it. A single training outlier can therefore alter all downstream evaluation inputs.",
            ),
        ],
        "tf-034": [
            ex(
                "Count errors for three groups",
                "Use rows (ID, group, truth, prediction): a A 1 1, b A 0 1, c B 1 1, d B 0 0, e C 1 0, f C 0 1, g C 1 1.",
                "group A 1/2, group B 0/2, group C 2/3 errors.",
                """rows3=[('a','A',1,1),('b','A',0,1),('c','B',1,1),('d','B',0,0),('e','C',1,0),('f','C',0,1),('g','C',1,1)]
report3={g:(sum(t!=p for i,k,t,p in rows3 if k==g),sum(k==g for i,k,t,p in rows3)) for g in ['A','B','C']}
assert report3=={'A':(1,2),'B':(0,2),'C':(2,3)}""",
                "Each group keeps its own numerator and denominator, so the small groups remain visibly small. Group C has the most errors but also the most rows; the pair, not a pooled accuracy, is the report.",
            ),
            ex(
                "Deduplicate before reporting",
                "Append three more copies of row g, then compare group C counts by row and by unique ID.",
                "C has 6 rows but 3 unique IDs; the row-level error rate 2/6 understates the 2/3 rate by ID.",
                """padded=rows3+[rows3[-1]]*3
unique=list({r[0]:r for r in padded}.values())
assert sum(k=='C' for i,k,t,p in padded)==6 and sum(k=='C' for i,k,t,p in unique)==3
assert sum(t!=p for i,k,t,p in padded if k=='C')==2
assert sum(t!=p for i,k,t,p in unique if k=='C')==2""",
                "Duplicated correct rows enlarge the denominator without adding evidence, halving the apparent error rate. Counting by unique ID restores the unit of evaluation.",
            ),
        ],
        "tf-035": [
            ex(
                "Align a fourth record",
                "Use truth a=0, b=1, c=2, d=4, model A predictions d 5, a 0, b 2, c 2 and model B predictions b 1, d 4, c 3, a 1. Compute paired squared-error differences by ID.",
                "paired differences [-1, 1, -1, 1]; mean 0, so neither model has lower MSE on this fixture.",
                """truth4={'a':0.,'b':1.,'c':2.,'d':4.}; a4={'d':5.,'a':0.,'b':2.,'c':2.}; b4={'b':1.,'d':4.,'c':3.,'a':1.}
diff4=np.array([(a4[i]-truth4[i])**2-(b4[i]-truth4[i])**2 for i in sorted(truth4)])
np.testing.assert_array_equal(diff4,[-1,1,-1,1])
assert diff4.mean()==0""",
                "Each model wins on two records, so the paired mean is exactly zero. Sorting the shared IDs pairs every prediction with its own truth regardless of dictionary insertion order.",
            ),
            ex(
                "Expose positional pairing",
                "Pair the original truth, model A and model B dictionaries by insertion order instead of ID and compare with the identity-aligned differences.",
                "positional differences [-9, 1, 0] instead of [-1, 0, -1].",
                """positional=np.array([(pa-t)**2-(pb-t)**2 for t,pa,pb in zip(truth.values(),a.values(),b.values())])
np.testing.assert_array_equal(positional,[-9,1,0])
assert not np.array_equal(positional,diff)""",
                "Model B was stored in the order c, a, b, so positional pairing scores its prediction for c against the truth for a. The code runs without error and produces plausible numbers, which is why identity alignment must be checked rather than assumed.",
            ),
        ],
        "llm-012": [
            ex(
                "Predict a hotter distribution",
                "Use scores [0.5, 3, 3.5, -1]. Name the greedy token, then predict how temperature 2 changes the probabilities of the top and bottom tokens.",
                "greedy token 2; at temperature 2 its probability falls, token 3 gains mass and the argmax stays 2.",
                """scores2=np.array([.5,3.,3.5,-1.]); base=softmax(scores2); hot=softmax(scores2/2)
assert int(np.argmax(scores2))==2 and base.argmax()==hot.argmax()==2
assert hot[2]<base[2] and hot[3]>base[3]""",
                "Dividing scores by a temperature above 1 shrinks their differences, which flattens the distribution without reordering it. Greedy decoding is therefore unaffected while sampling becomes more diverse.",
            ),
            ex(
                "Compute an exact two-token probability",
                "For scores [1, 0], compute the probability of token 0 at temperatures 1 and 0.5 and compare it with the logistic function.",
                "token 0 probability \\(1/(1+e^{-1})\\approx 0.731\\) at temperature 1 and \\(1/(1+e^{-2})\\approx 0.881\\) at temperature 0.5.",
                """pair=softmax([1.,0.]); sharp=softmax(np.array([1.,0.])/.5)
np.testing.assert_allclose(pair[0],1/(1+np.exp(-1)),atol=1e-12,rtol=0)
np.testing.assert_allclose(sharp[0],1/(1+np.exp(-2)),atol=1e-12,rtol=0)""",
                "With two tokens, softmax reduces to the logistic function of the score difference divided by the temperature. Halving the temperature doubles the effective difference from 1 to 2.",
            ),
        ],
        "llm-013": [
            ex(
                "Shift a batch of two sequences",
                "Shift IDs [[4, 1, 6, 2, 9], [3, 3, 8, 0, 5]] along the time axis into inputs and labels.",
                "inputs and labels both shape (2, 4); labels [[1, 6, 2, 9], [3, 8, 0, 5]].",
                """batch=np.array([[4,1,6,2,9],[3,3,8,0,5]]); x_in=batch[:,:-1]; y_out=batch[:,1:]
assert x_in.shape==y_out.shape==(2,4)
np.testing.assert_array_equal(y_out,[[1,6,2,9],[3,8,0,5]])""",
                "The shift is applied to the time axis of every sequence; the batch axis is untouched. Each sequence loses one prediction target because its final token has no successor.",
            ),
            ex(
                "Predict a partly hidden label bug",
                "For the second sequence, compare copied-input labels with the shifted targets and predict how many positions agree.",
                "copied labels agree once (the repeated 3) and differ at the other 3 positions.",
                """row=batch[1]; copied_row=row[:-1]; target_row=row[1:]
assert int(np.count_nonzero(copied_row==target_row))==1
assert int(np.count_nonzero(copied_row!=target_row))==3""",
                "A repeated token makes the identity-label bug agree with the true target at one position. A check that only looked for any agreement would pass; counting all disagreements still exposes the bug.",
            ),
        ],
        "llm-014": [
            ex(
                "Count transitions in new documents",
                "Use vocabulary A=0, B=1, C=2 and the documents CAAB and BCA; count transitions within each document.",
                "C to A: 2, A to A: 1, A to B: 1, B to C: 1; total 5; no B to B transition across the document boundary.",
                """docs2=[[2,0,0,1],[1,2,0]]; counts2=np.zeros((3,3),dtype=int)
for doc in docs2:
    for a,b in zip(doc[:-1],doc[1:]): counts2[a,b]+=1
assert counts2[2,0]==2 and counts2[0,0]==1 and counts2[0,1]==1 and counts2[1,2]==1
assert counts2.sum()==5 and counts2[1,1]==0""",
                "The first document ends in B and the second starts with B. Concatenating them would invent a B to B transition, so the zero in that cell checks the document boundary.",
            ),
            ex(
                "Predict two smoothed rows",
                "Apply add-one smoothing to the new counts and predict the rows for contexts A and C.",
                "row A [2/5, 2/5, 1/5]; row C [3/5, 1/5, 1/5].",
                """prob2=(counts2+1)/(counts2.sum(1,keepdims=True)+3)
np.testing.assert_allclose(prob2[0],[2/5,2/5,1/5],atol=1e-12,rtol=0)
np.testing.assert_allclose(prob2[2],[3/5,1/5,1/5],atol=1e-12,rtol=0)""",
                "Each row adds one pseudo-count per vocabulary item, so its denominator is the row count plus 3. Context A has two observed transitions and context C has two, but their distributions differ because the counts fall in different cells.",
            ),
        ],
        "llm-021": [
            ex(
                "Assign a second family policy",
                "Use documents p, p2, p3 in family J, q in K and r in L; map J to test, K to train and L to validation.",
                "p, p2 and p3 all test; one training document q; r in validation.",
                """family2={'p':'J','p2':'J','p3':'J','q':'K','r':'L'}; policy2={'J':'test','K':'train','L':'validation'}
manifest2={doc:policy2[group] for doc,group in family2.items()}
assert sorted(d for d,s in manifest2.items() if s=='test')==['p','p2','p3']
assert list(manifest2.values()).count('train')==1 and manifest2['r']=='validation'""",
                "Assigning whole families keeps all three related documents on the test side. The split sizes follow the family sizes, so a large family can leave very little training data.",
            ),
            ex(
                "Predict the effect of key order",
                "Serialize the same two-entry manifest with keys in opposite orders, with and without sort_keys=True, and compare SHA-256 hashes.",
                "raw JSON hashes differ when only key order changes; sort_keys=True makes them equal.",
                """forward=json.dumps({'a':'train','b':'test'}); backward=json.dumps({'b':'test','a':'train'})
assert hash_text(forward)!=hash_text(backward)
assert hash_text(json.dumps({'a':'train','b':'test'},sort_keys=True))==hash_text(json.dumps({'b':'test','a':'train'},sort_keys=True))""",
                "A hash identifies bytes, not meaning. A manifest hash is only a stable identity when the serialization is canonical, so the key order must be fixed before hashing.",
            ),
        ],
        "llm-025": [
            ex(
                "Count scores for a larger configuration",
                "Use batch 2, heads 4 and context 64 with 4-byte score elements.",
                "32768 score elements; 131072 bytes (128 KiB).",
                """scores_big=2*4*64*64
assert scores_big==32768 and scores_big*4==131072""",
                "Score elements scale with batch, heads and the square of the context. Doubling the context alone would multiply this count by four.",
            ),
            ex(
                "Predict cache growth with depth and context",
                "Use 3 layers, 2 heads, width per head 16, 4-byte elements and contexts 48 and 96; compare with the growth of the score matrix.",
                "36864 and 73728 cache bytes; the cache doubles while score elements quadruple.",
                """cache3=[2*3*1*2*t*16*4 for t in [48,96]]
assert cache3==[36864,73728] and cache3[1]==2*cache3[0]
assert (1*2*96*96)//(1*2*48*48)==4""",
                "The factor 2 counts keys and values. The cache grows linearly with context and with layers, while the per-layer score matrix grows quadratically with context.",
            ),
        ],
        "llm-027": [
            ex(
                "Weight three documents",
                "Combine document mean losses 2, 4 and 1 with token counts 2, 1 and 5.",
                "token-weighted mean 13/8 = 1.625; document mean 7/3, about 2.333.",
                """means3=np.array([2.,4.,1.]); counts3=np.array([2,1,5])
np.testing.assert_allclose(np.average(means3,weights=counts3),13/8,atol=1e-12,rtol=0)
np.testing.assert_allclose(means3.mean(),7/3,atol=1e-12,rtol=0)""",
                "The long, low-loss document dominates the token-weighted mean, while each document counts once in the document mean. The two summaries answer different questions and must be labelled.",
            ),
            ex(
                "Summarize a second calibration bin",
                "Use confidences 0.9, 0.9, 0.7, 0.9, 0.6 with correctness 1, 0, 1, 1, 0 in a single bin.",
                "count 5, mean confidence 0.8, accuracy 0.6: overconfident by 0.2.",
                """conf2=np.array([.9,.9,.7,.9,.6]); correct2=np.array([1,0,1,1,0])
assert len(conf2)==5; np.testing.assert_allclose(conf2.mean(),.8,atol=1e-12,rtol=0)
assert correct2.mean()==.6
np.testing.assert_allclose(conf2.mean()-correct2.mean(),.2,atol=1e-12,rtol=0)""",
                "The bin has the same mean confidence as Example B but lower accuracy, so its calibration gap is larger. Five predictions remain a small sample for estimating that gap.",
            ),
        ],
        "llm-033": [
            ex(
                "Compute a margin from log probabilities",
                "Use policy log probabilities -1 (chosen) and -4 (rejected), reference -2 and -3, and beta 0.25.",
                "margin 0.5; loss \\(\\log(1+e^{-0.5})\\approx 0.474\\), below \\(\\log 2\\).",
                """margin2=.25*((-1-(-4))-(-2-(-3))); loss2=np.logaddexp(0,-margin2)
assert margin2==.5
np.testing.assert_allclose(loss2,np.log1p(np.exp(-.5)),atol=1e-12,rtol=0)
assert loss2<np.log(2)""",
                "The policy prefers the chosen answer by 3 while the reference prefers it by 1, so the relative preference is 2 before scaling by beta. Any positive margin gives a loss below the zero-margin value \\(\\log 2\\).",
            ),
            ex(
                "Predict the effect of beta",
                "Keep the same log probabilities and raise beta to 1. Predict the margin and whether the loss rises or falls.",
                "margin 2; loss \\(\\log(1+e^{-2})\\approx 0.127\\), smaller than at beta 0.25.",
                """margin3=1.*((-1-(-4))-(-2-(-3))); loss3=np.logaddexp(0,-margin3)
assert margin3==2
np.testing.assert_allclose(loss3,np.log1p(np.exp(-2)),atol=1e-12,rtol=0)
assert loss3<loss2""",
                "Beta scales the same relative preference, so a larger beta makes a positive margin look more decisive and lowers the loss. It also makes a negative margin more costly.",
            ),
        ],
        "llm-034": [
            ex(
                "Quantize a second matrix",
                "Quantize W[[0.5, -1.2], [0.25, 2.0]] with one shared scale, the maximum absolute value divided by 127, and nearest-even rounding.",
                "scale 2/127; integer array [[32, -76], [16, 127]].",
                """w2=np.array([[.5,-1.2],[.25,2.]]); scale2=np.abs(w2).max()/127
q2=np.clip(np.rint(w2/scale2),-127,127).astype(np.int8)
np.testing.assert_array_equal(q2,[[32,-76],[16,127]]); assert scale2==2/127""",
                "The largest magnitude maps exactly to 127, and every other entry is rounded on the same grid. Values such as 31.75 and 15.875 round to the nearest integer without a tie.",
            ),
            ex(
                "Predict the reconstruction error",
                "Dequantize the new integers and predict the largest absolute weight error and the bound it must respect.",
                "largest error 0.5/127, about 0.0039, within the half-step bound 1/127.",
                """err=np.abs(q2*scale2-w2).max()
np.testing.assert_allclose(err,.5/127,atol=1e-12,rtol=0)
assert err<=scale2/2""",
                "Rounding moves each value by at most half a quantization step, here \\(1/127\\). The entry 0.5 maps to 31.75 steps and is rounded by a quarter step, the largest move in this matrix.",
            ),
        ],
        "llm-036": [
            ex(
                "Rank a different query",
                "Query has sides against the same six documents with token overlap and ID tie-breaks; return the top 3.",
                "top 3 IDs d1, d4, d5: two tied overlaps ordered by ID, then the single overlap.",
                """assert rank('has sides',docs,3)==['d1','d4','d5']""",
                "Documents d1 and d4 share both query words, so the ID rule orders them. Document d5 shares only has, which ranks it above every document with no overlap.",
            ),
            ex(
                "Measure recall with a tie-filled slot",
                "Use relevant IDs d3 and d4 for the query round circle and compute recall at 1 and 2.",
                "ranking d3, d1; recall 0.5 at both 1 and 2.",
                """relevant2={'d3','d4'}
top=rank('round circle',docs,2)
assert top==['d3','d1']
assert len(set(rank('round circle',docs,1))&relevant2)/len(relevant2)==.5
assert len(set(top)&relevant2)/len(relevant2)==.5""",
                "Only d3 overlaps the query, so the second slot is filled by the ID tie-break among zero-overlap documents. Recall stays at 0.5 because d4 is never retrieved.",
            ),
        ],
        "llm-037": [
            ex(
                "Classify five new cases",
                "Use r1 and r2 retrieval misses, r3 an unsupported answer, r4 a correct supported answer and r5 an abstention on an answerable question.",
                "2 retrieval misses, 1 unsupported answer, 1 abstention that was not appropriate and 1 correct answer.",
                """rows2=[{'id':'r1','miss':True,'unsupported':False,'abstain':False,'correct':False},{'id':'r2','miss':True,'unsupported':False,'abstain':False,'correct':False},{'id':'r3','miss':False,'unsupported':True,'abstain':False,'correct':False},{'id':'r4','miss':False,'unsupported':False,'abstain':False,'correct':True},{'id':'r5','miss':False,'unsupported':False,'abstain':True,'correct':False}]
assert sum(r['miss'] for r in rows2)==2 and sum(r['unsupported'] for r in rows2)==1
assert sum(r['abstain'] for r in rows2)==1 and sum(r['abstain'] and r['correct'] for r in rows2)==0""",
                "An abstention is only correct when the question cannot be answered from the evidence. Recording r5 as an incorrect abstention keeps caution from being counted as success.",
            ),
            ex(
                "Predict coverage and answered accuracy",
                "From the five new cases, compute the share of questions answered and the accuracy among answered questions.",
                "coverage 0.8; answered accuracy 0.25.",
                """answered=[r for r in rows2 if not r['abstain']]
assert len(answered)/len(rows2)==.8
assert sum(r['correct'] for r in answered)/len(answered)==.25""",
                "Four of five questions were answered and only r4 was correct. Reporting coverage beside answered accuracy prevents abstentions from silently raising or lowering the headline score.",
            ),
        ],
        "llm-038": [
            ex(
                "Accept the second allowed document",
                "Validate tool read_fixture with document_id d2 and check whether the returned proposal is a separate object.",
                "accepted; the returned proposal equals the input but is a separate copy.",
                """second={'tool':'read_fixture','document_id':'d2'}; copy2=validate(second)
assert copy2==second and copy2 is not second""",
                "Returning a copy means later mutation of the model's original object cannot change the proposal that passed validation.",
            ),
            ex(
                "Predict a case-changed tool name",
                "Submit tool READ_FIXTURE with document_id d1 and predict which check rejects it.",
                "ValueError 'unknown tool'; names are matched exactly, without case folding.",
                """try: validate({'tool':'READ_FIXTURE','document_id':'d1'})
except ValueError as error: assert str(error)=='unknown tool'
else: raise AssertionError('case-changed tool accepted')""",
                "The allowlist compares exact strings. Silently normalizing case would widen the set of accepted inputs beyond what was reviewed.",
            ),
        ],
        "llm-040": [
            ex(
                "Group a second fixture",
                "Use families A, B, B, C with paired differences [2, -1, 0, 1]; compute family means, the row mean and the equal-family mean.",
                "family means A 2, B -0.5, C 1; row mean 0.5; equal-family mean 5/6.",
                """fam2=np.array(['A','B','B','C']); d2=np.array([2.,-1.,0.,1.])
g2=np.array([d2[fam2==f].mean() for f in ['A','B','C']])
np.testing.assert_array_equal(g2,[2,-.5,1])
assert d2.mean()==.5
np.testing.assert_allclose(g2.mean(),5/6,atol=1e-12,rtol=0)""",
                "Family B contributes two rows to the row mean but one value to the equal-family mean, so the two targets differ even without duplication.",
            ),
            ex(
                "Predict bootstrap support",
                "Draw 2000 resamples of three family means with replacement using seed 3 and predict the range and number of distinct estimates.",
                "every estimate lies in [-0.5, 2]; at most 10 distinct means occur.",
                """idx=np.random.default_rng(3).integers(0,3,size=(2000,3)); est=g2[idx].mean(1)
assert est.min()>=-.5 and est.max()<=2
assert len(np.unique(np.round(est,12)))<=10""",
                "Each estimate averages three of the observed family means, so it cannot leave their range, and there are only 10 multisets of three draws from three values. More draws sample this small distribution more densely without adding families.",
            ),
        ],
    }
)

AUTHORED_VERIFY = {
    (
        "llm-029",
        "Calculate a local ratio",
    ): "Recompute 1.8/2.0 and (2.0 - 1.8)/2.0 from the table: the worksheet shows 0.9 and 0.10, with the decrease measured relative to A rather than B.",
    (
        "llm-029",
        "Reject an unsupported forecast",
    ): "Check that the answer states the observed compute range 1 to 2 and names at least two missing kinds of evidence before rejecting the forecast at compute 1000000.",
    (
        "llm-029",
        "Design a discriminating next run",
    ): "Check the proposed row against row A: only P differs (D 10000 and S 100 unchanged), and C and L are listed as quantities to measure rather than assumed values.",
    (
        "llm-029",
        "Write a bounded conclusion",
    ): "Check that the conclusion cites the A-to-B decrease from 2.0 to 1.8, marks row C as confounded and contains no prediction outside the observed rows.",
    (
        "llm-030",
        "Follow a paraphrase family",
    ): "Check that d4 inherits family F2 through its d3 relationship even though its hash differs, and that the record blocks F2 from training and prompt selection.",
    (
        "llm-030",
        "Separate permission and cleanliness",
    ): "Check that the record has two separate results, permission pass and evaluation independence fail, and that the exclusion follows from the failed check.",
    (
        "llm-030",
        "Audit preprocessing inputs",
    ): "Check that the audit lists d2 among the tokenizer fit sources but not among allowed training sources, and that the repair refits on d1 before evaluation is rerun.",
    (
        "llm-030",
        "Record an unresolved source",
    ): "Check that the d5 row keeps origin, permission and family unresolved, requires the actual hash and leaves the document unadmitted.",
    (
        "llm-039",
        "Analyze a counterfactual pair",
    ): "Check that the record holds qualifications identical, names the single changed field and contrasts the expected equal eligibility with the observed opposite outcomes.",
    (
        "llm-039",
        "Handle an untested group",
    ): "Check that group C reports count 0 with an undefined rate, not 0 percent or a pass, and that the claim says no evaluation evidence exists for the group.",
    (
        "llm-039",
        "Separate families from paraphrases",
    ): "Check that the report carries both counts, 20 variants and 1 independent family, and never presents the variants as 20 threat classes.",
    (
        "llm-039",
        "Write a finite claim",
    ): "Check that the conclusion mentions the one severe failure, the untested group C and the no-go decision, and that it limits the claim to this finite suite.",
    (
        "llm-041",
        "Name exact mask APIs",
    ): "Check each API row for polarity: SDPA attn_mask True participates, key_padding_mask True is ignored and Keras attention_mask True attends; the answer also notes the different shapes.",
    (
        "llm-041",
        "Specify evaluation dropout",
    ): "Check that the policy passes dropout_p=0.0 explicitly when training=False and does not rely on module.eval() to change a functional call.",
    (
        "llm-041",
        "Design a cross-framework oracle",
    ): "Recompute each output row as the mean of its legal value rows: [2, 0], ([2, 0] + [0, 2])/2 = [1, 1] and (2 + 0 + 6)/3 = 8/3 in both columns.",
    (
        "llm-041",
        "Preserve optionality",
    ): "Check that the record lists TensorFlow as unavailable and unexecuted rather than passed, keeps NumPy and PyTorch evidence separate and states that llm-042 does not depend on llm-041.",
}
