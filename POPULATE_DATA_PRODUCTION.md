# 📊 Populate Data on Production

## Current Status
✅ Dashboard is working (no more 500 error!)
✅ Map is displaying
❌ Barangay metadata is empty
❌ Zoning data is empty

## Fix: Populate the Data

### Step 1: Populate Barangay Metadata

In DigitalOcean Console, run:

```bash
python manage.py populate_barangay_metadata
```

This will populate the `BarangayMetadata` table with:
- Population data
- Land area
- Growth rates
- Economic classifications
- Elevation types

### Step 2: Populate Zoning Zones (Optional but Recommended)

```bash
python manage.py populate_zoning_zones
```

This will populate the `ZoningZone` table with:
- 69 zones from your parsed PDF data
- Zone types (R-1, R-2, C-1, etc.)
- Barangay associations
- Keywords for matching

---

## After Running Commands

1. **Refresh your dashboard page**
2. **The console errors should disappear**
3. **Zoning overlay should work**
4. **Zone analytics charts should show data**

---

## If You Get Celery/Channels Errors

If you see import errors, the commands will still work - those are just warnings about optional features.

---

**Run these two commands in DigitalOcean Console, then refresh your dashboard!** 🚀

