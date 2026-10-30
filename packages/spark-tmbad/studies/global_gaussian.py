"""Original exact low-rank Gaussian reference from bounded sufficient statistics.

This is study code, not a new package execution backend or general sparse
Laplace engine. A separate tiny dense oracle is intentionally limited to64rows.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Iterable
from typing import Any

from study_support import canonical


class NumericalCertificateError(ValueError):
    """The raw-statistic calculation cannot certify its requested quadratic form."""


class Sum:
    def __init__(self) -> None:
        self.total = 0.0
        self.correction = 0.0

    def add(self, value: float) -> None:
        if not math.isfinite(value):
            raise ValueError("Nonfinite sufficient-statistic contribution")
        updated = self.total + value
        self.correction += (
            (self.total - updated) + value
            if abs(self.total) >= abs(value)
            else (value - updated) + self.total
        )
        self.total = updated
        if not math.isfinite(self.total + self.correction):
            raise ValueError("Statistic accumulation overflow")

    def value(self) -> float:
        return self.total + self.correction


def dot(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vector dimensions differ")
    return math.fsum(x * y for x, y in zip(a, b, strict=True))


def transpose(a: list[list[float]]) -> list[list[float]]:
    return [list(row) for row in zip(*a, strict=True)]


def matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[dot(row, column) for column in transpose(b)] for row in a]


def matvec(a: list[list[float]], x: list[float]) -> list[float]:
    return [dot(row, x) for row in a]


def cholesky(a: list[list[float]]) -> list[list[float]]:
    n = len(a)
    if not 1 <= n <= 64 or any(len(row) != n for row in a):
        raise ValueError("Cholesky dimensions are unsupported")
    if not all(math.isfinite(x) for row in a for x in row):
        raise ValueError("Nonfinite covariance")
    scale = max(abs(x) for row in a for x in row)
    if scale == 0:
        raise NumericalCertificateError("Covariance is zero")
    if any(abs(a[i][j] - a[j][i]) > 1e-12 * scale for i in range(n) for j in range(n)):
        raise ValueError("Covariance must be symmetric")
    out = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            value = a[i][j] - math.fsum(out[i][k] * out[j][k] for k in range(j))
            if i == j:
                if value <= 64 * math.ulp(1.0) * scale:
                    raise NumericalCertificateError(
                        "Uncertifiable covariance pivot; no jitter applied"
                    )
                out[i][j] = math.sqrt(value)
            else:
                out[i][j] = value / out[j][j]
    return out


def solve_cholesky(lower: list[list[float]], b: list[float]) -> list[float]:
    n = len(lower)
    if len(b) != n:
        raise ValueError("Solve dimensions differ")
    first = [0.0] * n
    answer = [0.0] * n
    for i in range(n):
        first[i] = (b[i] - math.fsum(lower[i][j] * first[j] for j in range(i))) / lower[i][i]
    for i in reversed(range(n)):
        answer[i] = (
            first[i] - math.fsum(lower[j][i] * answer[j] for j in range(i + 1, n))
        ) / lower[i][i]
    return answer


def inverse_small(lower: list[list[float]]) -> list[list[float]]:
    if len(lower) > 8:
        raise ValueError("Only the bounded latent system may be inverted for trace calculations")
    columns = []
    for i in range(len(lower)):
        unit = [float(j == i) for j in range(len(lower))]
        columns.append(solve_cholesky(lower, unit))
    return transpose(columns)


def _finite_vector(value: Any, size: int) -> list[float]:
    if not isinstance(value, (list, tuple)) or len(value) != size:
        raise ValueError("Numeric vector shape differs")
    if any(
        type(x) not in (int, float)
        or not math.isfinite(x)
        or (type(x) is int and abs(x) > 2**53 - 1)
        for x in value
    ):
        raise ValueError("Numeric vectors require finite lossless values")
    return list(map(float, value))


def summarize(partition_id: int, rows: Iterable[dict[str, Any]], p: int, q: int) -> dict[str, Any]:
    if type(partition_id) is not int or partition_id < 0 or not 1 <= p <= 8 or not 1 <= q <= 8:
        raise ValueError("Invalid bounded sufficient-statistic dimensions")
    width = p + q + 1
    sums = [[Sum() for _ in range(width)] for _ in range(width)]
    count = xor = total = 0
    mask = (1 << 256) - 1
    for row in rows:
        x, z = _finite_vector(row["x"], p), _finite_vector(row["z"], q)
        y = _finite_vector([row["y"]], 1)[0]
        identifier = row["row_id"]
        if type(identifier) is not int or not 0 <= identifier <= 2**53 - 1:
            raise ValueError("Rows require exact nonnegative identifiers")
        vector = x + z + [y]
        for i in range(width):
            for j in range(width):
                sums[i][j].add(vector[i] * vector[j])
        h = int(hashlib.sha256(canonical([identifier, x, z, y])).hexdigest(), 16)
        xor ^= h
        total = (total + h) & mask
        count += 1
        if count > 2**53 - 1:
            raise ValueError("Exact count limit exceeded")
    return {
        "schema_version": 1,
        "partition_id": partition_id,
        "p": p,
        "q": q,
        "row_count": count,
        "gram": [[item.value() for item in line] for line in sums],
        "ledger": {"count": count, "xor": f"{xor:064x}", "sum": f"{total:064x}"},
    }


def combine(
    records: list[dict[str, Any]],
    *,
    expected_partitions: int,
    expected_rows: int,
    expected_ledger: dict[str, Any],
) -> dict[str, Any]:
    if (
        not 1 <= expected_partitions <= 4096
        or expected_rows < 1
        or len(records) != expected_partitions
    ):
        raise ValueError("Expected complete nonempty partition coverage")
    if sorted(row["partition_id"] for row in records) != list(range(expected_partitions)):
        raise ValueError("Partition identity is missing or duplicated")
    p, q = records[0]["p"], records[0]["q"]
    width = p + q + 1
    if not 1 <= p <= 8 or not 1 <= q <= 8:
        raise ValueError("Unqualified statistic dimensions")
    sums = [[Sum() for _ in range(width)] for _ in range(width)]
    count = xor = total = 0
    mask = (1 << 256) - 1
    for record in sorted(records, key=lambda row: row["partition_id"]):
        if record["p"] != p or record["q"] != q or record["schema_version"] != 1:
            raise ValueError("Statistic schemas differ")
        n = record["row_count"]
        ledger = record["ledger"]
        if type(n) is not int or n < 0 or ledger["count"] != n:
            raise ValueError("Statistic count/ledger differs")
        for name in ("xor", "sum"):
            text = ledger[name]
            if (
                not isinstance(text, str)
                or len(text) != 64
                or any(c not in "0123456789abcdef" for c in text)
            ):
                raise ValueError("Invalid bounded membership fingerprint")
        gram = record["gram"]
        if n == 0 and (
            any(x != 0 for row in gram for x in row)
            or any(int(ledger[name], 16) != 0 for name in ("xor", "sum"))
        ):
            raise ValueError("An empty partition must contain zero statistics and fingerprints")
        if len(gram) != width:
            raise ValueError("Gram shape differs")
        for i, line in enumerate(gram):
            values = _finite_vector(line, width)
            for j, x in enumerate(values):
                sums[i][j].add(x)
        count += n
        xor ^= int(ledger["xor"], 16)
        total = (total + int(ledger["sum"], 16)) & mask
    ledger = {"count": count, "xor": f"{xor:064x}", "sum": f"{total:064x}"}
    if count != expected_rows or ledger != expected_ledger:
        raise ValueError("Data identity/coverage differs from the fixed snapshot")
    return {
        "schema_version": 1,
        "p": p,
        "q": q,
        "row_count": count,
        "gram": [[x.value() for x in line] for line in sums],
        "ledger": ledger,
    }


def _positive_quadratic(value: float, scale: float, label: str) -> float:
    if not math.isfinite(value) or value <= 64 * math.ulp(1.0) * max(scale, 1e-300):
        raise NumericalCertificateError(
            label
            + " is nonpositive or cancellation-limited; center data or use a qualified QR reduction"
        )
    return value


def evaluate(
    statistics: dict[str, Any], theta: list[float], base_covariance: list[list[float]]
) -> dict[str, Any]:
    p, q, n = statistics["p"], statistics["q"], statistics["row_count"]
    if not 1 <= p <= 8 or not 1 <= q <= 8 or n < 1:
        raise ValueError("Unsupported global Gaussian dimensions")
    theta = _finite_vector(theta, p + 2)
    beta = theta[:p]
    s, t = math.exp(2 * theta[-2]), math.exp(2 * theta[-1])
    if not all(math.isfinite(x) and x > 0 for x in (s, t)):
        raise ValueError("Invalid Gaussian scales")
    if len(base_covariance) != q:
        raise ValueError("Latent base covariance shape differs")
    lower = cholesky(base_covariance)
    gram = statistics["gram"]
    width = p + q + 1
    if len(gram) != width:
        raise ValueError("Gram shape differs")
    gram = [_finite_vector(line, width) for line in gram]
    xx = [row[:p] for row in gram[:p]]
    xy = [row[-1] for row in gram[:p]]
    zx = [row[:p] for row in gram[p : p + q]]
    zz = [row[p : p + q] for row in gram[p : p + q]]
    zy = [row[-1] for row in gram[p : p + q]]
    yy = gram[-1][-1]
    two = 2 * dot(beta, xy)
    three = dot(beta, matvec(xx, beta))
    rr = _positive_quadratic(
        yy - two + three, abs(yy) + abs(two) + abs(three), "Residual quadratic"
    )
    cross = [v - w for v, w in zip(zy, matvec(zx, beta), strict=True)]
    lt = transpose(lower)
    g = matmul(matmul(lt, zz), lower)
    r = matvec(lt, cross)
    h = t / s
    a = [[float(i == j) + h * g[i][j] for j in range(q)] for i in range(q)]
    factor = cholesky(a)
    w = solve_cholesky(factor, r)
    inverse = inverse_small(factor)
    explained = h * dot(r, w)
    quadratic = _positive_quadratic(rr - explained, abs(rr) + abs(explained), "Marginal quadratic")
    trace = math.fsum(inverse[i][j] * g[j][i] for i in range(q) for j in range(q))
    quad2 = rr - 2 * explained + h * h * dot(w, matvec(g, w))
    _positive_quadratic(
        quad2,
        abs(rr) + 2 * abs(explained) + abs(h * h * dot(w, matvec(g, w))),
        "Inverse-squared quadratic",
    )
    wx = matmul(lt, zx)
    x_residual = [v - u for v, u in zip(xy, matvec(xx, beta), strict=True)]
    correction = matvec(transpose(wx), w)
    gradient = [-v / s + h * c / s for v, c in zip(x_residual, correction, strict=True)]
    gradient.extend([n - h * trace - quad2 / s, h * trace - h * dot(w, w) / s])
    value = 0.5 * (
        n * math.log(2 * math.pi)
        + n * math.log(s)
        + 2 * math.fsum(math.log(factor[i][i]) for i in range(q))
        + quadratic / s
    )
    posterior_covariance = [[t * x for x in row] for row in matmul(matmul(lower, inverse), lt)]
    return {
        "value": value,
        "gradient": gradient,
        "row_count": n,
        "p": p,
        "latent_rank": q,
        "latent_conditional_mean": [h * x for x in matvec(lower, w)],
        "latent_conditional_covariance": posterior_covariance,
        "scope": (
            "one global Gaussian latent vector; fixed population parameters; "
            "bounded sufficient statistics"
        ),
    }


def dense_oracle(
    rows: list[dict[str, Any]], theta: list[float], base_covariance: list[list[float]]
) -> float:
    """Independent tiny n-by-n Gaussian calculation, never the distributed algorithm."""
    n = len(rows)
    p = len(theta) - 2
    if not 1 <= n <= 64:
        raise ValueError("The independent dense oracle is limited to64 observations")
    s, t = math.exp(2 * theta[-2]), math.exp(2 * theta[-1])
    residual = [row["y"] - dot(row["x"], theta[:p]) for row in rows]
    covariance = [
        [
            s * float(i == j) + t * dot(rows[i]["z"], matvec(base_covariance, rows[j]["z"]))
            for j in range(n)
        ]
        for i in range(n)
    ]
    factor = cholesky(covariance)
    return 0.5 * (
        n * math.log(2 * math.pi)
        + 2 * math.fsum(math.log(factor[i][i]) for i in range(n))
        + dot(residual, solve_cholesky(factor, residual))
    )
