import numpy as np

def projection_and_rank():
    x = np.array([[1., 0.], [1., 1.], [1., 2.]])
    y = np.array([1., 2., 4.])
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    assert np.allclose(x.T @ residual, 0, atol=1e-12)
    redundant = np.column_stack([x, 2*x[:, 1]])
    assert np.linalg.matrix_rank(redundant) == 2
    print("Coefficients:", beta, "rank with duplicate direction:", 2)

def gradients_and_information():
    x = np.array([[1., 0.], [1., 1.], [1., 2.]])
    y, beta = np.array([1., 2., 4.]), np.array([0.2, 0.5])
    loss = lambda b: np.sum((x @ b-y)**2)
    h = 1e-6
    finite = np.array([(loss(beta+h*e)-loss(beta-h*e))/(2*h) for e in np.eye(2)])
    analytic = 2*x.T @ (x @ beta-y)
    assert np.allclose(finite, analytic, atol=1e-7)
    p, q = np.array([.5, .5]), np.array([.9, .1])
    kl = np.sum(p*np.log(p/q))
    assert kl > 0
    print("Gradient:", analytic, "KL in nats:", round(float(kl), 4))

def main():
    projection_and_rank()
    gradients_and_information()

if __name__ == "__main__":
    main()
