# 🔧 Fix: Add Columns Without psql

Since `psql` is not installed, use Django shell instead.

## Quick Fix: Use Django Shell

### Step 1: Run This Command
```bash
python manage.py shell
```

### Step 2: Copy and Paste This Code
Once you see `>>>`, paste this entire block:

```python
from django.db import connection

with connection.cursor() as cursor:
    # Add zone_type column
    try:
        cursor.execute("ALTER TABLE projeng_project ADD COLUMN zone_type VARCHAR(20) NULL;")
        print("✓ Added zone_type column")
    except Exception as e:
        if 'already exists' in str(e).lower():
            print("✓ zone_type already exists")
        else:
            print(f"Error: {e}")
    
    # Add zone_validated column
    try:
        cursor.execute("ALTER TABLE projeng_project ADD COLUMN zone_validated BOOLEAN DEFAULT FALSE;")
        print("✓ Added zone_validated column")
    except Exception as e:
        if 'already exists' in str(e).lower():
            print("✓ zone_validated already exists")
        else:
            print(f"Error: {e}")

print("✅ Columns added! Now exit and run: python manage.py migrate --fake projeng 0014")
```

### Step 3: Exit Shell
```python
exit()
```

### Step 4: Mark Migration as Applied
```bash
python manage.py migrate --fake projeng 0014
```

### Step 5: Verify
```bash
python manage.py showmigrations projeng
```

You should see `[X] 0014_add_zoning_zone_model`

---

## Alternative: One-Liner (Easier)

Run this single command:

```bash
python manage.py shell -c "from django.db import connection; c = connection.cursor(); c.execute('ALTER TABLE projeng_project ADD COLUMN IF NOT EXISTS zone_type VARCHAR(20) NULL'); c.execute('ALTER TABLE projeng_project ADD COLUMN IF NOT EXISTS zone_validated BOOLEAN DEFAULT FALSE'); print('✅ Done!')"
```

Then:
```bash
python manage.py migrate --fake projeng 0014
```

---

**After this, refresh your dashboard - the error should be fixed!** ✅

