-- 00_setup.sql
-- One-time schema creation and realistic seed data for the 60-day curriculum
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
  discount       NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (discount >= 0)
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
  discount_rate NUMERIC(4,3) NOT NULL CHECK (discount_rate BETWEEN 0 AND 1)
);

-- XML sample table
CREATE TABLE xml_docs (
  doc_id SERIAL PRIMARY KEY,
  payload XML NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Seed data
-- Countries and segments
WITH ctry AS (
  SELECT unnest(ARRAY['US','US','US','CA','GB','DE','FR','IN','AU','BR']) AS country
)
INSERT INTO customers(full_name,email,country,created_at,segment,attributes)
SELECT 
  'Customer ' || gs::text,
  'customer' || gs::text || '@example.com',
  (SELECT country FROM ctry ORDER BY random() LIMIT 1),
  now() - (INTERVAL '1 day' * (random()*730)::int),
  (ARRAY['standard','silver','gold','platinum'])[(1 + floor(random()*4))::int],
  jsonb_build_object(
    'channel', (ARRAY['web','mobile','store'])[(1 + floor(random()*3))::int],
    'referrer', (ARRAY['seo','email','ad','direct'])[(1 + floor(random()*4))::int]
  )
FROM generate_series(1, 500) gs;

INSERT INTO products(name, category, price, cost, created_at)
SELECT 
  'Product ' || gs::text,
  (ARRAY['Apparel','Electronics','Home','Beauty','Sports','Books'])[(1 + floor(random()*6))::int],
  round((10 + random()*490)::numeric, 2),
  round((5 + random()*200)::numeric, 2),
  now() - (INTERVAL '1 day' * (random()*730)::int)
FROM generate_series(1, 300) gs;

-- Departments
INSERT INTO departments(name)
SELECT unnest(ARRAY['Sales','Engineering','HR','Finance','Marketing','Operations']);

-- Employees with hierarchical managers
WITH base AS (
  SELECT gs AS n FROM generate_series(1, 100) gs
)
INSERT INTO employees(full_name, manager_id, department_id, hire_date, salary)
SELECT 
  'Employee ' || n::text,
  CASE WHEN n <= 5 THEN NULL ELSE (1 + floor(random()* (n-1))::int) END,
  (SELECT department_id FROM departments ORDER BY random() LIMIT 1),
  (CURRENT_DATE - ((random()*365*5)::int))::date,
  round((40000 + random()*90000)::numeric, 2)
FROM base;

-- Orders and items
WITH o AS (
  SELECT 
    gs AS n,
    (SELECT customer_id FROM customers ORDER BY random() LIMIT 1) AS cid,
    now() - (INTERVAL '1 hour' * (random()*24*365)::int) AS odt,
    (ARRAY['placed','paid','shipped','delivered','returned'])[(1 + floor(random()*5))::int] AS st
  FROM generate_series(1, 5000) gs
)
INSERT INTO orders(customer_id, order_date, status, total_amount)
SELECT cid, odt, st, 0 FROM o;

-- Items per order
WITH items AS (
  SELECT 
    o.order_id,
    p.product_id,
    (1 + floor(random()*5))::int AS qty,
    p.price AS unit_price,
    round((CASE WHEN random() < 0.2 THEN (random()*0.3) ELSE 0 END)::numeric, 2) AS discount
  FROM orders o
  JOIN LATERAL (
    SELECT product_id, price FROM products ORDER BY random() LIMIT (1 + floor(random()*5))::int
  ) p ON TRUE
)
INSERT INTO order_items(order_id, product_id, quantity, unit_price, discount)
SELECT order_id, product_id, qty, unit_price, discount FROM items;

-- Update order totals
UPDATE orders o
SET total_amount = sub.total
FROM (
  SELECT order_id, SUM((unit_price * quantity) * (1 - discount)) AS total
  FROM order_items
  GROUP BY order_id
) sub
WHERE sub.order_id = o.order_id;

-- Payments (some partial or multi-payments)
INSERT INTO payments(order_id, payment_date, amount, method)
SELECT 
  o.order_id,
  o.order_date + (random()*5 || ' days')::interval,
  round(o.total_amount * (CASE WHEN random() < 0.1 THEN 0.5 ELSE 1 END),2),
  (ARRAY['card','paypal','bank','credit'])[(1 + floor(random()*4))::int]
FROM orders o
WHERE random() > 0.05; -- a few unpaid

-- Events
INSERT INTO events(customer_id, event_time, event_type, metadata)
SELECT 
  (SELECT customer_id FROM customers ORDER BY random() LIMIT 1),
  now() - (random()*'180 days'::interval),
  (ARRAY['page_view','add_to_cart','checkout','purchase','support'])[(1 + floor(random()*5))::int],
  jsonb_build_object(
    'path', (ARRAY['/','/p/1','/p/2','/search','/cart','/help'])[(1 + floor(random()*6))::int],
    'device', (ARRAY['ios','android','web'])[(1 + floor(random()*3))::int],
    'campaign', (ARRAY['spring','summer','fall','winter','none'])[(1 + floor(random()*5))::int]
  )
FROM generate_series(1, 20000);

-- Expenses and budgets (2 years)
INSERT INTO expenses(category, amount, expense_date)
SELECT 
  (ARRAY['COGS','Marketing','Payroll','Infrastructure','G&A'])[(1 + floor(random()*5))::int],
  round((100 + random()*10000)::numeric, 2),
  (CURRENT_DATE - (random()*365*2)::int)::date
FROM generate_series(1, 10000);

INSERT INTO budgets(category, period, amount)
SELECT 
  cat,
  (date_trunc('month', CURRENT_DATE) - (gs || ' months')::interval)::date,
  round((CASE cat WHEN 'Marketing' THEN 200000 WHEN 'Payroll' THEN 800000 WHEN 'Infrastructure' THEN 300000 WHEN 'COGS' THEN 600000 ELSE 150000 END) * (0.7 + random()*0.6), 2)
FROM generate_series(0, 24) gs
CROSS JOIN (VALUES ('COGS'),('Marketing'),('Payroll'),('Infrastructure'),('G&A')) v(cat);

-- Promotions
INSERT INTO promotions(product_id, start_date, end_date, discount_rate)
SELECT 
  (SELECT product_id FROM products ORDER BY random() LIMIT 1),
  (CURRENT_DATE - (random()*180)::int)::date,
  (CURRENT_DATE + (random()*60)::int)::date,
  round((0.05 + random()*0.25)::numeric, 3)
FROM generate_series(1, 200);

-- XML docs
INSERT INTO xml_docs(payload)
SELECT xmlparse(document '<order><id>' || o.order_id || '</id><status>'|| o.status ||'</status></order>')
FROM orders o ORDER BY random() LIMIT 1000;

COMMIT;
