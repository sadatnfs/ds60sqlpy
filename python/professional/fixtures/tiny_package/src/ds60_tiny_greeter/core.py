"""Core behavior kept separate from the console adapter."""


def greeting(name: str) -> str:
    """Return a deterministic greeting."""

    clean_name = name.strip()
    if not clean_name:
        raise ValueError("name must contain at least one non-space character")
    return f"Hello, {clean_name}!"
