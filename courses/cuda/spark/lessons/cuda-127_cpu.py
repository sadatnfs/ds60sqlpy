"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

sales = [("A", 2), ("A", 4), ("B", 3)]
prices = {"A": 10, "B": 20}
revenue = {}
for product, quantity in sales:
    revenue[product] = revenue.get(product, 0) + quantity * prices[product]
assert sorted(revenue.items()) == [("A", 60), ("B", 60)]
print("CPU ETL oracle:", sorted(revenue.items()))
