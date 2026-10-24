-- 00_setup.sql
-- Repeatable schema creation and realistic seed data for the curriculum
-- Safe to run multiple times; drops and recreates the schema.

BEGIN;

-- Clean slate
DROP SCHEMA IF EXISTS training CASCADE;
CREATE SCHEMA training;
SET search_path TO training, public;

-- Core entities
CREATE TABLE customers (
  customer_id      SERIAL PRIMARY KEY,
  full_name        TEXT NOT NULL,
  email            TEXT UNIQUE,
  country          TEXT NOT NULL DEFAULT 'US',
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  segment          TEXT,
  attributes       JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE products (
  product_id   SERIAL PRIMARY KEY,
  name         TEXT NOT NULL,
  category     TEXT NOT NULL,
  price        NUMERIC(10,2) NOT NULL CHECK (price >= 0),
  cost         NUMERIC(10,2) NOT NULL CHECK (cost >= 0),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE orders (
  order_id     SERIAL PRIMARY KEY,
  customer_id  INT NOT NULL REFERENCES customers(customer_id),
  order_date   TIMESTAMPTZ NOT NULL DEFAULT now(),
  status       TEXT NOT NULL DEFAULT 'placed',
  total_amount NUMERIC(12,2) NOT NULL DEFAULT 0
);

CREATE TABLE order_items (
  order_item_id  SERIAL PRIMARY KEY,
  order_id       INT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
  product_id     INT NOT NULL REFERENCES products(product_id),
  quantity       INT NOT NULL CHECK (quantity > 0),
  unit_price     NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
  discount       NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (discount BETWEEN 0 AND 1)
);

CREATE TABLE payments (
  payment_id   SERIAL PRIMARY KEY,
  order_id     INT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
  payment_date TIMESTAMPTZ NOT NULL DEFAULT now(),
  amount       NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
  method       TEXT NOT NULL CHECK (method IN ('card','paypal','bank','credit'))
);

-- Organization / HR for hierarchies & self-joins
CREATE TABLE departments (
  department_id SERIAL PRIMARY KEY,
  name          TEXT NOT NULL UNIQUE
);

CREATE TABLE employees (
  employee_id   SERIAL PRIMARY KEY,
  full_name     TEXT NOT NULL,
  manager_id    INT REFERENCES employees(employee_id),
  department_id INT REFERENCES departments(department_id),
  hire_date     DATE NOT NULL DEFAULT CURRENT_DATE,
  salary        NUMERIC(10,2) NOT NULL CHECK (salary >= 0)
);

-- Events with JSONB payloads for semi-structured queries
CREATE TABLE events (
  event_id     BIGSERIAL PRIMARY KEY,
  customer_id  INT REFERENCES customers(customer_id),
  event_time   TIMESTAMPTZ NOT NULL DEFAULT now(),
  event_type   TEXT NOT NULL,
  metadata     JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Finance helpers
CREATE TABLE expenses (
  expense_id   SERIAL PRIMARY KEY,
  category     TEXT NOT NULL,
  amount       NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
  expense_date DATE NOT NULL
);

CREATE TABLE budgets (
  budget_id SERIAL PRIMARY KEY,
  category  TEXT NOT NULL,
  period    DATE NOT NULL, -- first day of month
  amount    NUMERIC(12,2) NOT NULL CHECK (amount >= 0)
);

CREATE TABLE promotions (
  promotion_id SERIAL PRIMARY KEY,
  product_id   INT NOT NULL REFERENCES products(product_id),
  start_date   DATE NOT NULL,
  end_date     DATE NOT NULL,
  discount_rate NUMERIC(4,3) NOT NULL CHECK (discount_rate BETWEEN 0 AND 1),
  CHECK (end_date >= start_date)
);

-- XML sample table
CREATE TABLE xml_docs (
  doc_id SERIAL PRIMARY KEY,
  payload XML NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Seed data
--
-- The course data is intentionally deterministic. Relationships are derived
-- from integer arithmetic instead of uncorrelated random() subqueries, which
-- PostgreSQL may evaluate only once per statement. Dates remain relative to
-- the transaction's CURRENT_DATE so "last N days" lessons do not go stale.

INSERT INTO customers(full_name, email, country, created_at, segment, attributes)
SELECT
  'Customer ' || gs,
  'customer' || gs || '@example.com',
  (ARRAY['US','CA','GB','DE','FR','IN','AU','BR'])[((gs - 1) % 8) + 1],
  CURRENT_DATE::timestamptz
    + interval '12 hours'
    - ((((gs * 17) % 1460) + 30) * interval '1 day')
    - (((gs * 13) % 24) * interval '1 hour'),
  (ARRAY['standard','silver','gold','platinum'])[((gs - 1) % 4) + 1],
  jsonb_build_object(
    'channel', (ARRAY['web','mobile','store'])[((gs - 1) % 3) + 1],
    'referrer', (ARRAY['seo','email','ad','direct'])[((gs - 1) % 4) + 1]
  )
FROM generate_series(1, 500) AS g(gs)
ORDER BY gs;

WITH product_seed AS (
  SELECT
    gs,
    (ARRAY['Apparel','Electronics','Home','Beauty','Sports','Books'])[((gs - 1) % 6) + 1] AS category,
    round((10 + ((gs * 37) % 49000) / 100.0)::numeric, 2) AS price
  FROM generate_series(1, 300) AS g(gs)
)
INSERT INTO products(name, category, price, cost, created_at)
SELECT
  'Product ' || gs,
  category,
  price,
  round(price * (0.35 + ((gs * 13) % 40) / 100.0)::numeric, 2),
  CASE
    -- Sold products predate the full order history, preserving temporal joins.
    WHEN gs <= 275 THEN
      CURRENT_DATE::timestamptz
        + interval '12 hours'
        - ((1825 + ((gs * 29) % 365)) * interval '1 day')
    -- Unsold products include recent catalog additions for date-filter lessons.
    ELSE
      CURRENT_DATE::timestamptz
        + interval '12 hours'
        - ((1 + ((gs * 29) % 75)) * interval '1 day')
  END
FROM product_seed
ORDER BY gs;

INSERT INTO departments(name)
SELECT name
FROM unnest(ARRAY['Sales','Engineering','HR','Finance','Marketing','Operations'])
  WITH ORDINALITY AS d(name, position)
ORDER BY position;

INSERT INTO employees(full_name, manager_id, department_id, hire_date, salary)
SELECT
  'Employee ' || employee_no,
  CASE
    WHEN employee_no <= 6 THEN NULL
    ELSE 1 + ((employee_no * 7) % (employee_no - 1))
  END,
  ((employee_no - 1) % 6) + 1,
  CURRENT_DATE - ((employee_no * 37) % 3650),
  round((40000 + ((employee_no * 7919) % 9000000) / 100.0)::numeric, 2)
FROM generate_series(1, 100) AS e(employee_no)
ORDER BY employee_no;

-- Customers outside BR receive 4-16 orders, all after signup and spread across
-- the customer's observed lifetime. BR is intentionally an event-only
-- customer market, so outer-join, EXCEPT, and anti-join exercises return
-- meaningful examples. The active cohort supplies more than three years of
-- complete history for YoY, retention, and forecasting lessons.
WITH generated_orders AS (
  SELECT
    c.customer_id,
    order_no,
    c.created_at
      + (CURRENT_TIMESTAMP - c.created_at)
        * (order_no::double precision / (5 + (c.customer_id % 13))::double precision) AS order_date,
    (ARRAY['placed','paid','shipped','delivered','returned'])
      [((c.customer_id + order_no - 1) % 5) + 1] AS status
  FROM customers c
  CROSS JOIN LATERAL generate_series(1, 4 + (c.customer_id % 13)) AS s(order_no)
  WHERE c.country <> 'BR'
)
INSERT INTO orders(customer_id, order_date, status, total_amount)
SELECT customer_id, order_date, status, 0
FROM generated_orders
ORDER BY customer_id, order_no;

-- Each order receives 1-5 distinct products drawn from products 1-275.
-- Products 276-300 intentionally remain unsold for outer/anti-join exercises;
-- all six categories are still represented among sold products.
WITH generated_items AS (
  SELECT
    o.order_id,
    item_no,
    1 + ((o.order_id * 17 + item_no * 31 - 1) % 275) AS product_id,
    1 + ((o.order_id + item_no) % 5) AS quantity,
    CASE
      WHEN (o.order_id + item_no) % 11 = 0 THEN 0.15::numeric
      WHEN (o.order_id + item_no) % 5 = 0 THEN 0.05::numeric
      ELSE 0::numeric
    END AS discount
  FROM orders o
  CROSS JOIN LATERAL generate_series(1, 1 + (o.order_id % 5)) AS s(item_no)
)
INSERT INTO order_items(order_id, product_id, quantity, unit_price, discount)
SELECT
  gi.order_id,
  gi.product_id,
  gi.quantity,
  p.price,
  gi.discount
FROM generated_items gi
JOIN products p ON p.product_id = gi.product_id
ORDER BY gi.order_id, gi.item_no;

UPDATE orders o
SET total_amount = totals.total
FROM (
  SELECT
    order_id,
    round(SUM((unit_price * quantity) * (1 - discount)), 2) AS total
  FROM order_items
  GROUP BY order_id
) AS totals
WHERE totals.order_id = o.order_id;

-- Placed orders remain unpaid. Other orders receive one or two payments, with
-- a deterministic subset intentionally left partially paid.
WITH payment_plan AS (
  SELECT
    o.order_id,
    o.order_date,
    o.total_amount,
    CASE WHEN o.order_id % 10 = 0 THEN 2 ELSE 1 END AS payment_parts,
    round(
      o.total_amount
        * CASE WHEN o.order_id % 17 = 0 THEN 0.50::numeric ELSE 1::numeric END,
      2
    ) AS target_paid
  FROM orders o
  WHERE o.status <> 'placed'
), payment_rows AS (
  SELECT
    pp.*,
    part_no,
    round(pp.target_paid / pp.payment_parts, 2) AS regular_part
  FROM payment_plan pp
  CROSS JOIN LATERAL generate_series(1, pp.payment_parts) AS p(part_no)
)
INSERT INTO payments(order_id, payment_date, amount, method)
SELECT
  order_id,
  LEAST(
    order_date + ((part_no * 6 + order_id % 48) * interval '1 hour'),
    CURRENT_TIMESTAMP
  ),
  CASE
    WHEN part_no < payment_parts THEN regular_part
    ELSE target_paid - regular_part * (payment_parts - 1)
  END,
  (ARRAY['card','paypal','bank','credit'])[((order_id + part_no - 1) % 4) + 1]
FROM payment_rows
ORDER BY order_id, part_no;

-- Forty events per customer provide complete overlap between behavioral and
-- transactional cohorts while retaining varied event types and metadata.
INSERT INTO events(customer_id, event_time, event_type, metadata)
SELECT
  c.customer_id,
  c.created_at
    + (CURRENT_TIMESTAMP - c.created_at)
      * (event_no::double precision / 41.0),
  (ARRAY['page_view','add_to_cart','checkout','purchase','support'])
    [((c.customer_id + event_no - 1) % 5) + 1],
  jsonb_build_object(
    'path', (ARRAY['/','/p/1','/p/2','/search','/cart','/help'])
      [((c.customer_id + event_no - 1) % 6) + 1],
    'device', (ARRAY['ios','android','web'])[((c.customer_id + event_no - 1) % 3) + 1],
    'campaign', (ARRAY['spring','summer','fall','winter','none'])
      [((c.customer_id * 3 + event_no - 1) % 5) + 1]
  )
FROM customers c
CROSS JOIN generate_series(1, 40) AS e(event_no)
ORDER BY c.customer_id, event_no;

INSERT INTO expenses(category, amount, expense_date)
SELECT
  (ARRAY['COGS','Marketing','Payroll','Infrastructure','G&A'])[((gs - 1) % 5) + 1],
  round((100 + ((gs * 104729) % 990000) / 100.0)::numeric, 2),
  CURRENT_DATE - ((gs * 19) % 730)
FROM generate_series(1, 10000) AS g(gs)
ORDER BY gs;

INSERT INTO budgets(category, period, amount)
SELECT
  category,
  (date_trunc('month', CURRENT_DATE) - (month_no * interval '1 month'))::date,
  round(
    base_amount
      * (0.85 + ((month_no * 7 + category_no * 11) % 31) / 100.0)::numeric,
    2
  )
FROM generate_series(0, 24) AS m(month_no)
CROSS JOIN (
  VALUES
    ('COGS', 600000::numeric, 1),
    ('Marketing', 200000::numeric, 2),
    ('Payroll', 800000::numeric, 3),
    ('Infrastructure', 300000::numeric, 4),
    ('G&A', 150000::numeric, 5)
) AS b(category, base_amount, category_no)
ORDER BY month_no, category_no;

WITH promotion_seed AS (
  SELECT
    gs,
    1 + ((gs * 43 - 1) % 300) AS product_id,
    CURRENT_DATE - ((gs * 13) % 360) AS start_date
  FROM generate_series(1, 200) AS g(gs)
), adjusted_promotions AS (
  SELECT ps.gs,
         ps.product_id,
         GREATEST(ps.start_date, p.created_at::date) AS start_date
  FROM promotion_seed ps
  JOIN products p USING (product_id)
)
INSERT INTO promotions(product_id, start_date, end_date, discount_rate)
SELECT
  product_id,
  start_date,
  start_date + 30 + ((gs * 17) % 90),
  (0.05 + ((gs * 7) % 26) / 100.0)::numeric(4,3)
FROM adjusted_promotions
ORDER BY gs;

INSERT INTO xml_docs(payload)
SELECT xmlparse(
  document
    '<order><id>' || o.order_id || '</id><status>' || o.status || '</status></order>'
)
FROM orders o
ORDER BY o.order_id
LIMIT 1000;

COMMIT;
