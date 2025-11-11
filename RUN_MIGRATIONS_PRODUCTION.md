# 🔧 Fix: Run Migrations on Production

## Problem
Error: `column projeng_project.zone_type does not exist`

This means the database migration hasn't been applied to your production database.

## Solution: Run Migrations on DigitalOcean

### Option 1: Using DigitalOcean Console (Recommended)

1. **Go to DigitalOcean Dashboard**
   - Visit: https://cloud.digitalocean.com
   - Click **"App Platform"** (left sidebar)
   - Click on your app: **"one-tagumvision"** or **"onetagumvision"**

2. **Open Console**
   - Click the **"Console"** tab (top menu)
   - This opens a terminal in your app container

3. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

4. **Verify Migration**
   ```bash
   python manage.py showmigrations projeng
   ```
   - You should see `[X] 0014_add_zoning_zone_model` checked

5. **Refresh Your Dashboard**
   - Go back to your app URL
   - The error should be fixed!

---

### Option 2: Trigger Redeployment (Automatic)

If your `start.sh` is configured correctly, migrations run automatically on deployment:

1. **Force a Redeployment**
   - Go to your App → **"Deployments"** tab
   - Click **"Create Deployment"** or **"Redeploy"**
   - This will run `python manage.py migrate --noinput` automatically

2. **Wait for Deployment**
   - Check the deployment logs
   - Look for: `Running migrations...`
   - Verify it shows: `Applying projeng.0014_add_zoning_zone_model... OK`

---

### Option 3: Check if Migration Already Ran

If you're not sure, check the migration status:

```bash
python manage.py showmigrations projeng
```

**Expected output:**
```
projeng
 [X] 0001_initial
 [X] 0002_...
 ...
 [X] 0013_barangaymetadata_and_more
 [ ] 0014_add_zoning_zone_model  ← This should be checked [X]
```

If `0014_add_zoning_zone_model` shows `[ ]` (unchecked), run:
```bash
python manage.py migrate projeng
```

---

## After Running Migrations

1. **Populate Zone Data** (Optional but Recommended)
   ```bash
   python manage.py populate_zoning_zones
   ```
   This loads the 69 zones from your parsed data.

2. **Test the Dashboard**
   - Visit: `https://your-app.ondigitalocean.app/dashboard/`
   - The error should be gone!
   - Zone analytics charts should work

---

## Troubleshooting

### If Migration Fails

**Error: "Migration dependencies not met"**
- Run: `python manage.py migrate` (without specifying app)
- This applies all pending migrations in order

**Error: "Table already exists"**
- The migration might have partially run
- Check: `python manage.py showmigrations projeng`
- If needed, fake the migration: `python manage.py migrate --fake projeng 0014`

### If Console Doesn't Work

1. **Check App Status**
   - Make sure your app is running
   - Check "Runtime Logs" for errors

2. **Try SSH/Console Alternative**
   - Some platforms use different console access
   - Check DigitalOcean documentation for your specific setup

---

## Quick Command Reference

```bash
# Check migration status
python manage.py showmigrations projeng

# Run all migrations
python manage.py migrate

# Run specific app migrations
python manage.py migrate projeng

# Populate zone data (after migration)
python manage.py populate_zoning_zones
```

---

**After running migrations, your dashboard should work!** ✅

