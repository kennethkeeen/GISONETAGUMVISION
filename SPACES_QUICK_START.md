# 🚀 DigitalOcean Spaces - Quick Start Guide

## ✅ Code Changes Complete!

All code changes have been made. Now you just need to:

1. **Create the Space** (5 minutes)
2. **Add Environment Variables** (5 minutes)
3. **Deploy** (automatic on push)

---

## 📝 Step 1: Create DigitalOcean Space

1. Go to [DigitalOcean Dashboard](https://cloud.digitalocean.com/spaces)
2. Click **"Create a Space"**
3. Configure:
   - **Name**: `gistagum-media` (must be globally unique)
   - **Region**: `Singapore (sgp1)` - matches your app
   - **File Listing**: **Private**
   - **CDN**: ✅ **Enable CDN**
4. Click **"Create a Space"**

---

## 🔑 Step 2: Get Access Keys

1. Go to **API** → **Spaces Keys**
2. Click **"Generate New Key"**
3. Name: `gistagum-spaces-key`
4. **Save both keys** (you'll only see the secret once!):
   - Access Key (starts with `DO00...`)
   - Secret Key (long random string)

---

## ⚙️ Step 3: Add Environment Variables

Go to your app → **Settings** → **App-Level Environment Variables**

Add these 7 variables (see `SPACES_ENV_VARIABLES.md` for details):

```
USE_SPACES=true
AWS_ACCESS_KEY_ID=<your-access-key> (SECRET)
AWS_SECRET_ACCESS_KEY=<your-secret-key> (SECRET)
AWS_STORAGE_BUCKET_NAME=gistagum-media
AWS_S3_ENDPOINT_URL=https://sgp1.digitaloceanspaces.com
AWS_S3_REGION_NAME=sgp1
AWS_S3_CUSTOM_DOMAIN=gistagum-media.sgp1.cdn.digitaloceanspaces.com
```

**Important:**
- Replace `gistagum-media` with your actual Space name
- Mark `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as **SECRET**
- Replace `<your-access-key>` and `<your-secret-key>` with actual values

---

## 🚀 Step 4: Deploy

1. **Commit and push** your code changes:
   ```bash
   git add .
   git commit -m "Add DigitalOcean Spaces support for media storage"
   git push
   ```

2. **DigitalOcean will auto-deploy** (if auto-deploy is enabled)

3. **Or manually deploy** from DigitalOcean dashboard

---

## ✅ Step 5: Verify

1. **Check app logs** - should see:
   ```
   ✅ DigitalOcean Spaces configured for media storage
   ```

2. **Test upload** - Upload an image through your app

3. **Check Spaces** - File should appear in your Space bucket

4. **View image** - Should load from CDN URL

---

## 📚 Documentation Files

- **`DIGITALOCEAN_SPACES_SETUP.md`** - Complete setup guide
- **`SPACES_ENV_VARIABLES.md`** - Detailed environment variables guide
- **`IMAGE_STORAGE_PLAN.md`** - Comparison of storage options

---

## 🔄 How It Works

### Development (Local):
- Uses local file storage (`/media/` folder)
- No Spaces credentials needed
- Works exactly as before

### Production (DigitalOcean):
- Automatically uses Spaces when environment variables are set
- Files uploaded to Spaces bucket
- Served via CDN for fast global delivery
- No code changes needed - it's automatic!

---

## 🐛 Troubleshooting

### Still using local storage?
- Check `USE_SPACES=true` (lowercase)
- Verify all environment variables are set
- Check app logs for warnings

### 403 Forbidden?
- Verify Access Keys are correct
- Check bucket name matches exactly
- Ensure Space is set to "Public" or files have correct ACL

### Images not loading?
- Check CDN is enabled on Space
- Verify `AWS_S3_CUSTOM_DOMAIN` is correct
- Check Space region matches endpoint

---

## 💰 Cost

- **$5/month** for first 250GB storage
- **$0.02/GB/month** for additional storage
- **$0.01/GB** for outbound transfer (first 1TB free)
- **CDN**: Included (free)

**Example:** 50GB storage + 100GB transfer = ~$5-6/month

---

## 🎉 That's It!

Once you complete Steps 1-4, your images will automatically be stored in DigitalOcean Spaces with CDN delivery!

**Need help?** Check the detailed guides or review the troubleshooting section.

