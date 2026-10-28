import pyarrow as pa
import pyarrow.compute as pc

quantities = pa.array([[2, None], [], None], type=pa.list_(pa.int64()))
assert quantities.to_pylist() == [[2, None], [], None]
assert quantities.offsets.to_pylist() == [0, 2, 2, 2]
assert quantities.null_count == 1 and quantities.values.null_count == 1
assert pc.list_value_length(quantities).to_pylist() == [2, 0, None]
address_type = pa.struct([("city", pa.string()), ("postal", pa.string())])
addresses = pa.array([{"city": "Example City", "postal": None}, None], type=address_type)
assert addresses.to_pylist() == [{"city": "Example City", "postal": None}, None]
left = pa.array(["east", "west", "east", None]).dictionary_encode()
right = pa.array(["west", "east", "west", None]).dictionary_encode()
assert left.dictionary[0].as_py() == "east"
assert right.dictionary[0].as_py() == "west"
assert left.indices.to_pylist() == right.indices.to_pylist()
assert left.dictionary_decode().to_pylist() != right.dictionary_decode().to_pylist()
assert left.dictionary_decode().to_pylist() == ["east", "west", "east", None]
print("List lengths preserve missing collections:", pc.list_value_length(quantities).to_pylist())
print("Same physical indices, different dictionaries:", left.indices.to_pylist())
print("Decoded left:", left.dictionary_decode().to_pylist())
print("Decoded right:", right.dictionary_decode().to_pylist())
