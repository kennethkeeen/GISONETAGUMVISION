# 🔧 Fix Container Exit Error - Celery Worker

## The Problem

DigitalOcean diagnostic shows:
- **Error**: "Container exited with non-zero code"
- **Reason**: "The container exited immediately after starting, indicating a potential issue with the Celery worker setup or dependencies."

## What I've Fixed

### 1. ✅ Added Error Handling
- Wrapped Celery configuration in try/except
- Added detailed error logging to stderr
- Errors will now show in deploy logs

### 2. ✅ Skip Placeholder REDIS_URL
- Added check to skip SSL configuration if REDIS_URL is placeholder
- Prevents SSL errors when REDIS_URL isn't set correctly

### 3. ✅ Better Error Messages
- Errors now print to stderr with full traceback
- Makes it easier to diagnose issues

## Common Causes & Fixes

### Cause 1: REDIS_URL is Placeholder
**Symptom**: Container exits immediately, no clear error

**Fix**:
1. Go to **App Platform** → **Worker Component** → **Environment Variables**
2. Check `REDIS_URL` - if it shows `redis://default:YOUR_PASSWORD@...`, it's a placeholder
3. Get your actual Valkey connection string from **Databases** → **Valkey** → **Connection Details**
4. Update `REDIS_URL` with the actual connection string
5. Save and redeploy

### Cause 2: DATABASE_URL Not Resolving
**Symptom**: Container exits, might see database errors

**Fix**:
1. Go to **Worker Component** → **Environment Variables**
2. Check `DATABASE_URL` - should be `${gistagum-db.DATABASE_URL}`
3. If it's not resolving, set it manually:
   - Go to **Databases** → **PostgreSQL** → **Connection Details**
   - Copy connection string
   - Paste into `DATABASE_URL` in worker environment variables
4. Save and redeploy

### Cause 3: Import Error
**Symptom**: Container exits, error in logs about missing module

**Fix**:
- Check deploy logs for the exact import error
- Common issues:
  - Missing `celery` package (should be in requirements.txt)
  - Missing `gistagum.celery` module (should exist)
  - Django settings error

### Cause 4: SSL Configuration Error
**Symptom**: Container exits, SSL-related errors

**Fix**:
- The code now skips SSL config if REDIS_URL is placeholder
- If you have a real REDIS_URL, make sure it's `rediss://` (double 's') for SSL
- SSL configuration is now handled automatically

## How to Diagnose

### Step 1: Check Deploy Logs
1. Go to **App Platform** → **Your App** → **Runtime Logs**
2. Select **Worker Component** from dropdown
3. Look for:
   - `ERROR: Failed to configure Celery: ...` (new error handling)
   - Any import errors
   - Database connection errors
   - SSL errors

### Step 2: Verify Environment Variables
1. Go to **Worker Component** → **Settings** → **Environment Variables**
2. Verify these are set:
   - ✅ `DJANGO_SETTINGS_MODULE` = `gistagum.settings`
   - ✅ `DATABASE_URL` = (actual connection string, not placeholder)
   - ✅ `REDIS_URL` = (actual connection string, not placeholder)
   - ✅ `CELERY_WORKER` = `true`

### Step 3: Check Run Command
1. Go to **Worker Component** → **Settings**
2. Verify **Run Command** is:
   ```
   celery -A gistagum worker --loglevel=info --concurrency=2
   ```

## Expected Behavior After Fix

### If REDIS_URL is Placeholder:
- Worker will start without SSL configuration
- Will use database as broker (fallback)
- Should see: `celery@hostname ready`

### If REDIS_URL is Set Correctly:
- Worker will configure SSL automatically
- Will use Valkey as broker
- Should see: `celery@hostname ready`

### If There's an Error:
- You'll see detailed error message in logs
- Error will include full traceback
- Makes it easy to identify the issue

## Next Steps

1. **Wait for deployment** - Changes have been pushed
2. **Check deploy logs** - Look for the new error messages
3. **Verify environment variables** - Make sure REDIS_URL and DATABASE_URL are set correctly
4. **Share error logs** - If it still fails, share the exact error from logs

## Quick Checklist

- [ ] REDIS_URL is set (not placeholder)
- [ ] DATABASE_URL is set (not placeholder)
- [ ] Run command is correct
- [ ] All environment variables are present
- [ ] Checked deploy logs for errors

