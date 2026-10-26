from render import add, ex, SPECS

TF = ("TensorFlow guide", "https://www.tensorflow.org/guide")
KERAS = ("Keras API", "https://keras.io/api/")
NP = ("NumPy reference", "https://numpy.org/doc/stable/reference/")
add(
    "tf-009",
    """Training is a sequence of state changes. An example is one input paired with its target. A batch is the set whose losses are reduced before a single update. An epoch is one pass through the chosen examples, whereas an optimizer step is one update. These units differ even on six records. A smaller batch means more updates per epoch, and later batches see weights already changed by earlier batches. Averaging the endpoint weights of separate runs cannot reconstruct this trajectory. Keep record IDs beside values, since a plausible loss cannot reveal that one record was omitted. A short final batch is a real batch unless a deliberate dropping policy removes it. Its mean loss has its own denominator.""",
    """The slice x[start:start+size] selects consecutive observations without copying the entire dataset. GradientTape records operations in its block; assign_sub applies the measured gradient only after the block. The update counter increments once per slice. The loss is recomputed at each new weight, so changing batch size changes both the number of updates and the values used to calculate later gradients. Use a small learning rate because the largest input here is six.""",
    [
        ("Epoch", "One complete traversal of the selected records."),
        ("Batch", "Observations contributing to one reduced gradient."),
        ("Step", "One optimizer update with the current state."),
    ],
    [
        ex(
            "Count updates",
            "Partition IDs 1..6 into batches of size two; retain each batch and count one update per batch.",
            "batches [[1,2],[3,4],[5,6]] and 3 updates.",
            """ids=list(range(1,7)); batches=[ids[i:i+2] for i in range(0,6,2)]
assert batches==[[1,2],[3,4],[5,6]]""",
            "The counter measures updates, not observations. Concatenating the three batches recovers the six original identities exactly once. This check detects both an omitted final slice and a loop that increments once per record.",
        ),
        ex(
            "Retain a remainder",
            "Partition five IDs by two and compare with explicitly dropping the short batch.",
            "sizes [2,2,1]; dropping retains only IDs1..4.",
            """ids=list(range(1,6)); batches=[ids[i:i+2] for i in range(0,5,2)]
assert list(map(len,batches))==[2,2,1]
assert sum((b for b in batches if len(b)==2),[])==[1,2,3,4]""",
            "An epoch with drop_remainder may not expose every record. Naming that choice avoids quietly changing the training population. The tail has one example and its mean gradient must divide by one.",
        ),
        ex(
            "Trace weight state",
            "Implement three batch updates for x=1..6,y=2x,w=0,rate=.01; record the weight before each update.",
            "3 finite, nonidentical updated weights.",
            """x=tf.constant([1.,2.,3.,4.,5.,6.]); y=2*x; w=tf.Variable(0.); history=[]
for i in range(0,6,2):
    with tf.GradientTape() as tape: loss=tf.reduce_mean((w*x[i:i+2]-y[i:i+2])**2)
    w.assign_sub(.01*tape.gradient(loss,w)); history.append(float(w))
assert len(history)==3 and all(np.isfinite(history))
assert len(set(history))==3""",
            "Each gradient depends on the current weight. Recording only the final loss would conceal whether the assignment happened. The finite and distinct states show real updates for this fixture without claiming that every possible dataset produces a different weight each time.",
        ),
        ex(
            "Compare batch policies",
            "Repeat one epoch with sizes one and three from exactly w=0; compare update counts and endpoint weights.",
            "6 versus2 steps and different endpoint weights.",
            """def train(size):
    w=tf.Variable(0.); steps=0
    for i in range(0,6,size):
        with tf.GradientTape() as tape: loss=tf.reduce_mean((w*x[i:i+size]-y[i:i+size])**2)
        w.assign_sub(.01*tape.gradient(loss,w)); steps+=1
    return float(w),steps
a,na=train(1); b,nb=train(3)
assert (na,nb)==(6,2) and abs(a-b)>1e-6""",
            "Both runs process six records but perform different optimization experiments. Equal epochs are not equal compute budgets. Resetting the variable is necessary because otherwise the second run would begin with the first run's trained state.",
        ),
        ex(
            "Preserve pairs",
            "Shuffle IDs with permutation [5,0,4,1,3,2] and apply the same permutation to inputs and targets.",
            "Every shuffled target equals twice its paired input.",
            """order=tf.constant([5,0,4,1,3,2]); sx=tf.gather(x,order); sy=tf.gather(y,order)
np.testing.assert_allclose(sy.numpy(),2*sx.numpy())
assert not np.allclose(y.numpy(),2*sx.numpy())""",
            "A shared index permutation preserves the relation between records. Independently shuffling targets creates a different task while preserving marginal value distributions, which is why checking only target histograms cannot detect this bug.",
        ),
        ex(
            "Aggregate unequal batches",
            "Combine batch mean losses2 and8 with counts2 and 1; compare mean-of-means with the record mean.",
            "record mean4; unweighted batch mean5.",
            """assert (2*2+8*1)/3==4
assert (2+8)/2==5""",
            "The correct epoch statistic counts examples. Batch means hide their denominators. Reconstruct sums by multiplying each mean by its batch count, sum those numerators, then divide by total examples.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-010",
    """A split defines what is unseen. If two rows belong to one account, putting one in training and one in validation exposes part of the validation entity during fitting. Grouped splitting assigns the entity once, then carries all of its rows together. Preprocessing is also fitting: a mean inferred from validation values has already consumed validation information even if no label was used. Store the training statistic and apply it unchanged to validation. This lesson uses literal account records so every crossing can be enumerated. The tiny fixture teaches isolation and does not establish that an account model will generalize to a future deployment.""",
    """Use a mapping from account to split before selecting values. Set intersection tests group isolation. NumPy mean reduces only the selected training values, and subtraction then broadcasts the scalar to both partitions. A validation perturbation should change transformed validation values while leaving the saved fit statistic unchanged. Hash canonical record IDs only after freezing the selection, and never refit merely because a held-out point looks extreme.""",
    [
        ("Split unit", "Entity assigned wholly to one partition."),
        ("Leakage", "Assessment information influencing fitting or selection."),
        ("Fit statistic", "A quantity estimated from training inputs and then frozen."),
    ],
    [
        ex(
            "Partition accounts",
            "Use account IDs A,A,B,B,C,C,D,D with values1,3,5,7,20,22,30,32; train on A,B.",
            "train mean4 and validation IDs C,D.",
            """groups=np.array(list('AABBCCDD')); x=np.array([1.,3.,5.,7.,20.,22.,30.,32.])
train=np.isin(groups,['A','B']); valid=~train; mean=x[train].mean()
assert mean==4 and set(groups[valid])=={'C','D'}""",
            "The boolean mask has one position per record. Its values come from group identity, not a target-dependent ranking. Training has four values and validation has four, but equal counts are incidental to the group-isolation contract.",
        ),
        ex(
            "Expose global fitting",
            "Change the last validation value to3200 and compare train-only and global means.",
            "training mean stays4; global mean changes.",
            """changed=x.copy(); changed[-1]=3200
assert changed[train].mean()==mean
assert changed.mean()!=x.mean()""",
            "A perturbation restricted to validation cannot influence a training-only mean. This controlled counterexample detects leakage more directly than inspecting the name of a preprocessing object.",
        ),
        ex(
            "Find crossing groups",
            "Assign alternating rows to train and validation and inspect intersections.",
            "A,B,C,D all cross the split.",
            """wrong=np.arange(8)%2==0
assert set(groups[wrong]) & set(groups[~wrong])==set('ABCD')""",
            "A row split can look balanced while violating the intended unit. Set intersection exposes the repeated accounts; disjoint row indices alone do not prove disjoint entities.",
        ),
        ex(
            "Apply frozen centering",
            "Center both partitions with training mean4 and compare validation centered values.",
            "validation values16,18,26,28.",
            """np.testing.assert_array_equal(x[valid]-mean,[16,18,26,28])
assert (x[train]-mean).mean()==0""",
            "Only the training values are guaranteed to have centered mean zero. Forcing validation to mean zero would estimate a new statistic and erase a potentially meaningful distribution shift.",
        ),
        ex(
            "Freeze selection identity",
            "Hash sorted training IDs before and after calculating validation errors.",
            "The selection hash is unchanged.",
            """import hashlib,json
ids=['a1','a2','b1','b2']; frozen=json.dumps(ids).encode(); digest=hashlib.sha256(frozen).hexdigest()
validation_error=float(np.mean((x[valid]-mean)**2))
assert validation_error>0 and hashlib.sha256(json.dumps(ids).encode()).hexdigest()==digest""",
            "The hash is a compact identity receipt, not proof of good split design. It can reveal accidental mutation after evaluation. The original IDs must still be available for review.",
        ),
        ex(
            "Transfer to unseen accounts",
            "Add account E with value1000 only to evaluation; specify whether its normalization can update the training mean.",
            "transformed value996; fitted mean remains4.",
            """new_value=1000-mean
assert new_value==996 and mean==4""",
            "A deployment input is transformed using the fitted state. Updating the mean online is a separate algorithm requiring an explicit policy and new evaluation; it is not a harmless formatting adjustment.",
        ),
    ],
    NP,
)
add(
    "tf-011",
    """Keras packages the same computation that the earlier tape lesson exposed. Dense computes a matrix product and optionally adds a bias. Compile selects the loss and optimizer but does not itself update weights. Training evaluates the forward function, reduces the loss, differentiates and applies the optimizer. To compare a high-level API with the hand-derived update, every relevant choice must match: no intercept, a zero initial weight, mean squared error, full-batch SGD and the same rate. Otherwise a difference may reflect a different model or objective instead of an API bug. Evaluation must be distinguished from a training call because it should not apply gradients.""",
    """Input(shape=(1,)) excludes the batch dimension. Dense(1,use_bias=False) creates a single trainable scalar kernel. Reshape the three observations to (3,1), matching targets exactly. Compile uses SGD(.1) with loss='mse'. train_on_batch executes one full-batch step without a data-shuffle dependency. get_weights returns NumPy copies useful for comparison. A new model is required for each independent control.""",
    [
        ("Dense", "An affine feature transformation with tracked weights."),
        ("Compile", "Configuration of loss, optimizer and metrics."),
        ("Training call", "Forward, differentiation and update on current weights."),
    ],
    [
        ex(
            "Construct a scalar model",
            "Create a zero-initialized single-unit model without bias and inspect its parameter count.",
            "one parameter and all initial predictions0.",
            """model=tf.keras.Sequential([tf.keras.Input(shape=(1,)),tf.keras.layers.Dense(1,use_bias=False,kernel_initializer='zeros')])
x=np.array([[1.],[2.],[3.]],dtype='float32'); y=2*x
assert model.count_params()==1
np.testing.assert_array_equal(model(x).numpy(),np.zeros((3,1)))""",
            "Excluding a bias preserves the exact scalar model yhat=w*x. A Dense layer with its default bias would introduce a second parameter and a second gradient, invalidating the direct comparison.",
        ),
        ex(
            "Audit the first update",
            "Compile with mean squared error and SGD(.1), then call train_on_batch once.",
            "kernel28/15 and post-update loss56/675 within1e-6.",
            """model.compile(optimizer=tf.keras.optimizers.SGD(.1),loss='mse')
model.train_on_batch(x,y)
np.testing.assert_allclose(model.get_weights()[0],[[28/15]],atol=1e-6,rtol=0)
np.testing.assert_allclose(np.mean((model(x).numpy()-y)**2),56/675,atol=1e-6,rtol=0)""",
            "The API may report the loss used for the update, rather than the loss at the updated weight. Recompute predictions after the step to distinguish before from after.",
        ),
        ex(
            "Inspect forward shape",
            "Pass two observations [[4],[5]] through the trained model and inspect output axes.",
            "shape(2,1), predictions112/15 and28/3.",
            """pred=model(np.array([[4.],[5.]],dtype='float32')).numpy()
assert pred.shape==(2,1)
np.testing.assert_allclose(pred[:,0],[112/15,28/3],atol=1e-6,rtol=0)""",
            "The leading dimension counts observations. Keeping the output column avoids broadcasting a vector target across a batch into a pairwise error matrix.",
        ),
        ex(
            "Evaluation leaves weights alone",
            "Snapshot the kernel, run a forward evaluation with training=False, and compare.",
            "kernel is exactly unchanged.",
            """before=model.get_weights()[0].copy(); model(x,training=False)
np.testing.assert_array_equal(before,model.get_weights()[0])""",
            "A forward evaluation can calculate predictions without an optimizer step. More complex layers have training-dependent behavior, which is why explicitly passing the flag becomes important later.",
        ),
        ex(
            "Show the extra intercept",
            "Construct an otherwise equivalent Dense layer with bias enabled and count trainable scalars.",
            "2 parameters; bias starts0.",
            """with_bias=tf.keras.Sequential([tf.keras.Input(shape=(1,)),tf.keras.layers.Dense(1,kernel_initializer='zeros',bias_initializer='zeros')])
assert with_bias.count_params()==2
np.testing.assert_array_equal(with_bias.get_weights()[1],[0])""",
            "A zero initial bias still has a gradient. Zero initialization does not freeze a parameter. Removing a parameter and initializing it to zero are different modeling decisions.",
        ),
        ex(
            "Compare the scalar oracle",
            "Compute the first gradient directly from NumPy residuals and inputs, without Keras.",
            "gradient-56/3 and update28/15.",
            """grad=2*np.mean((0*x-y)*x)
np.testing.assert_allclose(grad,-56/3,atol=1e-6,rtol=0)
np.testing.assert_allclose(-.1*grad,28/15,atol=1e-6,rtol=0)""",
            "An independent formula guards against using two wrappers around the same broken calculation. The float32 tolerance reflects arithmetic precision and does not excuse a mismatched target shape.",
        ),
    ],
    KERAS,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-012",
    """A regression investigation starts with a prediction unit and a split, not an optimizer. Here each row has three features and a deterministic target 2a-b+c. Four rows are reserved for fitting and two for assessment. A mean predictor is the baseline: it ignores features but provides a measured reference. A small linear model tests whether the features contain the intended relation. The split is fixed before any model decision. Training error shows fit to exposed records; holdout error measures only the two supplied unseen records, which is far too little for a broad reliability claim. Keep the arithmetic pilot alongside the final experiment because it tests an update independently of model quality.""",
    """The fixture is a float32 matrix with one row per observation. Slicing by saved IDs chooses rows in a known order. GradientTape differentiates mean squared residuals; SGD updates a three-by-one kernel. Compute the mean baseline from training targets only. A fixed loop limit makes runtime bounded and reports actual steps rather than treating a small loss as permission to continue indefinitely.""",
    [
        ("Baseline", "A simple prediction rule evaluated with the same split and metric."),
        ("Holdout", "Records excluded from fitting and model selection."),
        (
            "Evidence report",
            "Inputs, decisions, outputs and limits that make an experiment reviewable.",
        ),
    ],
    [
        ex(
            "Freeze six records",
            "Create the three-feature fixture below, assign IDs0..3 to train and 4..5 to holdout, and calculate targets.",
            "targets[0,2,-1,1,2,4], disjoint IDs.",
            """x=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1],[1,1,1],[2,1,1]],dtype='float32'); y=x@np.array([[2.],[-1.],[1.]],dtype='float32')
train=[0,1,2,3]; test=[4,5]
assert not set(train)&set(test)
np.testing.assert_array_equal(y[:,0],[0,2,-1,1,2,4])""",
            "The target formula is specified before fitting. This makes the learning problem inspectable, while still requiring the optimizer to recover useful weights from only the training subset.",
        ),
        ex(
            "Measure the baseline",
            "Use the training mean to predict both held-out targets and compute squared error.",
            "training mean.5; holdout MSE7.25.",
            """mean=float(y[train].mean()); baseline=float(np.mean((y[test]-mean)**2))
assert mean==.5 and baseline==7.25""",
            "Using the held-out mean would give the baseline access to assessment targets. Both the baseline and learned model must be evaluated on identical held-out IDs to support comparison.",
        ),
        ex(
            "Train a bounded model",
            "Initialize a three-by-one kernel at zero and make exactly100 full-training SGD updates at rate 0.1.",
            "100 updates; finite weights; training error below its initial value.",
            """w=tf.Variable(tf.zeros((3,1))); tx=tf.constant(x[train]); ty=tf.constant(y[train]); initial=float(tf.reduce_mean(ty**2))
for step in range(100):
    with tf.GradientTape() as tape: loss=tf.reduce_mean((tx@w-ty)**2)
    w.assign_sub(.1*tape.gradient(loss,w))
train_error=float(tf.reduce_mean((tx@w-ty)**2))
assert step+1==100 and train_error<initial and np.isfinite(w.numpy()).all()""",
            "The explicit step cap bounds the teaching run. Improvement is checked against the same initial training batch. It does not imply a universal learning-rate rule or a production acceptance threshold.",
        ),
        ex(
            "Open the holdout once",
            "Compute held-out MSE after the fixed100 updates and compare it with the frozen baseline.",
            "holdout error below7.25 on the two supplied records.",
            """test_error=float(np.mean((x[test]@w.numpy()-y[test])**2))
assert test_error<baseline
report={'train_mse':train_error,'test_mse':test_error,'test_count':2,'steps':100}
assert report['test_count']==2""",
            "Report training and held-out errors separately. The small test count is part of the result, not an inconvenient detail to suppress. Do not restart tuning after inspecting this value.",
        ),
        ex(
            "Preserve arithmetic evidence",
            "Derive a one-feature pilot update from x = [1, 2, 3] and target2x at w = 0,rate 0.1.",
            "weight28/15 and loss56/675.",
            """pilot=np.array([1.,2.,3.]); gradient=2*np.mean((-2*pilot)*pilot); updated=-.1*gradient
np.testing.assert_allclose([updated,np.mean((updated*pilot-2*pilot)**2)],[28/15,56/675],atol=1e-12,rtol=0)""",
            "A scalar diagnostic is a separate implementation check, not an alternative score for the three-feature model. Keeping both prevents an impressive-looking fit from concealing a broken update.",
        ),
        ex(
            "Reject a false conclusion",
            "Construct a report containing split IDs, errors, step count and limitations; refuse a production-quality claim from two holdout rows.",
            "report names2 holdout records and makes no population guarantee.",
            """report.update(train_ids=train,test_ids=test,limitation='Two synthetic holdout rows do not establish population reliability.')
assert report['test_ids']==[4,5] and 'do not establish' in report['limitation']""",
            "A reproducible experiment may still be too small for the intended decision. The correct result can be a limited demonstration with explicit next evidence, rather than an unsupported release recommendation.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-013",
    """A binary logit is an unrestricted score whose sigmoid is a probability under the chosen model. It is not already a probability. Binary cross entropy compares that probability with a zero-or-one target. A logits-aware implementation combines the sigmoid and logarithms into a stable calculation. The decision threshold is a separate policy: moving it changes predicted classes without changing the fitted scores. This distinction matters when false positives and false negatives have different costs. The three-point fixture is designed to make the boundary at probability one half explicit. It cannot show that the probabilities are calibrated on real observations.""",
    "`tf.math.sigmoid` converts each score independently. `sigmoid_cross_entropy_with_logits` requires labels and logits of equal shape and computes a loss per entry. `reduce_mean` chooses the example denominator. Compare `probability>=threshold` for a declared tie policy. Do not apply sigmoid twice or feed a probability to a function that expects a logit; both can produce finite but incorrectly interpreted losses.",
    [
        ("Logit", "An unrestricted binary score before the sigmoid transformation."),
        ("Threshold", "A probability boundary used to choose a class."),
        ("Binary cross entropy", "Negative log probability assigned to the observed binary label."),
    ],
    [
        ex(
            "Convert scores",
            "Convert logits[-2,0,2] into probabilities and inspect the central value.",
            "middle probability.5; probabilities increase.",
            """z=tf.constant([-2.,0.,2.]); p=tf.math.sigmoid(z).numpy()
assert p[1]==.5 and np.all(np.diff(p)>0)""",
            "The sigmoid is monotonic, so ordering survives. A score of zero lies at the probability midpoint, which makes it a useful exact boundary fixture.",
        ),
        ex(
            "Check the midpoint loss",
            "Calculate positive-label binary cross entropy at zero logit.",
            "loss log(2) within1e-6.",
            """loss=tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.constant([1.]),logits=tf.constant([0.]))
np.testing.assert_allclose(loss.numpy(),[np.log(2)],atol=1e-6,rtol=0)""",
            "A fifty-fifty prediction assigns probability one half to either outcome. Its negative logarithm provides an independent reference that does not depend on a trained model.",
        ),
        ex(
            "Move the threshold",
            "Compare decisions at thresholds.5 and.8 with >= ties.",
            "decisions[False,True,True] versus[False,False,True].",
            """assert (p>=.5).tolist()==[False,True,True]
assert (p>=.8).tolist()==[False,False,True]""",
            "Only the middle decision changes. Save scores independently from decisions so threshold exploration does not look like a second model fitting operation.",
        ),
        ex(
            "Expose a convention mismatch",
            "Treat probability.5 as if it were a logit and compare the positive-label loss with log2.",
            "wrong loss differs from log2 by more than.1.",
            """wrong=float(tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.constant(1.),logits=tf.constant(.5)))
assert abs(wrong-np.log(2))>.1""",
            "The mistaken argument is interpreted as a score favoring the positive class. The API cannot infer that the caller intended a probability; explicit naming and shape contracts are necessary.",
        ),
        ex(
            "Stress large scores",
            "Calculate losses for logits 1000,-1000 with labels1,0 using the logits-aware form.",
            "both finite losses approximately0.",
            """stable=tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.constant([1.,0.]),logits=tf.constant([1000.,-1000.])).numpy()
assert np.isfinite(stable).all(); np.testing.assert_allclose(stable,[0,0],atol=1e-6,rtol=0)""",
            "A naive log(sigmoid()) path can lose precision at extreme probabilities. The stable form handles the algebra before exponentiation creates overflow or logarithms receive rounded zero.",
        ),
        ex(
            "Count decisions separately",
            "For labels[0,1,1], count errors under the two thresholds.",
            "0 errors at.5 and 1 at.8 on this fixture.",
            """labels=np.array([0,1,1]); assert np.count_nonzero((p>=.5)!=labels)==0
assert np.count_nonzero((p>=.8)!=labels)==1""",
            "This count is a decision metric. It does not replace the probability loss and cannot show that threshold .5 is optimal for a different cost structure or population.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-014",
    """Multiclass and multilabel prediction answer different questions. In a multiclass task exactly one class is chosen, so a softmax distributes one unit of probability across mutually exclusive outcomes. In a multilabel task several labels may hold at once, so each label gets its own binary decision. A tensor with three outputs does not by itself tell you which task is intended. The target contract determines the activation, loss and denominator. Integer sparse targets name one class index; a vector such as [1,0,1] names two independently present labels. Converting one task into the other changes the meaning of the data.""",
    """Sparse categorical cross entropy takes class indices with shape(batch,), alongside logits shaped(batch,classes). Sigmoid cross entropy instead takes a binary matrix matching logits. Softmax reduces across the class axis. Explicitly check which axes a loss function reduces before comparing mean losses, particularly when multilabel losses are averaged across both labels and examples.""",
    [
        ("Multiclass", "One outcome among mutually exclusive categories."),
        ("Multilabel", "Independent binary outcomes that may coexist."),
        ("Sparse target", "An integer index of the observed class."),
    ],
    [
        ex(
            "Uniform class uncertainty",
            "Compute sparse cross entropy for target1 and three zero logits.",
            "loss log(3).",
            """logits=tf.zeros((1,3)); loss=tf.nn.sparse_softmax_cross_entropy_with_logits(labels=[1],logits=logits)
np.testing.assert_allclose(loss.numpy(),[np.log(3)],atol=1e-6,rtol=0)""",
            "Three equal scores create a uniform distribution. The target probability is one third, so the negative log likelihood is log3, independent of which class index is chosen.",
        ),
        ex(
            "Independent labels",
            "Calculate sigmoid probabilities for three zero logits and labels[1,0,1].",
            "three probabilities.5 with total1.5.",
            """probs=tf.math.sigmoid(logits).numpy()
np.testing.assert_array_equal(probs,[[.5,.5,.5]])
assert probs.sum()==1.5""",
            "Independent binary probabilities do not need to sum to one. Forcing a softmax here would make the two present labels compete for probability mass.",
        ),
        ex(
            "Contrast target shapes",
            "Build sparse targets[2,0] and multilabel targets[[1,0,1],[0,1,0]].",
            "shapes(2,) and(2,3).",
            """sparse=np.array([2,0],dtype=np.int32); multi=np.array([[1,0,1],[0,1,0]],dtype=np.float32)
assert sparse.shape==(2,) and multi.shape==(2,3)""",
            "A class index is a category identity, not a magnitude. The multilabel row contains three observations of presence. Keeping these shapes explicit prevents unintended broadcasting.",
        ),
        ex(
            "Verify softmax mass",
            "Apply softmax to[[2,0,-2]] and compare its sum with sigmoid output.",
            "softmax sum1; sigmoid sum1.5.",
            """z=tf.constant([[2.,0.,-2.]])
np.testing.assert_allclose(tf.nn.softmax(z).numpy().sum(),1,atol=1e-6,rtol=0)
np.testing.assert_allclose(tf.math.sigmoid(z).numpy().sum(),1.5,atol=1e-6,rtol=0)""",
            "The normalizer in softmax couples categories. Sigmoids do not share a normalizer, which is why changing one logit has different consequences in the two tasks.",
        ),
        ex(
            "Choose the denominator",
            "Compute binary cross entropy for two three-label rows of zero logits; compare sum with entry mean.",
            "sum6log2; meanlog2.",
            """losses=tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.constant(multi),logits=tf.zeros((2,3))).numpy()
np.testing.assert_allclose([losses.sum(),losses.mean()],[6*np.log(2),np.log(2)],atol=1e-6,rtol=0)""",
            "There are six binary entries but only two records. A mean per record of summed labels differs from a mean per binary entry by three. State the intended objective instead of comparing unlabelled loss numbers.",
        ),
        ex(
            "Reject an impossible class",
            "Validate a sparse class index before lookup in a three-class vocabulary.",
            "index3 is outside legal indices0,1,2.",
            """def validate_class(value):
    if not isinstance(value,int) or isinstance(value,bool) or not 0<=value<3: raise ValueError('class index')
    return value
assert validate_class(2)==2
try: validate_class(3)
except ValueError: pass
else: raise AssertionError('accepted unknown class')""",
            "A target index equal to the vocabulary size is out of range. Early validation keeps a category-definition failure distinct from an optimizer failure.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-015",
    """A data pipeline is part of the statistical experiment. It determines which records arrive, in what order, under which transformation and how many times. tf.data represents that sequence lazily. Constructing a Dataset is not evidence that its elements were visited. Carry record IDs through transformations so cardinality and pairing remain inspectable. A training-derived mean can be applied during mapping, but validation records must not participate in estimating it. Batching creates a new leading axis, and prefetch overlaps preparation with consumption without changing the desired order. This tiny pipeline uses literal arrays and no file or network side effects.""",
    """from_tensor_slices slices the leading axis of each tuple component together. map receives one ID and one value; arithmetic can use a frozen scalar mean. batch(2,drop_remainder=False) retains the final singleton. as_numpy_iterator materializes values for small teaching assertions, not an approach for collecting an unbounded production dataset. prefetch(1) limits the look-ahead buffer.""",
    [
        ("Cardinality", "Number of dataset elements at a specific pipeline stage."),
        ("Map", "A transformation applied to each element."),
        ("Prefetch", "Bounded preparation of upcoming elements before consumption."),
    ],
    [
        ex(
            "Observe batches",
            "Build a dataset from IDs0..4 and values1..5, then batch by2.",
            "batch sizes[2,2,1].",
            """ds=tf.data.Dataset.from_tensor_slices((np.arange(5),np.arange(1,6,dtype='float32')))
batches=list(ds.batch(2).as_numpy_iterator())
assert [len(ids) for ids,values in batches]==[2,2,1]""",
            "The input cardinality is five records but the batched cardinality is three elements. Naming the stage prevents a batch count from being mistaken for a dataset size.",
        ),
        ex(
            "Apply training statistics",
            "Use values1,2,3 to fit mean 2, then transform all five values without refitting.",
            "centered values[-1,0,1,2,3].",
            """mean=np.mean([1.,2.,3.]); centered=ds.map(lambda i,v:(i,v-tf.cast(mean,tf.float32)))
values=np.array([float(v) for i,v in centered.as_numpy_iterator()])
np.testing.assert_array_equal(values,[-1,0,1,2,3])""",
            "The held-out values4 and5 are transformed with the same mean. Their transformed average is not zero, which is expected when a frozen training transformation meets a different subset.",
        ),
        ex(
            "Retain IDs through mapping",
            "Reassemble the IDs after centering, batching and prefetch1.",
            "IDs0,1,2,3,4 in order.",
            """got=np.concatenate([i for i,v in centered.batch(2).prefetch(1).as_numpy_iterator()])
np.testing.assert_array_equal(got,np.arange(5))""",
            "Value-only comparisons cannot detect reordered or duplicated observations when values repeat. IDs provide an independent conservation check across the pipeline.",
        ),
        ex(
            "Compare explicit dropping",
            "Use drop_remainder=True and report which record disappears.",
            "sizes[2,2]; ID4 absent.",
            """dropped=list(ds.batch(2,drop_remainder=True).as_numpy_iterator())
assert [len(i) for i,v in dropped]==[2,2]
assert np.concatenate([i for i,v in dropped]).tolist()==[0,1,2,3]""",
            "Dropping can be intentional for fixed-shape training, but it changes the effective population of an epoch. A learner should record the omitted tail instead of calling the pipeline equivalent.",
        ),
        ex(
            "Recreate a deterministic traversal",
            "Construct the same literal dataset twice and compare complete ordered values.",
            "both traversals equal the original five pairs.",
            """again=tf.data.Dataset.from_tensor_slices((np.arange(5),np.arange(1,6,dtype='float32')))
a=[(int(i),float(v)) for i,v in ds.as_numpy_iterator()]
b=[(int(i),float(v)) for i,v in again.as_numpy_iterator()]
assert a==b==[(0,1.),(1,2.),(2,3.),(3,4.),(4,5.)]""",
            "A repeated traversal is meaningful because there is no hidden random map, file update or external fetch. Later random augmentation requires an additional policy and invariants.",
        ),
        ex(
            "Check paired transformation",
            "Scale values by2 and preserve IDs, then verify the value relation2*(ID+1).",
            "all five pairs satisfy the relation.",
            """scaled=ds.map(lambda i,v:(i,2*v))
assert all(float(v)==2*(int(i)+1) for i,v in scaled.as_numpy_iterator())""",
            "Keeping paired components in one dataset tuple prevents independent reorderings. The exact arithmetic relation detects a pipeline that transforms values while selecting unrelated IDs.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-016",
    """Stacking affine layers without an intervening nonlinearity still produces an affine function. XOR asks for opposite labels at the diagonally opposite corners of a square, a pattern one affine threshold cannot separate. Two rectified differences create the needed representation: h1=max(x1-x2,0), h2=max(x2-x1,0). Their sum is one exactly when the inputs differ. This hand-built network separates representational capacity from optimization. If the construction works but a fitted model does not, the architecture may be capable while the training procedure failed. Initialization changes the starting state and symmetry of fitting; it cannot repair an architecture that lacks the required function.""",
    """A Dense transform computes X@W. The chosen columns of W form x1-x2 and x2-x1. ReLU applies max(z,0) independently, then reduce_sum combines the hidden units. Before fitting, evaluate all four binary inputs. The affine contradiction comes from summing inequalities at the two positive and two negative corners, so it does not depend on testing many random initializations.""",
    [
        ("Nonlinearity", "A transformation that cannot be represented by a single affine map."),
        ("ReLU", "The rectified linear function max(z,0)."),
        ("Capacity", "The set of functions a model architecture can represent."),
    ],
    [
        ex(
            "Construct XOR",
            "Evaluate two rectified differences on inputs(0,0),(0,1),(1,0),(1,1).",
            "outputs[0,1,1,0].",
            """x=tf.constant([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
w=tf.constant([[1.,-1.],[-1.,1.]])
h=tf.nn.relu(x@w); output=tf.reduce_sum(h,axis=1)
np.testing.assert_array_equal(output.numpy(),[0,1,1,0])""",
            "The hidden features encode the two possible directions of disagreement. Their values are never simultaneously positive on the binary fixture, so their sum behaves like XOR.",
        ),
        ex(
            "Remove the nonlinearity",
            "Sum the two raw difference columns before applying a threshold.",
            "all four sums0.",
            """np.testing.assert_array_equal(tf.reduce_sum(x@w,axis=1).numpy(),[0,0,0,0])""",
            "The columns cancel exactly. The ReLU was the step that prevented the positive and negative differences from cancelling, rather than merely adding an extra layer name.",
        ),
        ex(
            "Compose affine matrices",
            "Multiply two fixed matrices and verify that a two-layer linear computation equals one matrix product.",
            "two paths agree within1e-6.",
            """a=tf.constant([[1.,2.],[3.,4.]]); b=tf.constant([[2.],[-1.]])
np.testing.assert_allclose(((x@a)@b).numpy(),(x@(a@b)).numpy(),atol=1e-6,rtol=0)""",
            "Associativity collapses linear layers. Bias terms can also be combined, so adding affine depth alone does not overcome the XOR separation problem.",
        ),
        ex(
            "Inspect a dead region",
            "Evaluate ReLU and its tape gradient at-2 and+2.",
            "values[0,2], gradients[0,1].",
            """z=tf.Variable([-2.,2.])
with tf.GradientTape() as tape: total=tf.reduce_sum(tf.nn.relu(z))
np.testing.assert_array_equal(tf.nn.relu(z).numpy(),[0,2]); np.testing.assert_array_equal(tape.gradient(total,z).numpy(),[0,1])""",
            "A negative preactivation has zero local derivative in this example. Units initialized or driven into inactive regions can receive no update from those observations, which is distinct from a missing gradient path.",
        ),
        ex(
            "Show symmetry",
            "Create two hidden units with identical columns and compare their activations on every XOR input.",
            "hidden columns match exactly.",
            """same=tf.constant([[1.,1.],[2.,2.]])
features=tf.nn.relu(x@same).numpy(); np.testing.assert_array_equal(features[:,0],features[:,1])""",
            "Identical initialization can leave units redundant under symmetric gradient updates. Distinct parameters do not automatically create distinct learned features.",
        ),
        ex(
            "Transfer outside the corners",
            "Evaluate the fixed construction at(.2,.8) and(.8,.2), and state what it computes away from binary inputs.",
            "both outputs.6; function is absolute difference.",
            """q=tf.constant([[.2,.8],[.8,.2]])
np.testing.assert_allclose(tf.reduce_sum(tf.nn.relu(q@w),axis=1).numpy(),[.6,.6],atol=1e-6,rtol=0)""",
            "The exact network computes absolute difference on continuous inputs. Calling it XOR outside the binary domain would conceal an assumption about the input space.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-017",
    """Regularization changes the training objective or the training computation. An L1 penalty sums absolute weights; an L2 penalty here sums squared weights, with its coefficient declared separately. These quantities differ from data loss and have different scaling. Dropout randomly removes activations during training while rescaling retained values; evaluation normally uses the unmodified activations. A random training call should be tested through invariants such as allowed output values and shape, not a hardcoded random bit pattern across platforms. Evaluation behavior should be deterministic for this isolated layer. None of these mechanisms automatically proves improved generalization.""",
    """reduce_sum(abs(w)) and reduce_sum(square(w)) implement the declared penalty conventions. Add lambda*penalty to data loss only when that is the intended objective. Dropout(rate=.5) with training=True maps each unit input to0 or2. training=False returns the input. Keras regularizer conventions and optimizer weight decay should be checked explicitly instead of being assumed interchangeable.""",
    [
        ("Penalty", "A parameter-dependent term added to an objective."),
        ("Dropout", "A stochastic training transformation that zeroes activations."),
        ("Evaluation mode", "Inference behavior with training-time stochastic changes disabled."),
    ],
    [
        ex(
            "Calculate penalties",
            "Compute L1 and squared L2 sums for weights[1,-2].",
            "L1=3; squaredL2=5.",
            """w=tf.constant([1.,-2.]); l1=float(tf.reduce_sum(tf.abs(w))); l2=float(tf.reduce_sum(w*w))
assert (l1,l2)==(3.,5.)""",
            "The name L2 can mean a norm or a squared penalty in different contexts. This exercise explicitly uses the sum of squares, avoiding an unexplained square root or half factor.",
        ),
        ex(
            "Switch dropout to evaluation",
            "Apply dropout.5 twice to ones with training=False.",
            "both outputs equal the input.",
            """layer=tf.keras.layers.Dropout(.5); x=tf.ones((4,8)); a=layer(x,training=False); b=layer(x,training=False)
np.testing.assert_array_equal(a.numpy(),x.numpy()); np.testing.assert_array_equal(b.numpy(),x.numpy())""",
            "Evaluation removes the random masking behavior. Testing repeated calls establishes this local contract without making claims about other random components in a full pipeline.",
        ),
        ex(
            "Inspect training invariants",
            "Call the same dropout layer with training=True and examine allowed output values.",
            "shape(4,8), values only0 or2.",
            """train=layer(x,training=True).numpy()
assert train.shape==(4,8) and set(np.unique(train))<={0.,2.}""",
            "The retained activations are scaled to keep their expectation unchanged. A finite fixture may coincidentally keep or drop many values; requiring an exact mask would overconstrain the test.",
        ),
        ex(
            "Separate objective terms",
            "Combine data loss2 with coefficient.1 times squaredL2 and report both components.",
            "data2, penalty.5, total2.5.",
            """data_loss=2.; coefficient=.1; penalty=coefficient*l2
assert penalty==.5 and data_loss+penalty==2.5""",
            "Logging only the total makes it hard to distinguish predictive error from a changing regularization cost. The coefficient is part of the objective definition.",
        ),
        ex(
            "Differentiate the penalty",
            "Differentiate.1*sum(w²) at[1,-2].",
            "gradient[.2,-.4].",
            """v=tf.Variable([1.,-2.])
with tf.GradientTape() as tape: penalty=.1*tf.reduce_sum(v*v)
np.testing.assert_allclose(tape.gradient(penalty,v).numpy(),[.2,-.4],atol=1e-6,rtol=0)""",
            "The derivative is2*lambda*w under the stated convention. A half-scaled penalty would have a different gradient, so a coefficient cannot be copied blindly between definitions.",
        ),
        ex(
            "Scale weights deliberately",
            "Double both weights and compare the new penalties with the original values.",
            "L1 doubles to6; squaredL2 quadruples to20.",
            """assert float(tf.reduce_sum(tf.abs(2*w)))==6
assert float(tf.reduce_sum((2*w)**2))==20""",
            "The different scaling explains why the penalties discourage large coefficients differently. This arithmetic does not establish which choice will work better on an unseen dataset.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
import tf018

add(
    "tf-019",
    """Convolutional layers reuse a small kernel at many positions. Each output sees a local patch, so the kernel has fewer parameters than an unconstrained map from every input pixel to every output pixel. TensorFlow applies cross-correlation: it slides the kernel without rotating it. A mathematical convolution would reverse spatial axes. Channels and batches add axes but do not change the basic local dot product. VALID padding includes only patches entirely inside the image; SAME padding inserts boundary values under a defined convention. The output shape depends on input size, kernel size, stride and padding, not on the apparent visual size of a plotted image.""",
    """tf.nn.conv2d expects image shape(batch,height,width,channels) and filter shape(height,width,input_channels,output_channels). A3x3 single-channel image and2x2 kernel with stride1 and VALID padding produce shape(1,2,2,1). The first result is1-5=-4. Rotating the kernel changes that sign. Keep the batch/channel singleton axes visible when checking shapes.""",
    [
        ("Kernel", "Shared weights applied to each local patch."),
        ("Stride", "Distance between adjacent kernel positions."),
        ("Receptive field", "Input positions that can influence an output."),
    ],
    [
        ex(
            "Compute local differences",
            "Apply kernel[[1,0],[0,-1]] to the image1..9 arranged3x3.",
            "all four outputs-4.",
            """image=tf.reshape(tf.range(1,10,dtype=tf.float32),(1,3,3,1)); kernel=tf.reshape(tf.constant([1.,0.,0.,-1.]),(2,2,1,1))
out=tf.nn.conv2d(image,kernel,strides=1,padding='VALID')
np.testing.assert_array_equal(out.numpy().reshape(2,2),np.full((2,2),-4))""",
            "Every patch has a bottom-right value four greater than its top-left value. The equal outputs are an arithmetic property of this ramp image, not a generic property of convolution.",
        ),
        ex(
            "Rotate the kernel",
            "Reverse both spatial axes and repeat the calculation.",
            "all outputs+4.",
            """rot=tf.reverse(kernel,axis=[0,1]); changed=tf.nn.conv2d(image,rot,strides=1,padding='VALID')
np.testing.assert_array_equal(changed.numpy().reshape(2,2),np.full((2,2),4))""",
            "Kernel orientation distinguishes cross-correlation from mathematical convolution. A symmetric kernel would hide this difference, which is why the asymmetric diagonal kernel is useful.",
        ),
        ex(
            "Count output positions",
            "Compare VALID stride1 and stride2.",
            "shapes(1,2,2,1) and(1,1,1,1).",
            """assert tuple(out.shape)==(1,2,2,1)
assert tuple(tf.nn.conv2d(image,kernel,strides=2,padding='VALID').shape)==(1,1,1,1)""",
            "A larger stride visits fewer legal patch starts. Shape arithmetic is a useful first check before interpreting any learned filter values.",
        ),
        ex(
            "Trace one pixel influence",
            "Add10 to the top-left image pixel and inspect which output changes.",
            "only output[0,0] increases10.",
            """changed_image=image.numpy().copy(); changed_image[0,0,0,0]+=10
delta=tf.nn.conv2d(changed_image,kernel,strides=1,padding='VALID').numpy()-out.numpy()
np.testing.assert_array_equal(delta.reshape(2,2),[[10,0],[0,0]])""",
            "The top-left pixel belongs only to the top-left valid patch. This controlled perturbation directly tests the local receptive field.",
        ),
        ex(
            "Count shared parameters",
            "Construct a bias-free Conv2D layer with2 filters of size2x2 on one input channel.",
            "8 trainable scalars regardless of image height.",
            """layer=tf.keras.layers.Conv2D(2,2,use_bias=False); layer(image)
assert layer.count_params()==8""",
            "Each output channel has its own four kernel coefficients. Reusing the layer at more spatial locations increases computation but does not create a separate weight set for each location.",
        ),
        ex(
            "Add a constant image offset",
            "Add100 to every pixel and compare outputs under the zero-sum kernel.",
            "output unchanged.",
            """offset=tf.nn.conv2d(image+100,kernel,strides=1,padding='VALID')
np.testing.assert_array_equal(offset.numpy(),out.numpy())""",
            "The kernel coefficients sum to zero, so a constant offset cancels. This invariance belongs to this kernel; a general learned kernel need not preserve it.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-020",
    """Pooling summarizes a local region without fitting a separate coefficient at each position. Max pooling retains the largest response; average pooling retains the mean. These summaries discard information and therefore have different invariances. Augmentation changes training inputs under an assumption that the desired label remains the same. A horizontal flip may preserve the label of a symmetric shape but can change a left-pointing arrow into a right-pointing arrow. The validity of an augmentation comes from task semantics, not from the availability of a library transform. Evaluation must use a fixed policy so score changes are not concealed by random transformations.""",
    """max_pool2d and avg_pool2d reduce spatial patches in a four-dimensional image tensor. flip_left_right reverses the width axis while preserving batch, height and channels. Use literal arrays to inspect these axes. Training augmentation and evaluation transformation should be separate functions, with evaluation returning a known deterministic input representation.""",
    [
        ("Pooling", "A local reduction that discards spatial detail."),
        ("Augmentation", "A training transformation justified by label semantics."),
        ("Label invariance", "The target remains valid after a transformation."),
    ],
    [
        ex(
            "Compare two reductions",
            "Pool patch[[1,3],[2,4]] with a2x2 window.",
            "max4; average2.5.",
            """x=tf.constant([[[[1.],[3.]],[[2.],[4.]]]])
assert float(tf.nn.max_pool2d(x,2,2,'VALID')[0,0,0,0])==4
assert float(tf.nn.avg_pool2d(x,2,2,'VALID')[0,0,0,0])==2.5""",
            "The max ignores the three smaller values, while the average uses every value equally. Equal output shapes do not mean equal retained information.",
        ),
        ex(
            "Inspect a flip",
            "Flip the patch horizontally and inspect every pixel.",
            "rows[3,1] and[4,2].",
            """flipped=tf.image.flip_left_right(x)
np.testing.assert_array_equal(flipped.numpy().reshape(2,2),[[3,1],[4,2]])""",
            "The operation reverses columns, not rows. Naming the width axis prevents a mistaken vertical transformation from silently changing a directional task.",
        ),
        ex(
            "Check an involution",
            "Flip twice and compare with the original image.",
            "all pixels restored exactly.",
            """np.testing.assert_array_equal(tf.image.flip_left_right(flipped).numpy(),x.numpy())""",
            "A horizontal flip is its own inverse. The round trip is a strong indexing check but does not prove that the intermediate image retained the original semantic label.",
        ),
        ex(
            "Expose discarded information",
            "Change the nonmaximum pixel1 to0 and recompute both pools.",
            "max still4; average2.25.",
            """altered=tf.constant([[[[0.],[3.]],[[2.],[4.]]]])
assert float(tf.nn.max_pool2d(altered,2,2,'VALID')[0,0,0,0])==4
assert float(tf.nn.avg_pool2d(altered,2,2,'VALID')[0,0,0,0])==2.25""",
            "The perturbation is invisible to max pooling. This helps explain why pooling creates robustness to some changes while also losing potentially useful detail.",
        ),
        ex(
            "Keep evaluation deterministic",
            "Define evaluation as an identity transform and compare repeated results with the source.",
            "both evaluations equal the original patch.",
            """def evaluate_image(value): return tf.identity(value)
np.testing.assert_array_equal(evaluate_image(x).numpy(),x.numpy())
np.testing.assert_array_equal(evaluate_image(x).numpy(),evaluate_image(x).numpy())""",
            "A deterministic evaluation path makes model comparisons interpretable. Random test augmentation would need a separately specified aggregation and uncertainty policy.",
        ),
        ex(
            "Reject a semantic flip",
            "Encode labels left and right and define the label change caused by horizontal reflection.",
            "left maps to right; retaining left is invalid.",
            """mirror={'left':'right','right':'left'}
assert mirror['left']=='right' and mirror[mirror['left']]=='left' """,
            "A reversible image transformation can still change the correct target. A valid training transform must either preserve the target or transform the target consistently, as this mapping demonstrates.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-021",
    """A padded sequence contains both real observations and artificial storage positions. An embedding lookup turns token IDs into vectors, but padding does not become a real token merely because it has a vector. Carry a valid-token mask alongside the sequence. When averaging token losses, divide by the number of valid targets rather than the padded length. Appending more padding should leave the score unchanged. Some layers propagate Keras masks, while custom arithmetic must apply them explicitly. This lesson treats token zero as padding under a declared vocabulary policy; another vocabulary may assign zero a real meaning.""",
    """The boolean comparison ids!=0 identifies valid tokens. tf.gather selects embedding rows in token order. tf.where(mask,loss,0) suppresses padding contributions, then reduce_sum(mask) supplies the denominator. Reject a completely padded sequence because it has no observed target loss. Avoid assuming that a numerical zero vector is an adequate replacement for an explicit mask.""",
    [
        ("Padding", "Artificial positions added to equalize storage shapes."),
        ("Embedding", "A learned or fixed vector table indexed by token ID."),
        ("Mask", "A boolean description of which positions participate."),
    ],
    [
        ex(
            "Mark valid positions",
            "Use token IDs[2,3,0] with zero declared padding.",
            "mask[True,True,False], count2.",
            """ids=tf.constant([2,3,0]); mask=ids!=0
assert mask.numpy().tolist()==[True,True,False]
assert int(tf.reduce_sum(tf.cast(mask,tf.int32)))==2""",
            "The mask derives from vocabulary semantics, not from the magnitude of an embedding vector. A real token could legitimately have a zero vector.",
        ),
        ex(
            "Normalize masked losses",
            "Use token losses[log2,log2,100] and exclude the padding position.",
            "masked meanlog2; padding loss100 has no effect.",
            """losses=tf.constant([np.log(2),np.log(2),100.],dtype=tf.float64)
mean=tf.reduce_sum(tf.where(mask,losses,0.))/tf.reduce_sum(tf.cast(mask,tf.float64))
np.testing.assert_allclose(float(mean),np.log(2),atol=1e-12,rtol=0)""",
            "The numerator and denominator must use the same participation policy. Zeroing the padding loss but dividing by three would understate the mean valid-token loss.",
        ),
        ex(
            "Check embedding axes",
            "Lookup IDs[2,3,0] in a fixed4x2 table.",
            "output shape(3,2); first row[2,2].",
            """table=tf.constant([[0.,0.],[1.,0.],[2.,2.],[3.,-1.]])
emb=tf.gather(table,ids)
assert tuple(emb.shape)==(3,2); np.testing.assert_array_equal(emb.numpy()[0],[2,2])""",
            "Lookup preserves token order and appends the feature dimension. It does not mix tokens or establish any language understanding by itself.",
        ),
        ex(
            "Append padding",
            "Add two padding IDs and arbitrary corresponding losses, then recalculate the masked mean.",
            "mean unchanged atlog2.",
            """extended=tf.constant([2,3,0,0,0]); m=extended!=0; l=tf.constant([np.log(2),np.log(2),100.,200.,300.],tf.float64)
v=tf.reduce_sum(tf.where(m,l,0.))/tf.reduce_sum(tf.cast(m,tf.float64))
np.testing.assert_allclose(float(v),float(mean),atol=1e-12,rtol=0)""",
            "Padding length is a storage choice. This metamorphic test catches any accidental use of padded length as the loss denominator.",
        ),
        ex(
            "Select the last valid state",
            "For token states[[2,2],[3,-1],[99,99]], select the final valid position.",
            "state[3,-1], not padding state[99,99].",
            """states=tf.constant([[2.,2.],[3.,-1.],[99.,99.]])
valid_states=tf.boolean_mask(states,mask)
np.testing.assert_array_equal(valid_states[-1].numpy(),[3,-1])""",
            "Indexing the last stored row confuses a padding slot with the last observation. The explicit mask keeps that distinction visible.",
        ),
        ex(
            "Refuse an empty denominator",
            "Write a masked-average helper and test an all-padding mask.",
            "ValueError for zero valid positions.",
            """def masked_mean(values,valid):
    values=np.asarray(values); valid=np.asarray(valid,dtype=bool)
    if values.shape!=valid.shape or not valid.any(): raise ValueError('valid targets required')
    return values[valid].mean()
try: masked_mean([1,2],[False,False])
except ValueError: pass
else: raise AssertionError('empty denominator accepted')""",
            "Returning zero for no targets would fabricate a perfect loss without any observations. Rejecting the case makes absence of evidence distinct from a measured zero error.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-022",
    """Attention mixes value vectors using weights derived from query-key scores. A causal mask restricts each query to its current and earlier positions. The mask must act before the key-axis softmax, otherwise forbidden positions can consume probability mass or influence normalization. Equal scores make the allowed distribution easy to calculate: each legal key receives equal weight. Prefix invariance is a direct information-boundary test: recomputing a shorter prefix should reproduce the full computation early outputs. This property must hold across every decoder component, not just attention. A passing mask test cannot detect a contaminated training corpus or incorrect target shifting.""",
    """Q@transpose(K) forms query-by-key scores, scaled by square root of key width. tf.linalg.band_part constructs the lower triangle. tf.where replaces forbidden scores with negative infinity before tf.nn.softmax(axis=-1). Multiplying weights by V returns one output vector per query. The supplied helper accepts only square, nonempty self-attention with matching row counts and finite data.""",
    [
        ("Query", "A vector used to request information from keys."),
        ("Key", "A vector scored against a query."),
        ("Causal mask", "A rule excluding future positions from a query."),
    ],
    [
        ex(
            "Calculate uniform mixtures",
            "Use zero3x2 queries and keys with V[[2,0],[0,2],[6,6]].",
            "outputs[[2,0],[1,1],[8/3,8/3]].",
            """q=np.zeros((3,2)); v=np.array([[2.,0.],[0.,2.],[6.,6.]])
out=attention(q,q,v).numpy()
np.testing.assert_allclose(out,[[2,0],[1,1],[8/3,8/3]],atol=1e-6,rtol=0)""",
            "Each row averages exactly its legal values. The first row copies one vector, the second averages two, and the third averages three. No learned weights are needed to inspect the boundary.",
        ),
        ex(
            "Perturb the future",
            "Replace only the third value with[100,200].",
            "first two rows unchanged; final row[34,202/3].",
            """future=v.copy(); future[2]=[100,200]; changed=attention(q,q,future).numpy()
np.testing.assert_allclose(changed[:2],out[:2],atol=1e-6,rtol=0)
np.testing.assert_allclose(changed[2],[34,202/3],atol=1e-6,rtol=0)""",
            "A change to a future value must not influence earlier queries. This causal assertion is more informative than a visually triangular attention plot.",
        ),
        ex(
            "Recompute every prefix",
            "For prefix lengths1,2,3 run the function anew on sliced Q,K,V.",
            "all prefix outputs match the full early rows.",
            """for cut in range(1,4):
    prefix=attention(q[:cut],q[:cut],v[:cut]).numpy()
    np.testing.assert_allclose(prefix,out[:cut],atol=1e-6,rtol=0)""",
            "The prefix computation reconstructs its mask and softmax. Slicing already-computed full weights would not independently test whether future information influenced them.",
        ),
        ex(
            "Expose post-softmax masking",
            "Multiply uniform1/3 weights by a triangle without renormalizing.",
            "row sums[1/3,2/3,1].",
            """broken=np.ones((3,3))/3*np.tri(3)
np.testing.assert_allclose(broken.sum(1),[1/3,2/3,1],atol=1e-12,rtol=0)""",
            "Zeros in forbidden positions do not prove a valid probability distribution. Masking after normalization leaves insufficient mass on early rows and changes their output scale.",
        ),
        ex(
            "Use nonuniform scores",
            "Set Q=K[[1,0],[0,1],[1,1]] and repeat the prefix test.",
            "prefix comparisons pass within1e-6.",
            """non=np.array([[1.,0.],[0.,1.],[1.,1.]])
full=attention(non,non,v).numpy()
for cut in range(1,4): np.testing.assert_allclose(attention(non[:cut],non[:cut],v[:cut]).numpy(),full[:cut],atol=1e-6,rtol=0)""",
            "Uniform scores can hide a missing scale factor or swapped query/key operation. A nonuniform fixture adds a second independent family of behavior.",
        ),
        ex(
            "Refuse malformed input",
            "Pass an empty sequence and a value matrix with the wrong row count.",
            "both raise ValueError.",
            """for args in [(np.empty((0,2)),np.empty((0,2)),np.empty((0,2))),(q,q,v[:2])]:
    try: attention(*args)
    except ValueError: pass
    else: raise AssertionError('bad shape accepted')""",
            "A probability distribution needs at least one legal key. Clear input failures prevent shape bugs from emerging later as unexplained NaNs or matrix multiplication errors.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
    """def attention(q,k,v):
    q,k,v=(np.asarray(a,dtype=np.float64) for a in (q,k,v))
    if any(a.ndim!=2 for a in (q,k,v)) or not len(q) or q.shape[1]==0: raise ValueError('nonempty matrices required')
    if k.shape!=q.shape or v.shape[0]!=len(q) or not all(np.isfinite(a).all() for a in (q,k,v)): raise ValueError('shape or finite contract')
    q,k,v=(tf.constant(a,tf.float64) for a in (q,k,v))
    scores=q@tf.transpose(k)/tf.sqrt(tf.cast(q.shape[1],tf.float64))
    allowed=tf.linalg.band_part(tf.ones((q.shape[0],q.shape[0]),dtype=tf.bool),-1,0)
    return tf.nn.softmax(tf.where(allowed,scores,tf.constant(-np.inf,tf.float64)),axis=-1)@v
""",
)
add(
    "tf-023",
    """An optimization loop can run without updating the intended parameter. A forward value calculated outside GradientTape may be disconnected even when its numeric value is correct. None means no recorded path, while a zero tensor means a recorded derivative evaluated to zero. Treating both as zero hides a model-construction failure. The loop must calculate loss inside the tape, request gradients for the intended variables, reject missing gradients, apply an update and recompute the post-update loss. A logged pre-update loss and post-update weight belong to different states. Tracing with tf.function changes how Python builds operations, so debug the eager state sequence first.""",
    """Use a new tape for every step. w.assign_sub(rate*gradient) mutates the tracked variable. Keep before/after weights as Python floats only for logging; converting the forward result to a NumPy value inside the loss would sever differentiation. Recompute yhat after assignment. The scalar pilot has a closed-form recurrence w_next=w-.1*(28/3)*(w-2).""",
    [
        ("Disconnected gradient", "No recorded differentiable path to the requested variable."),
        ("Zero gradient", "A connected derivative whose current value is zero."),
        ("State trace", "A record of values before and after each update."),
    ],
    [
        ex(
            "Expose a missing path",
            "Compute(w-2)² before opening a tape and ask that tape for its gradient.",
            "gradient is None.",
            """w=tf.Variable(0.,dtype=tf.float64); outside=(w-2)**2
with tf.GradientTape() as tape: loss=outside
assert tape.gradient(loss,w) is None""",
            "The tape cannot reconstruct operations it never recorded. The numerical loss4 alone does not reveal this missing dependency.",
        ),
        ex(
            "Distinguish an actual zero",
            "Compute the same objective inside the tape atw2.",
            "gradient is a tensor equal0.",
            """optimum=tf.Variable(2.,dtype=tf.float64)
with tf.GradientTape() as tape: loss=(optimum-2)**2
g=tape.gradient(loss,optimum); assert g is not None and float(g)==0""",
            "The path exists and its slope is zero at the optimum. Replacing every None with zero would make these semantically different observations indistinguishable.",
        ),
        ex(
            "Repair two updates",
            "Use x = [1, 2, 3],y = 2x,w = 0 and rate 0.1 for exactly 2 steps.",
            "weight448/225 within1e-12.",
            """x=tf.constant([1.,2.,3.],tf.float64); y=2*x; w=tf.Variable(0.,dtype=tf.float64); history=[]
for _ in range(2):
    with tf.GradientTape() as tape: loss=tf.reduce_mean((w*x-y)**2)
    g=tape.gradient(loss,w); assert g is not None
    w.assign_sub(.1*g); history.append(float(w))
np.testing.assert_allclose(float(w),448/225,atol=1e-12,rtol=0)""",
            "The first update is28/15 and the second moves closer to2. This exact recurrence tests the loop order independently of framework metrics.",
        ),
        ex(
            "Recompute loss after assignment",
            "Compare the two-step loss with the one-step loss56/675.",
            "two-step loss is smaller and nonnegative.",
            """after=float(tf.reduce_mean((w*x-y)**2))
assert 0<=after<56/675""",
            "A loss tensor saved from before assignment does not retroactively change when the variable changes. The new loss requires a new forward calculation.",
        ),
        ex(
            "Check gradient finiteness",
            "Inject a nonfinite target and refuse to apply its gradient.",
            "gradient is nonfinite and rejected before assignment.",
            """bad=tf.constant([2.,4.,np.inf],tf.float64); saved=float(w)
with tf.GradientTape() as tape: loss=tf.reduce_mean((w*x-bad)**2)
g=tape.gradient(loss,w)
assert not bool(tf.reduce_all(tf.math.is_finite(g))) and float(w)==saved""",
            "A bounded loop should check nonfinite state before contaminating weights. A skipped invalid update must be reported as a failure, not counted as a successful learning step.",
        ),
        ex(
            "Compare an analytic recurrence",
            "Calculate both updates with plain Python and compare each state with the tape trace.",
            "both recorded states match within1e-12.",
            """oracle=0.; expected=[]
for _ in range(2): oracle-=.1*(28/3)*(oracle-2); expected.append(oracle)
np.testing.assert_allclose(history,expected,atol=1e-12,rtol=0)""",
            "Comparing every state identifies the first divergence. A final-value-only check can hide compensating errors or incorrect intermediate logging.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-024",
    """A classifier experiment needs more than an accuracy number. Define which rows are independent, freeze training/validation/test groups, fit preprocessing only on training data and choose decisions before opening the test partition. The fixture uses the sign of a geometric coordinate so its labels can be inspected directly. A tiny linear sigmoid classifier is sufficient; extra hidden layers are optional, not a requirement. Confusion counts retain the error types and must sum to the test cardinality. Per-group reporting reveals failures that an aggregate can hide. A capstone is complete when its data and evaluation contracts are defensible, even if its measured score is disappointing.""",
    """Binary logits feed sigmoid cross entropy during training. After a fixed step budget, classify with logit>=0, equivalent to probability>=.5. Compute true-positive, false-positive, true-negative and false-negative counts with boolean masks. Keep counts as integers and divide only after establishing their denominators. Save the split IDs before any training operation.""",
    [
        ("Confusion counts", "Counts of correct and incorrect positive and negative decisions."),
        ("Decision policy", "A frozen rule converting scores into predictions."),
        ("Test unit", "The held-out entity counted once in final evaluation."),
    ],
    [
        ex(
            "Freeze geometry and groups",
            "Use training points[-2,-1,1,2], labels[0,0,1,1]; hold out[-3,3].",
            "4 train and2 test records with no shared IDs.",
            """x=np.array([[-2.],[-1.],[1.],[2.]],dtype='float32'); y=np.array([[0.],[0.],[1.],[1.]],dtype='float32')
test_x=np.array([[-3.],[3.]],dtype='float32'); test_y=np.array([0,1]); train_ids={'a','b','c','d'}; test_ids={'e','f'}
assert not train_ids&test_ids and len(test_ids)==2""",
            "The toy target is fully specified, so a learner can reason about errors without an opaque dataset. The holdout still has only two observations and cannot support broad conclusions.",
        ),
        ex(
            "Fit training preprocessing",
            "Calculate training mean and standard deviation, then apply them to both sets.",
            "mean0; scale sqrt2.5; test transformed symmetrically.",
            """mean=x.mean(0); scale=x.std(0); tx=(x-mean)/scale; vx=(test_x-mean)/scale
np.testing.assert_allclose(scale,[np.sqrt(2.5)],atol=1e-6,rtol=0)
assert mean[0]==0 and vx[0,0]==-vx[1,0]""",
            "The test coordinates never enter the mean or scale calculation. A symmetric result is expected here because the training fixture itself is symmetric.",
        ),
        ex(
            "Train within a fixed budget",
            "Initialize one weight 0 and run40 full-batch SGD steps at rate 0.1 using binary logits loss.",
            "40 finite updates and positive final weight.",
            """w=tf.Variable([[0.]],dtype=tf.float32)
for step in range(40):
    with tf.GradientTape() as tape: loss=tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=y,logits=tf.constant(tx)@w))
    w.assign_sub(.1*tape.gradient(loss,w))
assert step+1==40 and float(w[0,0])>0 and np.isfinite(w.numpy()).all()""",
            "The known sign relation creates a transparent diagnostic. The loop is intentionally bounded and does not tune its step count after viewing held-out predictions.",
        ),
        ex(
            "Account for every test row",
            "Threshold final test logits at0 and compute all four confusion counts.",
            "TP1,TN1,FP0,FN0; total2.",
            """pred=(vx@w.numpy()).ravel()>=0; truth=test_y.astype(bool)
counts={'tp':int(np.sum(pred&truth)),'tn':int(np.sum(~pred&~truth)),'fp':int(np.sum(pred&~truth)),'fn':int(np.sum(~pred&truth))}
assert counts=={'tp':1,'tn':1,'fp':0,'fn':0} and sum(counts.values())==2""",
            "The sum is a conservation test. Dropping difficult rows or counting a repeated record twice would invalidate the reported metric even if the remaining predictions were correct.",
        ),
        ex(
            "Compare a baseline",
            "Predict class0 for every held-out row and report its error count beside the model.",
            "baseline1 error; model0 on2 records.",
            """baseline=np.zeros(2,dtype=bool)
assert np.count_nonzero(baseline!=truth)==1 and np.count_nonzero(pred!=truth)==0""",
            "The baseline uses the same held-out observations and decision unit. Its simplicity makes the gain interpretable, but the tiny count leaves substantial uncertainty.",
        ),
        ex(
            "Expose a subgroup failure",
            "Assign test groups negative and positive; flip only the positive prediction and report group errors.",
            "negative0/1; positive1/1.",
            """broken=pred.copy(); broken[1]=False
report={g:(int(broken[i]!=truth[i]),1) for i,g in enumerate(['negative','positive'])}
assert report=={'negative':(0,1),'positive':(1,1)}""",
            "The aggregate error rate would be one half. Naming the affected group and its denominator preserves the mechanism of the failure and avoids treating two groups as equally reliable.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-025",
    """An embedding objective encourages relationships between representations. Dot products depend on both direction and magnitude, whereas cosine divides by both vector norms and measures direction. A positive pair is declared related; a negative pair is declared unrelated under a sampling policy. That policy is part of the task. If a duplicate of the positive is labelled negative, the objective asks the model to satisfy contradictory evidence. A numerical loss can still be finite in this situation, so inspect identities before optimizing. The three fixed vectors let you calculate every score and show why a higher dot product is not always stronger directional similarity.""",
    """reduce_sum(a*b) is a dot product for equal-length vectors. Divide by norm(a)*norm(b) for cosine and reject a zero norm. A two-candidate contrastive loss can be written as sparse softmax cross entropy with target index0. Temperature divides scores before normalization. It changes the sharpness of probabilities and the scale of gradients, not which candidate initially ranks first.""",
    [
        ("Positive pair", "Two examples declared related by the training task."),
        ("Negative pair", "An example pair declared unrelated under a sampling policy."),
        ("Cosine similarity", "Dot product divided by the product of vector lengths."),
    ],
    [
        ex(
            "Compare similarity measures",
            "Use anchor[1,0],positive[1,1],negative[0,1]; compute dots and cosines.",
            "dots1,0; cosines1/sqrt2,0.",
            """a=np.array([1.,0.]); pos=np.array([1.,1.]); neg=np.array([0.,1.])
assert (a@pos,a@neg)==(1,0)
np.testing.assert_allclose([(a@pos)/(np.linalg.norm(a)*np.linalg.norm(pos)),a@neg],[1/np.sqrt(2),0],atol=1e-12,rtol=0)""",
            "The positive is not parallel to the anchor, so its cosine is below one despite a dot product of one. Magnitudes and directions should not be conflated.",
        ),
        ex(
            "Scale a candidate",
            "Multiply the positive vector by10 and compare dot product and cosine.",
            "dot10; cosine unchanged.",
            """scaled=10*pos
assert a@scaled==10
np.testing.assert_allclose((a@scaled)/(np.linalg.norm(a)*np.linalg.norm(scaled)),1/np.sqrt(2),atol=1e-12,rtol=0)""",
            "Scaling changes the unnormalized score but leaves direction unchanged. This demonstrates why normalization is a modeling choice with consequences for retrieval rankings.",
        ),
        ex(
            "Calculate a contrastive loss",
            "Use logits[1,0] with the positive at index0.",
            "losslog(1+exp(-1)).",
            """loss=tf.nn.sparse_softmax_cross_entropy_with_logits(labels=[0],logits=[[1.,0.]])
np.testing.assert_allclose(loss.numpy(),[np.log1p(np.exp(-1))],atol=1e-6,rtol=0)""",
            "The loss encourages the positive score to exceed the negative score. It does not independently establish that the selected negative is semantically unrelated.",
        ),
        ex(
            "Detect a false negative",
            "Replace the negative vector and identity with the positive identity.",
            "duplicate positive/negative identity is flagged.",
            """positive_id='doc-a'; negative_id='doc-a'; duplicate=np.array_equal(pos,pos.copy())
assert duplicate and positive_id==negative_id""",
            "Identity checks belong before interpreting training loss. Two equal vectors may arise legitimately, but the same document explicitly labelled both positive and negative is a direct contradiction.",
        ),
        ex(
            "Observe temperature",
            "Compare softmax[1,0] at temperatures1 and.5.",
            "positive probability increases at.5; ranking stays0 first.",
            """p1=tf.nn.softmax([1.,0.]).numpy(); p2=tf.nn.softmax(np.array([1.,0.],dtype='float32')/.5).numpy()
assert p2[0]>p1[0] and int(p1.argmax())==int(p2.argmax())==0""",
            "A lower positive temperature sharpens this distribution. It is not a source of additional evidence and must not be confused with a calibrated probability of semantic truth.",
        ),
        ex(
            "Reject undefined cosine",
            "Implement cosine with finite and nonzero-norm checks; pass a zero anchor.",
            "ValueError for zero norm.",
            """def cosine(x,y):
    x,y=np.asarray(x),np.asarray(y); den=np.linalg.norm(x)*np.linalg.norm(y)
    if x.shape!=y.shape or not np.isfinite(den) or den==0: raise ValueError('finite nonzero vectors')
    return float(x@y/den)
try: cosine([0,0],[1,1])
except ValueError: pass
else: raise AssertionError('undefined cosine accepted')""",
            "Inventing zero similarity for a zero vector hides an undefined directional comparison. Rejecting it forces the caller to decide whether to skip, repair or represent missing information.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-026",
    """A custom layer separates construction of persistent parameters from repeated evaluation. Creating a new weight in every call would change the model whenever it sees another batch. Keras tracks weights created through add_weight, typically in build once the feature width is known. A residual connection adds an input to a transformed version of itself. Both operands must have compatible shapes; a projection is required if feature widths differ. This lesson uses a square linear residual with zero initial kernel, so its initial behavior is exactly the identity. The transparent starting function makes tracked-state and gradient tests easy to interpret.""",
    """build(input_shape) reads the trailing feature width and creates one square kernel. call(x) computes x+x@kernel. The same layer object reuses that kernel on later calls. trainable_variables supplies the variables the optimizer should update. A width mismatch should be reported rather than silently constructing a new parameter set. Batch length may change without changing feature width.""",
    [
        ("Tracked variable", "Persistent model state registered with the layer."),
        ("Residual", "An input added to a transformation with matching dimensions."),
        ("Build", "One-time creation of weights for a declared input shape."),
    ],
    [
        ex(
            "Create an identity residual",
            "Call a width2 residual with zero kernel on[[1,2],[3,4]].",
            "output equals input; one tracked kernel.",
            """layer=Residual(); x=tf.constant([[1.,2.],[3.,4.]]); out=layer(x)
np.testing.assert_array_equal(out.numpy(),x.numpy()); assert len(layer.trainable_variables)==1""",
            "The zero branch contributes nothing initially. This is a useful reference behavior but does not mean the branch has no gradient or will remain zero during training.",
        ),
        ex(
            "Reuse the state",
            "Call the layer on another batch of the same width and compare variable object identity.",
            "same variable object and variable count1.",
            """variable=layer.trainable_variables[0]; layer(tf.constant([[9.,8.]]))
assert layer.trainable_variables[0] is variable and len(layer.trainable_variables)==1""",
            "A new batch should change transient activations, not create a new model. Object identity complements a parameter count, since replacing one variable with another could preserve the count.",
        ),
        ex(
            "Assign a known transform",
            "Set the kernel to identity and inspect the residual output.",
            "output2*x.",
            """layer.kernel.assign(tf.eye(2)); np.testing.assert_array_equal(layer(x).numpy(),2*x.numpy())""",
            "The branch now reproduces the input, and the residual adds the original input again. The exact doubling exposes the addition instead of relying on random weights.",
        ),
        ex(
            "Reject an incompatible width",
            "Call the built width2 layer with a width3 input.",
            "ValueError naming feature width.",
            """try: layer(tf.ones((1,3)))
except ValueError: pass
else: raise AssertionError('width mismatch accepted')""",
            "A residual addition cannot repair a mismatched matrix product. Supporting a new feature width requires a separately designed projection or layer instance.",
        ),
        ex(
            "Check branch gradients",
            "Differentiate the sum of output entries with respect to the kernel.",
            "gradient matrix[[4,4],[6,6]].",
            """with tf.GradientTape() as tape: total=tf.reduce_sum(layer(x))
g=tape.gradient(total,layer.kernel)
np.testing.assert_array_equal(g.numpy(),[[4,4],[6,6]])""",
            "Each output column sees the same sum of input features under a sum objective. The identity skip path adds no kernel derivative, while the learned branch remains connected.",
        ),
        ex(
            "Count parameters by width",
            "Build a separate width3 layer and count its square kernel entries.",
            "9 parameters; width2 layer remains4.",
            """other=Residual(); other(tf.ones((1,3)))
assert other.count_params()==9 and layer.count_params()==4""",
            "Parameter growth is quadratic in this dense branch width. Batch size does not contribute to the count because the same kernel is shared across observations.",
        ),
    ],
    KERAS,
    "import numpy as np\nimport tensorflow as tf",
    """class Residual(tf.keras.layers.Layer):
    def build(self,input_shape):
        self.width=int(input_shape[-1])
        self.kernel=self.add_weight(name='kernel',shape=(self.width,self.width),initializer='zeros')
    def call(self,x):
        if x.shape[-1]!=self.width: raise ValueError('feature width mismatch')
        return x+x@self.kernel
""",
)
add(
    "tf-027",
    """Transfer learning reuses a representation for a related task. Freezing a base means its parameters should not receive optimizer updates while a new head learns from its outputs. The base can still perform computation; frozen does not mean bypassed. Normalization and dropout also have mode-dependent behavior, so a frozen base should be called with a deliberate training flag. Here a small deterministic two-feature transform stands in for the locally trained base from the classifier capstone. No pretrained weights are downloaded. A relabelled target tests whether the new head can change without altering the base. Unfreezing is a new phase with an explicit optimizer policy.""",
    """Set base.trainable=False before constructing the training variable list. Use base(x,training=False) to preserve its inference behavior. Train only head.trainable_variables. Snapshot all base weights before the update and compare arrays afterward. When unfreezing, use a new optimizer or explicitly build optimizer state for the newly trainable variables rather than assuming an old optimizer knows them.""",
    [
        ("Base", "The reused representation-producing part of a model."),
        ("Head", "A task-specific output mapping trained on that representation."),
        ("Freeze", "Exclude a parameter set from optimizer updates."),
    ],
    [
        ex(
            "Construct the local base",
            "Create a fixed two-feature identity Dense base and freeze it.",
            "base output equals input; no trainable base variables.",
            """base=tf.keras.layers.Dense(2,use_bias=False,kernel_initializer=tf.keras.initializers.Identity()); x=tf.constant([[1.,0.],[0.,1.],[1.,1.]])
base(x); base.trainable=False
np.testing.assert_array_equal(base(x).numpy(),x.numpy()); assert not base.trainable_variables""",
            "The identity fixture keeps transfer semantics visible. In the earlier capstone the base may be learned, but freezing should obey the same state contract.",
        ),
        ex(
            "Train a new head",
            "Attach a zero-initialized one-unit head; fit targets[1,2,3] for one SGD step.",
            "at least one head coefficient changes.",
            """head=tf.keras.layers.Dense(1,use_bias=False,kernel_initializer='zeros'); features=base(x,training=False); head(features); before=head.get_weights()[0].copy(); target=tf.constant([[1.],[2.],[3.]])
with tf.GradientTape() as tape: loss=tf.reduce_mean((head(features)-target)**2)
g=tape.gradient(loss,head.trainable_variables); tf.keras.optimizers.SGD(.1).apply_gradients(zip(g,head.trainable_variables))
assert not np.array_equal(before,head.get_weights()[0])""",
            "Zero initial outputs give nonzero residuals, so this fixture has an observable update. A trainable flag alone would not prove that an optimizer actually changed the head.",
        ),
        ex(
            "Prove base preservation",
            "Compare the base kernel with identity after head training.",
            "base weights remain byte-identical to identity.",
            """np.testing.assert_array_equal(base.get_weights()[0],np.eye(2,dtype='float32'))""",
            "A weight snapshot provides direct evidence. Checking only that base.trainable is false would miss an accidental explicit assignment outside the optimizer.",
        ),
        ex(
            "Compare predictions",
            "Evaluate the new head on all three local records and compare with initial zero predictions.",
            "all three predictions positive.",
            """pred=head(base(x,training=False)).numpy()
assert pred.shape==(3,1) and (pred>0).all()""",
            "The head has learned a direction toward the relabelled target. One update does not demonstrate good final fit, and the exercise does not present it as a completed training run.",
        ),
        ex(
            "Begin an explicit unfreeze phase",
            "Unfreeze the base and initialize a new SGD optimizer; differentiate a combined loss.",
            "both base and head now have connected gradients.",
            """base.trainable=True; variables=base.trainable_variables+head.trainable_variables
with tf.GradientTape() as tape: loss=tf.reduce_mean((head(base(x,training=False))-target)**2)
grads=tape.gradient(loss,variables)
assert len(grads)==2 and all(g is not None for g in grads)
tf.keras.optimizers.SGD(.01).apply_gradients(zip(grads,variables))""",
            "The lower rate is declared as part of a new phase, not inferred from a universal transfer rule. A new optimizer avoids silently reusing an incompatible slot-variable set.",
        ),
        ex(
            "Detect changed base state",
            "Compare the unfrozen base with its original identity after the explicit update.",
            "base is no longer identical.",
            """assert not np.array_equal(base.get_weights()[0],np.eye(2,dtype='float32'))""",
            "This control demonstrates that the preservation test is capable of detecting real changes. It helps distinguish successful freezing from a fixture whose gradients were zero everywhere.",
        ),
    ],
    KERAS,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-028",
    """A training checkpoint is more than a weight file. Adam keeps moving estimates of gradients and squared gradients, plus an update counter. Two runs with identical weights but different optimizer state can take different next steps. A restart test therefore compares an uninterrupted next update with a restored next update on the identical batch and dtype. Restoring in a new process tests reconstruction rather than accidental reuse of in-memory objects. Checkpoints are temporary in this lesson and are removed when the context exits. This validates a small deterministic CPU case; it does not promise bitwise reproducibility across hardware, versions or nondeterministic data pipelines.""",
    """Create the variable and optimizer, then build optimizer slots before restoring. tf.train.Checkpoint tracks both. save writes a numbered checkpoint prefix; restore(...).assert_consumed() detects missing tracked state. The child process constructs fresh objects and takes exactly one further update. Compare float32 weights with tolerance1e-6. A weights-only control resets optimizer history and should diverge on this fixture.""",
    [
        ("Optimizer state", "Accumulated information used to choose the next update."),
        ("Checkpoint", "Saved state sufficient for a declared continuation contract."),
        ("Restart parity", "Agreement between restored and uninterrupted next behavior."),
    ],
    [
        ex(
            "Create nontrivial optimizer state",
            "Take two Adam steps on(w-2)² fromw0 and inspect iterations.",
            "iteration count2 and positive weight.",
            """w,opt=make_state(); step(w,opt); step(w,opt)
assert int(opt.iterations)==2 and float(w)>0""",
            "A checkpoint made before any updates would not test restoration of nonzero moment estimates. Two steps create state that a fresh optimizer does not possess.",
        ),
        ex(
            "Save both state components",
            "Save a checkpoint containingw and Adam into a TemporaryDirectory.",
            "checkpoint index exists; no course source file is written.",
            """temporary=tempfile.TemporaryDirectory(); folder=Path(temporary.name)
checkpoint=tf.train.Checkpoint(weight=w,optimizer=opt); prefix=checkpoint.save(str(folder/'state'))
assert Path(prefix+'.index').is_file()""",
            "The returned prefix includes a save counter. Keep the exact prefix rather than guessing a filename. Temporary ownership confines the example to disposable local files.",
        ),
        ex(
            "Calculate the uninterrupted control",
            "Snapshot the saved weight and take one further step without restoring.",
            "iteration count3; weight changes.",
            """saved=float(w); step(w,opt); expected=float(w)
assert int(opt.iterations)==3 and expected!=saved""",
            "The control defines the next-step behavior before the restart comparison. It uses the same target, rate and optimizer configuration as the child process.",
        ),
        ex(
            "Restore in a fresh process",
            "Launch the existing interpreter with fresh variable/Adam objects, restore the saved prefix and take one step.",
            "child weight matches control within1e-6; child iterations3.",
            '''program=textwrap.dedent("""
import json,sys,tensorflow as tf
w=tf.Variable(0.,dtype=tf.float32); opt=tf.keras.optimizers.Adam(.1); opt.build([w])
c=tf.train.Checkpoint(weight=w,optimizer=opt); c.restore(sys.argv[1]).assert_consumed()
with tf.GradientTape() as tape: loss=(w-2)**2
opt.apply_gradients([(tape.gradient(loss,w),w)])
print(json.dumps({'weight':float(w),'iterations':int(opt.iterations)}))
""")
compile(program, "checkpoint-child", "exec")
result=subprocess.run([sys.executable,'-c',program,prefix],check=False,capture_output=True,text=True,timeout=60)
if result.returncode: raise RuntimeError('child process failed: '+result.stderr)
restored=json.loads(result.stdout.strip().splitlines()[-1])
np.testing.assert_allclose(restored['weight'],expected,atol=1e-6,rtol=0); assert restored['iterations']==3''',
            "A subprocess has no access to the parent live optimizer objects. Successful parity therefore tests reconstruction from disk. The strict restore check detects omitted variables rather than silently accepting partial state.",
        ),
        ex(
            "Expose a weights-only restart",
            "Set a fresh Adam variable to the saved weight without restoring optimizer moments, then take one step.",
            "next weight differs from the full-state control by more than1e-6.",
            """weights_only,fresh=make_state(); weights_only.assign(saved); step(weights_only,fresh)
assert abs(float(weights_only)-expected)>1e-6 and int(fresh.iterations)==1""",
            "The reset update counter and moments change Adam update even though the initial weight matches. This is why a model prediction parity does not establish training-resumption parity.",
        ),
        ex(
            "Verify cleanup",
            "Remove the owned temporary checkpoint directory and verify it no longer exists.",
            "temporary checkpoint directory absent.",
            """temporary.cleanup(); assert not folder.exists()""",
            "Cleanup affects only the directory created by this lesson. A real learner checkpoint should be stored deliberately under learner-owned artifacts and should never be removed by a course update.",
        ),
    ],
    ("TensorFlow Checkpoint", "https://www.tensorflow.org/api_docs/python/tf/train/Checkpoint"),
    "import numpy as np\nimport tensorflow as tf\nimport tempfile,json,subprocess,sys,textwrap\nfrom pathlib import Path",
    """def make_state():
    w=tf.Variable(0.,dtype=tf.float32); opt=tf.keras.optimizers.Adam(.1); opt.build([w]); return w,opt
def step(w,opt):
    with tf.GradientTape() as tape: loss=(w-2)**2
    opt.apply_gradients([(tape.gradient(loss,w),w)])
""",
)
add(
    "tf-029",
    """Floating-point arithmetic has a finite representable range. The probabilities implied by logits[1000,999] are well defined, but exponentiating those scores directly overflows ordinary floating-point types. Subtracting the maximum leaves the softmax unchanged because a common multiplicative factor cancels between numerator and denominator. A stable cross entropy works with shifted logits or a log-sum-exp expression, avoiding an unnecessary probability round trip. Numeric precision is a separate concern from objective correctness: a stable implementation can still optimize the wrong labels or denominator. Mixed precision may improve performance on some hardware, but this CPU fixture makes no speed claim.""",
    """Use tf.nn.sparse_softmax_cross_entropy_with_logits for the combined stable calculation. In NumPy, logaddexp(0,-1) gives the positive-first-class loss. finite checks should include gradients as well as forward outputs. float16 overflows at much smaller exponent arguments than float64. Compare using absolute tolerances appropriate to the dtype instead of exact equality for transcendental functions.""",
    [
        ("Overflow", "A finite mathematical result exceeds the numeric representation."),
        ("Log-sum-exp", "A stable way to calculate the logarithm of a sum of exponentials."),
        ("Precision", "The resolution of representable values, distinct from range."),
    ],
    [
        ex(
            "Expose naive overflow",
            "Exponentiate NumPy logits[1000,999] directly under an explicit error-state context.",
            "both exponentials are infinite.",
            """z=np.array([1000.,999.])
with np.errstate(over='ignore'): naive=np.exp(z)
assert np.isinf(naive).all()""",
            "The warning is intentionally scoped to a counterexample. Silencing all numerical warnings in a training program would hide unrelated failures.",
        ),
        ex(
            "Calculate stable loss",
            "Use a logits-aware TensorFlow loss for target0.",
            "losslog(1+exp(-1)) within1e-6.",
            """loss=tf.nn.sparse_softmax_cross_entropy_with_logits(labels=[0],logits=tf.constant([[1000.,999.]]))
np.testing.assert_allclose(loss.numpy(),[np.logaddexp(0,-1)],atol=1e-6,rtol=0)""",
            "The meaningful quantity is the difference between scores, not their shared offset. The stable form keeps that difference available without constructing enormous exponentials.",
        ),
        ex(
            "Check shift invariance",
            "Compare softmax[1000,999] with softmax[0,-1].",
            "probabilities agree within1e-6.",
            """np.testing.assert_allclose(tf.nn.softmax(z).numpy(),tf.nn.softmax([0.,-1.]).numpy(),atol=1e-6,rtol=0)""",
            "A common score shift cancels from the normalized distribution. This metamorphic property can catch an implementation that normalizes the wrong axis or clips scores inconsistently.",
        ),
        ex(
            "Inspect gradients",
            "Differentiate the stable target0 loss with respect to both logits.",
            "finite gradients summing approximately0.",
            """v=tf.Variable([[1000.,999.]])
with tf.GradientTape() as tape: objective=tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(labels=[0],logits=v))
g=tape.gradient(objective,v).numpy()
assert np.isfinite(g).all(); np.testing.assert_allclose(g.sum(),0,atol=1e-6,rtol=0)""",
            "The derivative of cross entropy is probability minus one-hot target. Its components sum to zero because the probabilities and target each sum to one.",
        ),
        ex(
            "Separate precision policies",
            "Compare float16 and float64 exponentiation of20.",
            "float16 overflows; float64 remains finite.",
            """with np.errstate(over='ignore'): low=np.exp(np.float16(20))
high=np.exp(np.float64(20))
assert np.isinf(low) and np.isfinite(high)""",
            "A lower-precision type changes range as well as resolution. Hardware support and loss scaling require separate experiments; a dtype cast alone is not evidence of safe mixed-precision training.",
        ),
        ex(
            "Validate input finiteness",
            "Reject a NaN logit before using a maximum-subtracted softmax helper.",
            "ValueError for NaN; finite input returns unit mass.",
            """def stable(values):
    values=np.asarray(values,dtype=float)
    if values.ndim!=1 or not len(values) or not np.isfinite(values).all(): raise ValueError('finite vector')
    mass=np.exp(values-values.max()); return mass/mass.sum()
try: stable([0,np.nan])
except ValueError: pass
else: raise AssertionError('NaN accepted')
np.testing.assert_allclose(stable(z).sum(),1,atol=1e-12,rtol=0)""",
            "Maximum subtraction prevents a particular overflow mechanism. It does not turn NaN or infinity into a valid probability distribution, so validation remains necessary.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-030",
    """A distributed or accumulated gradient must represent the intended global objective. If shards have different numbers of examples, averaging shard means equally weights shards rather than observations. A one-example shard with mean gradient2 and a three-example shard with mean6 combine to5 under an example mean, not4. Gradient accumulation has the same issue when microbatches differ in size. Accumulate gradient sums and counts, divide once, then apply one optimizer update. Applying an update after each microbatch is a different trajectory because later gradients use changed parameters. This lesson simulates all shards on one CPU and does not claim a distributed runtime was exercised.""",
    """The identity global_mean=sum(count*local_mean)/sum(count) is independent of a communication library. tf.reduce_sum exposes numerators. Hold weights fixed while accumulating gradients, then assign once. A regularization term needs a deliberate global scaling convention so it is not accidentally multiplied by the number of shards. The examples distinguish mathematical reduction from runtime placement.""",
    [
        ("Shard", "A subset of observations processed as one partition."),
        ("Gradient accumulation", "Combining gradients before one optimizer update."),
        ("Global denominator", "The total participating example count across partitions."),
    ],
    [
        ex(
            "Weight shard means",
            "Combine means2,6 with counts1,3 and compare equal shard averaging.",
            "global5; naive4.",
            """means=np.array([2.,6.]); counts=np.array([1,3])
assert np.average(means,weights=counts)==5 and means.mean()==4""",
            "Multiplying each local mean by its count restores the gradient numerator. The final division then gives each example equal weight.",
        ),
        ex(
            "Recover a full-batch mean",
            "Partition gradients[2,4,6,8] into sizes 1 and3 and reconstruct their mean.",
            "both full and reconstructed means5.",
            """g=np.array([2.,4.,6.,8.]); parts=[g[:1],g[1:]]
recombined=sum(p.sum() for p in parts)/sum(len(p) for p in parts)
assert recombined==g.mean()==5""",
            "The explicit per-example values are an independent oracle for the shard calculation. A test that compares two formulas using the same wrong weights would miss the error.",
        ),
        ex(
            "Accumulate squared-loss gradients",
            "At w = 0 use x = [1, 2, 3, 4],y = 2x; compare full-batch gradient with sum-then-divide microbatches.",
            "gradient-30 for both.",
            """x=tf.constant([1.,2.,3.,4.]); y=2*x; w=tf.Variable(0.)
with tf.GradientTape() as tape: full=tf.reduce_mean((w*x-y)**2)
full_g=tape.gradient(full,w); total=0.
for start,end in [(0,1),(1,4)]:
    with tf.GradientTape() as tape: summed=tf.reduce_sum((w*x[start:end]-y[start:end])**2)
    total+=float(tape.gradient(summed,w))
assert float(full_g)==total/4==-30""",
            "The variable remains fixed while all microbatch gradients are calculated. This is the condition under which accumulation matches the full-batch gradient.",
        ),
        ex(
            "Apply exactly one update",
            "Use rate 0.01 with accumulated global gradient-30.",
            "updated weight.3.",
            """w.assign_sub(.01*(total/4)); np.testing.assert_allclose(float(w),.3,atol=1e-6,rtol=0)""",
            "The update counter should increment once for this effective batch. Incrementing a learning-rate schedule once per microbatch changes the optimizer policy even if gradients are combined correctly.",
        ),
        ex(
            "Expose per-batch updates",
            "Update separately for the two microbatches and compare the final weight with.3.",
            "endpoint differs from.3.",
            """other=tf.Variable(0.)
for start,end in [(0,1),(1,4)]:
    with tf.GradientTape() as tape: loss=tf.reduce_mean((other*x[start:end]-y[start:end])**2)
    other.assign_sub(.01*tape.gradient(loss,other))
assert abs(float(other)-.3)>1e-6""",
            "The second gradient uses the weight changed by the first update. This is ordinary minibatch training, not a numerical implementation of one full-batch step.",
        ),
        ex(
            "Handle an empty shard",
            "Combine an empty shard and the four real gradients using sums and counts; reject a globally empty batch.",
            "empty shard contributes0; total remains5.",
            """parts=[np.array([],dtype=float),g]
count=sum(len(p) for p in parts)
assert count==4 and sum(p.sum() for p in parts)/count==5
assert sum(len(p) for p in [np.array([])])==0""",
            "A local empty shard need not invalidate a nonempty global batch, but mean(empty) is undefined. Carrying sums and counts avoids producing a NaN local mean.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-031",
    """tf.function traces Python code into a graph specialized for input signatures. Tracing is a setup activity; graph execution is the repeated tensor computation. Repeated calls with compatible shapes and dtypes can reuse a trace, while a new dtype often requires another graph. A Python print inside the function runs during tracing, not once per tensor execution. Benchmarking the first call together with later calls mixes compilation/setup costs with steady-state work. The tiny function here is useful for checking equivalence and trace behavior, not for claiming a universal speedup. A graph can be slower for a small workload or faster after sufficient reuse.""",
    """Decorate a pure tensor function with tf.function. experimental_get_tracing_count reports how many concrete traces were constructed. Use tf.constant with explicit dtype and compare eager and graph outputs. Materialize .numpy() before ending a timing interval when needed to ensure the computation completed. Avoid using Python lists with changing values as an accidental signature source.""",
    [
        ("Trace", "Construction of a graph from Python execution and input signatures."),
        ("Signature", "Input structure, dtype and shape constraints for graph reuse."),
        ("Warmup", "Initial calls excluded from steady-state measurement."),
    ],
    [
        ex(
            "Check eager arithmetic",
            "Evaluate x*x+1 at float32[1,2].",
            "output[2,5].",
            """x=tf.constant([1.,2.],tf.float32); eager=x*x+1
np.testing.assert_array_equal(eager.numpy(),[2,5])""",
            "The arithmetic provides a simple independent oracle. Correctness must be established before timing a graph implementation.",
        ),
        ex(
            "Compile and compare",
            "Wrap the same expression in tf.function and compare output.",
            "graph output equals eager output.",
            """@tf.function
def f(value): return value*value+1
np.testing.assert_array_equal(f(x).numpy(),eager.numpy()); first=f.experimental_get_tracing_count()
assert first>=1""",
            "The first call includes graph construction. An output match establishes this fixture computation, not performance or general input compatibility.",
        ),
        ex(
            "Reuse an equal signature",
            "Call with float32[3,4] and inspect trace count.",
            "output[10,17]; trace count unchanged.",
            """np.testing.assert_array_equal(f(tf.constant([3.,4.],tf.float32)).numpy(),[10,17])
assert f.experimental_get_tracing_count()==first""",
            "Values change while shape and dtype remain the same. Reusing a trace demonstrates the intended separation between graph structure and tensor values.",
        ),
        ex(
            "Change dtype deliberately",
            "Call with float64[1,2] and inspect trace count and output dtype.",
            "float64 result[2,5]; at least one new trace.",
            """out=f(tf.constant([1.,2.],tf.float64))
assert out.dtype==tf.float64 and f.experimental_get_tracing_count()>first
np.testing.assert_array_equal(out.numpy(),[2,5])""",
            "Dtype changes can affect kernels and arithmetic. Reporting them separately prevents an apparent performance regression from being attributed to values alone.",
        ),
        ex(
            "Measure only warmed calls",
            "After warmup, time10 repeated float32 calls and materialize outputs.",
            "10 finite outputs and nonnegative elapsed time.",
            """import time
f(x).numpy(); start=time.perf_counter()
for _ in range(10): result=f(x).numpy()
elapsed=time.perf_counter()-start
assert elapsed>=0 and np.isfinite(result).all()""",
            "The measured interval excludes the initial trace. This small sample is a timing observation for the current environment, not evidence that graph execution always wins.",
        ),
        ex(
            "Separate shape contracts",
            "Create a function with a variable-length float32 vector signature; call lengths2 and3.",
            "one trace reused; outputs have lengths2 and3.",
            """@tf.function(input_signature=[tf.TensorSpec([None],tf.float32)])
def g(value): return value*value+1
g(tf.constant([1.,2.])); count=g.experimental_get_tracing_count()
assert tuple(g(tf.constant([1.,2.,3.])).shape)==(3,) and g.experimental_get_tracing_count()==count""",
            "An explicit signature can permit varying dimensions without retracing. It is also a contract that rejects incompatible rank or dtype instead of silently accepting every input.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
)
add(
    "tf-032",
    """Saving has two distinct purposes: preserving a trainable Keras model and exporting an inference interface. The .keras format preserves a Keras model configuration and state; model.export creates an inference artifact that can be loaded through SavedModel. Keras3 does not use model.save(directory) as the export workflow. Prediction parity must be checked after reconstruction, ideally in a fresh process. Matching predictions says nothing about whether optimizer state can resume the same next update, which is the separate checkpoint lesson. This fixture has one fixed weight and a known signature, so failures can be attributed to persistence and interface behavior rather than training randomness.""",
    """Save the built model to a path ending.keras. Load it with tf.keras.models.load_model. Export to a different owned directory and load it with tf.saved_model.load; call its serve endpoint. TemporaryDirectory owns both outputs. The child process accepts only the two local artifact paths created by the parent and prints predictions as JSON. Compare using float32 tolerance1e-6.""",
    [
        ("Serialization", "Encoding model configuration and state into a recoverable artifact."),
        ("Export", "Publishing a fixed inference interface and its state."),
        ("Parity", "Agreement of outputs under declared inputs and tolerance."),
    ],
    [
        ex(
            "Create a fixed inference model",
            "Set a bias-free Dense weight to2 and predict on 1,3.",
            "predictions2,6.",
            """model=tf.keras.Sequential([tf.keras.Input(shape=(1,)),tf.keras.layers.Dense(1,use_bias=False,kernel_initializer=tf.keras.initializers.Constant(2.))])
x=np.array([[1.],[3.]],dtype='float32'); expected=model(x).numpy()
np.testing.assert_array_equal(expected,[[2],[6]])""",
            "A known fixed weight avoids making serialization success depend on a stochastic training result. The input shape and dtype are part of the inference contract.",
        ),
        ex(
            "Round-trip .keras",
            "Save and reload the model in a temporary directory.",
            "reloaded predictions match within1e-6.",
            """temporary=tempfile.TemporaryDirectory(); folder=Path(temporary.name); keras_path=folder/'model.keras'; model.save(keras_path)
loaded=tf.keras.models.load_model(keras_path)
np.testing.assert_allclose(loaded(x).numpy(),expected,atol=1e-6,rtol=0)""",
            "Reconstruction must use the saved artifact rather than another reference to the original model object. File existence alone does not establish that deserialization works.",
        ),
        ex(
            "Export an inference endpoint",
            "Call model.export into a different temporary subdirectory and load SavedModel.",
            "serve returns the same predictions.",
            """export_path=folder/'inference'; model.export(export_path)
exported=tf.saved_model.load(str(export_path))
np.testing.assert_allclose(exported.serve(tf.constant(x)).numpy(),expected,atol=1e-6,rtol=0)""",
            "The export exposes inference behavior. Treating it as interchangeable with a resumable training object would overstate what the endpoint contains.",
        ),
        ex(
            "Check both in a fresh process",
            "Load the .keras model and exported endpoint in a child interpreter and compare their outputs.",
            "both child outputs[[2],[6]].",
            '''program=textwrap.dedent("""
import json,sys,tensorflow as tf
x=tf.constant([[1.],[3.]])
a=tf.keras.models.load_model(sys.argv[1])(x).numpy().tolist()
exported=tf.saved_model.load(sys.argv[2])
b=exported.serve(x).numpy().tolist()
print(json.dumps([a,b]))
""")
compile(program, "checkpoint-child", "exec")
result=subprocess.run([sys.executable,'-c',program,str(keras_path),str(export_path)],capture_output=True,text=True,check=False,timeout=60)
if result.returncode: raise RuntimeError('child process failed: '+result.stderr)
a,b=json.loads(result.stdout.strip().splitlines()[-1])
np.testing.assert_allclose(a,expected,atol=1e-6,rtol=0); np.testing.assert_allclose(b,expected,atol=1e-6,rtol=0)''',
            "The child cannot reuse live model state from the parent. Keep the object returned by tf.saved_model.load in a named variable while calling serve: the exported function references resource variables owned by that object. Chaining load(...).serve(...) can let the owner disappear before its variables are used. Prediction parity therefore depends on both reconstructed state and correct object lifetime, not only a readable file.",
        ),
        ex(
            "Check a new batch length",
            "Use three valid rows instead of two with the restored model.",
            "output shape(3,1), predictions0,4,8.",
            """new=loaded(np.array([[0.],[2.],[4.]],dtype='float32')).numpy()
assert new.shape==(3,1); np.testing.assert_array_equal(new[:,0],[0,4,8])""",
            "The feature width stays fixed while batch length varies. This confirms the intended leading-axis flexibility, not support for arbitrary feature dimensions.",
        ),
        ex(
            "Remove only owned artifacts",
            "Clean the temporary directory and check both artifacts are absent.",
            "temporary directory absent.",
            """temporary.cleanup(); assert not folder.exists()""",
            "The example has no persistent model output by design. A real release should choose an explicit learner-owned artifact destination and retain a rollback version instead.",
        ),
    ],
    ("Keras saving and export", "https://keras.io/guides/serialization_and_saving/"),
    "import numpy as np\nimport tensorflow as tf\nimport tempfile,json,subprocess,sys,textwrap\nfrom pathlib import Path",
)
add(
    "tf-033",
    """Inference is a function with a data contract, not just a call to model.predict. The model expects a nonempty batch of two finite float32 features per record and accepts at most four records. Inputs outside that boundary should receive named failures rather than silent coercion. Batching should preserve record identity: predicting one record alone or alongside others should give the same result for this stateless model. This local contract does not start a server or claim security isolation. It establishes a small, reviewable boundary that an eventual service would need to enforce consistently.""",
    """np.asarray inspects the incoming data without automatically changing its dtype. Check rank, feature width, batch limit and finiteness before converting to a tensor. A fixed coefficient vector[2,-1] gives an independent expected output. Returning a new array prevents a caller from mutating stored input through a shared view. Validation order should make errors predictable enough to diagnose.""",
    [
        ("Inference contract", "Accepted inputs and guaranteed output structure for prediction."),
        ("Batch limit", "Maximum number of observations accepted in one call."),
        ("Finite value", "A numeric value that is neither NaN nor infinity."),
    ],
    [
        ex(
            "Predict a valid batch",
            "Predict for float32 rows[1,2],[3,4].",
            "outputs 0,2 with shape(2,).",
            """x=np.array([[1,2],[3,4]],dtype='float32'); result=predict(x)
np.testing.assert_array_equal(result,[0,2]); assert result.shape==(2,)""",
            "The reference coefficient vector makes output arithmetic transparent. Shape validation ensures the result is one scalar per input record.",
        ),
        ex(
            "Compare batch independence",
            "Predict each row independently and compare concatenated outputs with the batch result.",
            "exact equality for this fixed linear fixture.",
            """single=np.concatenate([predict(x[i:i+1]) for i in range(2)])
np.testing.assert_array_equal(single,result)""",
            "A stateless affine model should not depend on neighboring records. A training-mode normalization layer could violate this behavior, so the test is valuable when the implementation grows.",
        ),
        ex(
            "Reject empty and oversized batches",
            "Pass shapes(0,2) and(5,2).",
            "ValueError with batch in the message.",
            """for bad in [np.empty((0,2),dtype='float32'),np.zeros((5,2),dtype='float32')]:
    try: predict(bad)
    except ValueError as error: assert 'batch' in str(error)
    else: raise AssertionError('bad batch accepted')""",
            "An empty batch provides no predictions, and an oversized batch violates the declared resource budget. Both failures occur before the model computation.",
        ),
        ex(
            "Reject wrong feature structure",
            "Pass a vector[1,2] and a matrix with three columns.",
            "ValueError with shape in the message.",
            """for bad in [np.array([1,2],dtype='float32'),np.zeros((2,3),dtype='float32')]:
    try: predict(bad)
    except ValueError as error: assert 'shape' in str(error)
    else: raise AssertionError('bad shape accepted')""",
            "A single record still needs a batch axis. Guessing whether a vector represents one record or many one-feature records can silently change the meaning of data.",
        ),
        ex(
            "Reject nonfinite values and wrong dtype",
            "Pass a NaN row and an int64 row under the explicit float32 policy.",
            "ValueError for nonfinite; TypeError for dtype.",
            """try: predict(np.array([[np.nan,1]],dtype='float32'))
except ValueError: pass
else: raise AssertionError('NaN accepted')
try: predict(np.array([[1,2]],dtype='int64'))
except TypeError: pass
else: raise AssertionError('dtype silently coerced')""",
            "A strict dtype boundary makes precision changes visible. A different API could deliberately cast, but it would need to document and test that policy rather than do it implicitly.",
        ),
        ex(
            "Preserve the input",
            "Snapshot a valid batch, predict and mutate the returned result; compare the original input.",
            "input remains byte-identical.",
            """before=x.copy(); answer=predict(x); answer[0]=999
np.testing.assert_array_equal(x,before)""",
            "Ownership is part of the contract. An output view into caller or model state can turn a harmless downstream edit into a hidden data mutation.",
        ),
    ],
    TF,
    "import numpy as np\nimport tensorflow as tf",
    """def predict(values):
    x=np.asarray(values)
    if x.dtype!=np.float32: raise TypeError('float32 dtype required')
    if x.ndim!=2 or x.shape[1]!=2: raise ValueError('shape must be (batch,2)')
    if not 1<=len(x)<=4: raise ValueError('batch must contain 1..4 records')
    if not np.isfinite(x).all(): raise ValueError('finite values required')
    return (tf.constant(x)@tf.constant([[2.],[-1.]])).numpy()[:,0].copy()
""",
)
add(
    "tf-034",
    """A robustness report records which conditions were actually tested and which failures occurred. It does not convert a finite list of successful checks into a guarantee. Group metrics need counts, because zero errors among one rare-group observation is very weak evidence. Perturbations should preserve the intended label when interpreted as robustness tests; otherwise they define a new task. Duplicate records can make a score look more certain without adding independent evidence. Privacy claims require their own mechanisms and analysis. The absence of names in a synthetic fixture, or a successful perturbation test, is not proof of differential privacy or production safety.""",
    """Represent each result with a stable record ID, group, expected label and prediction. Aggregate integer errors and counts before calculating rates. Compare the set of unique IDs with row count to detect exact repetitions. Keep a model-card dictionary with intended use, evaluated units and untested conditions. A model card summarizes evidence; it is not itself a validation method.""",
    [
        ("Robustness", "Behavior under specified changes to inputs or conditions."),
        ("Subgroup", "A declared subset whose performance is evaluated separately."),
        ("Model card", "A structured account of intended use, evidence and limitations."),
    ],
    [
        ex(
            "Count errors by group",
            "Use groupsA,A,B with predictions1,0,0 and truth1,1,0.",
            "A1/2 errors; B0/1.",
            """rows=[('a','A',1,1),('b','A',1,0),('c','B',0,0)]
report={g:(sum(t!=p for i,k,t,p in rows if k==g),sum(k==g for i,k,t,p in rows)) for g in ['A','B']}
assert report=={'A':(1,2),'B':(0,1)}""",
            "Both numerator and denominator are visible. Reporting only rates would conceal the fact that groupB has a single observation.",
        ),
        ex(
            "Expose duplicate confidence",
            "Repeat the groupB row five times and compare row count with unique IDs.",
            "8 rows but only3 unique IDs.",
            """repeated=rows+[rows[-1]]*5
assert len(repeated)==8 and len({r[0] for r in repeated})==3""",
            "Duplicating a correct observation can improve a row-weighted score without testing a new case. Identity-aware evaluation prevents artificial increases in apparent evidence.",
        ),
        ex(
            "Evaluate fixed perturbations",
            "Use f(x)=x>=0 with base1 and perturbations-.1,-.9,-1.1.",
            "first two retain class1; final perturbation changes to0.",
            """base=1.; shifts=[-.1,-.9,-1.1]; pred=[int(base+s>=0) for s in shifts]
assert pred==[1,1,0]""",
            "The last perturbation crosses the defined decision boundary. Whether it is a robustness failure depends on whether the label is supposed to remain unchanged under that shift.",
        ),
        ex(
            "Keep severities separate",
            "Record one severe failure and nine minor passes; count severe failures independently of total pass rate.",
            "90percent passes and 1 severe failure.",
            """severity=['minor']*9+['severe']; passed=[True]*9+[False]
assert sum(passed)/len(passed)==.9
assert sum(s=='severe' and not p for s,p in zip(severity,passed))==1""",
            "A high average can hide a rare unacceptable outcome. The decision rule should state whether a severe failure blocks release regardless of the aggregate rate.",
        ),
        ex(
            "Write bounded claims",
            "Create a model card naming the three unique units and untested conditions.",
            "card includes count3 and an untested future-population condition.",
            """card={'evaluation_units':3,'intended_use':'synthetic teaching','untested':['future population','private training data'],'privacy_guarantee':False}
assert card['evaluation_units']==3 and 'future population' in card['untested'] and card['privacy_guarantee'] is False""",
            "Explicit limitations constrain how the results may be used. Declaring a missing guarantee is more informative than an unqualified claim that the model was checked.",
        ),
        ex(
            "Reject an empty group rate",
            "Compute a rate only when its group has observations.",
            "empty group producesNone, not0.",
            """def rate(errors,count): return None if count==0 else errors/count
assert rate(0,0) is None and rate(0,1)==0""",
            "No observations and zero observed failures are different states. Mapping both to zero would make an untested group look perfectly reliable.",
        ),
    ],
    ("Model Cards for Model Reporting", "https://arxiv.org/abs/1810.03993"),
)
add(
    "tf-035",
    """A model comparison should preserve pairing: both models predict the same held-out identities. Subtract each record loss before summarizing so shared difficulty remains represented. Resampling the pairs approximates variability under a stated sampling assumption; resampling each model separately discards their dependence. A fixed seed makes the teaching calculation reproducible, but it does not make a small sample representative. If related observations share a group, resample groups rather than pretending every row is independent. Model selection belongs on validation data. Opening the final test and then changing configuration consumes it as a selection source, even if the resulting number is still called test error.""",
    """Align dictionaries by stable IDs and verify equal key sets. Compute per-ID squared errors for each model and their difference. np.random.default_rng provides a local seeded generator. Sample integer indices with replacement and apply the same indices to the paired difference vector. A percentile interval describes this resampling calculation under its assumptions, not a universal confidence guarantee.""",
    [
        ("Paired difference", "LossA minus lossB for the same observation."),
        ("Bootstrap", "Resampling observed units with replacement."),
        ("Selection leakage", "Using assessment outcomes to choose the evaluated configuration."),
    ],
    [
        ex(
            "Align by identity",
            "Use trutha0,b1,c2 and two prediction dictionaries with different insertion order.",
            "paired differences[-1,0,-1].",
            """truth={'a':0.,'b':1.,'c':2.}; a={'a':0.,'b':2.,'c':2.}; b={'c':3.,'a':1.,'b':2.}
ids=sorted(truth); diff=np.array([(a[i]-truth[i])**2-(b[i]-truth[i])**2 for i in ids])
np.testing.assert_array_equal(diff,[-1,0,-1])""",
            "Dictionary insertion order is not an alignment contract. Joining by IDs keeps each difference attached to the same target record.",
        ),
        ex(
            "Calculate the mean difference",
            "Average the three paired loss differences and interpret its sign.",
            "mean-2/3; modelA has lower MSE on this fixture.",
            """np.testing.assert_allclose(diff.mean(),-2/3,atol=1e-12,rtol=0)""",
            "The sign depends on the declared subtraction order. A negative A-minus-B loss difference favors A for this metric and sample only.",
        ),
        ex(
            "Resample paired units",
            "Draw1000 bootstrap index rows with seed7 and average each selected difference vector.",
            "1000 finite estimates within[-1,0].",
            """rng=np.random.default_rng(7); indices=rng.integers(0,len(diff),size=(1000,len(diff))); estimates=diff[indices].mean(1)
assert estimates.shape==(1000,) and np.isfinite(estimates).all() and estimates.min()>=-1 and estimates.max()<=0""",
            "Sampling one difference vector automatically preserves pairing. The attainable bounds are known from the fixture, so they independently check the implementation.",
        ),
        ex(
            "Reproduce the resampling",
            "Repeat with a fresh seed7 generator and compare the entire estimate vector.",
            "exact same estimates.",
            """again=np.random.default_rng(7).integers(0,3,size=(1000,3))
np.testing.assert_array_equal(diff[again].mean(1),estimates)""",
            "The seed makes local execution repeatable. It does not address biased sampling, dependent observations or a metric chosen after seeing the results.",
        ),
        ex(
            "Refuse mismatched IDs",
            "Remove predictionc from one model and check alignment before computing differences.",
            "key-set mismatch detected.",
            """missing={k:v for k,v in b.items() if k!='c'}
assert set(missing)!=set(truth)""",
            "An inner join would silently evaluate only the overlapping records. Missing predictions should be accounted for under an explicit failure policy rather than dropped.",
        ),
        ex(
            "Keep selection and final evaluation separate",
            "Record configuration choice on validation and a single frozen-test assessment; reject a later test-driven retune.",
            "selection partition validation; final-test tuning prohibited.",
            """ledger=[{'action':'choose','partition':'validation'},{'action':'assess','partition':'test'}]
assert all(row['partition']=='validation' for row in ledger if row['action']=='choose')
bad={'action':'choose','partition':'test'}; assert bad['partition']!='validation' """,
            "The audit concerns information use, not filenames. Once the final test influences a new choice, a new untouched assessment is needed for a fresh final claim.",
        ),
    ],
    ("NumPy Generator", "https://numpy.org/doc/stable/reference/random/generator.html"),
)
add(
    "tf-036",
    """A model release is a decision backed by a bundle of evidence. It needs a prediction contract, frozen preprocessing, the identity of fitting and assessment records, and a recoverable artifact. A hash can detect accidental changes to bytes, but cannot establish that those bytes contain a good model or honest data split. A release gate combines independent checks and blocks when a required one fails. The tiny linear model is intentionally transparent so the lesson can concentrate on packaging and decision logic. A no-go is a valid capstone result. Production rollout, privacy guarantees and broad reliability remain outside this offline teaching exercise.""",
    """Serialize metadata with sorted keys and fixed separators before hashing. Keep schema, weights and split IDs in separate fields so a reviewer can identify what changed. Run prediction parity on fixed probes and reject a schema mismatch before inference. The checkpoint parity proof from tf-028 and export proof from tf-032 are distinct evidence items; neither should be replaced by a boolean invented without execution.""",
    [
        ("Release gate", "A conjunction of required checks that permits or blocks a decision."),
        ("Lineage", "The identities of data, preprocessing and artifacts used."),
        ("Rollback artifact", "A retained previous version that can restore a known state."),
    ],
    [
        ex(
            "Build a literal model bundle",
            "Create a float32 two-feature model with coefficient[2,-1] and schema width2.",
            "probe[3,4] predicts2.",
            """weights=np.array([[2.],[-1.]],dtype='float32'); schema={'features':['a','b'],'dtype':'float32','width':2}
model=tf.keras.Sequential([tf.keras.Input(shape=(2,)),tf.keras.layers.Dense(1,use_bias=False)]); model.layers[0].set_weights([weights])
np.testing.assert_array_equal(model(np.array([[3,4]],dtype='float32')).numpy(),[[2]])""",
            "A known probe connects the serialized feature order to numerical behavior. Swapping features would change the prediction even if the model file remained readable.",
        ),
        ex(
            "Freeze and hash a split manifest",
            "Hash train IDs[a,b] and test IDs[c,d] using canonical JSON.",
            "disjoint IDs and a64-character SHA256.",
            """import hashlib,json
split={'train':['a','b'],'test':['c','d']}; payload=json.dumps(split,sort_keys=True,separators=(',',':')).encode(); digest=hashlib.sha256(payload).hexdigest()
assert not set(split['train'])&set(split['test']) and len(digest)==64""",
            "The canonical representation avoids a digest change caused only by dictionary key order. The explicit intersection check verifies a property that a hash alone cannot establish.",
        ),
        ex(
            "Catch tampered lineage",
            "Change one test ID and compare the resulting digest.",
            "digest differs.",
            """changed={'train':['a','b'],'test':['c','e']}; other=hashlib.sha256(json.dumps(changed,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert other!=digest""",
            "This control proves the check is sensitive to the field that matters. It does not authenticate an author or replace a trusted distribution mechanism.",
        ),
        ex(
            "Block incompatible schemas",
            "Compare an incoming three-feature schema with the frozen two-feature schema before prediction.",
            "schema gate isFalse.",
            """incoming={'features':['a','b','c'],'dtype':'float32','width':3}
assert incoming!=schema""",
            "A model might accept a tensor through unintended broadcasting or fail later with a low-level error. A named schema gate explains the problem before executing the wrong interpretation.",
        ),
        ex(
            "Make the decision fail closed",
            "Evaluate required gates with an unexecuted restart proof represented asNone, then with an actual failed schema gate.",
            "both decisionsno-go.",
            """gates={'prediction':True,'split':True,'restart':None,'schema':True}
assert not all(value is True for value in gates.values())
gates.update(restart=True,schema=False); assert not all(value is True for value in gates.values())""",
            "Unknown evidence is not a pass. The lesson deliberately avoids fabricating a restart receipt and shows that even three passing checks cannot compensate for a required failed fourth check.",
        ),
        ex(
            "Retain a rollback decision",
            "Construct a release record with previous artifact ID, holdout count and limits; keep no-go when any gate fails.",
            "decisionno-go and previous artifactv1 retained.",
            """record={'candidate':'v2','previous':'v1','holdout_count':2,'decision':'go' if all(v is True for v in gates.values()) else 'no-go','limits':['synthetic fixture only']}
assert record['decision']=='no-go' and record['previous']=='v1' and record['holdout_count']==2""",
            "A release record should explain what can be restored and why a candidate was blocked. A failed capstone check is useful evidence, not an invitation to bypass the gate.",
        ),
    ],
    (
        "TensorFlow model persistence",
        "https://www.tensorflow.org/guide/keras/serialization_and_saving",
    ),
    "import numpy as np\nimport tensorflow as tf",
)

from tf031_depth import deepen as deepen_tracing

deepen_tracing(SPECS["tf-031"])


# Prose-only review layer; executable exercise contracts remain in this module.
from depth_reviews_tf import DEPTH_NOTES, DIAGNOSIS_NOTES

for identity, notes in DEPTH_NOTES.items():
    SPECS[identity]["mechanism_notes"] = notes
for identity, notes in DIAGNOSIS_NOTES.items():
    SPECS[identity]["diagnosis"] = notes
