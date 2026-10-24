import numpy as np

def meta_weights():
    effect=np.array([.2,.5]);variance=np.array([.1,.2])**2
    weight=1/variance;common=np.sum(weight*effect)/weight.sum();se=np.sqrt(1/weight.sum())
    random_weight=1/(variance+.04);random_mean=np.sum(random_weight*effect)/random_weight.sum()
    assert np.isclose(common,.26) and np.isclose(se,np.sqrt(1/125))
    assert random_mean>common and random_weight[0]/random_weight[1]<weight[0]/weight[1]
    print("Common-effect mean and SE:",common,se,"illustrative tau-squared=.04 mean:",random_mean)

def relative_and_circular():
    composition=np.array([1.,2.,7.]);scaled=10*composition
    assert np.allclose(composition/composition.sum(),scaled/scaled.sum())
    ratio=np.log(composition[0]/composition[1])
    assert np.isclose(ratio,np.log(scaled[0]/scaled[1]))
    radians=np.deg2rad([359.,1.]);circular=np.rad2deg(np.angle(np.mean(np.exp(1j*radians))))
    assert abs(circular)<1e-10 and np.mean([359.,1.])==180.
    print("Invariant log ratio:",ratio,"circular mean near zero:",circular)

def laplace_ratio():
    epsilon=1.;sensitivity=1.;scale=sensitivity/epsilon
    def density(output,count):return np.exp(-abs(output-count)/scale)/(2*scale)
    ratio=density(7.,6.)/density(7.,5.)
    assert np.isclose(ratio,np.exp(epsilon))
    assert sensitivity/.5>sensitivity/2.
    print("Adjacent-count density ratio:",ratio,"bound:",np.exp(epsilon))

def main():
    meta_weights();relative_and_circular();laplace_ratio()

if __name__ == "__main__":
    main()
