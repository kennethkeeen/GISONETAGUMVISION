# 🔧 Fix: zone_type Column Missing

## Quick Fix: Run These Commands in Console

### Step 1: Check Migration Status
```bash
python manage.py showmigrations projeng
```

**What to look for:**
- If you see `[ ] 0014_add_zoning_zone_model` (unchecked) = Migration not applied
- If you see `[X] 0014_add_zoning_zone_model` (checked) = Migration applied but column still missing

### Step 2: Run Migration
```bash
python manage.py migrate projeng
```

### Step 3: If Migration Fails - Check Dependencies
```bash
python manage.py migrate
```
(Run without specifying app to apply all pending migrations)

---

## Alternative: Manual SQL Fix (If Migration Won't Run)

If the migration keeps failing, you can add the columns manually:

### Step 1: Open Database Shell
```bash
python manage.py dbshell
```

### Step 2: Run These SQL Commands
```sql
-- Add zone_type column
ALTER TABLE projeng_project 
ADD COLUMN zone_type VARCHAR(20) NULL;

-- Add zone_validated column
ALTER TABLE projeng_project 
ADD COLUMN zone_validated BOOLEAN DEFAULT FALSE;

-- Create ZoningZone table
CREATE TABLE projeng_zoningzone (
    id BIGSERIAL PRIMARY KEY,
    zone_type VARCHAR(20) NOT NULL,
    barangay VARCHAR(255) NOT NULL,
    location_description TEXT NOT NULL,
    keywords JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX projeng_zon_baranga_8c8025_idx ON projeng_zoningzone(barangay, zone_type);
CREATE INDEX projeng_zon_is_acti_1819c4_idx ON projeng_zoningzone(is_active);
CREATE INDEX projeng_project_zone_type_idx ON projeng_project(zone_type);

-- Exit
\q
```

### Step 3: Mark Migration as Applied
```bash
python manage.py migrate --fake projeng 0014
```

---

## Verify Fix

After running either method, verify:

```bash
python manage.py dbshell
```

Then:
```sql
\d projeng_project
```

You should see:
- `zone_type` column
- `zone_validated` column

---

## Still Not Working?

**Check these:**

1. **Are you connected to the right database?**
   ```bash
   echo $DATABASE_URL
   ```

2. **Is the migration file present?**
   ```bash
   ls -la projeng/migrations/0014*.py
   ```

3. **Check for migration errors:**
   ```bash
   python manage.py migrate --verbosity 2
   ```

---

**Share the output of these commands if it still doesn't work!**

