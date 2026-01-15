# Day 20 — Solutions: Pandas Merging and Joins

We build product and order item tables, compute revenue by customer, demonstrate right join, and validate merge cardinality.

Contents
- Exercise 1: Join products/order_items/customer to compute revenue
- Exercise 2: Right join example and when it’s useful
- Exercise 3: validate='one_to_many' to catch duplicates

---

Setup
```python
import pandas as pd

customers = pd.DataFrame({"cid":[1,2,3], "name":["Ada","Alan","Linus"]})
products  = pd.DataFrame({"sku":["A","B"], "price":[10.0, 5.0]})
order_items = pd.DataFrame({
    "oid":[10,10,11,12],
    "cid":[1,1,1,3],
    "sku":["A","B","A","B"],
    "qty":[2,1,1,3],
})
```

Exercise 1 — Revenue by customer
```python
items = order_items.merge(products, on='sku', how='left', validate='m:1')
items = items.assign(revenue=items['qty'] * items['price'])
by_cust = (items
    .groupby('cid', as_index=False)
    .agg(revenue=('revenue','sum'))
    .merge(customers, on='cid', how='left', validate='1:1')
    .loc[:, ['cid','name','revenue']]
)
by_cust
```

Exercise 2 — Right join
```python
# Right join all customers with any orders (keep all orders even if cid missing from customers)
right_demo = order_items.merge(customers, on='cid', how='right', indicator=True)
right_demo['_merge'].value_counts()
```
When useful: preserving all rows from the right table regardless of matches (often you want left joins from a primary fact table; right is symmetric but less common).

Exercise 3 — validate to catch duplicates
```python
# Expect each (sku) to map to a single product row; enforce m:1
items = order_items.merge(products, on='sku', how='left', validate='m:1')
# If a product appears twice, pandas raises MergeError explaining the violation.
```
Notes
- Always think about join cardinality; use validate to enforce expectations.
- Align dtypes for keys before merging to avoid surprises.
