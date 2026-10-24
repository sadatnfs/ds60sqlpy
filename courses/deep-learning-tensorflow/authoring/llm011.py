from render import add, ex, SPECS

HELPER = '''def split_heads(values, heads):
    values = np.asarray(values)
    if values.ndim != 2 or min(values.shape) == 0:
        raise ValueError('nonempty token-by-feature input required')
    if type(heads) is not int or heads <= 0 or values.shape[1] % heads != 0:
        raise ValueError('positive head count must divide feature width')
    time, width = values.shape
    head_width = width // heads
    return values.reshape(time, heads, head_width).transpose(1, 0, 2)


def join_heads(values):
    values = np.asarray(values)
    if values.ndim != 3 or min(values.shape) == 0:
        raise ValueError('nonempty head-by-token-by-feature input required')
    heads, time, head_width = values.shape
    return values.transpose(1, 0, 2).reshape(time, heads * head_width)


def multihead(values, heads=2, causal=True):
    values = np.asarray(values, dtype=np.float64)
    if not np.isfinite(values).all():
        raise ValueError('finite values required')
    projected = split_heads(values, heads)
    head_width = projected.shape[-1]
    scores = projected @ projected.transpose(0, 2, 1) / np.sqrt(head_width)
    time = values.shape[0]
    allowed = np.tri(time, dtype=bool) if causal else np.ones((time, time), dtype=bool)
    masked = np.where(allowed[None, :, :], scores, -np.inf)
    mass = np.exp(masked - masked.max(axis=-1, keepdims=True))
    weights = mass / mass.sum(axis=-1, keepdims=True)
    head_outputs = weights @ projected
    return join_heads(head_outputs), weights


def tokenwise_feed_forward(values):
    values = np.asarray(values, dtype=np.float64)
    width = values.shape[-1]
    first_weight = np.eye(width)
    first_bias = np.full(width, -2.0)
    second_weight = np.eye(width)
    hidden = np.maximum(values @ first_weight + first_bias, 0)
    return hidden @ second_weight
'''

add('llm-011',
'''Multiple attention heads give a token several separately normalized views of its permitted context. Each head forms its own query/key comparisons and weighted value mixture. The outputs are concatenated along the feature dimension and then commonly mixed by a learned output projection. A head is not a separate sentence segment, and two heads do not imply that each sees half the tokens. Both can see the complete allowed prefix while using different projected features.

This chapter first treats head splitting as a layout operation, then performs an actual small NumPy multi-head attention calculation. The attention fixture uses identity query/key/value projections so the feature slices are directly inspectable. A real Transformer learns those projections before splitting; its heads can use different linear combinations of the original representation rather than being restricted to raw feature groups. The fixed identity fixture teaches the mechanism without pretending its feature groups are learned semantic concepts.

Residual connections and feed-forward networks complete different parts of the block. A residual adds a branch result back to its input and therefore requires matching shapes and meanings. It does not concatenate the two vectors. A tokenwise feed-forward network applies shared affine maps and a nonlinearity to each token independently. It can transform contextual features already mixed by attention without introducing another direct reduction across token positions.

The next decoder chapter combines these operations with learned embeddings, positional information and normalization. Here the goals are narrower and inspectable: preserve feature membership while splitting and joining, compute distinct head distributions, prove a causal-prefix property through the actual attention operation, and distinguish a valid residual sum from a shape-compatible but semantically wrong layout.''',
r'''### Trace the split and inverse

For X:[T,D] with T=2,D=4,H=2, the head width is d=D/H=2. Reshape [2,4] to [2,2,2] interpreted as [token,head,head_feature], then transpose to [head,token,head_feature]. These dimensions happen to have the same sizes, making axis names more informative than the printed shape alone.

With rows [0,1,2,3] and [4,5,6,7], head zero contains [[0,1],[4,5]], while head one contains [[2,3],[6,7]]. The inverse must first transpose [head,token,feature] back to [token,head,feature], then merge the last two axes. Flattening the head-major tensor directly instead creates rows [0,1,4,5] and [2,3,6,7]. Both arrays have shape [2,4], but the wrong version mixes features from different tokens.

### Compute attention within each head

The batched multiplication Q_h K_h^T produces [H,T,T], one query-by-key matrix for each head. The normalization axis is the final key axis. For a width-two head the scale is sqrt(2), and a causal Boolean triangle [T,T] broadcasts across the head axis. Multiplying weights [H,T,T] by V [H,T,2] returns [H,T,2]. Rejoining produces [T,4], preserving the width needed by a residual path.

For the three-token identity-projection fixture, head zero contains [1,0],[0,1],[1,1], while head one contains [1,1],[1,0],[0,1]. At query row one, the causal mask permits keys zero and one. Head zero has scores [0,1/sqrt(2)] and weights [1/(1+a),a/(1+a)] with a=exp(1/sqrt(2)). Head one has equal allowed scores [1/sqrt(2),1/sqrt(2)] and weights [1/2,1/2]. Their mixtures are therefore approximately [0.33023845,0.66976155] and exactly [1,0.5]. Concatenation gives [0.33023845,0.66976155,1,0.5] before any learned output projection.

### Residual and feed-forward equations

A residual computes R(x)=x+F(x). If F(x)=2x, R(x)=3x and its Jacobian is 3I. If F(x)=0, the residual is the identity. If F(x)=-x, the sum is zero and the Jacobian is zero. Thus the identity contribution can improve the available path, but a residual connection is not a universal proof against vanishing, exploding or cancelled gradients.

A usual feed-forward branch has F(x_t)=activation(x_t W1+b1) W2+b2, using the same weights at every token t. W1 can expand the hidden feature width and W2 return it to D for residual addition. The teaching fixture chooses identity weights and b1=-2 so the first row [0,1,2,3] becomes [0,0,0,1]. This isolates nonlinearity and tokenwise independence. A pair of affine maps without a nonlinearity collapses to one affine map; adding width alone would not create that nonlinear behavior.''',
[('Attention head','A separately normalized query/key/value computation over permitted token positions.'),('Head width','The feature dimension assigned to one head under a declared layout.'),('Concatenation','Joining head features while preserving each token row.'),('Residual addition','Adding a shape-compatible branch output back to its input.'),('Tokenwise feed-forward network','Shared nonlinear feature processing applied independently at each token.')],[
ex('Split and rejoin','Split X=[[0,1,2,3],[4,5,6,7]] into two heads, inspect membership, then invert the layout.','head zero is [[0,1],[4,5]], head one is [[2,3],[6,7]], and rejoining restores X exactly.',r'''values = np.arange(8).reshape(2, 4)
heads = split_heads(values, 2)
np.testing.assert_array_equal(heads[0], [[0, 1], [4, 5]])
np.testing.assert_array_equal(heads[1], [[2, 3], [6, 7]])
np.testing.assert_array_equal(join_heads(heads), values)
assert heads.shape == (2, 2, 2)''','Axis membership is the actual contract. Here every dimension has size two, so shape checks alone cannot distinguish a correct transpose from an incorrect one. Exact element placement supplies the missing evidence.'),
ex('Calculate a residual','Add branch 2X to X, then compare with zero and cancelling branches.','2X gives 3X, zero branch gives X, and branch -X gives zero; all retain the same shape.',r'''values = np.arange(8).reshape(2, 4)
branch = 2 * values
residual = values + branch
np.testing.assert_array_equal(residual, 3 * values)
np.testing.assert_array_equal(values + np.zeros_like(values), values)
np.testing.assert_array_equal(values + (-values), np.zeros_like(values))
assert residual.shape == values.shape''','Residual addition does not concatenate or double feature width. The cancelling branch is a counterexample to the idea that an identity skip always guarantees a nonzero final derivative or representation.'),
ex('Use a tokenwise nonlinear block','Apply the explicit identity-weight, bias-minus-two feed-forward branch to two token rows.','first output [0,0,0,1]; changing the second token does not change the first output.',r'''values = np.arange(8, dtype=np.float64).reshape(2, 4)
output = tokenwise_feed_forward(values)
np.testing.assert_array_equal(output[0], [0, 0, 0, 1])
changed = values.copy()
changed[1] = [100, 200, 300, 400]
np.testing.assert_array_equal(tokenwise_feed_forward(changed)[0], output[0])''','The nonlinearity changes feature behavior, while shared tokenwise application preserves independence across token rows. Context mixing is supplied by the attention branch, not by secretly reducing the time axis here.'),
ex('Test actual head mixtures and causal prefixes','Run the three-token four-feature fixture through two causal heads and compare independently recomputed prefixes.','head distributions differ as derived, row-one output is [1/(1+a),a/(1+a),1,0.5], and every prefix matches.',r'''values = np.array([[1., 0., 1., 1.], [0., 1., 1., 0.], [1., 1., 0., 1.]])
output, weights = multihead(values, heads=2, causal=True)
a = np.exp(1 / np.sqrt(2))
np.testing.assert_allclose(weights[0, 1, :2], [1 / (1 + a), a / (1 + a)], atol=1e-12, rtol=0)
np.testing.assert_allclose(weights[1, 1, :2], [0.5, 0.5], atol=1e-12, rtol=0)
np.testing.assert_array_equal(weights[:, 1, 2], [0, 0])
np.testing.assert_allclose(output[1], [1 / (1 + a), a / (1 + a), 1, 0.5], atol=1e-12, rtol=0)
for length in [1, 2, 3]:
    prefix, _ = multihead(values[:length], heads=2, causal=True)
    np.testing.assert_allclose(prefix, output[:length], atol=1e-12, rtol=0)''','This check exercises real score normalization and value mixing, extending the earlier tokenwise-only prefix check. The analytic row-one expectation is an independent oracle for head identity and the softmax axis. Prefix equality then checks the visibility boundary.'),
ex('Reject an indivisible width','Call the split helper with width 5 and two heads, then with zero heads and an empty token axis.','each invalid layout raises ValueError before reshape.',r'''for values, count in [(np.zeros((2, 5)), 2), (np.zeros((2, 4)), 0), (np.zeros((0, 4)), 2)]:
    try:
        split_heads(values, count)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid head layout accepted')''','A head dimension must be a positive integer under the fixed-width partition. Silently dropping or padding features would define a different representation and needs an explicit design, not an accidental reshape workaround.'),
ex('Detect a wrong rejoin','Flatten the head-major tensor directly and compare values with the correctly inverted transpose.','the wrong [2,4] result differs despite matching shape; the inverse operation restores X.',r'''values = np.arange(8).reshape(2, 4)
heads = split_heads(values, 2)
wrong = heads.reshape(2, 4)
np.testing.assert_array_equal(wrong, [[0, 1, 4, 5], [2, 3, 6, 7]])
assert wrong.shape == values.shape
assert not np.array_equal(wrong, values)
np.testing.assert_array_equal(join_heads(heads), values)''','Element count and final shape are necessary but insufficient. A semantic axis mistake can preserve both while routing one token\'s features into another token\'s representation.')],('Attention Is All You Need','https://arxiv.org/abs/1706.03762'),helper=HELPER)
spec = SPECS['llm-011']
spec['worked_examples'] = [spec['exercises'][0], spec['exercises'][3]]
spec['mechanism_notes'] = '''## Why several heads can help, and what they do not guarantee

A single head returns one normalized mixture of its value vectors for each query. Several heads can compute several mixtures before their results are combined. The output projection can then mix feature contributions across heads, rather than treating each head output as an isolated final answer. This expands the available computation, but it does not guarantee that every head learns a distinct useful role. Redundant or weak heads are possible, and interpreting one head as a particular linguistic relation requires evidence beyond an attractive attention plot.

At fixed model width D, the usual Q/K/V projections still contain about 3D squared weight entries and the output projection about D squared, regardless of how D is divided among heads. The per-head feature dimension becomes D/H, so total projected width remains D. Scores require H*T*T entries if materialized for full self-attention. More heads can therefore change the attention-state layout and its storage even when projection parameter count remains fixed. The efficient attention chapter later distinguishes these algebraic dimensions from a specific GPU kernel\'s memory traffic.

Causal visibility is applied independently in every head. Rejoining does not repair a head that read the future. Conversely, a correct head mask does not repair a feed-forward operation that accidentally reduces over time or a normalization step with the wrong axes. A complete decoder\'s prefix test must include every branch. This chapter\'s identity projections and simple feed-forward weights make the mechanisms inspectable; the learned, normalized full decoder appears in [llm-016](llm-016.md).

An output projection must return a compatible width before residual addition. If a residual uses a different width, a learned projection on the skip path can make dimensions compatible, but that is no longer an unchanged identity skip. The original Transformer block and many later variants choose the model width consistently so the addition has a clear interpretation. The [normalization and gated-block chapter](llm-045.md) develops pre/post normalization and SwiGLU; the [head-sharing chapter](llm-046.md) distinguishes ordinary multi-head attention from MQA and GQA.
'''
spec['diagnosis'] = '''If a split/rejoin test passes shapes but fails values, write an index label for every element before reshaping. Check that token index remains the outer row after joining. A contiguous array can still have the wrong semantic axis order; contiguity alone is not a correctness test.

If two heads unexpectedly have identical weights, inspect their projected inputs and the fixture symmetry before assuming a bug. In this chapter the chosen row-one distributions intentionally differ and have a hand-derived oracle. In a learned model, identical or nearly identical heads may be a real outcome. If weights do not sum to one over allowed keys, inspect the softmax reduction axis and masking order.

If a causal prefix fails, recompute the full sequence of transformations on the prefix. Inspect each head\'s forbidden weights and any token-coupling operation outside attention. If a feed-forward prefix changes when a later row changes, inspect whether a reduction or matrix multiplication is accidentally using the time dimension. Finally, distinguish residual addition from concatenation and avoid claiming that a skip connection proves healthy gradients under every branch function.'''
