"""Original JAX teaching units, independent of runtime registration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Case:
    title: str
    task: str
    expected: str
    explanation: str
    code: str
    hint: str


@dataclass(frozen=True)
class Unit:
    number: int
    title: str
    level: str
    prerequisites: tuple[int, ...]
    concepts: tuple[str, ...]
    outcome: str
    narrative: str
    derivation: str
    setup: str
    worked: tuple[Case, Case]
    practice: tuple[Case, Case, Case, Case, Case, Case]
    diagnosis: str
    transfer: str
    sources: tuple[tuple[str, str], ...]
    runtime: str = "jax-cpu"

    @property
    def id(self) -> str:
        return f"jax-{self.number:03d}"


HEADER = '''"""Small offline JAX mechanism investigation; CPU evidence only."""
from __future__ import annotations

import math
import numpy as np
import jax
import jax.numpy as jnp

# Choose precision before creating arrays; the usual JAX default is 32 bit.
jax.config.update("jax_enable_x64", True)


def close(actual, expected, *, atol=1e-10, rtol=1e-10):
    np.testing.assert_allclose(np.asarray(actual), expected, atol=atol, rtol=rtol)

'''


def case(title: str, task: str, expected: str, explanation: str, code: str, hint: str) -> Case:
    return Case(title, task, expected, explanation, code.strip(), hint)
