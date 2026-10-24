"""Straight-line reference for python-foundations-01, with no hidden state."""

apples = 2
pears = apples + 3
apples = 9
assert (apples, pears) == (9, 5)
boxes = 4
items_per_box = 6
items = boxes * items_per_box
assert items == 24
assert 0 * items_per_box == 0
assert "3" + "7" == "37"
assert 3 + 7 == 10
# The failing print(balance) is intentionally not executed before assignment.
balance = 10
assert balance == 10
quantity = 2
unit_price = 5
total = quantity * unit_price
quantity = 3
assert total == 10
assert quantity * unit_price == 15
# Four times five is twenty. Comments do not change this calculation.
assert 4 * 5 == 20
original = 8
copied = original
original = 11
assert (original, copied) == (11, 8)
tickets = 3
ticket_price = 7
order_discount = 2
payable = tickets * ticket_price - order_discount
assert payable == 19
assert 0 * ticket_price - 0 == 0
if __name__ == "__main__":
    print("Eight reference checks passed; compare your prediction traces as well.")
