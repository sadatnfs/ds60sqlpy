from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BLOCKS={
5:[r'''lemmas={('saw','VERB'):'see',('saw','NOUN'):'saw'}
print(lemmas[('saw','VERB')],lemmas[('saw','NOUN')])
assert lemmas[('saw','VERB')]=='see'
''',r'''tokens=['I','saw','her'];heads=[1,-1,1]
edges=[(tokens[head],tokens[i]) for i,head in enumerate(heads) if head!=-1]
print(edges)
assert edges==[('saw','I'),('saw','her')]
'''],
6:[r'''import math
factors=[3/10,3/9,3/10,3/9]
joint=math.prod(factors)
perplexity=math.exp(-sum(math.log(p) for p in factors)/4)
print(joint,perplexity)
assert math.isclose(joint,.01) and math.isclose(perplexity,math.sqrt(10))
''',r'''vocabulary_size=7
unseen_context=[1/vocabulary_size]*vocabulary_size
print(sum(unseen_context))
assert math.isclose(sum(unseen_context),1.)
empty_document_eos_probability=1/(3+7)
assert 1/empty_document_eos_probability==10
'''],
7:[r'''import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
v=TfidfVectorizer().fit(['tea tea cup','coffee cup'])
print(v.get_feature_names_out(),v.idf_)
a=np.log(3/2)+1
assert np.allclose(v.idf_,[a,1,a])
''',r'''x=v.transform(['tea tea cup','coffee cup']);q=v.transform(['tea'])
scores=(x@q.T).toarray().ravel()
print(scores)
assert np.isclose(scores[0],2*a/np.sqrt(1+4*a*a)) and scores[1]==0
'''],
8:[r'''import numpy as np
counts=np.array([[0.,3.],[3.,1.]])
likelihood=(counts+1)/(counts.sum(axis=1,keepdims=True)+2)
print(likelihood)
assert np.allclose(likelihood,[[1/5,4/5],[4/6,2/6]])
''',r'''weights=np.array([.5,.5])*likelihood[:,0]
posterior=weights/weights.sum()
print(posterior)
assert np.allclose(posterior,[3/13,10/13])
'''],
10:[r'''import itertools
start=[.6,.4];transition=[[.7,.3],[.4,.6]];emission=[[.6,.1],[.2,.7]]
paths={path:start[path[0]]*emission[0][path[0]]*transition[path[0]][path[1]]*emission[1][path[1]] for path in itertools.product(range(2),repeat=2)}
print(paths)
assert max(paths,key=paths.get)==(0,1)
''',r'''gold=['B-ORG','I-ORG','O'];pred=['B-ORG','O','O']
accuracy=sum(a==b for a,b in zip(gold,pred))/len(gold)
print(accuracy)
assert accuracy==2/3
assert (0,2,'ORG')!=(0,1,'ORG') # complete typed entity spans differ
'''],
11:[r'''import re
text='Ada joined Acme Labs in Paris.'
match=re.search(re.escape('Acme Labs'),text)
assert match is not None
print(match.span(),text[match.start():match.end()])
assert match.span()==(11,20)
''',r'''gold={('d1','PER',0,3),('d1','ORG',11,20),('d1','LOC',24,29)}
pred={('d1','PER',0,3),('d1','ORG',11,15)}
tp=len(gold&pred);fp=len(pred-gold);fn=len(gold-pred)
f1=2*tp/(2*tp+fp+fn)
print(tp,fp,fn,f1)
assert (tp,fp,fn,f1)==(1,1,2,.4)
'''],
12:[r'''import numpy as np
counts=np.array([[4.,3.,0.],[3.,4.,0.],[0.,0.,6.]])
value=np.log(counts[0,0]*counts.sum()/(counts[0].sum()*counts[:,0].sum()))
print(value)
assert np.isclose(value,np.log(80/49))
''',r'''a=np.array([1.,2.]);b=np.array([2.,1.]);rotation=np.array([[0.,-1.],[1.,0.]])
cosine=lambda x,y: x@y/(np.linalg.norm(x)*np.linalg.norm(y))
print(cosine(a,b),cosine(a@rotation,b@rotation))
assert np.isclose(cosine(a,b),cosine(a@rotation,b@rotation))
'''],
13:[r'''import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import NMF
counts=CountVectorizer().fit_transform(['cat pet','dog pet','car wheel','truck wheel'])
model=NMF(n_components=2,init='nndsvda',random_state=0,max_iter=1000)
w=model.fit_transform(counts);h=model.components_
print(w.shape,h.shape)
assert w.shape==(4,2) and np.all(w>=0) and np.all(h>=0)
''',r'''permuted=h[::-1]
a=h/np.linalg.norm(h,axis=1,keepdims=True)
b=permuted/np.linalg.norm(permuted,axis=1,keepdims=True)
match=np.argmax(a@b.T,axis=1)
print(match)
assert match.tolist()==[1,0]
'''],
14:[r'''import numpy as np
values=np.array([[1.,2.],[3.,4.],[100.,100.]])
mask=np.array([True,True,False])
print(values[mask].mean(axis=0))
assert np.allclose(values[mask].mean(axis=0),[2.,3.])
''',r'''loss=np.logaddexp(3.,1.)-3.
print(loss)
assert np.isclose(loss,np.log1p(np.exp(-2)))
'''],
15:[r'''import numpy as np
from scipy.special import logsumexp
x=np.array([[1.,0.],[0.,1.]])
scores=x@x.T/np.sqrt(2)
weights=np.exp(scores-logsumexp(scores,axis=1,keepdims=True))
print(weights@x)
assert np.allclose(weights.sum(axis=1),1.) and (weights@x)[0,1]>0
''',r'''logits=np.array([[2.,0.],[99.,-99.],[0.,2.]])
labels=np.array([0,-100,1]);valid=labels!=-100
selected=logits[valid];targets=labels[valid]
loss=np.mean(logsumexp(selected,axis=1)-selected[np.arange(len(targets)),targets])
print(loss)
assert np.isclose(loss,np.log1p(np.exp(-2)))
'''],
16:[r'''target=['repair']
decoder_input=['<BOS>',*target];prediction_target=[*target,'<EOS>']
print(decoder_input,prediction_target)
assert decoder_input==['<BOS>','repair'] and prediction_target==['repair','<EOS>']
''',r'''greedy_joint=.6*.5
alternative_joint=.4*1.
print(greedy_joint,alternative_joint)
assert alternative_joint>greedy_joint
'''],
17:[r'''from collections import Counter
candidate=Counter('the the the the'.split());reference=Counter('the cat'.split())
clipped=sum(min(count,reference[word]) for word,count in candidate.items())/sum(candidate.values())
print(clipped)
assert clipped==.25
''',r'''reference='service is not ready'.split();candidate='service is ready'.split()
matched=3;precision=matched/len(candidate);recall=matched/len(reference)
f1=2*precision*recall/(precision+recall)
print(precision,recall,f1)
assert precision==1 and recall==.75 and f1==6/7
# The source and candidate contradict despite high overlap.
'''],
18:[r'''text='服务正常'
print(len(text),len(text.encode('utf-8')),len(text.split()))
assert (len(text),len(text.encode('utf-8')),len(text.split()))==(4,12,1)
''',r'''english_correct,english_n=9,10
spanish_correct,spanish_n=1,2
pooled=(english_correct+spanish_correct)/(english_n+spanish_n)
macro=(english_correct/english_n+spanish_correct/spanish_n)/2
print(pooled,macro)
assert pooled==5/6 and macro==.7
'''],
19:[r'''import numpy as np
a=np.array([1,1,0,0,1,0]);b=np.array([1,0,0,0,1,1])
observed=np.mean(a==b);expected=a.mean()*b.mean()+(1-a.mean())*(1-b.mean())
kappa=(observed-expected)/(1-expected)
print(observed,expected,kappa)
assert np.isclose(kappa,1/3)
''',r'''ratings=np.array([[1,1,0],[1,1,1],[0,0,0]])
soft=ratings.mean(axis=1)
print(soft)
assert np.allclose(soft,[2/3,1,0])
'''],
20:[r'''import numpy as np
labels=np.array([[1,1,-1],[0,-1,0],[1,0,-1],[-1,-1,-1]])
coverage=np.any(labels!=-1,axis=1).mean()
conflict=(np.any(labels==0,axis=1)&np.any(labels==1,axis=1)).mean()
print(coverage,conflict)
assert coverage==.75 and conflict==.25
''',r'''p=np.array([.5,.6,.95,.1])
entropy=-p*np.log(p)-(1-p)*np.log(1-p)
order=np.argsort(-entropy,kind='stable')
print(order[:2])
assert order[:2].tolist()==[0,1]
'''],
21:[r'''import hashlib
normalize=lambda text:' '.join(text.casefold().split())
a=hashlib.sha256(normalize('Reset the router').encode()).hexdigest()
b=hashlib.sha256(normalize('reset  the router').encode()).hexdigest()
print(a==b)
assert a==b
''',r'''import numpy as np
groups={'a':[.2,.2],'b':[-.1],'c':[.3,.3,.3]}
family=np.mean([np.mean(values) for values in groups.values()])
rows=np.mean([value for values in groups.values() for value in values])
print(family,rows)
assert np.isclose(family,2/15) and np.isclose(rows,.2)
'''],
22:[r'''import math
idf=math.log(1+(3-2+.5)/(2+.5))
score=2*idf*2.2/(1+1.2*(.25+.75*2/(8/3)))
print(score)
assert score>1
''',r'''scores={}
for ranking in [['a','b','c'],['b','c','a']]:
    for rank,key in enumerate(ranking,1):scores[key]=scores.get(key,0)+1/(60+rank)
print(sorted(scores,key=lambda key:-scores[key]))
assert max(scores,key=scores.get)=='b'
'''],
23:[r'''docs=[{'id':'old','role':'ops','until':8},{'id':'current','role':'ops','until':20},{'id':'private','role':'finance','until':20}]
allowed=[d['id'] for d in docs if d['role']=='ops' and 10<=d['until']]
print(allowed)
assert allowed==['current']
''',r'''import numpy as np
p=np.array([50.,50.]);q=np.array([80.,20.])
distance=.5*np.abs(p/p.sum()-q/q.sum()).sum()
print(distance)
assert np.isclose(distance,.3)
'''],
24:[r'''import re
text='TKT-301 router packet loss'
ids=re.findall(r'(?<!\w)TKT-([0-9]{3})(?![0-9])',text)
print(ids)
assert ids==['301']
assert re.findall(r'(?<!\w)TKT-([0-9]{3})(?![0-9])','TKT-3019')==[]
''',r'''record={'source_id':'network','version':2,'quote':'Router resets require approved change.'}
packet={'ticket_id':'TKT-301','category':'network','status':'evidence-ready','evidence':[record]}
print(packet)
assert packet['evidence'][0]['version']==2
# The quoted rule does not establish that a reset was approved or executed.
''']}
for n in range(5,25):
    key=f'nlp-{n:03d}';guide=ROOT/'courses/nlp/guides'/f'{key}.md';text=guide.read_text()
    if n in BLOCKS and '### Executable worked traces' not in text:
        snippet='### Executable worked traces\n\nRun these two small blocks in order. They reproduce the numerical or structural observations above; the full reference additionally checks the exercise changes and failure cases.\n\n'+ '\n\n'.join('```python\n'+code.strip()+'\n```' for code in BLOCKS[n])+'\n\n'
        text=text.replace('## Run and inspect',snippet+'## Run and inspect')
        guide.write_text(text)
    answer=ROOT/'courses/nlp/solutions'/f'{key}_solutions.md';a=answer.read_text()
    if '## Mechanism review and counterexample' not in a:
        before=text.split('## Worked examples',1)[0]
        final_section=before.rsplit('\n## ',1)[1].split('\n',1)[1].strip()
        a+='\n## Mechanism review and counterexample\n\n'+final_section+'\n'
        answer.write_text(a)

RELATED={
14:'Compare [grounded claims](../../llm-applied/guides/llm-applied-011.md) and [retrieval/answer evaluation](../../llm-applied/guides/llm-applied-012.md) when a sentence retriever becomes part of a domain assistant. Similarity and claim support remain separate checks.',
15:'Continue with [SFT data and response masks](../../llm-applied/guides/llm-applied-014.md) for adaptation workflows. The [statistics book neural chapter](../../statistics-ml/chapters/33-deep-learning-language-and-generative-modeling.md) connects encoder mechanisms, weight adaptation and retrieved evidence.',
17:'The [statistics book LLM evaluation chapter](../../statistics-ml/chapters/34-generative-ai-and-language-model-evaluation.md) expands the sampling, judge and uncertainty design. The [applied retrieval/answer guide](../../llm-applied/guides/llm-applied-012.md) adds oracle-context controls.',
22:'Use [applied retrieval and answer evaluation](../../llm-applied/guides/llm-applied-012.md) to separate candidate retrieval from grounded generation. A higher ranking score is not a supported answer by itself.',
24:'Continue to [grounded claims and abstention](../../llm-applied/guides/llm-applied-011.md) and [retrieval/answer evaluation](../../llm-applied/guides/llm-applied-012.md) when extending this evidence packet into an assistant. Keep the classifier, retrieval and generation acceptance boundaries distinct.'
}
for n,body in RELATED.items():
    path=ROOT/'courses/nlp/guides'/f'nlp-{n:03d}.md';text=path.read_text()
    if '## Related local tracks' not in text:text=text.replace('## Ask an AI tutor about this lesson','## Related local tracks\n\n'+body+'\n\n## Ask an AI tutor about this lesson')
    path.write_text(text)
