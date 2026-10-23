import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

TRAIN=["tea tea cup","coffee cup"]

def main():
    vectorizer=TfidfVectorizer(norm="l2",smooth_idf=True,sublinear_tf=False)
    x=vectorizer.fit_transform(TRAIN)
    names=vectorizer.get_feature_names_out().tolist()
    assert names==["coffee","cup","tea"] and x.shape==(2,3)
    a=np.log(3/2)+1
    assert np.allclose(vectorizer.idf_,[a,1,a])
    raw=np.array([[0.,1.,2*a],[a,1.,0.]])
    expected=raw/np.linalg.norm(raw,axis=1,keepdims=True)
    assert np.allclose(x.toarray(),expected)
    query=vectorizer.transform(["tea"])
    score=(x@query.T).toarray().ravel()
    assert np.isclose(score[0],2*a/np.sqrt(1+4*a*a)) and score[1]==0
    before=vectorizer.vocabulary_.copy()
    unknown=vectorizer.transform(["matcha",""])
    assert unknown.nnz==0 and vectorizer.vocabulary_==before
    assert np.allclose(np.sqrt(x.multiply(x).sum(axis=1)).A.ravel(),1.)
    sublinear=TfidfVectorizer(norm=None,smooth_idf=True,sublinear_tf=True).fit(TRAIN)
    weighted=sublinear.transform(["tea tea cup"]).toarray()[0]
    tea=sublinear.vocabulary_["tea"]
    assert np.isclose(weighted[tea],(1+np.log(2))*a)
    print("nlp-007: manual DF/IDF/TF-IDF and sparse cosine match; OOV abstention boundary passed")

if __name__ == "__main__":
    main()
