# 🚀 Complete Worker Setup Guide for DigitalOcean

## ✅ What's Been Set Up

### Code Changes (Already Done):
1. ✅ **Celery installed** - Added to `requirements.txt`
2. ✅ **Celery configured** - `gistagum/celery.py` created
3. ✅ **Settings updated** - Celery configuration in `settings.py`
4. ✅ **Background tasks created** - `projeng/tasks.py` with report generation tasks
5. ✅ **Worker component configured** - Added to `.do/app.yaml`

### What You Need to Do in DigitalOcean:

---

## Step 1: Update REDIS_URL (REQUIRED)

**The worker needs Redis/Valkey to work!**

1. **Go to DigitalOcean Dashboard**
2. **Click "Databases"** → Your Valkey database
3. **Wait for "Online"** status
4. **Click "Connection Details"**
5. **Copy the connection string** (should be `rediss://default:PASSWORD@HOST:PORT`)

6. **Go to App Platform** → Your App → **Settings**
7. **Find `REDIS_URL`** in Environment Variables
8. **Click "Edit"**
9. **Replace placeholder** with your actual connection string
10. **Save**

**Important:** Use `rediss://` (double 's') for SSL connections!

---

## Step 2: Verify Worker Component

After you push the changes, DigitalOcean should automatically create the worker component.

1. **Go to App Platform** → Your App → **Settings**
2. **Check "Components"** section
3. **You should see:**
   - `gisonetagumvision` (Web Service)
   - `gisonetagumvision-worker` (Worker)

### If Worker Doesn't Appear:

**Option A: Wait for Auto-Deploy**
- DigitalOcean will create it after detecting the `.do/app.yaml` changes
- Wait 3-5 minutes after pushing

**Option B: Manually Add Worker**
1. **Go to Components** → **"Add Component"**
2. **Select "Worker"**
3. **Configure:**
   - **Name**: `gisonetagumvision-worker`
   - **Source**: Same GitHub repo
   - **Run Command**: `celery -A gistagum worker --loglevel=info --concurrency=2`
   - **Instance Size**: 1GB RAM, 1 vCPU
   - **Environment Variables**: Copy from Web Service
4. **Save**

---

## Step 3: Configure Worker Health Check

**Important:** Workers don't serve HTTP, so HTTP health checks won't work!

### Option 1: Disable Health Check (Recommended for Workers)
1. **Go to Worker Component** → **Settings**
2. **Find "Health Checks"**
3. **Click "Edit"**
4. **Disable health check** or set to very lenient:
   - **Initial Delay**: 60 seconds
   - **Period**: 30 seconds
   - **Timeout**: 10 seconds
   - **Failure Threshold**: 10 (very lenient)

### Option 2: Use TCP Health Check
- Change from HTTP to TCP
- Port: Any port (workers don't listen, but TCP check is less strict)

---

## Step 4: Verify Worker is Running

1. **Go to "Runtime Logs"** tab
2. **Select Worker Component** (dropdown at top)
3. **Look for:**
   ```
   celery@hostname ready
   ```
4. **Check for errors** - Should see Celery starting up

### Expected Logs:
```
celery@hostname v5.3.4 (emerald-rush)
...
[tasks]
  . projeng.tasks.generate_project_report_csv
  . projeng.tasks.generate_project_report_excel
  . projeng.tasks.generate_project_report_pdf
  . projeng.tasks.send_notification_email
  . projeng.tasks.process_delayed_projects
...
celery@hostname ready
```

---

## Step 5: Test Background Tasks

### Test from Django Shell:
1. **Go to "Console"** tab in DigitalOcean
2. **Run:**
   ```python
   python manage.py shell
   ```
3. **Test a task:**
   ```python
   from projeng.tasks import generate_project_report_csv
   from django.contrib.auth.models import User
   
   user = User.objects.first()
   project_id = 1  # Use an actual project ID
   
   # Queue the task
   task = generate_project_report_csv.delay(project_id, user.id)
   print(f"Task ID: {task.id}")
   print(f"Status: {task.status}")
   ```

### Check Task Status:
```python
from celery.result import AsyncResult

task_id = "your-task-id-here"
result = AsyncResult(task_id)
print(f"Status: {result.status}")
print(f"Result: {result.result}")
```

---

## Troubleshooting

### Worker Not Starting:

**Error: "ModuleNotFoundError: celery"**
- **Fix**: Wait for build to complete, Celery should be installed

**Error: "Connection refused" (Redis)**
- **Fix**: Check `REDIS_URL` is set correctly
- **Fix**: Verify Valkey database is "Online"

**Error: "No module named 'gistagum.celery'"**
- **Fix**: Make sure `gistagum/__init__.py` exists and imports Celery

### Tasks Not Processing:

**Tasks queued but not processing:**
1. **Check worker logs** - Is worker running?
2. **Check Redis/Valkey** - Is it online?
3. **Check task registration** - Are tasks showing in worker logs?

**Task fails immediately:**
1. **Check worker logs** - Error message will show
2. **Check database connection** - Worker needs DATABASE_URL
3. **Check imports** - All dependencies must be available

---

## Cost Breakdown

### With Worker:
- **Web Service**: $50/month (2GB RAM, 2 instances)
- **Worker**: $24/month (1GB RAM, 1 instance)
- **Valkey**: $15/month
- **Total: $89/month**

### Benefits:
- ✅ Background report generation
- ✅ Better user experience (no timeouts)
- ✅ Scheduled tasks capability
- ✅ Scalable architecture

---

## Next Steps

### 1. Convert Existing Views to Use Background Tasks

I can help you convert your report export views to use background tasks. This will:
- Make reports generate in background
- Show "Processing..." message to users
- Notify when report is ready

### 2. Add Scheduled Tasks

Set up periodic tasks like:
- Daily report generation
- Project status updates
- Cleanup tasks

### 3. Add Task Status Tracking

Create a page to:
- View task status
- Download completed reports
- See task history

---

## Summary

✅ **Celery configured and ready**
✅ **Background tasks created**
✅ **Worker component in app.yaml**
✅ **Ready to deploy!**

**Next:** 
1. Update `REDIS_URL` in DigitalOcean
2. Wait for deployment
3. Verify worker is running
4. Start using background tasks!

---

## Quick Reference

### Worker Command:
```bash
celery -A gistagum worker --loglevel=info --concurrency=2
```

### Available Tasks:
- `generate_project_report_csv(project_id, user_id)`
- `generate_project_report_pdf(project_id, user_id)`
- `generate_project_report_excel(project_id, user_id)`
- `send_notification_email(user_id, subject, message)`
- `process_delayed_projects()` (scheduled task)

### Queue a Task:
```python
from projeng.tasks import generate_project_report_csv
task = generate_project_report_csv.delay(project_id, user_id)
```

