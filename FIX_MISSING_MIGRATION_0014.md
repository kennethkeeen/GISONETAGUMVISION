# 🔧 Fix: Migration 0014 Not Applied

## Problem
Migration `0014_add_zoning_zone_model` is missing from the applied migrations list.

## Solution: Check and Apply Migration

### Step 1: Check if Migration File Exists
```bash
ls -la projeng/migrations/0014*.py
```

**Expected:** Should show `0014_add_zoning_zone_model.py`

### Step 2: If File Exists - Apply It
```bash
python manage.py migrate projeng 0014
```

### Step 3: If File Doesn't Exist - Create It
```bash
python manage.py makemigrations projeng
```

Then apply:
```bash
python manage.py migrate projeng
```

---

## Alternative: Manual SQL Fix (Fastest)

If the migration file is missing or won't apply, add columns manually:

### Step 1: Open Database Shell
```bash
python manage.py dbshell
```

### Step 2: Run SQL Commands
```sql
-- Add zone_type column
ALTER TABLE projeng_project 
ADD COLUMN IF NOT EXISTS zone_type VARCHAR(20) NULL;

-- Add zone_validated column  
ALTER TABLE projeng_project 
ADD COLUMN IF NOT EXISTS zone_validated BOOLEAN DEFAULT FALSE;

-- Exit
\q
```

### Step 3: Create ZoningZone Table
```sql
CREATE TABLE IF NOT EXISTS projeng_zoningzone (
    id BIGSERIAL PRIMARY KEY,
    zone_type VARCHAR(20) NOT NULL,
    barangay VARCHAR(255) NOT NULL,
    location_description TEXT NOT NULL,
    keywords JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS projeng_zon_baranga_8c8025_idx 
ON projeng_zoningzone(barangay, zone_type);

CREATE INDEX IF NOT EXISTS projeng_zon_is_acti_1819c4_idx 
ON projeng_zoningzone(is_active);
```

### Step 4: Mark Migration as Applied
```bash
python manage.py migrate --fake projeng 0014
```

---

## Quick One-Liner Fix

If you want to do it all at once:

```bash
python manage.py dbshell <<EOF
ALTER TABLE projeng_project ADD COLUMN IF NOT EXISTS zone_type VARCHAR(20) NULL;
ALTER TABLE projeng_project ADD COLUMN IF NOT EXISTS zone_validated BOOLEAN DEFAULT FALSE;
\q
EOF
python manage.py migrate --fake projeng 0014
```

---

## Verify Fix

After running, check:
```bash
python manage.py showmigrations projeng
```

You should now see:
```
[X] 0014_add_zoning_zone_model
```

Then refresh your dashboard - the error should be gone!

