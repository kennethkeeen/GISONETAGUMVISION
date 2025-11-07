# ✅ Worker Component Setup Complete

## What I've Set Up

### 1. ✅ Celery Configuration
- Added `celery==5.3.4` to `requirements.txt`
- Created `gistagum/celery.py` with Celery configuration
- Updated `gistagum/__init__.py` to load Celery
- Added Celery settings to `gistagum/settings.py`

### 2. ✅ Background Tasks Created
Created `projeng/tasks.py` with background tasks:
- `generate_project_report_csv` - Generate CSV reports in background
- `generate_project_report_pdf` - Generate PDF reports in background
- `generate_project_report_excel` - Generate Excel reports in background
- `send_notification_email` - Send emails in background
- `process_delayed_projects` - Flag overdue projects (scheduled task)

### 3. ✅ Worker Component Configuration
- Updated `.do/app.yaml` with worker component
- Configured to run: `celery -A gistagum worker --loglevel=info --concurrency=2`
- Added all necessary environment variables

---

## Next Steps in DigitalOcean

### Step 1: Update REDIS_URL
1. **Go to App Platform** → Your App → **Settings**
2. **Find `REDIS_URL`** in Environment Variables
3. **Replace placeholder** with your actual Valkey connection string:
   ```
   rediss://default:PASSWORD@HOST:PORT
   ```
4. **Save** - This is needed for Celery to work

### Step 2: Verify Worker Component
1. **Go to App Platform** → Your App → **Settings**
2. **Check Components** - You should see:
   - `gisonetagumvision` (Web Service)
   - `gisonetagumvision-worker` (Worker)
3. **If worker doesn't exist**, DigitalOcean will create it after you push

### Step 3: Push Changes
```bash
git add .
git commit -m "Add Celery worker configuration for background tasks"
git push origin main
```

### Step 4: Wait for Deployment
- DigitalOcean will automatically deploy
- Wait 3-5 minutes
- Check Runtime Logs for worker startup

---

## How to Use Background Tasks

### Example: Generate Report in Background

**Before (Synchronous):**
```python
def export_project_report(request, pk):
    # This blocks the request until report is generated
    report = generate_report(pk)
    return HttpResponse(report)
```

**After (Asynchronous with Worker):**
```python
from projeng.tasks import generate_project_report_csv

def export_project_report(request, pk):
    # Queue task - returns immediately
    task = generate_project_report_csv.delay(pk, request.user.id)
    return JsonResponse({
        'task_id': task.id,
        'status': 'processing',
        'message': 'Report is being generated. You will be notified when ready.'
    })
```

### Check Task Status
```python
from celery.result import AsyncResult

def check_task_status(request, task_id):
    task = AsyncResult(task_id)
    return JsonResponse({
        'status': task.status,
        'result': task.result if task.ready() else None
    })
```

---

## What Tasks Can Run in Background

### ✅ Good for Background:
- **Large PDF generation** (>10 seconds)
- **Excel exports** with many rows
- **Bulk email sending**
- **Data processing** (calculations, aggregations)
- **Scheduled tasks** (daily reports, cleanup)

### ❌ Keep Synchronous:
- **Quick operations** (<5 seconds)
- **User needs immediate result**
- **Simple database queries**

---

## Worker Component Details

### Configuration:
- **Command**: `celery -A gistagum worker --loglevel=info --concurrency=2`
- **Concurrency**: 2 tasks at a time
- **Instance**: 1GB RAM, 1 vCPU
- **Cost**: ~$24/month

### Health Check:
- Uses HTTP health check on `/health/`
- Worker doesn't serve HTTP, so health check might need adjustment
- Can disable health check for workers if needed

---

## Monitoring Workers

### Check Worker Status:
1. **Go to Runtime Logs**
2. **Look for**: `celery@hostname ready`
3. **Check for errors**: Any task failures will show in logs

### Task Queue:
- Tasks are queued in Redis/Valkey
- Workers pick up tasks automatically
- Failed tasks can be retried

---

## Troubleshooting

### Worker Not Starting:
1. **Check REDIS_URL** - Must be set correctly
2. **Check Runtime Logs** - Look for Celery errors
3. **Verify Celery installed** - Check build logs

### Tasks Not Processing:
1. **Check Redis/Valkey** - Must be online
2. **Check worker logs** - See if tasks are being picked up
3. **Verify task registration** - Tasks must be in `tasks.py`

### Health Check Failing:
- Workers don't serve HTTP, so HTTP health checks won't work
- Can disable health check or use TCP check instead

---

## Cost Summary

### With Worker:
- Web Service: $50/month
- Worker: $24/month
- Valkey: $15/month
- **Total: $89/month**

### Benefits:
- ✅ Background processing
- ✅ Better user experience
- ✅ Scalability
- ✅ Scheduled tasks

---

## Next: Convert Existing Views

You can now convert your report generation views to use background tasks. I can help you do this if you want!

**Example views to convert:**
- `export_project_report` → Use `generate_project_report_csv.delay()`
- `export_reports_pdf` → Use background task
- `export_reports_excel` → Use background task

---

## Summary

✅ **Celery installed and configured**
✅ **Background tasks created**
✅ **Worker component configured**
✅ **Ready to use!**

**Next:** Push changes and configure REDIS_URL in DigitalOcean!

