-- Prepared extension, separate table and acceptance receipt required.
CREATE EXTERNAL TABLE ds60.orders_iceberg (id INT, region STRING, amount INT)
STORED BY ICEBERG LOCATION 'file:///warehouse/orders_iceberg';
INSERT INTO ds60.orders_iceberg VALUES (1, 'east', 4), (2, 'west', 9), (3, 'east', 7);
SELECT * FROM ds60.orders_iceberg ORDER BY id;
