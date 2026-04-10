-- Insert orders
INSERT INTO orders (customer_id, order_date, total_amount, status, shipping_address, payment_method) VALUES
(1, '2024-12-01', 149.99, 'completed', '123 Main St, New York, NY 10001', 'credit_card_4532'),
(2, '2024-12-02', 299.99, 'completed', '456 Oak Ave, Los Angeles, CA 90001', 'credit_card_5123'),
(3, '2024-12-03', 89.99, 'shipped', '789 Pine Rd, Chicago, IL 60601', 'credit_card_4916'),
(1, '2024-12-04', 199.99, 'completed', '123 Main St, New York, NY 10001', 'credit_card_4532'),
(4, '2024-12-05', 449.99, 'processing', '321 Elm St, Houston, TX 77001', 'credit_card_5412'),
(5, '2024-12-06', 99.99, 'shipped', '654 Maple Dr, Phoenix, AZ 85001', 'paypal'),
(2, '2024-12-07', 349.99, 'completed', '456 Oak Ave, Los Angeles, CA 90001', 'credit_card_5123'),
(6, '2024-12-08', 179.99, 'processing', '987 Cedar Ln, Philadelphia, PA 19101', 'credit_card_4539'),
(7, '2024-12-09', 259.99, 'completed', '147 Birch Way, San Antonio, TX 78201', 'credit_card_5321'),
(3, '2024-12-10', 129.99, 'shipped', '789 Pine Rd, Chicago, IL 60601', 'credit_card_4916');

-- Transactions table with credit card info
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10, 2),
    card_number VARCHAR(19),
    card_holder VARCHAR(100),
    cvv VARCHAR(4),
    status VARCHAR(20)
);

-- Insert transactions (with fake but realistic-looking credit cards)
INSERT INTO transactions (order_id, transaction_date, amount, card_number, card_holder, cvv, status) VALUES
(1, '2024-12-01', 149.99, '4532-1234-5678-9010', 'John Smith', '123', 'approved'),
(2, '2024-12-02', 299.99, '5123-4567-8901-2345', 'Jane Doe', '456', 'approved'),
(3, '2024-12-03', 89.99, '4916-7890-1234-5678', 'Michael Johnson', '789', 'approved'),
(4, '2024-12-04', 199.99, '4532-1234-5678-9010', 'John Smith', '123', 'approved'),
(5, '2024-12-05', 449.99, '5412-3456-7890-1234', 'Emily Williams', '234', 'pending'),
(7, '2024-12-07', 349.99, '5123-4567-8901-2345', 'Jane Doe', '456', 'approved'),
(8, '2024-12-08', 179.99, '4539-2345-6789-0123', 'Sarah Jones', '567', 'pending'),
(9, '2024-12-09', 259.99, '5321-6789-0123-4567', 'James Garcia', '890', 'approved'),
(10, '2024-12-10', 129.99, '4916-7890-1234-5678', 'Michael Johnson', '789', 'approved');

-- User activity log
CREATE TABLE user_activity (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    activity_type VARCHAR(50),
    ip_address VARCHAR(45),
    user_agent TEXT,
    activity_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert activity logs
INSERT INTO user_activity (customer_id, activity_type, ip_address, user_agent, activity_timestamp) VALUES
(1, 'login', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', '2024-12-01 09:00:00'),
(1, 'view_product', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', '2024-12-01 09:15:00'),
(1, 'add_to_cart', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', '2024-12-01 09:20:00'),
(2, 'login', '10.0.0.50', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', '2024-12-02 10:00:00'),
(2, 'search', '10.0.0.50', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', '2024-12-02 10:05:00'),
(3, 'login', '172.16.0.75', 'Mozilla/5.0 (X11; Linux x86_64)', '2024-12-03 11:00:00');

-- Products table (no PII, for quality testing)
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    description TEXT,
    price DECIMAL(10, 2),
    stock_quantity INTEGER,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert products with some nulls for quality testing
INSERT INTO products (name, description, price, stock_quantity, category) VALUES
('Laptop Pro 15', 'High-performance laptop', 1299.99, 50, 'Electronics'),
('Wireless Mouse', NULL, 29.99, 200, 'Electronics'),
('USB-C Cable', '6ft charging cable', NULL, 500, 'Accessories'),
('Mechanical Keyboard', 'RGB backlit keyboard', 89.99, 0, 'Electronics'),
('Monitor 27"', '4K UHD display', 449.99, NULL, 'Electronics'),
('Desk Lamp', 'LED adjustable lamp', 39.99, 150, 'Office'),
('Notebook', NULL, 12.99, 1000, 'Stationery'),
('Pen Set', 'Professional writing set', NULL, 300, 'Stationery'),
('Headphones', 'Noise-canceling wireless', 199.99, 75, 'Electronics'),
('Webcam HD', '1080p streaming camera', 79.99, NULL, 'Electronics');

-- Create table with intentional quality issues
CREATE TABLE data_quality_test (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    metric_value DECIMAL(10, 2),
    measurement_date DATE,
    notes TEXT,
    status VARCHAR(20)
);

-- Insert data with quality issues (nulls, duplicates)
INSERT INTO data_quality_test (user_id, metric_value, measurement_date, notes, status) VALUES
(1, 100.50, '2024-12-01', 'Normal reading', 'valid'),
(1, 100.50, '2024-12-01', 'Normal reading', 'valid'),  -- Duplicate
(2, NULL, '2024-12-02', NULL, 'valid'),  -- Nulls
(3, 250.75, '2024-12-03', 'High reading', 'valid'),
(NULL, 180.00, '2024-12-04', 'Unknown user', 'invalid'),  -- Null user
(4, -50.00, '2024-12-05', 'Invalid negative', 'error'),  -- Data anomaly
(5, 300.00, NULL, 'Missing date', 'valid'),  -- Null date
(2, NULL, '2024-12-02', NULL, 'valid');  -- Duplicate with nulls

-- Create indexes
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_ssn ON customers(ssn);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_transactions_order ON transactions(order_id);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO testuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO testuser;

-- Summary
SELECT 'Database initialized with test data' as status,
       (SELECT COUNT(*) FROM customers) as customers,
       (SELECT COUNT(*) FROM orders) as orders,
       (SELECT COUNT(*) FROM transactions) as transactions,
       (SELECT COUNT(*) FROM products) as products;