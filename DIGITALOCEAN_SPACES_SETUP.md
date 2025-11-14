# 🚀 DigitalOcean Spaces Implementation Guide

## Step-by-Step Setup for Image Storage

---

## Phase 1: Create DigitalOcean Spaces Bucket

### 1.1 Create the Space
1. Go to [DigitalOcean Dashboard](https://cloud.digitalocean.com/)
2. Click **"Spaces"** in the left sidebar
3. Click **"Create a Space"**
4. Configure:
   - **Name**: `gistagum-media` (or your preferred name - must be globally unique)
   - **Region**: `Singapore (sgp1)` - matches your app region
   - **File Listing**: **Private** (recommended for security)
   - **CDN**: ✅ **Enable CDN** (recommended for performance)
5. Click **"Create a Space"**

### 1.2 Get Access Keys
1. Go to **API** → **Spaces Keys** in DigitalOcean dashboard
2. Click **"Generate New Key"**
3. Give it a name: `gistagum-spaces-key`
4. **IMPORTANT**: Copy and save:
   - **Access Key** (starts with something like `DO00...`)
   - **Secret Key** (long random string - you can only see it once!)

**⚠️ Save these keys securely - you'll need them in the next steps!**

---

## Phase 2: Install Required Packages

### 2.1 Add to requirements.txt
Add these packages to your `requirements.txt`:

```txt
django-storages==1.14.2
boto3==1.34.0
```

### 2.2 Install Locally (for testing)
```bash
pip install django-storages boto3
```

---

## Phase 3: Update Django Settings

### 3.1 Update `gistagum/settings.py`

You'll need to:
1. Add `storages` to `INSTALLED_APPS`
2. Configure Spaces settings
3. Update `MEDIA_ROOT` and `MEDIA_URL`

**Configuration will be added to your settings.py file.**

---

## Phase 4: Add Environment Variables to DigitalOcean

### 4.1 In DigitalOcean App Platform
1. Go to your app in DigitalOcean dashboard
2. Click **Settings** → **App-Level Environment Variables**
3. Add these variables:

```
AWS_ACCESS_KEY_ID = <your-spaces-access-key>
AWS_SECRET_ACCESS_KEY = <your-spaces-secret-key>
AWS_STORAGE_BUCKET_NAME = gistagum-media
AWS_S3_ENDPOINT_URL = https://sgp1.digitaloceanspaces.com
AWS_S3_REGION_NAME = sgp1
AWS_S3_CUSTOM_DOMAIN = <your-space-name>.sgp1.cdn.digitaloceanspaces.com
```

**Note**: Replace:
- `<your-spaces-access-key>` with your Access Key from Step 1.2
- `<your-spaces-secret-key>` with your Secret Key from Step 1.2
- `<your-space-name>` with your actual Space name (e.g., `gistagum-media`)

### 4.2 Mark as Secrets
- Mark `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as **SECRET** type
- This hides them in the UI for security

---

## Phase 5: Update Code

### 5.1 Settings Configuration
The settings will be updated to:
- Use Spaces for media files
- Keep static files local (or you can move those too later)
- Handle both development (local) and production (Spaces)

### 5.2 URL Configuration
Update `gistagum/urls.py` to serve media files correctly in development.

---

## Phase 6: Testing

### 6.1 Test Locally First
1. Set environment variables locally (or use `.env` file)
2. Run migrations (if any)
3. Test uploading an image
4. Verify it appears in your Spaces bucket

### 6.2 Test in Production
1. Deploy to DigitalOcean
2. Test image upload
3. Verify images load correctly
4. Check CDN delivery

---

## Phase 7: Migration Strategy (Optional)

### Option A: Gradual Migration (Recommended)
- New uploads go to Spaces
- Old files stay on volume
- Migrate old files gradually (if needed)

### Option B: Full Migration
- Migrate all existing files to Spaces
- Remove volume mount
- Update all references

---

## 📋 Checklist

- [ ] Created DigitalOcean Space
- [ ] Generated Access Keys
- [ ] Saved keys securely
- [ ] Added packages to requirements.txt
- [ ] Updated settings.py
- [ ] Added environment variables to DigitalOcean
- [ ] Tested locally
- [ ] Deployed to production
- [ ] Tested image upload
- [ ] Verified images load correctly
- [ ] (Optional) Migrated existing files

---

## 🔍 Verification Steps

### After Setup:
1. **Upload a test image** through your app
2. **Check Spaces bucket** - file should appear there
3. **View image in app** - should load from CDN
4. **Check browser network tab** - should show CDN URL

### Expected URLs:
- **Before**: `https://yourapp.ondigitalocean.app/media/project_images/image.jpg`
- **After**: `https://gistagum-media.sgp1.cdn.digitaloceanspaces.com/project_images/image.jpg`

---

## 🐛 Troubleshooting

### Issue: Images not uploading
- Check environment variables are set correctly
- Verify Access Keys are correct
- Check Space name matches `AWS_STORAGE_BUCKET_NAME`

### Issue: Images not loading
- Verify CDN is enabled on Space
- Check `AWS_S3_CUSTOM_DOMAIN` is correct
- Ensure Space is set to "Public" or files have correct permissions

### Issue: 403 Forbidden errors
- Check Access Keys have correct permissions
- Verify bucket name is correct
- Check region matches

---

## 💡 Next Steps After Implementation

1. **Monitor storage usage** in DigitalOcean dashboard
2. **Set up alerts** for storage limits
3. **Consider backup strategy** (Spaces has versioning)
4. **Optimize images** (compression, resizing) if needed
5. **Set up CloudFront** (if you need even better CDN performance)

---

**Ready to implement?** I'll help you update the code files! 🚀

