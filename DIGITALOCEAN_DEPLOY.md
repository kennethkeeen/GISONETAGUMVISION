# DigitalOcean App Platform Deployment Guide

## Why DigitalOcean App Platform?

✅ **$200 Free Trial** - 60 days free credit  
✅ **Docker Support** - Your Dockerfile works perfectly  
✅ **GDAL Support** - System libraries install correctly  
✅ **Production-Ready** - Enterprise-grade infrastructure  
✅ **Managed Database** - Optional Postgres addon  
✅ **Auto-Deploys** - Push to GitHub, auto-deploy  
✅ **Easy Scaling** - Upgrade when needed  

## Step-by-Step Setup

### Step 1: Sign Up & Get Free Trial
1. Go to https://www.digitalocean.com
2. Click "Sign Up"
3. Create account (email or GitHub)
4. **You'll get $200 free credit for 60 days!**
5. Verify your email

### Step 2: Create App Platform Project
1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Choose "GitHub" as source
4. Authorize DigitalOcean to access GitHub
5. Select your repository: `kennethkeeen/GISONETAGUMVISION`
6. Click "Next"

### Step 3: Configure Build Settings
DigitalOcean will auto-detect your Dockerfile. Verify:

- **Type:** Docker
- **Dockerfile Path:** `Dockerfile` (should auto-detect)
- **Docker Build Command:** (leave empty - uses Dockerfile)
- **Docker Run Command:** (leave empty - uses CMD from Dockerfile)

### Step 4: Configure App Settings
1. **App Name:** `gistagum` (or any name)
2. **Region:** Choose closest to you (e.g., NYC, SFO, AMS)
3. **Plan:** 
   - **Free Trial:** Start with "Basic" plan (uses free credit)
   - After trial: ~$5-12/month for small app

### Step 5: Add Environment Variables
Click "Edit" next to Environment Variables, add:

```
DJANGO_SETTINGS_MODULE=gistagum.settings
DJANGO_SECRET_KEY=<generate-a-long-random-string>
DEBUG=false
ALLOWED_HOSTS=your-app.ondigitalocean.app
CSRF_TRUSTED_ORIGINS=https://your-app.ondigitalocean.app
```

**For Database:**
- **Option A (Use Neon):** Add `DATABASE_URL=<your-neon-connection-string>`
- **Option B (Use DigitalOcean Postgres):** Add database component (see Step 6)

### Step 6: Add Database (Optional)
If you want to use DigitalOcean's managed Postgres instead of Neon:

1. Click "Add Component" → "Database"
2. Choose "PostgreSQL"
3. Settings:
   - **Name:** `gistagum-db`
   - **Version:** Latest (14 or 15)
   - **Plan:** Basic ($15/month) or use free trial credit
4. DigitalOcean will auto-add `DATABASE_URL` environment variable

**OR keep using Neon** (free) - just add the DATABASE_URL manually.

### Step 7: Configure Resources
1. **Instance Size:** 
   - **Free Trial:** Basic ($5/month) - uses free credit
   - **After Trial:** Basic ($5/month) or Professional ($12/month)
2. **Instance Count:** 1 (can scale later)

### Step 8: Add Persistent Storage (for media files)
1. Click "Add Component" → "Volume"
2. Settings:
   - **Name:** `media-storage`
   - **Mount Path:** `/app/media`
   - **Size:** 1GB (minimum)
   - Uses free trial credit

### Step 9: Review & Deploy
1. Review all settings
2. Click "Create Resources"
3. DigitalOcean will:
   - Build your Docker image
   - Run migrations (via Dockerfile CMD)
   - Collect static files
   - Deploy your app
4. Watch the build logs

### Step 10: Create Admin User
After deployment:

1. Go to your app → "Runtime Logs"
2. Click "Console" tab
3. Run:
```bash
python manage.py createsuperuser
```

### Step 11: Access Your App
- **Live site:** `https://your-app.ondigitalocean.app`
- **Admin:** `https://your-app.ondigitalocean.app/admin`

---

## DigitalOcean Pricing

### Free Trial
- **$200 credit** for 60 days
- Enough for:
  - App Platform: ~$5-12/month
  - Managed Postgres: ~$15/month (optional)
  - Storage: ~$1/month
  - **Total:** ~$6-28/month (covered by $200 credit)

### After Trial (if you continue)
- **Basic App:** $5/month (512MB RAM, 1GB storage)
- **Professional App:** $12/month (1GB RAM, better performance)
- **Managed Postgres:** $15/month (optional - or keep using Neon free)
- **Storage:** $0.10/GB/month

**Minimum after trial:** ~$5-12/month (without managed DB)

---

## Why DigitalOcean is Great

1. **Enterprise-Grade:** Used by millions of developers
2. **Docker Support:** Your Dockerfile works perfectly
3. **GDAL Support:** All system libraries install correctly
4. **Reliable:** 99.99% uptime SLA
5. **Global CDN:** Fast worldwide
6. **Easy Scaling:** Upgrade with one click
7. **Great Docs:** Excellent documentation

---

## Troubleshooting

**Build fails?**
- Check build logs in DigitalOcean dashboard
- Verify Dockerfile is correct
- Check environment variables are set

**Database connection error?**
- Verify DATABASE_URL is correct
- Check database is running (if using DO Postgres)
- Test Neon connection string

**Static files not loading?**
- DigitalOcean runs collectstatic via Dockerfile ✅
- WhiteNoise configured ✅

**App crashes?**
- Check runtime logs
- Verify all environment variables
- Check ALLOWED_HOSTS matches your domain

---

## Next Steps After Deployment

1. **Custom Domain:** Add your own domain (free)
2. **SSL Certificate:** Auto-configured (free)
3. **Monitoring:** Built-in app metrics
4. **Backups:** Configure automatic backups
5. **Scaling:** Scale up when needed

---

## Cost Summary

**Free Trial (60 days):**
- $200 credit
- Enough for full setup
- No charges during trial

**After Trial:**
- **Minimum:** $5/month (Basic app, use Neon DB)
- **Recommended:** $12/month (Professional app, better performance)
- **With DO Postgres:** $27/month (Professional + Managed DB)

**Recommendation:** Use Neon (free) for database, pay $5-12/month for hosting

---

## Quick Start Commands

After setup, updates are automatic:
```bash
git add .
git commit -m "Update app"
git push
```

DigitalOcean auto-deploys on push! 🚀

