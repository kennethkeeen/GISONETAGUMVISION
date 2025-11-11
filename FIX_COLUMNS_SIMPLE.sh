#!/bin/bash
# Simple script to add zone columns - run this in DigitalOcean Console

python manage.py shell << 'EOF'
from django.db import connection
c = connection.cursor()
try:
    c.execute("ALTER TABLE projeng_project ADD COLUMN IF NOT EXISTS zone_type VARCHAR(20) NULL")
    print("Added zone_type column")
except Exception as e:
    print(f"zone_type: {e}")
try:
    c.execute("ALTER TABLE projeng_project ADD COLUMN IF NOT EXISTS zone_validated BOOLEAN DEFAULT FALSE")
    print("Added zone_validated column")
except Exception as e:
    print(f"zone_validated: {e}")
print("Done")
EOF

