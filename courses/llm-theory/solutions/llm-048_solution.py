"""llm-048: bounded local reference checks. No network or persistent data writes."""

import numpy as np

def probabilities(value):
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


def verify():
    # Exercise 1: Prove one-step distribution preservation
    p=np.array([.5,.3,.2]); q=np.array([.2,.5,.3]); acceptance,residual,rejection=correction(p,q)
    accepted_mass=q*acceptance
    np.testing.assert_allclose(accepted_mass,[.2,.3,.2],atol=1e-12,rtol=0)
    np.testing.assert_allclose(rejection,.3,atol=1e-12,rtol=0); np.testing.assert_allclose(residual,[1,0,0],atol=1e-12,rtol=0)
    np.testing.assert_allclose(accepted_mass+rejection*residual,p,atol=1e-12,rtol=0)

    # Exercise 2: Exercise acceptance andcorrection paths
    rejected=one_step(p,q,1,.8,.9); accepted=one_step(p,q,2,.5,.1)
    assert rejected=={'token':0,'accepted':False} and accepted=={'token':2,'accepted':True}

    # Exercise 3: Check an all-accepted round andbonus token
    same=lambda prefix:p
    all_accepted=speculative_round([],same,same,[.1,.6],[.9,.9],.7,budget=3)
    assert all_accepted['tokens']==[0,1,1] and all_accepted['accepted_count']==2 and not all_accepted['rejected']

    # Exercise 4: Stop at the first rejection
    round_result=speculative_round([2],lambda prefix:p,lambda prefix:q,[.1,.3],[.2,.9],.4,budget=3)
    assert round_result['proposals']==[0,1] and round_result['tokens']==[0,0] and round_result['accepted_count']==1 and round_result['rejected']

    # Exercise 5: Rollback actual K/V arrays
    cache=TinyCache([2]); old_length=len(cache.tokens)
    for token in round_result['proposals']: cache.append(token)
    broken=TinyCache(cache.tokens)
    apply_round(cache,old_length,round_result); fresh=TinyCache([2,0,0])
    assert cache.tokens==fresh.tokens; np.testing.assert_allclose(cache.keys,fresh.keys,atol=0,rtol=0); np.testing.assert_allclose(cache.output(),fresh.output(),atol=1e-12,rtol=0)
    broken.append(0); assert broken.tokens!=fresh.tokens and not np.allclose(broken.output(),fresh.output())

    # Exercise 6: Handle equality,EOS,budgets andinvalid support
    alpha,none,mass=correction(p,p); assert mass==0 and none is None and np.all(alpha==1)
    eos=speculative_round([],same,same,[.95,.1],[.2,.2],.1,budget=3,eos=2); assert eos['tokens']==[2]
    limited=speculative_round([],same,same,[.1,.6],[.9,.9],.7,budget=2); assert len(limited['tokens'])==2
    try: one_step(np.array([.5,.5]),np.array([1.,0.]),1,.2,.3)
    except ValueError: pass
    else: raise AssertionError('impossible draft token accepted')
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
