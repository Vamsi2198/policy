"""Quick check - what masking policies exist?"""
import snowflake.connector
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

p = config['platform']
conn = snowflake.connector.connect(
    account=p['account'], user=p['user'], password=p['password'],
    warehouse=p['warehouse'], database=p['database'], 
    schema=p['schema'], role=p['role']
)

print("\n=== MASKING POLICIES ===")
cur = conn.cursor()
cur.execute("SHOW MASKING POLICIES")
policies = cur.fetchall()
print(f"Total policies: {len(policies)}")
for p in policies:
    print(f"  - {p[1]}")

print("\n=== MASKED COLUMNS ===")
cur.execute("""
    SELECT TABLE_NAME, COLUMN_NAME, MASKING_POLICY_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'PUBLIC'
    AND TABLE_NAME = 'CUSTOMERS'
    AND MASKING_POLICY_NAME IS NOT NULL
""")
cols = cur.fetchall()
print(f"Total masked columns: {len(cols)}")
for c in cols:
    print(f"  - {c[0]}.{c[1]} → {c[2]}")

conn.close()
print("\nDone!")
