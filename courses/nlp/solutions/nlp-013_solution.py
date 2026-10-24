import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.decomposition import TruncatedSVD,NMF,LatentDirichletAllocation

DOCS=["cat kitten pet","dog puppy pet","car wheel road","truck wheel road"]

def aligned_similarity(a,b):
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
    if a.shape!=b.shape:raise ValueError("same topic and vocabulary dimensions required")
    an=np.linalg.norm(a,axis=1,keepdims=True);bn=np.linalg.norm(b,axis=1,keepdims=True)
    if np.any(an==0) or np.any(bn==0):raise ValueError("nonzero topics required")
    similarity=(a/an)@(b/bn).T
    rows,cols=linear_sum_assignment(-similarity)
    return cols,similarity[rows,cols]

def main():
    vectorizer=CountVectorizer();counts=vectorizer.fit_transform(DOCS)
    tfidf=TfidfTransformer().fit_transform(counts)
    lsa=TruncatedSVD(n_components=2,random_state=0).fit(tfidf)
    z=lsa.transform(tfidf)
    assert z.shape==(4,2)
    reconstructed=z@lsa.components_
    assert np.linalg.norm(tfidf.toarray()-reconstructed)<np.linalg.norm(tfidf.toarray())
    assert np.allclose((-z)@(-lsa.components_),reconstructed)
    nmf=NMF(n_components=2,init="nndsvda",random_state=0,max_iter=1000)
    w=nmf.fit_transform(counts);h=nmf.components_
    assert np.all(w>=0) and np.all(h>=0) and w.shape==(4,2)
    pet=vectorizer.vocabulary_["pet"];wheel=vectorizer.vocabulary_["wheel"]
    assert np.argmax(h[:,pet])!=np.argmax(h[:,wheel])
    lda=LatentDirichletAllocation(n_components=2,learning_method="batch",max_iter=30,random_state=0)
    proportions=lda.fit_transform(counts)
    assert proportions.shape==(4,2) and np.allclose(proportions.sum(axis=1),1.)
    cols,scores=aligned_similarity(h,h[::-1])
    assert cols.tolist()==[1,0] and np.allclose(scores,1.)
    before=vectorizer.vocabulary_.copy()
    heldout=vectorizer.transform(["newplanet pet"])
    assert "newplanet" not in before and vectorizer.vocabulary_==before and heldout.shape[1]==counts.shape[1]
    print("nlp-013: actual LSA/NMF/LDA shapes and constraints; permutation-aligned topic comparison passed")

if __name__ == "__main__":
    main()
