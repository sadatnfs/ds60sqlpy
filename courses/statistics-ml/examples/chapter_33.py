import numpy as np


def gradient_check():
    x = np.array([1.0, 2.0])
    w = np.array([0.2, -0.1])
    target = 0.8

    def loss(weights):
        prediction = np.tanh(x @ weights)
        return 0.5 * (prediction - target) ** 2

    prediction = np.tanh(x @ w)
    gradient = (prediction - target) * (1 - prediction**2) * x
    eps = 1e-6
    numerical = np.empty_like(w)
    for i in range(len(w)):
        step = np.zeros_like(w)
        step[i] = eps
        numerical[i] = (loss(w + step) - loss(w - step)) / (2 * eps)
    assert np.allclose(gradient, numerical, atol=1e-8)
    assert loss(w - 0.1 * gradient) < loss(w)
    print("Analytic and numerical gradient:", gradient, numerical)


def causal_attention():
    x = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])

    def attention(values):
        logits = values @ values.T / np.sqrt(values.shape[1])
        mask = np.triu(np.ones(logits.shape, dtype=bool), k=1)
        logits = np.where(mask, -np.inf, logits)
        weights = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        weights /= weights.sum(axis=1, keepdims=True)
        return weights @ values, weights

    output, weights = attention(x)
    changed = x.copy()
    changed[2] = [100.0, -100.0]
    later, _ = attention(changed)
    assert np.allclose(weights.sum(axis=1), 1.0)
    assert np.allclose(weights[np.triu_indices(3, k=1)], 0.0)
    assert np.allclose(output[:2], later[:2])
    print("Causal attention weights:", weights)


def low_rank_update():
    base = np.zeros((8, 6))
    a = np.arange(12, dtype=float).reshape(2, 6) / 10
    b = np.arange(16, dtype=float).reshape(8, 2) / 20
    update = b @ a
    effective = base + update
    assert effective.shape == (8, 6) and np.linalg.matrix_rank(update) <= 2
    assert a.size + b.size == 28 and base.size == 48
    print("Full weights versus adapter parameters:", base.size, a.size + b.size)


def response_only_loss():
    target_probability = np.array([0.01, 0.02, 0.8, 0.5])
    response_mask = np.array([False, False, True, True])
    loss = -np.log(target_probability[response_mask]).mean()
    changed = target_probability.copy()
    changed[:2] = [0.9, 0.9]
    assert np.isclose(loss, -np.log(changed[response_mask]).mean())
    assert np.isclose(loss, -np.log(0.4) / 2)
    print("Response-only negative log likelihood:", loss)


def evidence_packet():
    docs = [
        ("runbook-v2", "restart requires an approved change"),
        ("runtime-17", "restart completed at 14:00"),
        ("glossary-v1", "a restart creates a new process"),
    ]
    query = set("restart approved change".split())
    scored = sorted(
        ((len(query & set(text.split())), doc_id, text) for doc_id, text in docs), reverse=True
    )
    packet = [{"source_id": doc_id, "text": text} for score, doc_id, text in scored[:2]]
    assert packet[0]["source_id"] == "runbook-v2"
    assert all(item["source_id"] and item["text"] for item in packet)
    print("Retrieved evidence packet:", packet)


def main():
    gradient_check()
    causal_attention()
    low_rank_update()
    response_only_loss()
    evidence_packet()


if __name__ == "__main__":
    main()
