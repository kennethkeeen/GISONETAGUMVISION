# DigitalOcean Deployment Checklist

## ✅ Pre-Deployment (Already Done)

- [x] Dockerfile configured for DigitalOcean
- [x] Environment variables setup in settings.py
- [x] DATABASE_URL support configured
- [x] WhiteNoise for static files configured
- [x] Gunicorn configured
- [x] Requirements.txt updated
- [x] Secret key generated (see below)

## 🔑 Your Generated Secret Key

**Save this - you'll need it for DigitalOcean:**

```
DJANGO_SECRET_KEY=&3)uw&3z9k2&f-zbw39f)9grk!w)0g27=85!omr$#72!s@(d&^
```

## 📋 Step-by-Step Deployment

### Step 1: Sign Up for DigitalOcean
1. Go to **https://www.digitalocean.com**
2. Click **"Sign Up"**
3. Create account (email or GitHub recommended)
4. **Verify your email** (check inbox)
5. **You'll get $200 free credit for 60 days!**

### Step 2: Create App Platform Project
1. Go to **https://cloud.digitalocean.com/apps**
2. Click **"Create App"** button (top right)
3. Choose **"GitHub"** as source
4. **Authorize DigitalOcean** to access your GitHub
5. Select repository: **`kennethkeeen/GISONETAGUMVISION`**
6. Click **"Next"**

### Step 3: Configure Build Settings
DigitalOcean should auto-detect your Dockerfile. Verify:

- **Type:** `Docker` ✅
- **Dockerfile Path:** `Dockerfile` ✅
- **Docker Build Command:** (leave empty) ✅
- **Docker Run Command:** (leave empty) ✅

If not auto-detected, manually set:
- **Dockerfile Path:** `Dockerfile`

### Step 4: Configure App Settings
1. **App Name:** `gistagum` (or any name you like)
2. **Region:** Choose closest to you:
   - **NYC** (New York)
   - **SFO** (San Francisco)
   - **AMS** (Amsterdam)
   - **SGP** (Singapore)
3. **Plan:** 
   - Select **"Basic"** plan ($5/month - uses free credit)
   - Or **"Professional"** ($12/month - better performance)

### Step 5: Add Environment Variables
Click **"Edit"** next to Environment Variables, then add these **one by one**:

```
DJANGO_SETTINGS_MODULE=gistagum.settings
```

```
DJANGO_SECRET_KEY=&3)uw&3z9k2&f-zbw39f)9grk!w)0g27=85!omr$#72!s@(d&^
```

```
DEBUG=false
```

```
ALLOWED_HOSTS=*.ondigitalocean.app
```

```
CSRF_TRUSTED_ORIGINS=https://*.ondigitalocean.app
```

**For Database - Choose ONE:**

**Option A: Use Neon (Free)**
```
DATABASE_URL=<paste-your-neon-connection-string-here>
```

**Option B: Use DigitalOcean Postgres (see Step 6)**

### Step 6: Add Database (Optional - Only if NOT using Neon)
If you want DigitalOcean's managed Postgres instead of Neon:

1. Click **"Add Component"** → **"Database"**
2. Choose **"PostgreSQL"**
3. Settings:
   - **Name:** `gistagum-db`
   - **Version:** Latest (15 recommended)
   - **Plan:** Basic ($15/month - uses free credit)
4. DigitalOcean will **automatically add** `DATABASE_URL` environment variable

**Recommendation:** Use Neon (free) to save money!

### Step 7: Add Persistent Storage (for media files)
1. Click **"Add Component"** → **"Volume"**
2. Settings:
   - **Name:** `media-storage`
   - **Mount Path:** `/app/media`
   - **Size:** 1GB (minimum)
   - Uses free trial credit (~$0.10/month)

### Step 8: Review & Deploy
1. **Review** all settings:
   - App name ✅
   - Region ✅
   - Environment variables ✅
   - Database ✅
   - Storage ✅
2. Click **"Create Resources"**
3. DigitalOcean will:
   - Build your Docker image
   - Install all dependencies (including GDAL)
   - Run migrations automatically
   - Collect static files
   - Deploy your app
4. **Watch the build logs** - it takes 5-10 minutes

### Step 9: Get Your App URL
After deployment completes:
- Your app will be at: `https://your-app-name.ondigitalocean.app`
- Copy this URL - you'll need it!

### Step 10: Update ALLOWED_HOSTS (if needed)
1. Go to your app → **"Settings"** → **"App-Level Environment Variables"**
2. Update `ALLOWED_HOSTS` with your actual domain:
   ```
   ALLOWED_HOSTS=your-app-name.ondigitalocean.app
   ```
3. Update `CSRF_TRUSTED_ORIGINS`:
   ```
   CSRF_TRUSTED_ORIGINS=https://your-app-name.ondigitalocean.app
   ```
4. Click **"Save"** - app will redeploy automatically

### Step 11: Create Admin User
1. Go to your app → **"Runtime Logs"**
2. Click **"Console"** tab
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow prompts to create admin account

### Step 12: Test Your App
1. Visit: `https://your-app-name.ondigitalocean.app`
2. Test login with your admin account
3. Check admin panel: `https://your-app-name.ondigitalocean.app/admin`

---

## 🎉 You're Done!

Your app is now live on DigitalOcean!

---

## 📝 Important Notes

### Environment Variables Summary
Make sure these are set in DigitalOcean:
- ✅ `DJANGO_SETTINGS_MODULE=gistagum.settings`
- ✅ `DJANGO_SECRET_KEY=<the-key-above>`
- ✅ `DEBUG=false`
- ✅ `DATABASE_URL=<your-neon-url>`
- ✅ `ALLOWED_HOSTS=*.ondigitalocean.app` (or your specific domain)
- ✅ `CSRF_TRUSTED_ORIGINS=https://*.ondigitalocean.app`

### Neon Database URL Format
Your Neon connection string should look like:
```
postgresql://username:password@host.neon.tech/dbname?sslmode=require
```

### Cost After Free Trial
- **Basic App:** $5/month
- **Professional App:** $12/month (recommended for production)
- **Storage:** $0.10/GB/month
- **Database:** Use Neon (free) or DO Postgres ($15/month)

**Minimum cost:** $5/month (Basic app + Neon DB)

---

## 🔄 Updating Your App

Just push to GitHub:
```bash
git add .
git commit -m "Update app"
git push
```

DigitalOcean **automatically redeploys**! 🚀

---

## 🆘 Troubleshooting

**Build fails?**
- Check build logs in DigitalOcean dashboard
- Verify Dockerfile is correct
- Check all environment variables are set

**Database connection error?**
- Verify DATABASE_URL is correct
- Check Neon database is running
- Test connection string format

**App crashes?**
- Check runtime logs
- Verify ALLOWED_HOSTS matches your domain
- Check all environment variables

**Static files not loading?**
- DigitalOcean runs collectstatic automatically ✅
- WhiteNoise is configured ✅

---

## 📞 Need Help?

If you get stuck at any step, let me know which step and I'll help you!

