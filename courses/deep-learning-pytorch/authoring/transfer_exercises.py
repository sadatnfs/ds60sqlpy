"""Transfer exercises that reuse each worked mechanism on new inputs.

The worked examples stay unchanged. Each lesson whose reference is not bound
to an immutable runtime receipt gets three new exercises here; they become
exercises 1-3 and the original exercises 4-6 follow. Every program builds its
own fixture from the lesson imports and helpers, so it can run after the
original exercises without depending on their mutated state.
"""

# Long lines preserve authored prose and exercise programs.
# ruff: noqa: E501

from render import ex

TRANSFER = {}
AUTHORED_VERIFY = {}


def transfer(lesson_id, *exercises):
    assert len(exercises) == 3, lesson_id
    TRANSFER[lesson_id] = list(exercises)


def written(exercise, verify):
    return dict(exercise, verify=verify)


transfer(
    "torch-001",
    written(
        ex(
            "Name the unit for grouped rows",
            "A table has six rows from three customers, two rows per customer, and the task predicts next month's spend for each customer. Name the prediction unit and the unit that must stay together in a split.",
            "prediction unit: one customer for the next month; split unit: customer, so 3 independent units rather than 6 rows.",
            """Rows: 6 (c1, c1, c2, c2, c3, c3)
Prediction unit: one customer-month forecast
Split unit: customer; both rows of a customer go to the same side
Independent units available: 3""",
            "The row count overstates the evidence when rows share an identity. Grouping the split by customer keeps one customer's history from appearing on both sides.",
        ),
        "Your worksheet names the customer as both the prediction and split unit and states the count 3; a split that places c1 rows on both sides is marked invalid.",
    ),
    written(
        ex(
            "Recompute a training-only baseline",
            "Use training targets 1, 3, 5 to predict a constant on holdout targets 7 and 9. Report the constant, the holdout residuals and the holdout MSE.",
            "constant 3; residuals 4 and 6; squared errors 16 and 36; MSE 26.",
            """Training mean=(1+3+5)/3=3
Holdout residuals (target minus prediction)=7-3, 9-3 = 4, 6
Squared errors=16, 36
MSE=52/2=26""",
            "The constant comes only from training targets. Using the holdout mean 8 would give MSE 1 but would make the holdout part of fitting.",
        ),
        "Your table shows the mean 3 computed from training targets only and the two squared errors summing to 52 over a denominator of 2; a version that uses the holdout mean 8 is labeled leaked.",
    ),
    written(
        ex(
            "Classify evidence for a generated fixture",
            "A notebook reports zero error for the rule y = 3x on points that were generated from y = 3x, and it contains no optimizer log. Classify what the zero error establishes.",
            "an analytic oracle consistent with the generator; no training evidence; no evidence about unseen data.",
            """Rule source: written by hand, identical to the generator
Observed error: 0 on generated points
Training evidence: absent (no initial state, updates or final state recorded)
Population evidence: absent (no independent sample)""",
            "Agreement between a rule and the process that generated its test points is an arithmetic check. A training claim needs a recorded optimizer run, and a population claim needs independent data.",
        ),
        "Your answer separates the three evidence types and names the missing optimizer record and missing independent sample as the two absent items.",
    ),
)
AUTHORED_VERIFY[("torch-001", "Audit selection leakage")] = (
    "Your timeline shows the holdout score influencing the learning-rate change and relabels that data as validation; the report names a new untouched set as the only valid final assessment."
)
AUTHORED_VERIFY[("torch-001", "Align a framework comparison")] = (
    "Your checklist names all six contracts (pairing, dtype, initial weight, reduction, rate and optimizer rule) and orders the comparisons forward loss, gradient, updated weight and new loss."
)
AUTHORED_VERIFY[("torch-001", "Bound the conclusion")] = (
    "Your report contains one sentence on what the CPU run checked and one listing unestablished properties, and contains no production-quality claim."
)

transfer(
    "torch-002",
    ex(
        "Predict a 3-by-2 layout",
        "Create a float32 CPU tensor from values 0..5 reshaped to (3, 2) and predict its stride before printing it.",
        "shape (3, 2), stride (2, 1), float32 on CPU.",
        """grid=torch.arange(6,dtype=torch.float32).reshape(3,2)
assert tuple(grid.shape)==(3,2) and grid.stride()==(2,1) and grid.dtype==torch.float32 and grid.device.type=='cpu'""",
        "A row-major (3, 2) layout moves two stored elements per row step and one per column step, so the stride is (2, 1) rather than the (3, 1) of the worked tensor.",
    ),
    ex(
        "Write through a column view",
        "Take column 1 of the (3, 2) tensor as a view, set its last entry to -7 and inspect the original tensor and the view's stride.",
        "`grid[2, 1]` becomes -7; the column view has stride (2,).",
        """column=grid[:,1]; column[2]=-7
assert grid[2,1].item()==-7 and column.stride()==(2,)""",
        "Basic slicing returns a view, so the write lands in the shared storage. The view steps two elements per entry because it skips the other column.",
    ),
    ex(
        "Separate contiguous from clone",
        "Call contiguous() and clone() on the already contiguous grid, then write 100 into the [0, 0] entry of the first result and -100 into the second.",
        "contiguous() returns the same storage, so `grid[0, 0]` becomes 100; the clone write leaves grid unchanged.",
        """same=grid.contiguous(); owned=grid.clone()
same[0,0]=100; owned[0,0]=-100
assert same.data_ptr()==grid.data_ptr() and grid[0,0].item()==100 and owned[0,0].item()==-100""",
        "contiguous() only guarantees a layout; for an already contiguous tensor it returns the tensor itself. clone() is the operation that promises independent storage.",
    ),
)

transfer(
    "torch-003",
    ex(
        "Compute a new affine output",
        "Set a 2-to-1 Linear layer's weight to [[2, -1]] and its bias to 0.5 in float64, then evaluate the rows [1, 1] and [0, 2].",
        "outputs [[1.5], [-1.5]] with shape (2, 1).",
        """small=nn.Linear(2,1,dtype=torch.float64)
with torch.no_grad(): small.weight.copy_(torch.tensor([[2.,-1.]],dtype=torch.float64)); small.bias.fill_(.5)
inputs=torch.tensor([[1.,1.],[0.,2.]],dtype=torch.float64); scored=small(inputs)
torch.testing.assert_close(scored,torch.tensor([[1.5],[-1.5]],dtype=torch.float64),atol=1e-12,rtol=0)""",
        "Each row is a dot product with the stored weight row plus the bias: 2-1+0.5 and 0-2+0.5.",
    ),
    ex(
        "Predict a parameter count",
        "Before creating it, predict the registered scalar count and the state_dict shapes of nn.Linear(4, 3), then check them.",
        "15 scalars: weight (3, 4) and bias (3,).",
        """wide=nn.Linear(4,3)
assert sum(p.numel() for p in wide.parameters())==15 and tuple(wide.weight.shape)==(3,4) and tuple(wide.bias.shape)==(3,)""",
        "The stored weight is (out, in), so 3 rows of 4 coefficients, plus one bias per output.",
    ),
    ex(
        "Rebuild the output by hand",
        "For the 2-to-1 layer, compute inputs @ weight.T + bias without calling the module and compare it with the module output.",
        "the manual result equals [[1.5], [-1.5]] within 1e-12.",
        """manual=inputs@small.weight.T+small.bias
torch.testing.assert_close(manual,scored,atol=1e-12,rtol=0)""",
        "Transposing the stored (out, in) weight gives the (in, out) matrix used in the mathematical form XW+b.",
    ),
)

transfer(
    "torch-004",
    ex(
        "Reduce a new residual vector",
        "Use residuals [3, 0, -1, 2] against zero targets and compute the sum and mean squared reductions.",
        "squared entries 9, 0, 1, 4; sum 14; mean 3.5.",
        """fresh=torch.tensor([3.,0.,-1.,2.],dtype=torch.float64); zeros=torch.zeros_like(fresh)
assert F.mse_loss(fresh,zeros,reduction='sum').item()==14 and F.mse_loss(fresh,zeros,reduction='mean').item()==3.5""",
        "The sum adds the four squares; the mean divides that sum by the four participating entries.",
    ),
    ex(
        "Predict the effect of an appended zero",
        "Append one zero residual to the same vector and recompute both reductions before running them.",
        "sum stays 14; mean falls to 2.8 because the denominator becomes 5.",
        """padded=torch.cat([fresh,torch.zeros(1,dtype=torch.float64)])
assert F.mse_loss(padded,torch.zeros_like(padded),reduction='sum').item()==14
np.testing.assert_allclose(F.mse_loss(padded,torch.zeros_like(padded),reduction='mean').item(),2.8,atol=1e-12,rtol=0)""",
        "A zero entry adds nothing to the numerator but still counts in the mean's denominator, which is why padding must be masked.",
    ),
    ex(
        "Compare gradient scale for four entries",
        "Differentiate the sum and the mean of squares for a fresh copy of [3, 0, -1, 2].",
        "sum gradient [6, 0, -2, 4]; it equals 4 times the mean gradient.",
        """c=fresh.clone().requires_grad_(); total_grad=torch.autograd.grad((c*c).sum(),c)[0]
d=fresh.clone().requires_grad_(); mean_grad=torch.autograd.grad((d*d).mean(),d)[0]
torch.testing.assert_close(total_grad,torch.tensor([6.,0.,-2.,4.],dtype=torch.float64),atol=1e-12,rtol=0)
torch.testing.assert_close(total_grad,4*mean_grad,atol=1e-12,rtol=0)""",
        "Each derivative of a square is 2r; the mean divides every component by the entry count 4.",
    ),
)

transfer(
    "torch-006",
    ex(
        "Trace the chain at a new point",
        "Use w=2, z=2*w, a=z*z and loss=(a-1)**2, and predict each intermediate value and dloss/dw.",
        "z = 4, a = 16, loss 225, gradient 480.",
        """w2=torch.tensor(2.,dtype=torch.float64,requires_grad=True); z2=2*w2; a2=z2*z2; loss2=(a2-1)**2
assert (z2.item(),a2.item(),loss2.item())==(4.,16.,225.) and torch.autograd.grad(loss2,w2)[0].item()==480""",
        "The local factors are 2(a-1)=30, 2z=8 and dz/dw=2, so the chain gives 30*8*2=480.",
    ),
    ex(
        "Check the new slope numerically",
        "Compare 480 with a central difference of ((2w)**2-1)**2 at w=2 using h=1e-5.",
        "the central difference agrees with 480 within 1e-6.",
        """step=1e-5; quartic=lambda value:((2*value)**2-1)**2
np.testing.assert_allclose((quartic(2+step)-quartic(2-step))/(2*step),480,atol=1e-6,rtol=0)""",
        "For this quartic the truncation error is about h**2 times the third derivative 768 divided by 6, far below the tolerance.",
    ),
    ex(
        "Update a leaf under no_grad",
        "Repeat the in-place add on a leaf that requires gradients, but inside torch.no_grad().",
        "the update succeeds; the value is 2 and the tensor is still a leaf that requires gradients.",
        """guarded=torch.tensor(1.,requires_grad=True)
with torch.no_grad(): guarded.add_(1)
assert guarded.item()==2 and guarded.requires_grad and guarded.is_leaf""",
        "Optimizers update parameters exactly this way: the mutation is not recorded in a graph, so autograd allows it.",
    ),
)

transfer(
    "torch-007",
    ex(
        "Predict a nonleaf gradient",
        "Create leaf v=1.0 and intermediate u=3v, retain u's gradient and backpropagate u*u.",
        "u.grad is 6 and v.grad is 18; u is not a leaf.",
        """v=torch.tensor(1.,requires_grad=True); u=3*v; u.retain_grad(); (u*u).backward()
assert v.grad.item()==18 and u.grad.item()==6 and not u.is_leaf""",
        "d(u*u)/du=2u=6, and the extra factor du/dv=3 gives 18 at the leaf.",
    ),
    ex(
        "Accumulate three backward calls",
        "At w=1, backpropagate (w-2)**2 three times without clearing the gradient.",
        "each call contributes -2, so the stored gradient is -6.",
        """p=torch.tensor(1.,requires_grad=True)
for _ in range(3): ((p-2)**2).backward()
assert p.grad.item()==-6""",
        "Backward adds into .grad; three fresh graphs each add 2(w-2)=-2.",
    ),
    ex(
        "Clear with zero_ and with None",
        "Clear the accumulated gradient with p.grad.zero_() and backpropagate once, then set it to None and backpropagate once more.",
        "both routes end at -2; after the None assignment the gradient is absent until the next backward.",
        """p.grad.zero_(); ((p-2)**2).backward(); assert p.grad.item()==-2
p.grad=None; assert p.grad is None; ((p-2)**2).backward(); assert p.grad.item()==-2""",
        "zero_ keeps an allocated zero tensor; None removes it, which lets a later check distinguish no gradient from a zero gradient.",
    ),
)

transfer(
    "torch-008",
    ex(
        "Compute a new initial loss",
        "Use float64 x = 1, 2, targets y = 3x and scalar w = 0, and calculate the mean squared loss.",
        "loss 22.5.",
        """xs=torch.tensor([1.,2.],dtype=torch.float64); ys=3*xs; ws=nn.Parameter(torch.tensor(0.,dtype=torch.float64))
objective=((ws*xs-ys)**2).mean(); np.testing.assert_allclose(objective.item(),22.5,atol=1e-12,rtol=0)""",
        "The residuals are -3 and -6, so the mean of 9 and 36 is 22.5.",
    ),
    ex(
        "Predict the gradient before stepping",
        "Backpropagate the new loss and compare the gradient with your hand calculation before any update.",
        "gradient -15; w still 0.",
        """objective.backward(); np.testing.assert_allclose(ws.grad.item(),-15,atol=1e-12,rtol=0)
assert ws.item()==0""",
        "The derivative is the mean of 2(wx-y)x, here the mean of -6 and -24.",
    ),
    ex(
        "Apply one step with a new rate",
        "Take one SGD step with learning rate 0.05 and recompute the loss.",
        "w = 0.75; loss 12.65625.",
        """sgd=torch.optim.SGD([ws],lr=.05); sgd.step()
np.testing.assert_allclose(ws.item(),.75,atol=1e-12,rtol=0)
np.testing.assert_allclose(((ws*xs-ys)**2).mean().item(),12.65625,atol=1e-12,rtol=0)""",
        "The step moves w by 0.05*15; the residual factor becomes 0.75-3=-2.25, and 2.25 squared times the mean of x squared (2.5) gives 12.65625.",
    ),
)

transfer(
    "torch-009",
    ex(
        "Partition with batch size 4",
        "Partition IDs 1..10 into batches of 4 without dropping the tail.",
        "batch sizes 4, 4, 2; the last batch is [9, 10].",
        """ten=list(range(1,11)); quads=[ten[i:i+4] for i in range(0,len(ten),4)]
assert [len(batch) for batch in quads]==[4,4,2] and quads[-1]==[9,10]""",
        "Ceil(10/4)=3 batches; only the last one is short.",
    ),
    ex(
        "Count updates with a dropped tail",
        "With 10 records, batch size 4 and the short tail dropped, count optimizer steps per epoch and over 3 epochs.",
        "2 steps per epoch and 6 in total; records 9 and 10 never contribute in unshuffled order.",
        """steps_per_epoch=len(ten)//4
assert steps_per_epoch==2 and 3*steps_per_epoch==6 and [i for batch in quads[:steps_per_epoch] for i in batch]==list(range(1,9))""",
        "Dropping the tail changes both the step count and which records are ever seen when the order is fixed.",
    ),
    ex(
        "Trace two single-record updates",
        "Train w from 0 on x = 1, 2 with y = 2x, batch size 1 and learning rate 0.1, clearing gradients before each step.",
        "weights 0.4 then 1.68.",
        """pair_x=torch.tensor([1.,2.],dtype=torch.float64); pair_y=2*pair_x; weight=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); opt=torch.optim.SGD([weight],lr=.1); trace=[]
for index in range(2):
    opt.zero_grad(set_to_none=True); ((weight*pair_x[index]-pair_y[index])**2).backward(); opt.step(); trace.append(weight.item())
np.testing.assert_allclose(trace,[.4,1.68],atol=1e-12,rtol=0)""",
        "The first gradient is 2(0-2)=-4; the second, at w=0.4, is 2(0.8-4)*2=-12.8.",
    ),
)

transfer(
    "torch-010",
    ex(
        "Inspect a different record",
        "Read item 5 of the literal Accounts dataset.",
        "ID 5, group C, value 22.",
        """record=Accounts()[5]
assert record[0]==5 and record[1]=='C' and record[2].item()==22""",
        "The dataset returns the original index with the group label, so downstream code can audit identities.",
    ),
    ex(
        "Hold out a different pair of groups",
        "Train on groups A and C and hold out B and D with Subset; check the group sets and the training mean.",
        "disjoint group sets; training mean 11.5.",
        """pool=Accounts(); keep=[i for i in range(len(pool)) if pool[i][1] in {'A','C'}]; rest=[i for i in range(len(pool)) if i not in keep]
fit=torch.utils.data.Subset(pool,keep); held=torch.utils.data.Subset(pool,rest)
assert {row[1] for row in fit}=={'A','C'} and not {row[1] for row in fit}&{row[1] for row in held}
assert torch.stack([row[2] for row in fit]).mean().item()==11.5""",
        "The training values are 1, 3, 20 and 22. A different group choice changes the fitted statistic, which is why it must be fitted after the split.",
    ),
    ex(
        "Apply the new frozen transform",
        "Center the held-out values with the training mean 11.5.",
        "-6.5, -4.5, 18.5, 20.5.",
        """shifted_values=torch.stack([row[2] for row in held])-11.5
torch.testing.assert_close(shifted_values,torch.tensor([-6.5,-4.5,18.5,20.5],dtype=torch.float64),atol=0,rtol=0)""",
        "The held-out values 5, 7, 30 and 32 are transformed with the frozen training statistic, never with their own mean.",
    ),
)

transfer(
    "torch-011",
    ex(
        "Evaluate a module with a nonzero buffer",
        "Build ScalarModel, set its offset buffer to 1 under no_grad and evaluate x = 1, 2, 3.",
        "outputs [1, 1, 1]; offset is a buffer, not a parameter.",
        """shifted=ScalarModel()
with torch.no_grad(): shifted.offset.fill_(1.)
xs=torch.tensor([1.,2.,3.],dtype=torch.float64)
assert shifted(xs).tolist()==[1.,1.,1.] and 'offset' not in dict(shifted.named_parameters())""",
        "With weight 0 the forward pass returns only the buffer, which participates in computation without being optimized.",
    ),
    ex(
        "Predict one step with the offset present",
        "Train the shifted module one SGD step with learning rate 0.1 toward y = 2x using mean squared error.",
        "initial loss 35/3; new weight 22/15; offset still 1.",
        """optimizer2=torch.optim.SGD(shifted.parameters(),lr=.1); optimizer2.zero_grad(set_to_none=True)
loss2=((shifted(xs)-2*xs)**2).mean(); loss2.backward(); optimizer2.step()
np.testing.assert_allclose(loss2.item(),35/3,atol=1e-12,rtol=0)
np.testing.assert_allclose(shifted.weight.item(),22/15,atol=1e-12,rtol=0); assert shifted.offset.item()==1""",
        "The residuals are -1, -3 and -5. The weight gradient is the mean of 2rx, -44/3, so the step adds 4.4/3; the buffer is not in the optimizer.",
    ),
    ex(
        "Count state in a ModuleList",
        "Put two ScalarModel instances in nn.ModuleList and count parameters, buffers and state_dict keys.",
        "2 parameters, 2 buffers and keys 0.weight, 0.offset, 1.weight, 1.offset.",
        """pair=nn.ModuleList([ScalarModel(),ScalarModel()])
assert len(list(pair.parameters()))==2 and len(list(pair.buffers()))==2
assert set(pair.state_dict())=={'0.weight','0.offset','1.weight','1.offset'}""",
        "A registered container prefixes each child's state with its index, unlike a plain Python list.",
    ),
)

transfer(
    "torch-013",
    ex(
        "Convert new logits",
        "Apply sigmoid to the float64 logits -1, 1 and 3.",
        "probabilities about 0.2689, 0.7311 and 0.9526; the first two sum to 1.",
        """other=torch.tensor([-1.,1.,3.],dtype=torch.float64); converted=torch.sigmoid(other)
np.testing.assert_allclose(converted.tolist(),[1/(1+np.exp(1)),1/(1+np.exp(-1)),1/(1+np.exp(-3))],atol=1e-12,rtol=0)
np.testing.assert_allclose((converted[0]+converted[1]).item(),1,atol=1e-12,rtol=0)""",
        r"\(\sigma(-z)=1-\sigma(z)\), so opposite logits give complementary probabilities.",
    ),
    ex(
        "Compute a negative-label loss",
        "Compute BCEWithLogitsLoss for logit 2 with label 0.",
        r"loss \(\log(1+e^{2})\), about 2.1269, within 1e-12.",
        """negative=F.binary_cross_entropy_with_logits(torch.tensor([2.],dtype=torch.float64),torch.tensor([0.],dtype=torch.float64))
np.testing.assert_allclose(negative.item(),np.log1p(np.exp(2)),atol=1e-12,rtol=0)""",
        r"For label 0 the loss is \(-\log(1-\sigma(z))=\log(1+e^{z})\); a confident wrong score is penalized heavily.",
    ),
    ex(
        "Threshold the new probabilities",
        "Classify the new probabilities at thresholds 0.5 and 0.75, counting a probability equal to the threshold as positive.",
        "labels False, True, True versus False, False, True.",
        """assert (converted>=.5).tolist()==[False,True,True] and (converted>=.75).tolist()==[False,False,True]""",
        "0.7311 passes 0.5 but not 0.75, so the threshold is a policy choice applied after the model's probability.",
    ),
)

transfer(
    "torch-017",
    ex(
        "Compute penalties for a new vector",
        "Use weights 3, -4, 0 and compute the L1 and squared L2 sums.",
        "L1 = 7; squared L2 = 25.",
        """penalized=torch.tensor([3.,-4.,0.]); assert penalized.abs().sum().item()==7 and penalized.square().sum().item()==25""",
        "L1 adds absolute values; squared L2 adds squares, so the zero weight contributes to neither.",
    ),
    ex(
        "Predict train-mode values for p=0.25",
        "Apply Dropout(0.25) in train mode to a (3, 5) tensor of ones and inspect every value.",
        "shape (3, 5); each value is 0 or 4/3.",
        """quarter=nn.Dropout(.25); quarter.train(); kept=quarter(torch.ones((3,5)))
assert tuple(kept.shape)==(3,5) and all(value==0 or abs(value-4/3)<1e-6 for value in kept.flatten().tolist())""",
        "Retained activations are scaled by 1/(1-p) so the expected value stays 1; the exact retained pattern is random.",
    ),
    ex(
        "Confirm eval disables the new rate",
        "Switch the same Dropout(0.25) layer to eval mode and apply it to the ones tensor.",
        "output exactly equals the input.",
        """quarter.eval(); assert torch.equal(quarter(torch.ones((3,5))),torch.ones((3,5)))""",
        "Eval mode makes Dropout the identity regardless of p.",
    ),
)

transfer(
    "torch-018",
    ex(
        "Predict a running mean with momentum 0.25",
        "Apply a fresh BatchNorm1d(2, momentum=0.25) in train mode to rows [2, 4] and [6, 8].",
        "batch means [4, 6]; running mean [1, 1.5].",
        """quarter_bn=nn.BatchNorm1d(2,momentum=.25); quarter_bn.train(); quarter_bn(torch.tensor([[2.,4.],[6.,8.]]))
torch.testing.assert_close(quarter_bn.running_mean,torch.tensor([1.,1.5]),atol=1e-6,rtol=0)""",
        "PyTorch momentum weights the new statistic: 0.75*0+0.25*[4, 6].",
    ),
    ex(
        "Predict the running variance",
        "Inspect the same layer's running variance after that one update.",
        "running variance [2.75, 2.75].",
        """torch.testing.assert_close(quarter_bn.running_var,torch.tensor([2.75,2.75]),atol=1e-6,rtol=0)""",
        "Each column has unbiased variance 8, so the update is 0.75*1+0.25*8.",
    ),
    ex(
        "Normalize a new LayerNorm row",
        "Apply a default LayerNorm(3) to the row [1, 2, 3].",
        r"approximately [-1.2247, 0, 1.2247], equal to \([-1, 0, 1]/\sqrt{2/3+10^{-5}}\) within 1e-5.",
        """ln3=nn.LayerNorm(3); row=ln3(torch.tensor([[1.,2.,3.]]))
torch.testing.assert_close(row,torch.tensor([[-1.,0.,1.]])/(2/3+1e-5)**.5,atol=1e-5,rtol=0)""",
        "LayerNorm uses the row's own mean 2 and biased variance 2/3, plus epsilon, with default unit scale and zero shift.",
    ),
)

transfer(
    "torch-019",
    ex(
        "Apply a summing kernel",
        "Apply the 2-by-2 kernel of ones to the 3-by-3 image with values 1..9 in NCHW layout.",
        "outputs [[12, 16], [24, 28]] in shape (1, 1, 2, 2).",
        """ramp=torch.arange(1,10,dtype=torch.float64).reshape(1,1,3,3); ones_kernel=torch.ones((1,1,2,2),dtype=torch.float64)
summed=F.conv2d(ramp,ones_kernel)
assert summed.tolist()==[[[[12.,16.],[24.,28.]]]]""",
        "Each output adds one 2-by-2 window: 1+2+4+5, 2+3+5+6, 4+5+7+8 and 5+6+8+9.",
    ),
    ex(
        "Predict the shape with padding",
        "Repeat the summing kernel with padding=1 and predict the output shape and its top-left value.",
        "shape (1, 1, 4, 4); top-left value 1.",
        """padded_out=F.conv2d(ramp,ones_kernel,padding=1)
assert tuple(padded_out.shape)==(1,1,4,4) and padded_out[0,0,0,0].item()==1""",
        "The width becomes floor((3+2-2)/1)+1=4, and the corner window contains three padded zeros and the pixel 1.",
    ),
    ex(
        "Permute a two-channel image",
        "Stack the image and its negative as two channels, convert NCHW to NHWC and read the channel pair at row 0, column 2.",
        "NHWC shape (1, 3, 3, 2); the pair is [3, -3].",
        """two=torch.cat([ramp,-ramp],dim=1); channels_last=two.permute(0,2,3,1)
assert tuple(channels_last.shape)==(1,3,3,2) and channels_last[0,0,2].tolist()==[3.,-3.]""",
        "After the permutation the channel axis is last, so one spatial position holds both channel values.",
    ),
)

transfer(
    "torch-020",
    ex(
        "Pool a new patch",
        "Pool the patch [[5, -1], [2, 6]] with a 2-by-2 window.",
        "max 6; average 3.",
        """patch=torch.tensor([[[[5.,-1.],[2.,6.]]]])
assert F.max_pool2d(patch,2).item()==6 and F.avg_pool2d(patch,2).item()==3""",
        "Max keeps one response; average uses all four values, including the negative one.",
    ),
    ex(
        "Flip the height axis instead",
        "Flip the same patch along the height axis and read its rows.",
        "rows [2, 6] and [5, -1].",
        """vertical=torch.flip(patch,dims=(-2,)); assert vertical[0,0].tolist()==[[2.,6.],[5.,-1.]]""",
        "In NCHW layout dimension -2 is height, so the rows swap while each row keeps its order.",
    ),
    ex(
        "Pool a 4-by-4 map",
        "Apply 2-by-2 max and average pooling to the 4-by-4 map with values 0..15.",
        "max [[5, 7], [13, 15]]; average [[2.5, 4.5], [10.5, 12.5]].",
        """grid=torch.arange(16.).reshape(1,1,4,4)
assert F.max_pool2d(grid,2).tolist()==[[[[5.,7.],[13.,15.]]]] and F.avg_pool2d(grid,2).tolist()==[[[[2.5,4.5],[10.5,12.5]]]]""",
        "Each output summarizes one nonoverlapping window; the bottom-right window is 10, 11, 14, 15.",
    ),
)

transfer(
    "torch-021",
    ex(
        "Look up a short sequence",
        "With the same 4-by-2 table and padding_idx=0, look up IDs [[1, 0, 0]] and build the validity mask.",
        "values [[1, 0], [0, 0], [0, 0]]; mask [[True, False, False]].",
        """lookup_table=torch.tensor([[0.,0.],[1.,0.],[2.,2.],[3.,-1.]]); lookup=nn.Embedding.from_pretrained(lookup_table,freeze=False,padding_idx=0)
short_ids=torch.tensor([[1,0,0]]); short_values=lookup(short_ids)
assert short_values.tolist()==[[[1.,0.],[0.,0.],[0.,0.]]] and (short_ids!=0).tolist()==[[True,False,False]]""",
        "The two padding positions read the zero row; only the mask says they are not real tokens.",
    ),
    ex(
        "Count gradients for repeated IDs",
        "Look up IDs [[2, 2, 3]] in that embedding, sum the outputs and backpropagate.",
        "row 2 gradient [2, 2]; row 3 [1, 1]; rows 0 and 1 zero.",
        """lookup(torch.tensor([[2,2,3]])).sum().backward()
assert lookup.weight.grad.tolist()==[[0.,0.],[0.,0.],[2.,2.],[1.,1.]]""",
        "Each occurrence adds a gradient of ones to its row, so a repeated ID accumulates twice.",
    ),
    ex(
        "Pack a batch with two lengths",
        "Run a GRU(2, 2) whose parameters are all 0.1 on two padded sequences of lengths 2 and 1, packed, and compare each final state with its unpadded run.",
        "both final states match their unpadded runs within 1e-6.",
        """rnn=nn.GRU(2,2,batch_first=True)
with torch.no_grad():
    for weight in rnn.parameters(): weight.fill_(.1)
batch=torch.tensor([[[1.,0.],[2.,2.]],[[3.,-1.],[0.,0.]]]); packed_batch=nn.utils.rnn.pack_padded_sequence(batch,torch.tensor([2,1]),batch_first=True,enforce_sorted=False)
_,states=rnn(packed_batch); _,first=rnn(batch[:1,:2]); _,second=rnn(batch[1:,:1])
torch.testing.assert_close(states[:,0],first[:,0],atol=1e-6,rtol=0); torch.testing.assert_close(states[:,1],second[:,0],atol=1e-6,rtol=0)""",
        "Packing stops the second sequence after its one real step, so its final state ignores the padding row.",
    ),
)

transfer(
    "torch-022",
    ex(
        "Mix new values causally",
        "Use zero 3-by-2 queries and keys with values [4, 0], [0, 4], [1, 1] and a causal allowed mask.",
        "outputs [4, 0], [2, 2] and [5/3, 5/3].",
        """zq=torch.zeros((3,2),dtype=torch.float64); vv=torch.tensor([[4.,0.],[0.,4.],[1.,1.]],dtype=torch.float64); causal=torch.ones((3,3),dtype=torch.bool).tril()
torch.testing.assert_close(attention(zq,zq,vv,causal),torch.tensor([[4.,0.],[2.,2.],[5/3,5/3]],dtype=torch.float64),atol=1e-12,rtol=0)""",
        "Equal scores make each row the mean of its allowed values.",
    ),
    ex(
        "Predict a bidirectional change",
        "Allow every position (an all-True mask) and change only the third value to [10, 10].",
        "every row becomes [14/3, 14/3]; without a causal mask the change reaches all rows.",
        """full_mask=torch.ones((3,3),dtype=torch.bool); moved=vv.clone(); moved[2]=torch.tensor([10.,10.])
torch.testing.assert_close(attention(zq,zq,moved,full_mask),torch.full((3,2),14/3,dtype=torch.float64),atol=1e-12,rtol=0)""",
        "The mask, not the attention formula, decides whether later positions can influence earlier outputs.",
    ),
    ex(
        "Compute one nonuniform weight",
        "Use queries, keys and values equal to the 2-by-2 identity with a causal mask.",
        r"row 0 is [1, 0]; row 1 is [1-p, p] with \(p=\sigma(1/\sqrt{2})\), about 0.6698.",
        """qk=torch.eye(2,dtype=torch.float64); weight=1/(1+np.exp(-1/np.sqrt(2)))
result=attention(qk,qk,qk,torch.ones((2,2),dtype=torch.bool).tril())
torch.testing.assert_close(result,torch.tensor([[1.,0.],[1-weight,weight]],dtype=torch.float64),atol=1e-12,rtol=0)""",
        r"Row 1 compares scores 0 and \(1/\sqrt{2}\); a two-way softmax of a score difference is a sigmoid.",
    ),
)

transfer(
    "torch-023",
    ex(
        "Detect a detached intermediate",
        "With Parameter w=1, compute h=(3w).detach() and loss=(h-1)**2, then inspect tracking and attempt backward.",
        "loss.requires_grad is False and backward raises RuntimeError.",
        """wd=nn.Parameter(torch.tensor(1.,dtype=torch.float64)); hidden_value=(wd*3).detach(); cut=(hidden_value-1)**2
assert not cut.requires_grad
try: cut.backward()
except RuntimeError: pass
else: raise AssertionError('detached intermediate backpropagated')""",
        "Detaching any intermediate cuts every path from the loss to the parameter, not only the final step.",
    ),
    ex(
        "Trace two updates on a new target",
        "Train w from 0 on x = 1, 2, 3 with y = 3x, two SGD steps with learning rate 0.1, clearing gradients before each.",
        "weights 2.8 then 224/75.",
        """wt=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); xt=torch.tensor([1.,2.,3.],dtype=torch.float64); yt=3*xt; opt_t=torch.optim.SGD([wt],lr=.1); seen=[]
for _ in range(2):
    opt_t.zero_grad(set_to_none=True); ((wt*xt-yt)**2).mean().backward(); opt_t.step(); seen.append(wt.item())
np.testing.assert_allclose(seen,[2.8,224/75],atol=1e-12,rtol=0)""",
        "The error w-3 shrinks by the factor 1-0.1*28/3=1/15 per step: -3, -0.2, then -1/75.",
    ),
    ex(
        "Clip a new gradient",
        "Assign gradient [6, 8] to a parameter vector and clip it to norm 5.",
        "returned norm 10; clipped gradient approximately [3, 4].",
        """vector=nn.Parameter(torch.zeros(2)); vector.grad=torch.tensor([6.,8.])
norm=torch.nn.utils.clip_grad_norm_([vector],5.)
assert norm.item()==10; torch.testing.assert_close(vector.grad,torch.tensor([3.,4.]),atol=1e-5,rtol=0)""",
        "clip_grad_norm_ returns the norm before clipping and rescales by about 5/10, keeping the direction.",
    ),
)

transfer(
    "torch-024",
    ex(
        "Fit normalization on new training values",
        "Use training inputs 0, 2, 4, 6, compute the mean and population standard deviation, and transform the test input 8.",
        r"mean 3; scale \(\sqrt{5}\); transformed test value \(\sqrt{5}\), about 2.2361.",
        """fresh_x=torch.tensor([[0.],[2.],[4.],[6.]]); centre=fresh_x.mean(0); spread=fresh_x.std(0,correction=0)
assert centre.item()==3; np.testing.assert_allclose(spread.item(),np.sqrt(5),atol=1e-6,rtol=0)
np.testing.assert_allclose(((torch.tensor([[8.]])-centre)/spread).item(),np.sqrt(5),atol=1e-6,rtol=0)""",
        "The squared deviations 9, 1, 1, 9 average to 5; the test value uses the frozen training statistics.",
    ),
    ex(
        "Count a new confusion table",
        "Compare predictions True, False, True, True with truth True, False, False, True.",
        "TP 2, TN 1, FP 1, FN 0.",
        """predicted=torch.tensor([True,False,True,True]); actual=torch.tensor([True,False,False,True])
counts={'TP':int((predicted&actual).sum()),'TN':int((~predicted&~actual).sum()),'FP':int((predicted&~actual).sum()),'FN':int((~predicted&actual).sum())}
assert counts=={'TP':2,'TN':1,'FP':1,'FN':0}""",
        "Every prediction lands in exactly one cell, so the four counts sum to the record count 4.",
    ),
    ex(
        "Classify with a fixed weight",
        "With weight 2 and no bias, classify the normalized inputs -1.5, -0.2, 0 and 0.4 at logit 0, counting 0 as positive.",
        "False, False, True, True.",
        """logits_t=2*torch.tensor([-1.5,-.2,0.,.4]); assert (logits_t>=0).tolist()==[False,False,True,True]""",
        "The decision depends on the sign of the logit; the tie rule assigns the zero logit to the positive class.",
    ),
)

transfer(
    "torch-025",
    ex(
        "Score a new pair",
        "Compute the dot product and cosine similarity of [3, 4] and [4, 3].",
        "dot 24; cosine 0.96.",
        """left=torch.tensor([3.,4.],dtype=torch.float64); right=torch.tensor([4.,3.],dtype=torch.float64)
assert torch.dot(left,right).item()==24
np.testing.assert_allclose(F.cosine_similarity(left,right,dim=0).item(),.96,atol=1e-12,rtol=0)""",
        "Both vectors have norm 5, so the cosine is 24/25.",
    ),
    ex(
        "Predict scores after negation",
        "Negate the second vector and recompute both scores.",
        "dot -24; cosine -0.96.",
        """assert torch.dot(left,-right).item()==-24
np.testing.assert_allclose(F.cosine_similarity(left,-right,dim=0).item(),-.96,atol=1e-12,rtol=0)""",
        "Negation reverses direction, so both scores change sign while the magnitudes stay the same.",
    ),
    ex(
        "Compute a three-candidate loss",
        "Use logits [2, 0, 0] with target 0.",
        r"cross entropy \(\log(1+2e^{-2})\), about 0.2395, within 1e-12.",
        """three=torch.tensor([[2.,0.,0.]],dtype=torch.float64)
np.testing.assert_allclose(F.cross_entropy(three,torch.tensor([0])).item(),np.log1p(2*np.exp(-2)),atol=1e-12,rtol=0)""",
        "Each extra negative candidate adds its exponential to the denominator, so the loss grows with the candidate count.",
    ),
)

transfer(
    "torch-026",
    ex(
        "Apply a swapping kernel",
        "Create Residual(2), set its kernel to [[0, 1], [1, 0]] and its scale buffer to 2, and evaluate the row [1, 2].",
        "output [[5, 4]].",
        """swap=Residual(2); xs=torch.tensor([[1.,2.]],dtype=torch.float64)
with torch.no_grad(): swap.kernel.copy_(torch.tensor([[0.,1.],[1.,0.]],dtype=torch.float64)); swap.scale.fill_(2.)
assert swap(xs).tolist()==[[5.,4.]]""",
        "x@kernel swaps the features to [2, 1]; the residual adds 2 times that to [1, 2].",
    ),
    ex(
        "Predict state for a wider module",
        "Create Residual(3) and count its parameter scalars and buffers.",
        "9 kernel scalars and 1 buffer.",
        """wide_residual=Residual(3)
assert sum(p.numel() for p in wide_residual.parameters())==9 and len(list(wide_residual.buffers()))==1""",
        "The kernel is width by width; the scale is one registered buffer regardless of width.",
    ),
    ex(
        "Differentiate Cube at a new point",
        "Backpropagate the sum of 3*Cube(x) at x = -1.",
        "gradient 9.",
        """point=torch.tensor([-1.],dtype=torch.float64,requires_grad=True); (3*Cube.apply(point)).sum().backward()
assert point.grad.item()==9""",
        "The custom backward multiplies the incoming gradient 3 by 3x**2=3.",
    ),
)

transfer(
    "torch-027",
    ex(
        "Freeze a scaling base",
        "Create a bias-free 2-to-2 base whose weight is 2 times the identity, freeze it and evaluate the row [1, 2].",
        "output [[2, 4]]; the base weight does not require gradients.",
        """doubling=nn.Linear(2,2,bias=False)
with torch.no_grad(): doubling.weight.copy_(2*torch.eye(2))
doubling.requires_grad_(False)
probe_x=torch.tensor([[1.,2.]]); assert doubling(probe_x).tolist()==[[2.,4.]] and not doubling.weight.requires_grad""",
        "Freezing changes trainability, not the function the base computes.",
    ),
    ex(
        "Predict the head update",
        "Attach a zero-initialized bias-free 2-to-1 head, take one SGD step with learning rate 0.1 toward target 1 using mean squared error.",
        "head weight [0.4, 0.8]; the base receives no gradient.",
        """new_head=nn.Linear(2,1,bias=False)
with torch.no_grad(): new_head.weight.zero_()
head_opt=torch.optim.SGD(new_head.parameters(),lr=.1); head_opt.zero_grad(set_to_none=True)
(new_head(doubling(probe_x))-torch.tensor([[1.]])).square().mean().backward(); head_opt.step()
torch.testing.assert_close(new_head.weight,torch.tensor([[.4,.8]]),atol=1e-6,rtol=0)
assert doubling.weight.grad is None""",
        "The head sees features [2, 4]; the gradient 2(0-1)[2, 4] times -0.1 gives [0.4, 0.8].",
    ),
    ex(
        "Count trainable parameters",
        "Count the scalars that still require gradients across the frozen base and the new head.",
        "2 trainable scalars, all in the head.",
        """trainable=sum(p.numel() for p in [*doubling.parameters(),*new_head.parameters()] if p.requires_grad)
assert trainable==2""",
        "Only the head's two weights are trainable; the four frozen base weights are excluded.",
    ),
)

transfer(
    "torch-028",
    ex(
        "Predict Adam's first step",
        "From a fresh make_state(), take one step with zero noise and compare the weight with the learning rate 0.05.",
        "weight 0.05 within 1e-6.",
        """fresh_model,fresh_adam=make_state(); step(fresh_model,fresh_adam,torch.zeros((2,1)))
np.testing.assert_allclose(fresh_model.weight.item(),.05,atol=1e-6,rtol=0)""",
        "After bias correction the first Adam update is the learning rate times g/(|g|+eps), so its size is about 0.05 whatever the gradient magnitude.",
    ),
    ex(
        "Inspect the new optimizer state",
        "List the state entries Adam stores for that parameter after one step.",
        "keys step, exp_avg and exp_avg_sq; step equals 1.",
        """fresh_param=next(fresh_model.parameters())
assert set(fresh_adam.state[fresh_param])=={'step','exp_avg','exp_avg_sq'} and fresh_adam.state[fresh_param]['step'].item()==1""",
        "These moment estimates and the step count determine the next update, so a restart must restore them.",
    ),
    ex(
        "Replay a saved random state",
        "Save torch.get_rng_state(), draw three values, restore the state and draw again.",
        "the two draws are identical.",
        """saved_rng=torch.get_rng_state(); first_draw=torch.rand(3)
torch.set_rng_state(saved_rng); assert torch.equal(torch.rand(3),first_draw)""",
        "Restoring the generator state reproduces later random draws such as dropout masks or data noise.",
    ),
)

transfer(
    "torch-029",
    ex(
        "Find the float64 overflow boundary",
        "Exponentiate float64 values 709 and 710.",
        r"\(e^{709}\) is finite (about 8.2e307); \(e^{710}\) overflows to inf.",
        """big=torch.tensor([709.,710.],dtype=torch.float64); grown=torch.exp(big)
assert torch.isfinite(grown[0]) and torch.isinf(grown[1])""",
        r"The float64 maximum is about 1.8e308, between \(e^{709}\) and \(e^{710}\); for float32 the boundary lies between 88 and 89.",
    ),
    ex(
        "Compute a stable loss for target 1",
        "Use float32 logits [1000, 998] with target class 1.",
        r"loss \(\log(1+e^{2})\), about 2.1269, within 1e-5.",
        """wide_logits=torch.tensor([[1000.,998.]])
np.testing.assert_allclose(F.cross_entropy(wide_logits,torch.tensor([1])).item(),np.log1p(np.exp(2)),atol=1e-5,rtol=0)""",
        "cross_entropy subtracts the maximum logit internally, so only the difference of 2 matters.",
    ),
    ex(
        "Check a new shift",
        "Compare the softmax of [1000, 998] with the softmax of [5, 3].",
        "both are about [0.8808, 0.1192] and match within 1e-6.",
        """torch.testing.assert_close(torch.softmax(wide_logits[0],0),torch.softmax(torch.tensor([5.,3.]),0),atol=1e-6,rtol=0)
np.testing.assert_allclose(torch.softmax(torch.tensor([5.,3.]),0)[0].item(),1/(1+np.exp(-2)),atol=1e-6,rtol=0)""",
        "Subtracting 995 from both logits leaves the probabilities unchanged.",
    ),
)

transfer(
    "torch-031",
    ex(
        "Establish a new eager oracle",
        "Evaluate g(x)=2x-1 eagerly at the float32 inputs [0, 3].",
        "output [-1, 5].",
        """def affine(value): return 2*value-1
points=torch.tensor([0.,3.]); assert affine(points).tolist()==[-1.,5.]""",
        "The eager result is the oracle every captured or compiled version must match.",
    ),
    ex(
        "Capture the new function",
        "Compile g with a counting backend that returns graph.forward and compare it with the eager output.",
        "at least one captured graph; outputs match exactly.",
        """captured=[]
def counting(graph,example_inputs): captured.append(graph); return graph.forward
compiled_affine=torch.compile(affine,backend=counting,fullgraph=True,dynamic=False)
torch.testing.assert_close(compiled_affine(points),affine(points),atol=0,rtol=0); assert len(captured)>=1""",
        "The transparent backend runs the captured graph unchanged, so equality tests capture rather than optimization.",
    ),
    ex(
        "Predict recompilation for a new shape",
        "Call the compiled function with a three-element input, then with a second three-element input.",
        "the first three-element call adds a graph; the repeated shape reuses it.",
        """before_three=len(captured); compiled_affine(torch.tensor([1.,2.,3.])); after_three=len(captured)
compiled_affine(torch.tensor([4.,5.,6.])); assert after_three>before_three and len(captured)==after_three""",
        "With dynamic=False each new input shape fails a guard and is captured again; an identical signature passes the guard.",
    ),
)

transfer(
    "torch-032",
    ex(
        "Predict a new inference output",
        "Set a bias-free 2-to-1 Linear weight to [1, 3] and predict the rows [1, 2] and [3, 4].",
        "outputs [[7], [15]].",
        """other_model=nn.Linear(2,1,bias=False)
with torch.no_grad(): other_model.weight.copy_(torch.tensor([[1.,3.]]))
other_model.eval(); rows=torch.tensor([[1.,2.],[3.,4.]]); assert other_model(rows).tolist()==[[7.],[15.]]""",
        "Each prediction is 1*first+3*second.",
    ),
    ex(
        "Load state into matching and mismatched modules",
        "Load the model's state_dict into a fresh bias-free Linear(2, 1) and into a Linear(2, 1) that has a bias.",
        "the matching module reproduces the outputs; the module with a bias raises RuntimeError for the missing key.",
        """copy_model=nn.Linear(2,1,bias=False); copy_model.load_state_dict(other_model.state_dict())
torch.testing.assert_close(copy_model(rows),other_model(rows),atol=0,rtol=0)
try: nn.Linear(2,1).load_state_dict(other_model.state_dict())
except RuntimeError: pass
else: raise AssertionError('missing bias accepted')""",
        "A state_dict holds named tensors, not the architecture; strict loading checks that the names match.",
    ),
    ex(
        "Export the new model in memory",
        "Export the new model for the two-row input and compare the exported module's predictions.",
        "exported predictions match [[7], [15]] within 1e-6.",
        """exported_other=torch.export.export(other_model,(rows,),strict=True).module()
torch.testing.assert_close(exported_other(rows),other_model(rows),atol=1e-6,rtol=0)""",
        "The exported program records the computation for the example shape; this check runs without writing files.",
    ),
)

transfer(
    "torch-033",
    ex(
        "Predict a new valid batch",
        "Predict the float32 rows [0, 1], [2, 0] and [1, 1] with the lesson's weight [2, -1].",
        "outputs [-1, 4, 1] with shape (3,).",
        """rows=torch.tensor([[0.,1.],[2.,0.],[1.,1.]]); assert predict(rows).tolist()==[-1.,4.,1.]""",
        "Each output is 2*first-second, returned as a one-dimensional batch.",
    ),
    ex(
        "Check the batch boundary",
        "Predict a batch of four rows of ones, then a batch of five.",
        "four rows return shape (4,); five rows raise ValueError.",
        """assert tuple(predict(torch.ones((4,2))).shape)==(4,)
try: predict(torch.ones((5,2)))
except ValueError: pass
else: raise AssertionError('oversized batch accepted')""",
        "The contract accepts 1 to 4 rows; testing both sides of the limit shows where it applies.",
    ),
    ex(
        "Reject a float64 batch",
        "Pass the three valid rows converted to float64.",
        "TypeError rather than a silent conversion.",
        """try: predict(rows.double())
except TypeError: pass
else: raise AssertionError('float64 accepted')""",
        "Refusing other floating dtypes keeps the caller responsible for an explicit, visible conversion.",
    ),
)

transfer(
    "torch-034",
    ex(
        "Count errors for three groups",
        "Use groups A, B, B, C with truth 0, 1, 1, 0 and predictions 0, 0, 1, 1.",
        "A: 0 of 1 wrong; B: 1 of 2; C: 1 of 1.",
        """truth_t=torch.tensor([0,1,1,0]); pred_t=torch.tensor([0,0,1,1]); groups_t=['A','B','B','C']; wrong=pred_t!=truth_t
summary={g:(int(wrong[torch.tensor([x==g for x in groups_t])].sum()),groups_t.count(g)) for g in ['A','B','C']}
assert summary=={'A':(0,1),'B':(1,2),'C':(1,1)}""",
        "Group C's single record makes its error rate 1, a reason to report counts with every rate.",
    ),
    ex(
        "Deduplicate repeated identities",
        "Use row identities p, q, q, r, r, r and count rows, unique identities and the largest repeat.",
        "6 rows, 3 unique identities, largest repeat 3.",
        """rows_t=['p','q','q','r','r','r']; assert len(rows_t)==6 and len(set(rows_t))==3 and max(rows_t.count(i) for i in set(rows_t))==3""",
        "Identity r would carry half of a row-weighted score.",
    ),
    ex(
        "Trace a new perturbation",
        "Classify x>=0 at base 0.5 after shifts -0.4, -0.5 and -0.6.",
        "labels 1, 1, 0; the shift of -0.5 lands exactly on the boundary.",
        """start=torch.tensor(.5); moves=torch.tensor([-.4,-.5,-.6]); assert ((start+moves)>=0).long().tolist()==[1,1,0]""",
        "The boundary case shows why the tie rule must be stated with a perturbation test.",
    ),
)

transfer(
    "torch-035",
    ex(
        "Align a new pair of models",
        "Use truth x=1, y=2 with model A predictions x=1, y=4 and model B predictions y=2, x=0 in different dictionary order.",
        "paired squared-loss differences A minus B: [-1, 4].",
        """truth2={'x':1.,'y':2.}; model_a={'x':1.,'y':4.}; model_b={'y':2.,'x':0.}; keys=sorted(truth2)
paired=torch.tensor([(model_a[k]-truth2[k])**2-(model_b[k]-truth2[k])**2 for k in keys],dtype=torch.float64)
assert paired.tolist()==[-1.,4.]""",
        "Sorting identities before pairing keeps each difference on one record.",
    ),
    ex(
        "Interpret the new mean contrast",
        "Average the two paired differences and state which model the fixture favors.",
        "mean 1.5, favoring model B on this loss.",
        """assert paired.mean().item()==1.5""",
        "A positive mean of A minus B losses means A has the larger loss.",
    ),
    ex(
        "Bound the new bootstrap means",
        "Draw 500 two-index bootstrap samples with Generator seed 11 and inspect the possible means.",
        "every mean is -1, 1.5 or 4.",
        """gen=torch.Generator().manual_seed(11); draws=torch.randint(0,2,(500,2),generator=gen); boot=paired[draws].mean(1)
assert set(boot.tolist())<={-1.,1.5,4.} and boot.min()>=-1 and boot.max()<=4""",
        "With two differences, a resample of size two can only average two copies of one value or one of each.",
    ),
)

transfer(
    "torch-036",
    ex(
        "Freeze a new split",
        "Assign IDs a, b, c, d to training and e, f to holdout and check that the sets are disjoint.",
        "4 training and 2 holdout IDs with no overlap.",
        """release_split={'train':['a','b','c','d'],'test':['e','f']}
assert not set(release_split['train'])&set(release_split['test']) and (len(release_split['train']),len(release_split['test']))==(4,2)""",
        "The manifest records identities, so a later reader can confirm the separation without the data.",
    ),
    ex(
        "Predict a ten-step weight",
        "Train a zero-initialized float64 Linear(1, 1) without bias for 10 SGD steps with learning rate 0.01 on x = 1, 2, 3 and y = 2x.",
        "weight 2-2*(68/75)**10, about 1.2492, within 1e-12.",
        """ten_model=nn.Linear(1,1,bias=False,dtype=torch.float64)
with torch.no_grad(): ten_model.weight.zero_()
ten_opt=torch.optim.SGD(ten_model.parameters(),lr=.01); ten_x=torch.tensor([[1.],[2.],[3.]],dtype=torch.float64)
for _ in range(10):
    ten_opt.zero_grad(set_to_none=True); (ten_model(ten_x)-2*ten_x).square().mean().backward(); ten_opt.step()
np.testing.assert_allclose(ten_model.weight.item(),2-2*(68/75)**10,atol=1e-12,rtol=0)""",
        "Each step multiplies the error w-2 by 1-0.01*28/3=68/75, so the budget sets a predictable endpoint.",
    ),
    ex(
        "Hash bytes deterministically",
        "Compute the SHA-256 of the bytes weights-v2 twice and of weights-v3 once.",
        "identical bytes give identical 64-character digests; one changed byte changes the digest.",
        """first_hash=hashlib.sha256(b'weights-v2').hexdigest()
assert first_hash==hashlib.sha256(b'weights-v2').hexdigest() and first_hash!=hashlib.sha256(b'weights-v3').hexdigest() and len(first_hash)==64""",
        "A recorded digest lets a loader reject any modified artifact before trusting its contents.",
    ),
)
