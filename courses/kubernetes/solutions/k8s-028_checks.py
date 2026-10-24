def accepted(packet):
    return all(
        packet[k]
        for k in (
            "application",
            "data",
            "allowed_path",
            "denied_path",
            "authorization",
            "cleanup_or_retention",
        )
    )


def main():
    packet = dict.fromkeys(
        (
            "application",
            "data",
            "allowed_path",
            "denied_path",
            "authorization",
            "cleanup_or_retention",
        ),
        True,
    )
    assert accepted(packet)
    for key in packet:
        bad = {**packet, key: False}
        assert not accepted(bad)
    before = "h1"
    read_after = "h1"
    assert before == read_after
    print("k8s-028 synthetic multi-gate capstone logic passed; full host acceptance is separate")


if __name__ == "__main__":
    main()
