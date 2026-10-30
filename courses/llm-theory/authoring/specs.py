from render import add, ex, SPECS

NP = "import numpy as np"
TORCH = (
    "import numpy as np\nimport torch\nfrom torch import nn\nfrom torch.nn import functional as F"
)


def expert(
    number,
    mental,
    anatomy,
    terms,
    exercises,
    source,
    derivation,
    case_study,
    decisions,
    helper="",
    imports=NP,
    links="",
):
    identity = f"llm-{number:03d}"
    add(identity, mental, anatomy, terms, exercises, source, imports, helper, decisions)
    SPECS[identity]["derivation"] = derivation
    SPECS[identity]["case_study"] = case_study
    SPECS[identity]["appendix"] = "## Additional primary references\n\n" + links if links else ""


expert(
    43,
    """Transformer architecture describes which positions exchange information and how those representations are used. An encoder can let every source position attend to every other available source position. A causal decoder restricts a target position to its current and earlier input positions. An encoder-decoder combines a source encoder with a causal target decoder whose cross-attention can read the encoded source. These are information-flow choices,not three names for the same mask.

The training objective is another choice. A masked-token encoder predicts selected corrupted source positions using surrounding context. An autoregressive decoder predicts the next token from a prefix. A sequence-to-sequence model predicts target tokens conditioned on an entire source and an earlier target prefix. Teacher forcing supplies the correct previous target tokens during training;it does not permit the current target answer to leak into its own prediction. An encoder may use future source words because the complete source is available,but a streaming task may impose a different availability contract.

This lesson implements the three attention information patterns on literal vectors. It does not train BERT,T5 or a foundation model. The small calculation is enough to show which perturbations may affect which outputs,which axes a cross-attention score matrix has,and why objective masks and attention masks must be checked separately.""",
    """The attention helper accepts Q shaped(Tq,d),K shaped(Tk,d),V shaped(Tk,dv) and a boolean allowed matrix(Tq,Tk). It validates nonempty legal rows,then uses a stable row-wise softmax of Q@K.T/sqrt(d). Encoder self-attention has Tq=Tk=source length and an all-allowed source mask. Causal decoder self-attention has a lower triangle over target-prefix positions. Cross-attention can be rectangular,with target queries and source keys/values. Labels and loss masks are constructed independently from these attention masks.""",
    [
        (
            "Encoder",
            "A representation network over source positions whose complete context may be available.",
        ),
        ("Causal decoder", "A network preserving the target-prefix information boundary."),
        (
            "Cross-attention",
            "Attention whose queries and keys/values come from different sequences.",
        ),
        (
            "Teacher forcing",
            "Using observed prior target tokens as decoder input during supervised training.",
        ),
        (
            "Objective mask",
            "The target positions included in the loss,distinct from the attention access mask.",
        ),
    ],
    [
        ex(
            "Compare bidirectional and causal mixtures",
            "Use zero queries/keys and values[[2,0],[0,2],[6,6]] under all-allowed and causal masks.",
            "encoder rows all[8/3,8/3];decoder rows[2,0],[1,1],[8/3,8/3].",
            """q=np.zeros((3,2)); values=np.array([[2.,0.],[0.,2.],[6.,6.]])
encoder,_=attention(q,q,values,np.ones((3,3),dtype=bool))
decoder,_=attention(q,q,values,np.tri(3,dtype=bool))
np.testing.assert_allclose(encoder,np.tile([8/3,8/3],(3,1)),atol=1e-12,rtol=0)
np.testing.assert_allclose(decoder,[[2,0],[1,1],[8/3,8/3]],atol=1e-12,rtol=0)""",
            "The score arithmetic is identical;the allowed information differs. A future source change may affect an encoder output when the whole source is available,while a future target change must not affect an earlier causal output.",
        ),
        ex(
            "Trace rectangular cross-attention",
            "Use two zero target queries,three zero source keys and the same source values.",
            "score/weight shape(2,3);output shape(2,2);both outputs[8/3,8/3].",
            """target_queries=np.zeros((2,2)); source_keys=np.zeros((3,2))
cross,weights=attention(target_queries,source_keys,values,np.ones((2,3),dtype=bool))
assert weights.shape==(2,3) and cross.shape==(2,2)
np.testing.assert_allclose(cross,np.tile([8/3,8/3],(2,1)),atol=1e-12,rtol=0)""",
            "The output count follows the query sequence,not the source length. A square-mask assumption would incorrectly reject or distort ordinary encoder-decoder attention.",
        ),
        ex(
            "Build shifted decoder targets",
            "For target IDs[5,7,3],prepend BOS 1 and form input/label pairs.",
            "inputs[1,5,7];labels[5,7,3];diagonal allowed without seeing the target itself.",
            """target=np.array([5,7,3]); inputs=np.concatenate([[1],target[:-1]]); labels=target.copy(); mask=np.tri(3,dtype=bool)
np.testing.assert_array_equal(inputs,[1,5,7]); np.testing.assert_array_equal(labels,[5,7,3])
assert mask[0,0] and not mask[0,1]""",
            "The current decoder input is the previous target under this shifted convention. Allowing the diagonal is compatible with causality;copying the current answer into the same input position would not be.",
        ),
        ex(
            "Separate masked-token supervision",
            "Corrupt source[2,5,7] at the middle position with MASK 0 and supervise only that original token.",
            "input[2,0,7];one active label 5;bidirectional context remains allowed.",
            """original=np.array([2,5,7]); corrupted=original.copy(); corrupted[1]=0; active=np.array([False,True,False])
np.testing.assert_array_equal(corrupted,[2,0,7]); assert original[active].tolist()==[5]
assert np.ones((3,3),dtype=bool)[1].all()""",
            "The source attention mask and the loss participation mask have different shapes and purposes. A masked-language objective does not require a causal triangle over the complete source.",
        ),
        ex(
            "Perturb future target values",
            "Change only the third value vector and compare the first two encoder/decoder outputs.",
            "encoder prefix changes;causal decoder prefix stays fixed.",
            """changed=values.copy(); changed[2]=[100,200]
new_encoder,_=attention(q,q,changed,np.ones((3,3),dtype=bool)); new_decoder,_=attention(q,q,changed,np.tri(3,dtype=bool))
assert not np.allclose(new_encoder[:2],encoder[:2])
np.testing.assert_allclose(new_decoder[:2],decoder[:2],atol=1e-12,rtol=0)""",
            "This is a direct information-flow test. The encoder behavior is valid for a fully available source but invalid if those same positions represent unavailable future targets.",
        ),
        ex(
            "Combine source padding with cross-attention",
            "Mark the third source position as padding for both target queries.",
            "both cross outputs[1,1];padded source weight 0.",
            """allowed=np.array([[True,True,False],[True,True,False]])
masked,weights=attention(target_queries,source_keys,values,allowed)
np.testing.assert_allclose(masked,[[1,1],[1,1]],atol=1e-12,rtol=0)
np.testing.assert_array_equal(weights[:,2],[0,0])""",
            "Padding describes source availability,not target causality. A decoder may need a causal self-attention mask and a separate source-padding cross-attention mask in the same block.",
        ),
    ],
    ("Attention Is All You Need", "https://arxiv.org/abs/1706.03762"),
    r"""For one attention operation, let Q have Tq query rows and K,V have Tk source rows. Scores are \(S=\frac{QK^{\mathsf T}}{\sqrt{d}}\),so S is Tq by Tk. For each queryi,normalize only allowed keysj:

\[
A_{ij}=\frac{\exp(S_{ij}-m_i)}{\sum_{k\in\mathcal A_i}\exp(S_{ik}-m_i)},\qquad O_i=\sum_{j\in\mathcal A_i}A_{ij}V_j.
\]

Encoder self-attention can use all nonpadding source indices. Decoder self-attention uses j<=i under the shifted-target convention. Cross-attention uses source keys and target queries,so its mask need not be square. The output feature width is dv,while its row count remains Tq.

An autoregressive objective factors p(y|x)=product_t p(y_t|x,y_<t). A masked-source objective instead sums losses over a chosen subset M of corrupted source positions. The formula does not make these objectives interchangeable:they expose different conditioning information and supervise different events. In particular,teacher forcing supplies y_<t,not y_t,to the target position predicting y_t.""",
    """A study-summary assistant receives a complete report and generates a structured summary. An encoder-decoder can encode the whole report before target generation. If the product changes to a live transcription assistant,the source is no longer fully available;reusing an unrestricted source encoder would violate the streaming contract. The architecture name did not become wrong in isolation. The input-availability assumption changed. A useful test perturbs text that arrives later and checks whether earlier published outputs depend on it under the intended serving policy.""",
    """Choose an encoder-style representation for tasks such as document classification or masked representation learning when the whole input is available. Choose a causal decoder for prefix-conditioned generation. Encoder-decoder designs make the source/target distinction explicit and can support translation,summarization andstructured transformations. These are architectural tendencies,not guarantees that one family always wins.

Do not infer the training objective from a diagram alone. Check token shifting,corruption,loss masks,source availability and evaluation units. Prefix invariance proves one information boundary;it does not prove dataset independence,correct labels or factual reliability. Keep those checks separate when building a subject assistant.""",
    helper="""def attention(q,k,v,allowed):
    q,k,v=(np.asarray(value,dtype=np.float64) for value in (q,k,v)); allowed=np.asarray(allowed)
    if any(value.ndim!=2 for value in (q,k,v)) or not len(q) or not len(k) or q.shape[1]==0: raise ValueError('nonempty matrices required')
    if q.shape[1]!=k.shape[1] or k.shape[0]!=v.shape[0] or allowed.shape!=(len(q),len(k)): raise ValueError('attention shape mismatch')
    if allowed.dtype!=np.bool_: raise TypeError('boolean allowed mask required')
    if not allowed.any(1).all() or not all(np.isfinite(value).all() for value in (q,k,v)): raise ValueError('finite legal rows required')
    with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
        scores=q@k.T/np.sqrt(q.shape[1])
    if not np.isfinite(scores[allowed]).all(): raise ValueError('finite computed attention scores required')
    masked=np.where(allowed,scores,-np.inf)
    with np.errstate(over='ignore',under='ignore'):
        mass=np.exp(masked-masked.max(1,keepdims=True))
    weights=mass/mass.sum(1,keepdims=True)
    return weights@v,weights
""",
    links="[BERT and masked bidirectional pretraining](https://arxiv.org/abs/1810.04805), [T5 and text-to-text objectives](https://arxiv.org/abs/1910.10683).",
)
expert(
    44,
    """Position mechanisms tell attention how token order or distance should influence a comparison. Learned absolute embeddings attach vectors to positions,while relative-position methods make pairwise relationships explicit. Rotary position embeddings,RoPE,rotate pairs of query andkey features by position-dependent angles. The dot product between rotated vectors then depends on their relative offset through a rotation identity. Values are not automatically rotated by that standard construction.

ALiBi uses a different mechanism:it adds a distance-dependent bias directly to attention scores,typically penalizing distant allowed keys under a causal decoder. A bias is not an access mask. Future keys still need to be excluded. Different heads can use different slopes,which creates different recency preferences.

A formula accepting a large position index does not prove that a trained model will use long context reliably. Training length,frequency choices,precision,attention patterns andevaluation tasks all matter. This chapter tests exact geometric identities,causal bias behavior andcache-position bookkeeping. It makes no claim that a particular RoPE scaling orALiBi configuration preserves quality outside its measured training/evaluation range.""",
    """The RoPE helper pairs adjacent features and uses inverse frequencies base**(-2*i/d) for pair index i. For each positionp,it applies a2Drotation byp*frequency to the corresponding query orkey pair. Head width must be positive andeven. ALiBi scores add-slope*(query_position-key_position) for legal past/current keys,then apply the causal mask before softmax. Cached keys retain the position assigned when they were created;do not rotate an already rotated key again or restart offsets for a new token.""",
    [
        ("RoPE", "Rotary position embedding applied to query/key feature pairs."),
        ("Relative offset", "The difference between two token positions."),
        ("ALiBi", "Attention with linear distance biases added to scores."),
        ("Position offset", "The absolute index of a newly appended cached token."),
        (
            "Length extrapolation",
            "Using context lengths beyond those supported by the training/evaluation evidence.",
        ),
    ],
    [
        ex(
            "Rotate a two-dimensional vector",
            "Rotate[1,0] bypi/2 and check length preservation.",
            "approximately[0,1];norm 1.",
            """vector=np.array([1.,0.]); rotated=rotate(vector,np.pi/2)
np.testing.assert_allclose(rotated,[0,1],atol=1e-12,rtol=0)
np.testing.assert_allclose(np.linalg.norm(rotated),1,atol=1e-12,rtol=0)""",
            "A rotation changes direction while preserving the Euclidean norm. This separates position encoding from arbitrary magnitude scaling.",
        ),
        ex(
            "Verify the relative dot-product identity",
            "Useq[1,2],k[3,-1],angles m=.3,n=1.1.",
            "dot(Rm q,Rn k)=dot(q,R(n-m)k) within1e-12.",
            """q=np.array([1.,2.]); k=np.array([3.,-1.]); m=.3; n=1.1
left=rotate(q,m)@rotate(k,n); right=q@rotate(k,n-m)
np.testing.assert_allclose(left,right,atol=1e-12,rtol=0)""",
            "The transpose of a rotation is its inverse,so the absolute angles combine into their difference. This is an algebraic property,not a measured long-context quality result.",
        ),
        ex(
            "Inspect an ALiBi causal row",
            "Use zero content scores for query position 2,keys 0,1,2 and slope log2.",
            "normalized weights[1/7,2/7,4/7].",
            """positions=np.arange(3); score=-np.log(2)*(2-positions); mass=np.exp(score-score.max()); weights=mass/mass.sum()
np.testing.assert_allclose(weights,[1/7,2/7,4/7],atol=1e-12,rtol=0)""",
            "The distance penalties produce exponentials1/4,1/2,1 before normalization. The current key receives the largest weight under this illustrative slope.",
        ),
        ex(
            "Apply multi-frequency RoPE",
            "Use width 4,base10000 and positions0,1 on two fixed vectors;inspect pair norms.",
            "frequencies1,.01;each pair norm preserved.",
            """values=np.array([[1.,0.,3.,4.],[2.,1.,0.,2.]])
encoded=rope(values,np.array([0,1]),base=10000.)
np.testing.assert_allclose(np.linalg.norm(encoded.reshape(2,2,2),axis=-1),np.linalg.norm(values.reshape(2,2,2),axis=-1),atol=1e-12,rtol=0)
np.testing.assert_allclose(10000.**(-2*np.arange(2)/4),[1,.01],atol=1e-12,rtol=0)""",
            "Different feature pairs rotate at different rates. The fixture uses adjacent-pair layout;other implementations may store paired components differently and need a layout translation.",
        ),
        ex(
            "Catch a cache offset reset",
            "Encode the third key at position2 and compare with mistakenly encoding it at position0.",
            "correct incremental encoding matches full encoding;reset differs.",
            """keys=np.array([[1.,0.],[0.,1.],[1.,1.]])
full=rope(keys,np.arange(3)); incremental=rope(keys[2:],np.array([2])); reset=rope(keys[2:],np.array([0]))
np.testing.assert_allclose(incremental,full[2:],atol=1e-12,rtol=0)
assert not np.allclose(reset,full[2:])""",
            "A cache contains position-dependent key state. Correct tensor dimensions do not reveal that a new token was assigned the wrong position.",
        ),
        ex(
            "Separate computability from extrapolation evidence",
            "Compute a finite encoding at position1000000,then record that no trained-model quality was measured.",
            "finite vector;long_context_quality_verified=False;odd width rejected.",
            """far=rope(np.array([[1.,0.,1.,0.]]),np.array([1_000_000]))
assert np.isfinite(far).all(); report={'formula_evaluated':True,'long_context_quality_verified':False}; assert not report['long_context_quality_verified']
try: rope(np.ones((1,3)),np.array([0]))
except ValueError: pass
else: raise AssertionError('odd rotary width accepted')""",
            "A valid sine/cosine calculation says nothing about whether a model learned useful behavior at that distance. The dimension check is a mathematical contract,the quality question is empirical.",
        ),
    ],
    ("RoFormer and RoPE", "https://arxiv.org/abs/2104.09864"),
    r"""For one feature pair,define

\[
R(\theta)=\begin{bmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{bmatrix}.
\]

Because R(m)^T R(n)=R(n-m),the attention numerator obeys(R(m)q)^T(R(n)k)=q^T R(n-m)k. The identity holds independently for each paired subspace. With head widthd andpair index i,the illustrative standard frequency isomega_i=base^(-2i/d),so positionp contributes anglep*omega_i. This is a layout andfrequency contract;changing thebase orscaling positions changes the trained computation.

For a causal ALiBi head with positive slopesa,the allowed score isS_ij=q_i^T k_j/sqrt(d)-sa*(i-j) forj<=i. Future positions are excluded by the mask. With zero content scores,i=2 andsa=log2,the unnormalized masses are1/4,1/2,1,which normalize to1/7,2/7,4/7. A linear bias by itself would reward future positions wheni-j isnegative,so it cannot replace thecausal mask.""",
    """An incremental decoder passes allprefix tests at short length butdiverges after reusing a cache. The model weightshave notchanged. Inspection shows each newkeywasrotated usingposition0 instead of the accumulatedcache length. Recomputing the samekey at its correctabsolute positionrestores parity. Another commonfailure rotates storedkeys asecondtime whencombiningcache andnewtokens. Both bugs arestate/layout errors,not evidence thatRoPE itself lacks long-context capacity. Only afterthese invariants pass does a length-generalization study become interpretable.""",
    """Use positional mechanisms according to the architecture and its training contract. Learned absolute tables impose an explicit index range unless extended;rotary andbias formulas can be evaluated beyond the training length butstill need empirical validation. Compare methods on tasks requiring information at different distances,not merely a longer prompt that can be answered from its final sentence.

Do not claim that changing aRoPE base orapplying a scaling recipe preserves quality without a measured model-specific study. Check dtype precision,position offsets,cache layout andmasking first. ForALiBi,record theactual per-head slope policy;the single slope here is a hand-checkable fixture rather than a claim to reproduce everypaper configuration.""",
    helper="""def rotate(vector,angle):
    c,s=np.cos(angle),np.sin(angle); return np.array([[c,-s],[s,c]])@np.asarray(vector,dtype=float)
def rope(values,positions,base=10000.):
    values=np.asarray(values,dtype=np.float64); positions=np.asarray(positions,dtype=np.float64)
    if values.ndim!=2 or values.shape[1]==0 or values.shape[1]%2 or positions.shape!=(len(values),): raise ValueError('even feature width and one position per row required')
    if not np.isfinite(values).all() or not np.isfinite(positions).all() or not np.isfinite(base) or base<=0: raise ValueError('finite rotary inputs required')
    width=values.shape[1]; pairs=values.reshape(len(values),width//2,2); angles=positions[:,None]*base**(-2*np.arange(width//2)/width)
    c,s=np.cos(angles),np.sin(angles); result=np.empty_like(pairs)
    result[...,0]=pairs[...,0]*c-pairs[...,1]*s; result[...,1]=pairs[...,0]*s+pairs[...,1]*c
    return result.reshape(values.shape)
""",
    links="[ALiBi](https://arxiv.org/abs/2108.12409), [Transformer-XL and relative-position context](https://arxiv.org/abs/1901.02860).",
)
expert(
    45,
    """Normalization placement changes the residual network\'s gradient path. Apre-norm block computesx+F(Norm(x)),leaving an explicit identity path around the transformed branch. Apost-norm block computesNorm(x+F(x)),so the normalizer lies on the combined residual path. With a zero branch,pre-norm is exactly the identity whilepost-norm still changes the input. This local observation helps explain optimization behavior,but it does not establish a universal best architecture or learning-rate schedule.

RMSNorm divides by root-mean-square magnitude without subtracting the feature mean. LayerNorm subtracts the mean andnormalizes centered variance. Their invariances differ:adding a constant to everyfeature leaves LayerNorm\'s centered values unchanged,but generally changes RMSNorm. Both typically use learned gain andan epsilon whose placement matters numerically.

A gated feed-forward network multiplies two projections. SwiGLU usesSiLU(xWg) elementwise multiplied byxWu,then projects back withWd. It has three weight matrices rather than thetwo of aplain feed-forward block. A fair parameter comparison must adjust hidden widths oracknowledge the largerbudget. This lesson uses actualPyTorchautograd to inspect normalization Jacobians andgate gradients.""",
    """All examples usefloat64 andsmallfeature widths. RMSNorm computesx/sqrt(mean(x²)+eps) timesgain. LayerNorm computes(x-mean(x))/sqrt(mean((x-mean(x))²)+eps). Apre/post comparison uses a zero linearbranch so the residual distinction is isolated. SwiGLU usesF.silu for thegate projection andan elementwise product withtheup projection. Check the three matrix shapes beforecounting parameters orrequesting gradients.""",
    [
        ("Pre-norm", "Normalization inside the transformed residual branch."),
        ("Post-norm", "Normalization applied after combining residual andbranch."),
        ("RMSNorm", "Normalization by root-mean-square magnitude without mean subtraction."),
        ("SwiGLU", "A gated feed-forward transformation using aSiLU-activated gate."),
        ("Jacobian", "The matrix of output sensitivities toinput coordinates."),
    ],
    [
        ex(
            "Compare RMSNorm and LayerNorm",
            "Normalize vector [3,4] with unit gain and epsilon 1e-8.",
            "RMSNorm mean nonzero;LayerNorm mean approximately 0.",
            """x=torch.tensor([3.,4.],dtype=torch.float64)
rms=rms_norm(x); centered=layer_norm(x)
assert abs(rms.mean().item())>.5
np.testing.assert_allclose(centered.mean().item(),0,atol=1e-12,rtol=0)
np.testing.assert_allclose(rms.detach().numpy(),np.array([3.,4.])/np.sqrt(12.5+1e-8),atol=1e-12,rtol=0)""",
            "The two methods normalize different statistics. Equal output shape does not imply that one is a drop-in numerical replacement for the other.",
        ),
        ex(
            "Trace pre/post residual Jacobians",
            "Set the transformed branch to zero and compare pre-norm x with post-norm LayerNorm(x).",
            "pre-normJacobianidentity;post-normJacobianannihilatesaconstantshift.",
            """value=torch.tensor([1.,2.,4.],dtype=torch.float64,requires_grad=True)
pre=torch.autograd.functional.jacobian(lambda z:z+0*layer_norm(z),value)
post=torch.autograd.functional.jacobian(lambda z:layer_norm(z+0*z),value)
torch.testing.assert_close(pre,torch.eye(3,dtype=torch.float64),atol=1e-12,rtol=0)
torch.testing.assert_close(post@torch.ones(3,dtype=torch.float64),torch.zeros(3,dtype=torch.float64),atol=1e-10,rtol=0)""",
            "The zero-branch control isolates placement. LayerNorm removes a common feature shift,so its derivative along the all-ones direction is zero rather than identity.",
        ),
        ex(
            "Calculate a SwiGLU gate derivative",
            "Use scalar g0,u2 and output SiLU(g)*u.",
            "output0;gradient with respect to g is 1;with respect to u is 0.",
            """gate=torch.tensor(0.,dtype=torch.float64,requires_grad=True); up=torch.tensor(2.,dtype=torch.float64,requires_grad=True)
output=F.silu(gate)*up; output.backward()
assert output.item()==0 and gate.grad.item()==1 and up.grad.item()==0""",
            "At zero,SiLU has derivative one-half. Multiplication by up2 givesgategradient1,while the up branch sees the zero gate value. A connected zero gradient is not a missing path.",
        ),
        ex(
            "Check the RMSNorm Jacobian formula",
            "Compare autograd with J=I/r-xxT/(d*r³) at x = [1, 2, 3].",
            "matrices agree within 1e-10.",
            """value=torch.tensor([1.,2.,3.],dtype=torch.float64,requires_grad=True); r=torch.sqrt(value.square().mean()+1e-8); width=value.numel()
analytic=torch.eye(width,dtype=torch.float64)/r-torch.outer(value,value)/(width*r**3)
automatic=torch.autograd.functional.jacobian(rms_norm,value)
torch.testing.assert_close(automatic,analytic,atol=1e-10,rtol=0)""",
            "The derivative contains a direct coordinate term andacoupling term through the sharedRMSdenominator. Omitting the coupling would treat normalization as constant scaling and produce incorrect gradients.",
        ),
        ex(
            "Match feed-forward parameter budgets",
            "Compare plain FFN model width d=4,hidden6 with SwiGLU hidden width 4,excluding biases;execute a gated block with input and output width 4.",
            "both 48 weight entries;output shape(2,4).",
            """d=4; plain_hidden=6; gated_hidden=4
assert 2*d*plain_hidden==3*d*gated_hidden==48
inputs=torch.tensor([[1.,0.,-1.,2.],[0.,1.,2.,-1.]],dtype=torch.float64); wg=torch.eye(4,dtype=torch.float64); wu=2*wg; wd=.5*wg
result=(F.silu(inputs@wg)*(inputs@wu))@wd
assert tuple(result.shape)==(2,4) and torch.isfinite(result).all()""",
            "Matching hidden widths would not match parameter counts. The2/3 width relation is a budget arithmetic rule here,not a universal model-quality prescription.",
        ),
        ex(
            "Test invariance and zero-vector boundaries",
            "Shiftx1,2,3 by5,compare the two normalizers,and normalize zero.",
            "LayerNorm shift invariant;RMSNorm changes;both zero cases finite.",
            """base=torch.tensor([1.,2.,3.],dtype=torch.float64)
torch.testing.assert_close(layer_norm(base+5),layer_norm(base),atol=1e-12,rtol=0)
assert not torch.allclose(rms_norm(base+5),rms_norm(base))
assert torch.isfinite(rms_norm(torch.zeros(3,dtype=torch.float64))).all()""",
            "Epsilon handles zero magnitude,but doesnotcreate the mean-subtraction invariance thatRMSNorm deliberately omits. These invariants clarify what information each normalizer removes.",
        ),
    ],
    ("Root Mean Square Layer Normalization", "https://arxiv.org/abs/1910.07467"),
    r"""For feature vectorx in R^d andunitgain,let r=sqrt((1/d)sum_j x_j²+epsilon). Then y_i=x_i/r. Differentiate both the numerator anddenominator:

\[
\frac{\partial y_i}{\partial x_j}=\frac{\delta_{ij}}{r}-\frac{x_i x_j}{d r^3}.
\]

A learned per-feature gaing_i multiplies rowi of thisJacobian. RMSNorm doesnot subtractmu,so aconstantshift generally changes itsdirection andscale. LayerNorm first centersx-mu,which removes theall-ones shift direction.

For aresidual branchF,pre-norm isy=x+F(N(x));itsJacobian isI+J_F J_N. Post-norm isy=N(x+F(x));itsJacobian isJ_N(I+J_F). WithF=0,thefirstisI andthesecondisJ_N. This is alocalmechanism comparison,not acomplete theorem abouttraining everydeepnetwork.

Withrow-vector inputs,plainFFN isphi(xW1)W2 andhas2dh weights. SwiGLU is[SiLU(xWg) elementwise_mul(xWu)]Wd andhas3dh weights. To compare equalweightbudgets,chooseh_gated=(2/3)h_plain wheninteger dimensions permit. SiLU(g)=g*sigmoid(g),so itsderivative issigmoid(g)+g*sigmoid(g)*(1-sigmoid(g)). Atg0,thederivative is1/2.""",
    """A decoder refactor replaces aplainFFN withSwiGLU whilekeeping thehiddenwidth unchanged andreports aqualitygain as proof thatgating isbetter. Theparametercount increased by50percent in theFFN block,so theexperiment changed bothmechanism andbudget. A second refactor movesnormalization across theresidual add whilekeeping theoptimizer settings fixed. A newgradient problem isthen blamed ontheactivation. The controlledzero-branchJacobian andparameter-count calculations separate these confounders before a largertraining comparison.""",
    """Use normalization andgating choices as part of a complete architecture andtraining policy. Pre-norm often offers a direct residual gradient path,but final normalization,initialization,depth andoptimizer settings stillmatter. RMSNorm preserves a different setofinvariances thanLayerNorm. A swap requires a model-specific evaluation orretraining plan rather than anassumption ofnumerical equivalence.

ForSwiGLU,record thegate activation,projection layouts,bias policy,hiddenwidth andparameter budget. Inspectbothgate andupbranch gradients when aunit appearsinactive. A zero gradient at a particular input canfollow directly fromtheproduct structure andneednot indicate abrokenautograd graph. Compare actualheld-out taskquality andresourceuse aftermechanical checks pass.""",
    helper="""def rms_norm(x,eps=1e-8): return x/torch.sqrt(x.square().mean(-1,keepdim=True)+eps)
def layer_norm(x,eps=1e-8):
    centered=x-x.mean(-1,keepdim=True)
    return centered/torch.sqrt(centered.square().mean(-1,keepdim=True)+eps)
""",
    imports=TORCH,
    links="[GLU variants andSwiGLU](https://arxiv.org/abs/2002.05202), [Pre/post normalization analysis](https://arxiv.org/abs/2002.04745).",
)
expert(
    46,
    """Attention architecture and attention execution are separate design dimensions. Multi-head attention,MHA,uses distinct query,key andvalue heads. Multi-query attention,MQA,shares one key/value head across query heads. Grouped-query attention,GQA,uses an intermediate number of key/value heads,with several query heads sharing each pair. The query-head count can remain fixed while cached key/value storage shrinks. This changes the representation constraint,so replacing arbitrary MHA weights with shared heads does not guarantee identical model quality or outputs.

FlashAttention addresses a different problem:how to execute exact attention while reducing expensive memory traffic. Its GPU implementations use tiling and hardware-aware scheduling. A useful mathematical ingredient is an online softmax normalizer that updates a running maximum,denominator andweighted-value numerator across blocks. This allows the exact output to be accumulated without retaining the entire score matrix.

The reference here implements grouped head selection and blockwise stable attention in NumPy. It verifies algebraic parity with a dense oracle and reports the largest score block used by the routine. It is not a FlashAttention kernel,does not benchmark a GPU,and does not claim that the whole test process avoids dense allocations because the independent oracle deliberately constructs them.""",
    """For the single-batch reference,Q has shape(Hq,T,d),K shape(Hkv,T,d),andV shape(Hkv,T,dv),withHq divisible byHkv. Queryheadh uses key/value headh//(Hq/Hkv). The dense helper normalizes allowed keys per query. The online helper processes legal key blocks,skips blocks with no allowed keys,and rescales old accumulated state whenever a larger score appears. It rejects an entirely masked row rather than returning an invented distribution.""",
    [
        ("MHA", "Attention with one key/value head per query head."),
        ("MQA", "Attention sharing one key/value head across all query heads."),
        ("GQA", "Attention sharing key/value heads within groups of query heads."),
        ("Online softmax state", "A running maximum,normalizer andweighted-value numerator."),
        (
            "IO-aware kernel",
            "An implementation designed around memory hierarchy andtraffic,not only arithmetic count.",
        ),
    ],
    [
        ex(
            "Count cache and projection dimensions",
            "Use batch 1,time 5,query heads 4,head width 2,float32,and compare KV heads 4,2,1.",
            "raw KV bytes 320,160,80;projection weights 256,192,160 for model width 8 without biases.",
            """query_heads=4; head_width=2; width=8; time=5
cache_bytes=[2*1*time*kv_heads*head_width*4 for kv_heads in [4,2,1]]
parameters=[width*(query_heads*head_width)+2*width*(kv_heads*head_width)+(query_heads*head_width)*width for kv_heads in [4,2,1]]
assert cache_bytes==[320,160,80] and parameters==[256,192,160]""",
            "The cache factor2 counts keys and values. These are raw tensor/weight counts excluding allocator,activation,quantization-metadata and communication overhead.",
        ),
        ex(
            "Verify grouped heads against an equivalent repeated-head oracle",
            "Use 4 query heads and 2 KV heads;repeat each KV head twice only in the dense oracle.",
            "outputs agree within1e-12;shape(4,3,2).",
            """q=np.arange(24,dtype=float).reshape(4,3,2)/10
k=np.arange(12,dtype=float).reshape(2,3,2)/7
v=np.array([[[1.,0.],[0.,2.],[3.,1.]],[[2.,1.],[1.,4.],[5.,2.]]])
grouped=gqa(q,k,v)
expanded_k=np.repeat(k,2,axis=0); expanded_v=np.repeat(v,2,axis=0)
oracle=np.stack([dense(q[h],expanded_k[h],expanded_v[h],np.tri(3,dtype=bool)) for h in range(4)])
assert grouped.shape==(4,3,2); np.testing.assert_allclose(grouped,oracle,atol=1e-12,rtol=0)""",
            "The comparison manufactures identical shared heads,so parity is expected. It does not say that an arbitrary trained four-KV-head model can be compressed to two heads without changing behavior.",
        ),
        ex(
            "Trace online softmax at extreme scores",
            "Combine scores1000,999,998 and values1,3,5 in blocks of2.",
            "finite output equals a maximum-shifted dense calculation.",
            """scores=np.array([1000.,999.,998.]); values=np.array([[1.],[3.],[5.]])
online,peak=online_row(scores,values,2)
mass=np.exp(np.array([0.,-1.,-2.])); expected=(mass@values)/mass.sum()
np.testing.assert_allclose(online,expected,atol=1e-12,rtol=0); assert peak==2 and np.isfinite(online).all()""",
            "When the running maximum changes,the old numerator and denominator must both be rescaled. Updating only one produces a plausible but incorrect weighted average.",
        ),
        ex(
            "Compare several block sizes under causal masking",
            "Use five nonuniform query/key rows and compare block sizes 1,2,3,5 with dense attention.",
            "all outputs agree within1e-12;largest temporary score block does not exceed the chosen size.",
            """queries=np.array([[1.,0.],[0.,1.],[1.,1.],[-1.,2.],[2.,-1.]])
keys=np.array([[2.,0.],[1.,1.],[0.,2.],[-1.,1.],[1.,-2.]])
values=np.arange(10,dtype=float).reshape(5,2); allowed=np.tri(5,dtype=bool); expected=dense(queries,keys,values,allowed)
for block in [1,2,3,5]:
    output,peak=online_attention(queries,keys,values,allowed,block)
    np.testing.assert_allclose(output,expected,atol=1e-12,rtol=0); assert peak<=block""",
            "The odd length exercises a partial final block. The mask makes some early-row blocks empty,which the implementation must skip without generating negative-infinity subtractionNaNs.",
        ),
        ex(
            "Preserve a causal prefix under future changes",
            "Change only value rows 3 and 4 and comparethefirstthree online outputs.",
            "first three rows unchanged.",
            """changed=values.copy(); changed[3:]+=100
altered,_=online_attention(queries,keys,changed,allowed,2)
np.testing.assert_allclose(altered[:3],expected[:3],atol=1e-12,rtol=0)""",
            "Block processing must preserve the same information boundary as dense attention. Tiling is not permission to normalize with future values or include masked keys in the denominator.",
        ),
        ex(
            "Reject invalid grouping and empty support",
            "Try 4 query heads with3KVheads,and an all-false attention row.",
            "both raise ValueError;no output NaNs are accepted.",
            """try: gqa(np.zeros((4,2,2)),np.zeros((3,2,2)),np.zeros((3,2,2)))
except ValueError: pass
else: raise AssertionError('indivisible head grouping accepted')
bad=allowed.copy(); bad[0]=False
try: online_attention(queries,keys,values,bad,2)
except ValueError: pass
else: raise AssertionError('empty attention support accepted')""",
            "Head mapping needs an integer group size,and each query needs at least one legal key. Clear validation separates architecture misuse from numerical-kernel failure.",
        ),
    ],
    ("GQA", "https://arxiv.org/abs/2305.13245"),
    r"""LetB bebatch size,L thecached token count,Hkv thekey/value head count,d thehead width ands thebytes perentry. RawKVstorage is2*B*L*Hkv*d*s. Queryheads do not multiply this storage again. With modelwidthD,Hq queryheads andoutputwidthD,the bias-free projection count isD*(Hq*d)+2D*(Hkv*d)+(Hq*d)*D.

For one query,maintainm=max(previous scores),ell=sum exp(score-m),andn=sum exp(score-m)*value. When a block with scoresb arrives,letm_new=max(m,max(b)) andalpha=exp(m-m_new). Then

\[
\ell_{new}=\alpha\ell+\sum_j\exp(b_j-m_{new}),\quad
n_{new}=\alpha n+\sum_j\exp(b_j-m_{new})v_j.
\]

The final attention output isn/ell. Both accumulated quantities use the same reference maximum,so their ratio equals the dense softmax-weighted sum up to floating-point rounding. The recurrence preserves exact attention semantics while permitting a tiled execution strategy. A fastGPUimplementation must additionally manage memory layout,parallelism,backward recomputation andhardware scheduling;those are not measured by thisNumPyreference.""",
    """A serving team reduces KVheads from8to2 andobserves a fourfold reduction in the rawcache formula. It then predicts a fourfold end-to-end speedup. That conclusion ignores weight reads,attention arithmetic,batching,otherlayers andcommunication. Separately,a blockwise implementation matches most dense outputs butfails after a block containing a muchlarger score. Its denominator isrescaled butitsweighted numerator isnot. The tiny1000,999,998 fixture andmultiple block sizes expose thatalgebraic bug before anyGPUbenchmark is meaningful.""",
    """UseMQA orGQA when thearchitecture andtraining evidence support sharing keys/values toreduce incrementalcache costs. Treat converting existing weights as a model-change problem requiring adaptation/evaluation,not a pure storage-format rewrite. Use IO-aware exact-attention kernels when theprepared hardware/backend supports them andtheir correctness andperformance aremeasured on representative shapes.

Do not conflate fewerKVheads with FlashAttention. One changes model structure andcache dimensions;theother changes execution of anattention computation. Do not claim that thisreference measures peakmemory orGPUthroughput. Its dense oracle intentionally allocates thefullscore matrix tocheck theblockwise result,andPythonloops are not a proxy for anoptimizedkernel.""",
    helper="""def scaled_scores(q,k):
    if q.ndim!=2 or k.ndim!=2 or q.shape[1]==0 or q.shape[1]!=k.shape[1]: raise ValueError('positive matching head width required')
    with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
        scores=q@k.T/np.sqrt(q.shape[1])
    if not np.isfinite(scores).all(): raise ValueError('finite computed attention scores required')
    return scores
def dense(q,k,v,allowed):
    scores=scaled_scores(q,k); masked=np.where(allowed,scores,-np.inf)
    if not allowed.any(1).all(): raise ValueError('each query requires a legal key')
    mass=np.exp(masked-masked.max(1,keepdims=True)); return mass/mass.sum(1,keepdims=True)@v
def gqa(q,k,v):
    q,k,v=(np.asarray(value,dtype=float) for value in (q,k,v))
    if any(value.ndim!=3 for value in (q,k,v)) or not len(q) or not len(k) or q.shape[1]==0 or q.shape[2]==0 or v.shape[2]==0 or not all(np.isfinite(value).all() for value in (q,k,v)) or len(q)%len(k) or k.shape[:2]!=v.shape[:2] or q.shape[1:]!=k.shape[1:]: raise ValueError('self-attention grouped head contract')
    group=len(q)//len(k); allowed=np.tri(q.shape[1],dtype=bool)
    return np.stack([dense(q[head],k[head//group],v[head//group],allowed) for head in range(len(q))])
def online_row(scores,values,block_size):
    scores=np.asarray(scores,dtype=float); values=np.asarray(values,dtype=float)
    if scores.ndim!=1 or not len(scores) or values.ndim!=2 or len(values)!=len(scores) or type(block_size) is not int or block_size<=0 or not np.isfinite(scores).all() or not np.isfinite(values).all(): raise ValueError('finite nonempty online row and positive block required')
    maximum=-np.inf; denominator=0.; numerator=np.zeros(values.shape[1]); peak=0
    for start in range(0,len(scores),block_size):
        block=scores[start:start+block_size]; local_values=values[start:start+block_size]; peak=max(peak,len(block))
        new_maximum=max(maximum,float(block.max()))
        with np.errstate(over='ignore',invalid='ignore',divide='ignore',under='ignore'):
            scale=0. if maximum==-np.inf else np.exp(maximum-new_maximum)
            mass=np.exp(block-new_maximum)
            numerator=scale*numerator+mass@local_values
            denominator=scale*denominator+mass.sum()
        if not np.isfinite(numerator).all() or not np.isfinite(denominator) or denominator<=0:
            raise ValueError('finite online attention accumulators required')
        maximum=new_maximum
    with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
        output=numerator/denominator
    if not np.isfinite(output).all(): raise ValueError('finite online attention output required')
    return output,peak
def online_attention(q,k,v,allowed,block_size):
    q,k,v=(np.asarray(value,dtype=float) for value in (q,k,v)); allowed=np.asarray(allowed)
    if any(value.ndim!=2 for value in (q,k,v)) or not len(q) or q.shape[1]==0 or q.shape[1]!=k.shape[1] or len(k)!=len(v) or allowed.shape!=(len(q),len(k)) or allowed.dtype!=np.bool_: raise ValueError('attention shapes and boolean mask required')
    if not allowed.any(1).all() or not all(np.isfinite(value).all() for value in (q,k,v)) or type(block_size) is not int or block_size<=0: raise ValueError('finite legal attention rows and positive block required')
    outputs=[]; peak=0
    for row in range(len(q)):
        maximum=-np.inf; denominator=0.; numerator=np.zeros(v.shape[1])
        for start in range(0,len(k),block_size):
            mask=allowed[row,start:start+block_size]
            if not mask.any(): continue
            keys=k[start:start+block_size][mask]; values=v[start:start+block_size][mask]; scores=scaled_scores(q[row:row+1],keys)[0]; peak=max(peak,len(scores))
            new_maximum=max(maximum,float(scores.max()))
            with np.errstate(over='ignore',invalid='ignore',divide='ignore',under='ignore'):
                scale=0. if maximum==-np.inf else np.exp(maximum-new_maximum)
                mass=np.exp(scores-new_maximum)
                numerator=scale*numerator+mass@values
                denominator=scale*denominator+mass.sum()
            if not np.isfinite(numerator).all() or not np.isfinite(denominator) or denominator<=0:
                raise ValueError('finite online attention accumulators required')
            maximum=new_maximum
        with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
            output=numerator/denominator
        if not np.isfinite(output).all(): raise ValueError('finite online attention output required')
        outputs.append(output)
    return np.stack(outputs),peak
""",
    links="[MQA](https://arxiv.org/abs/1911.02150), [FlashAttention](https://arxiv.org/abs/2205.14135), [Online softmax normalizer](https://arxiv.org/abs/1805.02867).",
)
expert(
    47,
    """A mixture-of-experts layer routes each token to a subset of specialized transformations. The total model can contain many expert parameters while activating only a few pertoken. That does not make memory orcommunication free:all experts must be stored somewhere,and distributed routing moves token activations to the devices owning selected experts. Uneven routing can overload one expert while others remain idle.

The router produces scores orprobabilities overexperts. A top-k decision selects indices,then a declared gate rule weights the selected outputs. Some designs retain selected probabilities from thefullsoftmax;others renormalize among selected experts. Those choices change gradients andoutput scale. This lesson states its rule explicitly:the top-k mixture renormalizes selected mass,while thecapacity demonstration uses a unit-weight top1 expert delta inside a residual path.

Capacity bounds how many tokens anexpert accepts inonebatch. Overflow needs a visible policy,such asdropping theexpert delta andusing the residual path. A load-balancing auxiliary objective can encourage lessconcentrated routing,butit doesnot prove that a system achieves good load balance,quality orthroughput. The reference uses literal linear experts andfinite-difference router gradients;it doesnot launch expert-parallel workers orclaim large-model scaling.""",
    """Inputs have shape(tokens,model_width),routerlogits(tokens,experts),andexpertmatrices(experts,model_width,output_width). Stable descending argsort declares a lowest-index tie policy. The selected gates are normalized before combining expert outputs. Thecapacity helper tracks assignedcounts,acceptedcounts anddropped-token flags separately. A Switch-style auxiliary term uses hard assignment fractionsf andmean router probabilitiesP,with thehard fractions heldfixed for a local gradient calculation.""",
    [
        ("Sparse expert activation", "Evaluating only selected experts for each token."),
        ("Router", "A function producing expert-selection scores for each token."),
        ("Capacity", "A bound on tokens admitted to anexpert inonebatch."),
        (
            "Load-balancing loss",
            "An auxiliary objective encouraging a lessconcentrated routing distribution.",
        ),
        (
            "Expert parallelism",
            "Placing different experts on different devices andmoving activations between them.",
        ),
    ],
    [
        ex(
            "Calculate a top2 expert mixture",
            "Use experts I,2I,-I and three token/router rows with selected probabilities 3/4 and 1/4.",
            "outputs[1.25,0],[0,1.75],[-.25,-.25].",
            """x=np.array([[1.,0.],[0.,1.],[1.,1.]])
experts=np.stack([np.eye(2),2*np.eye(2),-np.eye(2)])
logits=np.array([[np.log(3),0.,-100.],[0.,np.log(3),-100.],[-100.,0.,np.log(3)]])
output,indices,gates=mixture(x,logits,experts,2)
np.testing.assert_allclose(output,[[1.25,0],[0,1.75],[-.25,-.25]],atol=1e-12,rtol=0)
np.testing.assert_allclose(gates.sum(1),1,atol=1e-12,rtol=0)""",
            "The third token combines a negative expert with a positive expert,so routing can change the function rather than merely selecting a faster implementation of the same computation.",
        ),
        ex(
            "Enforce expert capacity with residual fallback",
            "Route four tokens to experts0,0,1,0 with capacity2 and unit top1 gates.",
            "assigned counts 3,1;accepted2,1;last token drops its expert delta and keeps its input.",
            """tokens=np.array([[1.,0.],[0.,1.],[1.,1.],[2.,1.]])
route_logits=np.array([[5.,0.],[4.,0.],[0.,4.],[3.,0.]])
residual,dropped,assigned,accepted=capacity_route(tokens,route_logits,experts[:2],2)
assert assigned.tolist()==[3,1] and accepted.tolist()==[2,1] and dropped.tolist()==[False,False,False,True]
np.testing.assert_allclose(residual,[[2,0],[0,2],[3,3],[2,1]],atol=1e-12,rtol=0)""",
            "The dropped token is not deleted from the sequence or loss denominator. Its residual path is explicit,and the drop count remains available for quality and load analysis.",
        ),
        ex(
            "Compute a load-balancing term",
            "Use hard fractions f[.75,.25],mean routerprobabilitiesP[.7,.3],expert count 2 and coefficient .01.",
            "auxiliary loss .012;balanced fixture .01.",
            """fractions=np.array([.75,.25]); mean_probability=np.array([.7,.3]); coefficient=.01
loss=coefficient*2*np.dot(fractions,mean_probability)
np.testing.assert_allclose(loss,.012,atol=1e-12,rtol=0)
np.testing.assert_allclose(coefficient*2*np.dot([.5,.5],[.5,.5]),.01,atol=1e-12,rtol=0)""",
            "The term measures a routing-related objective under the declared formula. A lower auxiliary value is not itself evidence that task loss,capacity drops or distributed utilization improved.",
        ),
        ex(
            "Trace a local router gradient",
            "Perturb the first logit of the first top-2 mixture row without changing selected experts.",
            "derivative of first output coordinate is -3/16 within1e-8.",
            """h=1e-6; plus=logits.copy(); minus=logits.copy(); plus[0,0]+=h; minus[0,0]-=h
numeric=(mixture(x,plus,experts,2)[0][0,0]-mixture(x,minus,experts,2)[0][0,0])/(2*h)
np.testing.assert_allclose(numeric,-3/16,atol=1e-8,rtol=0)""",
            "Within a fixedselectedset,the normalized gates vary smoothly. At a top-k membership boundary,the hard index choice is not differentiable in the same way. Do not interpret this local derivative as differentiating through every routing decision.",
        ),
        ex(
            "Separate total and active parameter counts",
            "Use 8 two-layer experts with width64,hidden128 and top-2 activation,excluding router and biases.",
            "total 131072 expert weights;32768selectedexpertweights per token.",
            """expert_count,width,hidden,active=8,64,128,2
assert expert_count*2*width*hidden==131072
assert active*2*width*hidden==32768""",
            "Inactive expert weights still occupy memory somewhere. Active-weight arithmetic does not measure peak memory,token dispatch cost orall-to-all communication.",
        ),
        ex(
            "Validate routing policy and ties",
            "Reject top-k 0 and capacity0;check equal router logits choose lower indices deterministically.",
            "invalid policies raise ValueError;top-2 tie indices 0,1.",
            """_,tied,_=mixture(np.ones((1,2)),np.zeros((1,3)),experts,2); assert tied.tolist()==[[0,1]]
for action in [lambda:mixture(x,logits,experts,0),lambda:capacity_route(tokens,route_logits,experts[:2],0)]:
    try: action()
    except ValueError: pass
    else: raise AssertionError('invalid routing policy accepted')""",
            "Tie and overflow policies affect reproducibility and which tokens receive expert computation. They must be explicit before comparing model quality or load statistics.",
        ),
    ],
    ("Switch Transformers", "https://arxiv.org/abs/2101.03961"),
    r"""For tokenx_t,router probabilities arep_t=softmax(z_t). LetS_t bethetop-kexpert set. Thisreference usesg_ti=p_ti/sum_(j in S_t)p_tj fori inS_t andzerootherwise,theny_t=sum_i g_ti E_i(x_t). Thisrenormalizedgatepolicy isnotidentical toretaining theoriginalselected probabilities.

For a fixedselectedset,the derivative of aweightedscalar expertoutputy withrespecttorouterlogitz_j isg_j*(e_j-y). Withselectedexpertoutputs1 and2 andgates3/4,1/4,wehavey=5/4 anddy/dz_0=(3/4)*(1-5/4)=-3/16. Hardchanges intop-kmembership requireseparate reasoning.

A Switch-style auxiliary term isL_aux=alpha*N*sum_i f_i P_i,wheref_i isthefractionofhardassignments toexperti andP_i isthemeanrouterprobability. Thehardfraction vector isnotdifferentiable;theprobability vector is. ForTtokens andfixedf,thelocal derivative isalpha*N/T * p_tj * (f_j-sum_i f_i p_ti). Theexamplecoefficient.01 is a declaredfixture choice,not a universal setting.

ForEexperts eachwithtwo bias-freelinear matricesD-by-H andH-by-D,totalexpertweightsare2EDH. Top-k activatesk experts pertoken,butstorageandcommunicationdependonhowallEexperts areplacedandserved.""",
    """A batch routes75percent ofits tokens tooneoftwoexperts. Capacityallows onlyhalfthebatch perexpert,so someexpert deltas aredropped despite lowaverage deviceutilization. Reporting only “two active experts pertoken” hides thebottleneck. A useful trace records pre-capacity assignments,acceptedcounts,drops andtaskerrors foraffectedtokens. Increasingcapacitymayreduce dropswhileincreasingactivationmemory. Changingrouterregularizationmayimprovebalancewhilealteringtaskquality. Those are measurable tradeoffs,not consequencesofparametercountalone.""",
    """Use sparse experts when thearchitecture,training andserving stack can supportconditional computation anditsrouting overhead. Measure tokenload distributions andtail behavior,not justmeanexpert utilization. Keep capacity,tie handling,gate normalization andoverflowpolicy in theartifact contract.

Do not claim that a model withmanytotalparameters has thecompute cost ofa small densemodel without accounting forrouter work,expert shapes,communication andbatching. ThisCPUreference executes small matrices locally anddoesnotverify distributed dispatch,network bandwidth orhardware throughput. A realexpert-parallel acceptance test needs those measurements andfailure/straggler behavior separately.""",
    helper="""def softmax_rows(logits):
    logits=np.asarray(logits,dtype=float)
    if logits.ndim!=2 or not logits.shape[1] or not np.isfinite(logits).all(): raise ValueError('finite router matrix required')
    mass=np.exp(logits-logits.max(1,keepdims=True)); return mass/mass.sum(1,keepdims=True)
def mixture(x,logits,experts,k):
    x,logits,experts=(np.asarray(value,dtype=float) for value in (x,logits,experts))
    if x.ndim!=2 or logits.ndim!=2 or experts.ndim!=3 or len(x)!=len(logits) or logits.shape[1]!=len(experts) or x.shape[1]!=experts.shape[1] or type(k) is not int or not 1<=k<=len(experts): raise ValueError('expert shapes and top-k required')
    probabilities=softmax_rows(logits); indices=np.argsort(-logits,axis=1,kind='stable')[:,:k]; selected=np.take_along_axis(probabilities,indices,axis=1); gates=selected/selected.sum(1,keepdims=True)
    output=np.zeros((len(x),experts.shape[2]))
    for row in range(len(x)):
        for slot,expert in enumerate(indices[row]): output[row]+=gates[row,slot]*(x[row]@experts[expert])
    return output,indices,gates
def capacity_route(x,logits,experts,capacity):
    x,logits,experts=(np.asarray(value,dtype=float) for value in (x,logits,experts))
    if type(capacity) is not int or capacity<=0 or experts.shape[1:]!=(x.shape[1],x.shape[1]) or logits.shape!=(len(x),len(experts)): raise ValueError('positive capacity and square expert shapes required')
    chosen=np.argmax(logits,axis=1); assigned=np.bincount(chosen,minlength=len(experts)); accepted=np.zeros(len(experts),dtype=int); dropped=np.zeros(len(x),dtype=bool); output=x.copy()
    for row,expert in enumerate(chosen):
        if accepted[expert]>=capacity: dropped[row]=True; continue
        output[row]+=x[row]@experts[expert]; accepted[expert]+=1
    return output,dropped,assigned,accepted
""",
    links="[GShard and expert parallelism](https://arxiv.org/abs/2006.16668), [ST-MoE training considerations](https://arxiv.org/abs/2202.08906).",
)
expert(
    48,
    """Speculative decoding proposes several tokens with a cheaper draft model andverifies them against a target model. Exact speculative sampling is not simply accepting a token when thetwo argmaxes agree. The acceptance rule andthe correction distribution are chosen so the emitted token law remains thetarget distribution under thedeclared sampling policy. This preserves a distribution,not necessarily the same individual sample produced by another random-number schedule.

For targetprobabilitiesp anddraftprobabilitiesq at thesameprefix,adrafttokeni isaccepted withprobabilitymin(1,p_i/q_i). Ifrejected,sample fromthenormalized positive part ofp-q. Accepted draftmass andcorrected rejectionmass add back topexactly. The distributions mustalready include theintended temperature orfiltering policy,andboth models mustrefer tothesame token identities.

A multi-token round accepts a contiguous prefix ofdraftproposals. At thefirstrejection,discard theunaccepted suffix andemit one correction token. Ifallproposals areaccepted,an additional token can be drawn fromthetarget\'s next distribution when thebudget permits. Cachedkeys/values fordiscarded draftpositions mustbe rolled back,andthe correction orbonus token mustbe appended at its correctposition. The reference uses exact probability tables andreal small NumPyK/Varrays. Itdoesnotrun a fastservingkernel orclaim a measuredspeedup.""",
    """Validate finite nonnegative probability vectors withunitmass. Sample using anexplicit draw in[0,1),with half-open cumulative intervals. Compute acceptance ratios only whereq ispositive;azero-qtoken cannotbe avaliddraftsample. The round helper stores thedraft distributions at theirproposal prefixes,then verifies in order andstops at thefirstrejection oracceptedEOS. A TinyCache stores position-dependentkeyvectors andvaluevectors so rollback canbe checked against a fresh reconstruction.""",
    [
        (
            "Draft distribution",
            "The proposal model's next-token probabilities at a specific prefix.",
        ),
        ("Acceptance probability", "The correction rulemin(1,p_i/q_i) for a sampled draft token."),
        ("Residual distribution", "Normalized positive mass fromp-q used after rejection."),
        ("Bonus token", "A target-sampled next token after an entirely accepted proposal block."),
        (
            "Cache rollback",
            "Removing state for unaccepted speculative positions before continuing.",
        ),
    ],
    [
        ex(
            "Prove one-step distribution preservation",
            "Use p[.5,.3,.2] and q[.2,.5,.3];calculate accepted mass,rejection mass and residual.",
            "accepted mass[.2,.3,.2];rejection .3;residual[1,0,0];combined mass p.",
            """p=np.array([.5,.3,.2]); q=np.array([.2,.5,.3]); acceptance,residual,rejection=correction(p,q)
accepted_mass=q*acceptance
np.testing.assert_allclose(accepted_mass,[.2,.3,.2],atol=1e-12,rtol=0)
np.testing.assert_allclose(rejection,.3,atol=1e-12,rtol=0); np.testing.assert_allclose(residual,[1,0,0],atol=1e-12,rtol=0)
np.testing.assert_allclose(accepted_mass+rejection*residual,p,atol=1e-12,rtol=0)""",
            "The equality is an exact probability decomposition up to floating-point arithmetic. It is stronger than observing approximate frequencies in a finite simulation.",
        ),
        ex(
            "Exercise acceptance and correction paths",
            "Propose token 1 with acceptance draw .8,then token 2 with draw .5.",
            "token 1 rejected and corrected to 0;token 2 accepted.",
            """rejected=one_step(p,q,1,.8,.9); accepted=one_step(p,q,2,.5,.1)
assert rejected=={'token':0,'accepted':False} and accepted=={'token':2,'accepted':True}""",
            "For token 1,the acceptance threshold is.3/.5=.6. For token 2,it is.2/.3=2/3. The supplied draws make both branches deterministic and inspectable.",
        ),
        ex(
            "Check an all-accepted round and bonus token",
            "Set draft and target equal top;propose tokens0,1 with draws .1,.6,and use bonus draw .7.",
            "emitted[0,1,1];accepted_count2;no rejection.",
            """same=lambda prefix:p
all_accepted=speculative_round([],same,same,[.1,.6],[.9,.9],.7,budget=3)
assert all_accepted['tokens']==[0,1,1] and all_accepted['accepted_count']==2 and not all_accepted['rejected']""",
            "Whenthemodelsagree,acceptance isone. Thethirdtokencomesfromthetargetdistributionaftertheacceptedprefix,not from aresidual thathaszeromass.",
        ),
        ex(
            "Stop at the first rejection",
            "Use constant target p,draft q,proposal draws .1,.3 and acceptance draws .2,.9.",
            "draft[0,1];accepted prefix[0];correction 0;emitted[0,0].",
            """round_result=speculative_round([2],lambda prefix:p,lambda prefix:q,[.1,.3],[.2,.9],.4,budget=3)
assert round_result['proposals']==[0,1] and round_result['tokens']==[0,0] and round_result['accepted_count']==1 and round_result['rejected']""",
            "Theunacceptedtoken1andsuffixcannotremainin the output prefix. Any future target probability must condition on theacceptedtoken0 andcorrection0 instead.",
        ),
        ex(
            "Rollback actual K/V arrays",
            "Start cache prefix[2],append the two proposals,then roll back and append the correction;compare with a fresh cache[2,0,0].",
            "tokens,keys,values andattentionoutputmatch;keepingrejectedtokenbreaks parity.",
            """cache=TinyCache([2]); old_length=len(cache.tokens)
for token in round_result['proposals']: cache.append(token)
broken=TinyCache(cache.tokens)
apply_round(cache,old_length,round_result); fresh=TinyCache([2,0,0])
assert cache.tokens==fresh.tokens; np.testing.assert_allclose(cache.keys,fresh.keys,atol=0,rtol=0); np.testing.assert_allclose(cache.output(),fresh.output(),atol=1e-12,rtol=0)
broken.append(0); assert broken.tokens!=fresh.tokens and not np.allclose(broken.output(),fresh.output())""",
            "The cache stores numerical position-dependentkeys,not only a token list. Retaining a rejected suffix changes both context and position offsets even if the next sampled token is correct.",
        ),
        ex(
            "Handle equality, EOS, budgets and invalid support",
            "Check p=q has no residual,stoponanacceptedEOS2,capoutputat2tokens,and reject a zero-probability draft proposal.",
            "rejectionmass0,residualNone;EOS stops;cap respected;invalidproposalraisesValueError.",
            """alpha,none,mass=correction(p,p); assert mass==0 and none is None and np.all(alpha==1)
eos=speculative_round([],same,same,[.95,.1],[.2,.2],.1,budget=3,eos=2); assert eos['tokens']==[2]
limited=speculative_round([],same,same,[.1,.6],[.9,.9],.7,budget=2); assert len(limited['tokens'])==2
try: one_step(np.array([.5,.5]),np.array([1.,0.]),1,.2,.3)
except ValueError: pass
else: raise AssertionError('impossible draft token accepted')""",
            "An accepted EOS ends generation immediately,andabudget is not permission to append an extra bonus. Equal distributions must avoid dividingbyazero residual normalizer. Invalidsupport should fail clearly rather than fabricate a probability.",
        ),
    ],
    ("Exact speculative decoding", "https://arxiv.org/abs/2211.17192"),
    r"""At one fixedprefix,letdraft tokenX~q. Itsacceptedmass at tokeni isq_i*min(1,p_i/q_i)=min(p_i,q_i). DefineR=1-sum_i min(p_i,q_i). Becauseboth distributions sumtoone,R=sum_i max(p_i-q_i,0). ForR>0,the correctiondistribution isr_i=max(p_i-q_i,0)/R. Therefore

\[
P(\text{emitted}=i)=\min(p_i,q_i)+Rr_i=p_i.
\]

Forp=(.5,.3,.2) andq=(.2,.5,.3),acceptedmass is(.2,.3,.2),R=.3,andr=(1,0,0). A naïve rejection fallback sampling directly fromp wouldinstead produceacceptedmass+R*p=(.35,.39,.26),which isnotp. The residual correction isessential.

For a block ofgamma proposals,eachq_i andp_i mustrefer to theprefix containing theprevious accepted proposals. Verification stops at thefirstrejection. Thetarget can evaluate causal logits for theproposedblock inone appropriatelybatched forwardpass,butthisreference evaluates tinyprobability tables individually forclarity. Afterallgammaacceptances,theextra tokenusesp_(gamma+1),not aresidual. Exactness assumes thedeclared targetdistribution,tokenization andsampling transformations areconsistent;finiteprecision andimplementation bugs stillneed testing.""",
    """A decoder\'s sampled token histogram looks close to thetarget,butmulti-round generation diverges after arejection. Theacceptance formula iscorrect. Thetargetcache stillcontains the rejectedproposal andone laterdrafttoken,so the nextquery uses a differentprefix andwrongposition. Rebuilding a freshcache fromthecommittedtokens exposes thedifference immediately. Thefix rolls both draft andtargetcaches backto old_prefix_length+accepted_count,then processes the correction token through eachmodel\'s ownprojection. Sharing rawK/Vbetween differentmodels would be another invalidshortcut.""",
    """Use speculative decoding when a cheaperdraft model achieves enoughagreement withthetarget andthe servingstack can exploitparallel verification. Measure acceptance length,draft cost,targetverification cost,cachework,batch effects andend-to-end latency. A highacceptance rate alone doesnotprove aspeedup ifdraft orcoordination overhead dominates.

Do notreplace theexact correction rulewithargmax agreement orsample-from-target fallback whileclaiming distribution preservation. Keep token vocabularies andeffective sampling policies aligned. Exactdistribution preservation doesnotmean identical randomsamples undera differentRNGschedule. ThisCPUreference establishes algebra andcache-state behavior only;itdoesnotmeasure GPUkernels,distributed serving orproductionquality.""",
    helper="""def probabilities(value):
    value=np.asarray(value,dtype=np.float64)
    if value.ndim!=1 or not len(value) or not np.isfinite(value).all() or (value<0).any() or not np.isclose(value.sum(),1,rtol=0,atol=1e-12): raise ValueError('finite nonnegative unit probability vector required')
    return value/value.sum()
def draw(probability,uniform):
    probability=probabilities(probability)
    if not np.isfinite(uniform) or not 0<=uniform<1: raise ValueError('draw must be in [0,1)')
    support=np.flatnonzero(probability>0)
    cumulative=np.minimum(np.cumsum(probability[support]),1.)
    cumulative[-1]=1.
    selected=np.searchsorted(cumulative,uniform,side='right')
    return int(support[selected])
def correction(p,q):
    p,q=probabilities(p),probabilities(q)
    if p.shape!=q.shape: raise ValueError('matching vocabulary required')
    ratio=np.divide(p,q,out=np.zeros_like(p),where=q>0); acceptance=np.minimum(1.,ratio)
    positive=np.maximum(p-q,0.); rejection=float(positive.sum())
    return acceptance,None if rejection==0 else positive/rejection,rejection
def one_step(p,q,token,acceptance_draw,residual_draw):
    p,q=probabilities(p),probabilities(q)
    if p.shape!=q.shape or type(token) is not int or not 0<=token<len(q) or q[token]<=0: raise ValueError('token must have draft support')
    if not 0<=acceptance_draw<1: raise ValueError('acceptance draw in [0,1) required')
    acceptance,residual,rejection=correction(p,q)
    if acceptance_draw<acceptance[token]: return {'token':token,'accepted':True}
    if residual is None: raise ValueError('rejection impossible for equal distributions')
    return {'token':draw(residual,residual_draw),'accepted':False}
def speculative_round(prefix,target,draft,draft_draws,acceptance_draws,extra_draw,budget,eos=None):
    if type(budget) is not int or budget<=0 or not draft_draws: raise ValueError('positive budget and proposals required')
    proposals=[]; distributions=[]
    for uniform in draft_draws[:budget]:
        distribution=probabilities(draft(list(prefix)+proposals)); token=draw(distribution,uniform); distributions.append(distribution); proposals.append(token)
        if token==eos: break
    if len(acceptance_draws)<len(proposals): raise ValueError('one acceptance draw per proposal required')
    accepted=[]
    for index,token in enumerate(proposals):
        p=probabilities(target(list(prefix)+accepted)); result=one_step(p,distributions[index],token,acceptance_draws[index],extra_draw)
        if not result['accepted']: return {'tokens':accepted+[result['token']],'accepted_count':len(accepted),'rejected':True,'proposals':proposals}
        accepted.append(token)
        if token==eos: return {'tokens':accepted,'accepted_count':len(accepted),'rejected':False,'proposals':proposals}
    count=len(accepted)
    if count<budget: accepted.append(draw(target(list(prefix)+accepted),extra_draw))
    return {'tokens':accepted,'accepted_count':count,'rejected':False,'proposals':proposals}
class TinyCache:
    table=np.array([[1.,0.],[0.,1.],[1.,1.]])
    def __init__(self,tokens):
        self.tokens=[]; self.keys=np.empty((0,2)); self.values=np.empty((0,2))
        for token in tokens: self.append(token)
    def append(self,token):
        if type(token) is not int or not 0<=token<len(self.table): raise ValueError('token outside fixture vocabulary')
        position=len(self.tokens); value=self.table[token]; key=value+position*np.array([.2,-.1]); self.tokens.append(token); self.keys=np.vstack([self.keys,key]); self.values=np.vstack([self.values,value])
    def truncate(self,length):
        if type(length) is not int or not 0<=length<=len(self.tokens): raise ValueError('invalid cache rollback length')
        self.tokens=self.tokens[:length]; self.keys=self.keys[:length].copy(); self.values=self.values[:length].copy()
    def output(self):
        if not self.tokens: raise ValueError('nonempty cache required')
        score=self.keys@self.keys[-1]/np.sqrt(2); mass=np.exp(score-score.max()); return mass/mass.sum()@self.values
def apply_round(cache,old_length,result):
    cache.truncate(old_length+result['accepted_count'])
    for token in result['tokens'][result['accepted_count']:]: cache.append(token)
""",
    links="[Speculative sampling independently developed byChen etal.](https://arxiv.org/abs/2302.01318).",
)

# Editorial pass: keep equations and their surrounding prose independently readable.
SPECS["llm-043"][
    "derivation"
] = r"""Let Q have shape(Tq,d), K shape(Tk,d), and V shape(Tk,dv), where d is the positive shared query/key feature width and dv is the value feature width. Scores are \(S=\frac{QK^{\mathsf T}}{\sqrt{d}}\), so the score matrix is Tq by Tk. For each query i, A_i is its nonempty allowed key set and m_i=max_(j in A_i) S_ij is the maximum allowed score. Normalize only that allowed set:

\[
A_{ij}=\frac{\exp(S_{ij}-m_i)}{\sum_{k\in\mathcal A_i}\exp(S_{ik}-m_i)},\qquad O_i=\sum_{j\in\mathcal A_i}A_{ij}V_j.
\]

Encoder self-attention can use every nonpadding source index. Decoder self-attention uses j<=i under the shifted-target convention. Cross-attention uses target queries and source keys, so its mask need not be square. Output row count follows Tq; output feature width follows V.

An autoregressive objective factors p(y|x) into the product over t of p(y_t|x,y_<t). A masked-source objective instead sums losses over a selected set of corrupted source positions. These objectives expose different conditioning information and supervise different events. Teacher forcing supplies previous target tokens, not the current answer, to the position predicting that answer. The loss mask identifies supervised events; the attention mask identifies accessible context. They must not be substituted for each other."""
SPECS["llm-044"]["derivation"] = r"""For one feature pair, define the rotation

\[
R(\theta)=\begin{bmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{bmatrix}.
\]

The identity R(m)^T R(n)=R(n-m) gives dot(R(m)q,R(n)k)=dot(q,R(n-m)k). Absolute rotations therefore introduce a relative-position dependence into the query-key dot product. This identity holds separately in each paired feature subspace.

For head width d and pair index i, this fixture uses omega_i=base^(-2i/d), so position p contributes angle p*omega_i. With d=4 and base=10000, the two frequencies are 1 and .01. Different implementations may pair feature coordinates differently; a layout translation is required before copying weights or caches.

For a causal ALiBi head with positive slope a, the allowed score is q_i^T k_j/sqrt(d)-a*(i-j) for j<=i. Future positions still require a mask. With zero content scores, query position 2 and a=log(2), the unnormalized masses are 1/4, 1/2 and 1. Their normalized values are 1/7, 2/7 and 4/7. Without a causal mask, the distance expression could reward future positions, so a positional bias cannot serve as an access-control rule."""
SPECS["llm-045"][
    "derivation"
] = r"""For a feature vector x in R^d with unit gain, let r=sqrt(mean(x²)+epsilon) and y_i=x_i/r. Differentiating both numerator and denominator gives

\[
\frac{\partial y_i}{\partial x_j}=\frac{\delta_{ij}}{r}-\frac{x_i x_j}{d r^3}.
\]

A learned gain g_i multiplies row i of this Jacobian. RMSNorm does not subtract the feature mean, so adding a constant generally changes its output. LayerNorm first subtracts that mean and therefore removes the all-ones shift direction.

For a residual branch F and normalizer N, pre-norm is y=x+F(N(x)), with Jacobian I+J_F J_N. Post-norm is y=N(x+F(x)), with Jacobian J_N(I+J_F). Setting F=0 isolates the placement: the first Jacobian is I, while the second remains J_N. This local identity-path argument is not a complete theorem about every training configuration.

A bias-free plain feed-forward block phi(xW1)W2 has 2dh weights. SwiGLU, [SiLU(xWg) elementwise_mul(xWu)]Wd, has 3dh weights. Equal weight budgets therefore use gated hidden width two-thirds of the plain hidden width when dimensions permit. SiLU(g)=g*sigmoid(g), with derivative sigmoid(g)+g*sigmoid(g)*(1-sigmoid(g)). At g=0 this derivative is 1/2, which explains the scalar gate-gradient example."""
SPECS["llm-046"]["derivation"] = (
    "Let B be batch size, L cached token count, Hkv key/value head count, d head width and s bytes per entry. Raw key/value storage is 2*B*L*Hkv*d*s. Query heads do not multiply that storage a second time. With model width D and Hq query heads, the bias-free projection count is \\(N_{\\mathrm{proj}}=D(H_qd)+2D(H_{kv}d)+(H_qd)D\\).\n\nFor one query, maintain a running maximum m, denominator \\(\\ell=\\sum_j\\exp(s_j-m)\\), and numerator \\(n=\\sum_j\\exp(s_j-m)v_j\\) over the processed legal keys. When a new score block b arrives, define m_new=max(m,max(b)) and alpha=exp(m-m_new). Update both accumulated quantities:\n\n\\[\n\\ell_{new}=\\alpha\\ell+\\sum_j\\exp(b_j-m_{new}),\\quad\nn_{new}=\\alpha n+\\sum_j\\exp(b_j-m_{new})v_j.\n\\]\n\nThe final output is \\(o=n/\\ell\\). Both quantities now use the same reference maximum, so their ratio matches dense softmax attention up to floating-point rounding. Skipping a fully masked block is valid; accepting a query with no legal key is not valid under this lesson contract.\n\nThis recurrence supports tiled execution without retaining the whole score matrix. A fast GPU implementation additionally manages memory layout, synchronization, parallelism and backward recomputation. Those implementation and hardware properties are not measured by this NumPy reference."
)
SPECS["llm-047"]["derivation"] = (
    "For token x_t, let router probabilities p_t=softmax(z_t), and let S_t be its selected top-k expert set. This reference uses g_ti=p_ti/sum_(j in S_t)p_tj for selected experts and zero otherwise. The output is y_t=sum_i g_ti E_i(x_t). Retaining the original selected probabilities instead would define a different gate policy.\n\nWithin a fixed selected set, a scalar mixture has derivative dy/dz_j=g_j*(e_j-y). With expert outputs 1 and 2 and gates 3/4 and 1/4, y=5/4 and the first-logit derivative is (3/4)*(1-5/4)=-3/16. A change in top-k membership introduces a hard selection boundary, so this local derivative must not be described as differentiating every routing decision.\n\nA Switch-style auxiliary term is L_aux=alpha*N*sum_i f_i P_i. Here f_i is the fraction of hard assignments to expert i, and P_i is the mean router probability. The hard fraction vector is not differentiable; the probability vector is. For T tokens and fixed f, the derivative for one logit is \\(\\frac{\\partial L_{\\mathrm{aux}}}{\\partial z_{tj}}=\\frac{\\alpha N}{T}p_{tj}\\left(f_j-\\sum_i f_ip_{ti}\\right)\\). The coefficient .01 is a declared fixture setting.\n\nFor E experts with two bias-free matrices D-by-H and H-by-D, total expert weights are 2EDH. Top-k activates k experts per token, but storage and communication still depend on placement and serving of all E experts."
)
SPECS["llm-048"][
    "derivation"
] = r"""At one fixed prefix, sample a draft token X from q. Its accepted mass at token i is q_i*min(1,p_i/q_i)=min(p_i,q_i). Define R=1-sum_i min(p_i,q_i). Since both distributions sum to one, R=sum_i max(p_i-q_i,0). For R>0, use residual r_i=max(p_i-q_i,0)/R. Then

\[
P(\text{emitted}=i)=\min(p_i,q_i)+Rr_i=p_i.
\]

For p=(.5,.3,.2) and q=(.2,.5,.3), accepted mass is (.2,.3,.2), rejection mass is .3, and the residual is (1,0,0). Sampling directly from p after rejection would instead produce (.35,.39,.26), which is not p. The residual correction is essential.

For gamma proposals, every draft and target distribution must refer to the same accepted prefix at that position. Stop verification at the first rejection. If all gamma proposals are accepted, sample the extra token from the next target distribution, not from a zero-mass residual. The target can verify causal logits for a proposed block in an appropriately batched forward pass; this reference evaluates tiny probability tables individually for clarity.

Exactness concerns the declared target sampling distribution, including its temperature or filtering policy. It does not promise identical individual samples under a different random-number schedule. Numerical precision, vocabulary alignment, termination and cache state remain implementation contracts that require tests."""
case_studies = {
    43: "A study-summary assistant receives a complete report and generates a structured summary. An encoder-decoder may encode the entire report before target generation. If the product changes to live transcription, future source text is no longer available. Reusing unrestricted source attention would violate the streaming contract. The architecture name did not change; the input-availability assumption did. Perturb text that arrives later and test whether earlier published outputs depend on it under the intended serving policy.",
    44: "An incremental decoder passes short-prefix tests but diverges after cache reuse. Its weights are unchanged. Each new key was rotated at position zero instead of at the accumulated cache offset. Encoding the key at the correct position restores parity. A second failure rotates already-rotated cached keys again. These are state and layout errors, not evidence about long-context model quality. Resolve them before attempting an extrapolation study.",
    45: "A refactor replaces a plain feed-forward block with SwiGLU while retaining the hidden width. The feed-forward parameter count rises by50percent, so a quality difference cannot be attributed only to gating. Another refactor moves normalization across the residual addition while keeping the optimizer unchanged. The zero-branch Jacobian and equal-budget calculation separate these changes before a larger training comparison.",
    46: "A serving team reduces KV heads from eight to two and observes a fourfold reduction in raw cache bytes. That does not imply a fourfold end-to-end speedup: weight reads, other layers, batching and communication remain. Separately, a blockwise implementation fails after a block with a much larger score because it rescales the denominator but not the numerator. The extreme-score fixture exposes that algebraic error before a GPU benchmark is meaningful.",
    47: "A batch routes75percent of its tokens to one of two experts, but capacity allows only half the batch per expert. Some expert deltas are dropped despite low average device utilization. Record assigned counts, accepted counts, drops and task errors for affected tokens. Increasing capacity may reduce drops while increasing activation memory. Router regularization may improve balance while changing task quality. These are measured tradeoffs, not consequences of parameter counts alone.",
    48: "A decoder uses the correct acceptance formula but diverges after a rejection. Its target cache still contains the rejected proposal and a later draft token, so the next query sees the wrong prefix and position. Rebuilding a fresh cache from committed tokens exposes the error. Roll both model caches back to old_prefix_length+accepted_count, then process the correction token through each model independently. Raw K/V tensors from different models are not interchangeable.",
}
for number, text in case_studies.items():
    SPECS[f"llm-{number:03d}"]["case_study"] = text
SPECS["llm-045"]["exercises"][1]["expected"] = (
    "pre-norm Jacobian is identity; post-norm Jacobian annihilates a constant feature shift."
)
SPECS["llm-048"]["exercises"][2]["why"] = (
    "When draft and target distributions agree, every proposal is accepted. The extra token comes from the target distribution after the accepted prefix, not from a residual whose mass is zero."
)
SPECS["llm-048"]["exercises"][4]["expected"] = (
    "tokens, keys, values and attention output match a fresh cache; retaining a rejected token breaks parity."
)
SPECS["llm-048"]["exercises"][5]["expected"] = (
    "rejection mass is 0 and residual is None; accepted EOS stops generation; the token cap is respected; unsupported proposals raise ValueError."
)

# Final numeric-domain repairs: preserve finite support and refuse accumulator overflow.
SPECS["llm-046"]["anatomy"] += (
    "\n\nThe online implementation checks its weighted-value numerator and denominator after every block, then checks the divided output. It raises ValueError when these intermediates exceed finite floating-point range, even if another evaluation order could produce a representable final average. Finite inputs and scores alone do not guarantee a finite unnormalized numerator."
)
SPECS["llm-048"]["anatomy"] += (
    "\n\nSampling builds the cumulative distribution on positive-support entries only, then maps the selected index back to the original token ID. The final cumulative boundary is assigned to the last positive entry, so floating-point rounding cannot create a tail interval for a zero-probability token. Half-open interval behavior is retained at internal boundaries."
)
