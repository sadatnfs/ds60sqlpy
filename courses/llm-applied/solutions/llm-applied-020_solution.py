"""llm-applied-020: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Construct paired retrieval features
    queries=torch.eye(2); documents=torch.eye(2); labels=torch.tensor([0,1]); projection=nn.Parameter(torch.zeros((2,2)))
    scores=(queries@projection)@documents.T
    assert tuple(scores.shape)==(2,2) and labels.tolist()==[0,1]

    # Exercise 2: Train the query projection
    opt=torch.optim.SGD([projection],lr=.5); initial=F.cross_entropy(scores,labels).item()
    for _ in range(30):
        opt.zero_grad(set_to_none=True); scores=(queries@projection)@documents.T; loss=F.cross_entropy(scores,labels); loss.backward(); opt.step()
    final_scores=(queries@projection)@documents.T
    assert F.cross_entropy(final_scores,labels).item()<initial and final_scores.argmax(1).tolist()==[0,1]

    # Exercise 3: Evaluate a perturbed held-out query
    held=torch.tensor([[.9,.1]]); held_scores=(held@projection)@documents.T
    assert held_scores.argmax(1).item()==0

    # Exercise 4: Train a pairwise reranker
    weight=nn.Parameter(torch.zeros(2)); positive=torch.tensor([1.,0.]); negative=torch.tensor([0.,1.]); optimizer=torch.optim.SGD([weight],lr=.2); first=F.softplus(-(positive@weight-negative@weight)).item()
    for _ in range(20):
        optimizer.zero_grad(set_to_none=True); objective=F.softplus(-(positive@weight-negative@weight)); objective.backward(); optimizer.step()
    assert positive@weight>negative@weight and F.softplus(-(positive@weight-negative@weight)).item()<first

    # Exercise 5: Detect a false-negative identity
    pair={'positive':'doc-a','negative':'doc-a'}
    assert pair['positive']==pair['negative']

    # Exercise 6: Bound the model claim
    receipt={'query_projection_updates':30,'reranker_updates':20,'literal_feature_fixture':True,'pretrained_semantic_encoder':False,'natural_language_quality_measured':False}
    assert receipt['query_projection_updates']==30 and not receipt['natural_language_quality_measured']
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
