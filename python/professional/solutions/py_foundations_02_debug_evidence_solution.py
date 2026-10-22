"""Small reproducible checks for python-foundations-02."""

raw = " 08 "
assert repr(raw) == "' 08 '"
quantity = int(raw)
assert quantity == 8 and quantity + 1 == 9
try:
    int("eight")
except ValueError:
    invalid_word_seen = True
else:
    invalid_word_seen = False
assert invalid_word_seen
assert (19 >= 20, 20 >= 20, 21 >= 20) == (False, True, True)
try:
    int("4.5")
except ValueError:
    invalid_integer_seen = True
else:
    invalid_integer_seen = False
assert invalid_integer_seen
price = 7
quantity = 3
discount = 2
assert price * (quantity - discount) == 7
assert price * quantity - discount == 19
assert price * (quantity - 0) == price * quantity - 0 == 21
try:
    parsed_quantity = int("unknown")
    conversion_status = "accepted"
except ValueError:
    conversion_status = "invalid quantity"
assert conversion_status == "invalid quantity"
try:
    parsed_quantity = int("4")
    conversion_status = "accepted"
except ValueError:
    conversion_status = "invalid quantity"
assert conversion_status == "accepted" and parsed_quantity == 4
assert "2" + "3" == "23"
assert 2 + 3 == 5
assert 20 >= 20
assert 7 * 3 - 2 == 19
if __name__ == "__main__":
    print("Boundary and regression checks passed; inspect your investigation log too.")
