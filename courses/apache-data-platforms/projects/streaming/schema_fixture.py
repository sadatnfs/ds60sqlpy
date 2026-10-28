"""Local application validation only; no schema-registry service is implied."""

import json


def validate(encoded):
    row = json.loads(encoded)
    if type(row) is not dict or not {"id", "amount"} <= set(row):
        raise ValueError("Missing required field")
    if type(row["id"]) is not str or type(row["amount"]) is not int:
        raise ValueError("Incompatible field type")
    return {"id": row["id"], "amount": row["amount"]}


assert validate('{"id":"a","amount":4}') == {"id": "a", "amount": 4}
assert validate('{"id":"a","amount":4,"region":"east"}') == {"id": "a", "amount": 4}
for source in ['{"id":"a","amount":"four"}', '{"id":"a","amount":true}', '{"id":"a"}']:
    try:
        validate(source)
    except ValueError:
        pass
    else:
        raise AssertionError("Incompatible event accepted")
print("Local validator: additive field accepted; missing/incompatible amount rejected")
