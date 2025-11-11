# How to Fix "Zoning data loaded: 0 barangays" Error

## Problem
The console shows "Zoning data loaded: 0 barangays" because the `BarangayMetadata` table is empty.

## Solution: Populate the Database

### Step 1: Temporarily Disable Celery Import (if needed)

If you get a `ModuleNotFoundError: No module named 'celery'` error, temporarily comment out the celery import:

**File: `gistagum/__init__.py`**
```python
# Temporarily comment this out if celery is not installed
# from .celery import app as celery_app

__all__ = []
```

### Step 2: Run the Populate Command

```bash
cd C:\Users\kenne\Desktop\GISTAGUM
python manage.py populate_barangay_metadata
```

**Expected Output:**
```
Created: Apokon
Created: Bincungan
Created: Busaon
...
Successfully processed 23 barangays
   Created: 23
   Updated: 0
   Total in database: 23
```

### Step 3: Restore Celery Import (if you commented it out)

**File: `gistagum/__init__.py`**
```python
from .celery import app as celery_app

__all__ = ['celery_app']
```

### Step 4: Refresh the Browser

1. Hard refresh: `Ctrl + Shift + R` (or `Ctrl + F5`)
2. Check the console - you should now see:
   ```
   ✓ Zoning data loaded: 23 barangays
   Sample barangay names: ['Apokon', 'Bincungan', 'Busaon', 'Canocotan', 'Cuambogan']
   ```

## Alternative: Use Django Admin

If the command doesn't work, you can manually add data through Django Admin:

1. Go to: `http://your-domain/admin/projeng/barangaymetadata/`
2. Click "Add Barangay Metadata"
3. Fill in the data for each barangay

## Verification

After populating, verify the data exists:

```bash
python manage.py shell
```

Then in the shell:
```python
from projeng.models import BarangayMetadata
print(f"Total barangays: {BarangayMetadata.objects.count()}")
# Should print: Total barangays: 23
```

## Troubleshooting

### Error: "No module named 'celery'"
- Solution: Temporarily comment out the celery import in `gistagum/__init__.py` before running the command

### Error: "Table doesn't exist"
- Solution: Run migrations first:
  ```bash
  python manage.py makemigrations projeng
  python manage.py migrate projeng
  ```

### Command runs but no data appears
- Check if you're connected to the correct database
- Verify the command output shows "Created: ..." messages
- Check database directly or use Django admin to verify records exist

