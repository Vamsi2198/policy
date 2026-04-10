#!/usr/bin/env python3
"""
Create a simple SQLite demo database for testing PII masking
"""
import sqlite3
import os

def create_demo_database():
    """Create demo SQLite database with sample PII data"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), "demo.db")
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  Removed existing database")
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"🔨 Creating demo database: {db_path}")
    
    # Create customers table
    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT
        )
    """)
    
    # Insert sample data with PII
    sample_data = [
        (1, 'John Smith', 'john.smith@email.com', '555-123-4567', '123 Main St', 'New York', 'NY', '10001'),
        (2, 'Jane Doe', 'jane.doe@email.com', '555-234-5678', '456 Oak Ave', 'Los Angeles', 'CA', '90001'),
        (3, 'Bob Johnson', 'bob.johnson@email.com', '555-345-6789', '789 Pine Rd', 'Chicago', 'IL', '60601'),
        (4, 'Alice Williams', 'alice.w@email.com', '555-456-7890', '321 Elm St', 'Houston', 'TX', '77001'),
        (5, 'Charlie Brown', 'charlie.b@email.com', '555-567-8901', '654 Maple Dr', 'Phoenix', 'AZ', '85001'),
        (6, 'Diana Prince', 'diana.prince@email.com', '555-678-9012', '987 Cedar Ln', 'Philadelphia', 'PA', '19019'),
        (7, 'Eve Martinez', 'eve.m@email.com', '555-789-0123', '147 Birch Way', 'San Antonio', 'TX', '78201'),
        (8, 'Frank Wilson', 'frank.wilson@email.com', '555-890-1234', '258 Spruce Ct', 'San Diego', 'CA', '92101'),
        (9, 'Grace Lee', 'grace.lee@email.com', '555-901-2345', '369 Willow Ave', 'Dallas', 'TX', '75201'),
        (10, 'Henry Davis', 'henry.d@email.com', '555-012-3456', '741 Ash Blvd', 'San Jose', 'CA', '95101')
    ]
    
    cursor.executemany("""
        INSERT INTO customers (customer_id, name, email, phone, address, city, state, zip_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_data)
    
    conn.commit()
    
    # Verify data
    cursor.execute("SELECT COUNT(*) FROM customers")
    count = cursor.fetchone()[0]
    
    print(f"✅ Created customers table with {count} records")
    
    # Show sample
    print(f"\n📋 Sample data:")
    cursor.execute("SELECT customer_id, name, email, phone FROM customers LIMIT 3")
    for row in cursor.fetchall():
        print(f"   ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Phone: {row[3]}")
    
    conn.close()
    
    print(f"\n✅ Demo database ready: {db_path}")
    print(f"\n🎯 Now update config.yaml to use SQLite:")
    print(f"""
platform:
  type: sqlite
  database: "{db_path}"
""")
    
    return db_path

if __name__ == "__main__":
    create_demo_database()
