import numpy as np

def baselines_and_smoothing():
    y=np.array([10.,12.,14.,16.]);h=np.arange(1,4)
    naive=np.repeat(y[-1],3);drift=y[-1]+h*(y[-1]-y[0])/(len(y)-1)
    level=y[0]
    for value in y[1:]:level=.5*value+.5*level
    assert naive.tolist()==[16.,16.,16.]
    assert drift.tolist()==[18.,20.,22.] and level==14.25
    print("Naive:",naive,"drift:",drift,"SES level:",level)

def recursive_ar():
    phi=.5;intercept=2.;current=10.;forecast=[]
    for _ in range(4):
        current=intercept+phi*current;forecast.append(current)
    assert np.allclose(forecast,[7.,5.5,4.75,4.375])
    assert intercept/(1-phi)==4.
    print("AR forecasts:",forecast,"long-run mean:",4.)

def scalar_kalman():
    prior_mean=0.;prior_variance=4.;measurement=3.;measurement_variance=1.
    gain=prior_variance/(prior_variance+measurement_variance)
    posterior=prior_mean+gain*(measurement-prior_mean)
    variance=(1-gain)*prior_variance
    assert np.isclose(gain,.8) and np.isclose(posterior,2.4) and np.isclose(variance,.8)
    noisy_gain=4/(4+16)
    assert noisy_gain<gain
    print("Kalman gain, posterior mean, variance:",gain,posterior,variance)

def volatility_update():
    omega,alpha,beta=.1,.2,.7
    next_variance=omega+alpha*3**2+beta*1.
    assert np.isclose(next_variance,2.6) and alpha+beta<1
    print("Variance after shock 3:",next_variance)

def main():
    baselines_and_smoothing();recursive_ar();scalar_kalman();volatility_update()

if __name__ == "__main__":
    main()
