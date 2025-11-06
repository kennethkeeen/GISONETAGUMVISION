# Render Deployment Guide - BEST OPTION

## Why Render is Best for Your System

✅ **Production-ready** - Built for real apps  
✅ **Docker support** - Your Dockerfile works perfectly  
✅ **GDAL support** - System libraries install correctly  
✅ **Managed services** - Less maintenance  
✅ **Free tier** - $0/month after card verification  
✅ **Auto-deploys** - Push to GitHub, auto-deploy  

## Step-by-Step Setup

### Step 1: Sign Up
1. Go to https://render.com
2. Sign up with GitHub
3. Verify your email

### Step 2: Add Payment Method
- Click "Add Payment Method"
- Add a card (won't be charged on free tier)
- This just verifies your account

### Step 3: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repo: `kennethkeeen/GISONETAGUMVISION`
3. Settings:
   - **Name:** `gistagum-app` (or any name)
   - **Environment:** `Docker`
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Dockerfile Path:** `Dockerfile`
   - **Docker Build Command:** (leave empty - Render uses Dockerfile)
   - **Docker Start Command:** (leave empty - uses CMD from Dockerfile)

### Step 4: Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Settings:
   - **Name:** `gistagum-db`
   - **Database:** `gistagum`
   - **User:** `gistagum`
   - **Region:** Same as your web service
   - **Plan:** Free
3. Click "Create Database"
4. Copy the **Internal Database URL** (you'll need this)

### Step 5: Configure Environment Variables
In your Web Service → Environment tab, add:

```
DJANGO_SETTINGS_MODULE=gistagum.settings
DJANGO_SECRET_KEY=<generate-a-long-random-string>
DEBUG=false
DATABASE_URL=<paste-internal-database-url-from-step-4>
ALLOWED_HOSTS=your-app.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com
```

**OR use your Neon database:**
```
DATABASE_URL=<your-neon-connection-string>
```

### Step 6: Add Persistent Disk (for media files)
1. In Web Service → Settings → Disks
2. Click "Create Disk"
3. Name: `media`
4. Mount Path: `/app/media`
5. Size: 1GB (free tier)

### Step 7: Deploy
1. Click "Create Web Service"
2. Render will build your Docker image
3. Watch the build logs
4. Once deployed, you'll get: `https://your-app.onrender.com`

### Step 8: Create Admin User
1. Go to your service → Logs
2. Click "Shell" tab
3. Run:
```bash
python manage.py createsuperuser
```

### Step 9: Access Your App
- **Live site:** `https://your-app.onrender.com`
- **Admin:** `https://your-app.onrender.com/admin`

---

## Render Free Tier Limits

- **750 hours/month** compute time
- **512MB RAM** per service
- **1GB disk** storage
- **Free PostgreSQL** (limited)
- Perfect for small to medium apps!

---

## Why This is Best for Your System

1. **GDAL Support:** Docker ensures all system libraries install
2. **Production Ready:** Built for real apps
3. **Reliable:** 99.9% uptime SLA
4. **Easy Updates:** Just push to GitHub
5. **Scalable:** Easy to upgrade when needed

---

## Troubleshooting

**Build fails?**
- Check logs in Render dashboard
- Verify Dockerfile is correct
- Check environment variables

**Database connection error?**
- Verify DATABASE_URL is correct
- Check database is running
- Use Internal Database URL for Render Postgres

**Static files not loading?**
- Render runs collectstatic via Dockerfile ✅
- WhiteNoise configured ✅

---

## Next Steps

After deployment, you can:
- Add custom domain (free)
- Set up monitoring
- Configure backups
- Scale up when needed

**Cost:** $0/month (free tier)  
**Card Required:** Yes (verification only, won't charge)

---

## Alternative: If You Can't Add Card

Use **Replit + Neon + Cloudinary** (completely free, no card)

