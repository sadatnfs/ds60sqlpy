"""Phase-safe diagnostics preserve native ACL execution and conceal account data."""

from scripts.check_windows_private_acl import instrument_script, observed_phases


def test_native_diagnostics_extract_only_known_fixed_phases() -> None:
    output = (
        "synthetic-account-name\nDS60-ACL-PHASE:startup\nprivate-path-value\n"
        "DS60-ACL-PHASE:read-acl\nDS60-ACL-PHASE:untrusted-value\n"
    )
    assert observed_phases(output) == ["startup", "read-acl"]
    assert observed_phases(output.encode()) == ["startup", "read-acl"]
    assert observed_phases(None) == []


def test_native_phase_instrumentation_preserves_original_statements() -> None:
    source = (
        "\n$sid=identify\nif($env:DS60_PRIVATE_ESTABLISH) {\n  Set-Acl fixture\n}\n$observed=read\n"
    )
    instrumented = instrument_script(source)
    original = "\n".join(
        line
        for line in instrumented.splitlines()
        if not line.startswith("Write-Output 'DS60-ACL-PHASE:")
    )
    assert original == source.rstrip("\n")
    assert instrumented.index("PHASE:identity") < instrumented.index("$sid=identify")
    assert instrumented.index("PHASE:read-acl") < instrumented.index("$observed=read")
