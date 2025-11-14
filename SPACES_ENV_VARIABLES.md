# 🔐 DigitalOcean Spaces Environment Variables

## Required Environment Variables for DigitalOcean App Platform

Add these environment variables in your DigitalOcean App Platform dashboard:

### Step-by-Step Instructions:

1. Go to your app in [DigitalOcean Dashboard](https://cloud.digitalocean.com/apps)
2. Click **Settings** → **App-Level Environment Variables**
3. Click **Edit** or **Add Variable**
4. Add each variable below:

---

## Environment Variables to Add:

### 1. Enable Spaces
```
Key: USE_SPACES
Value: true
Scope: RUN_AND_BUILD_TIME
Type: Plain Text
```

### 2. Spaces Access Key
```
Key: AWS_ACCESS_KEY_ID
Value: <your-spaces-access-key>
Scope: RUN_AND_BUILD_TIME
Type: SECRET ⚠️ (Mark as Secret!)
```

**How to get this:**
- Go to DigitalOcean Dashboard → **API** → **Spaces Keys**
- Generate a new key or use existing one
- Copy the **Access Key** (starts with `DO00...`)

### 3. Spaces Secret Key
```
Key: AWS_SECRET_ACCESS_KEY
Value: <your-spaces-secret-key>
Scope: RUN_AND_BUILD_TIME
Type: SECRET ⚠️ (Mark as Secret!)
```

**How to get this:**
- Same as above, copy the **Secret Key**
- ⚠️ You can only see this once! Save it securely.

### 4. Spaces Bucket Name
```
Key: AWS_STORAGE_BUCKET_NAME
Value: gistagum-media
Scope: RUN_AND_BUILD_TIME
Type: Plain Text
```

**Note:** Replace `gistagum-media` with your actual Space name (the one you created in Phase 1)

### 5. Spaces Endpoint URL
```
Key: AWS_S3_ENDPOINT_URL
Value: https://sgp1.digitaloceanspaces.com
Scope: RUN_AND_BUILD_TIME
Type: Plain Text
```

**Note:** 
- If your Space is in Singapore: `https://sgp1.digitaloceanspaces.com`
- If your Space is in New York: `https://nyc3.digitaloceanspaces.com`
- If your Space is in Amsterdam: `https://ams3.digitaloceanspaces.com`
- Check your Space region in DigitalOcean dashboard

### 6. Spaces Region (Optional - defaults to sgp1)
```
Key: AWS_S3_REGION_NAME
Value: sgp1
Scope: RUN_AND_BUILD_TIME
Type: Plain Text
```

**Note:** Should match your Space region (sgp1, nyc3, ams3, etc.)

### 7. CDN Domain (Optional but Recommended)
```
Key: AWS_S3_CUSTOM_DOMAIN
Value: gistagum-media.sgp1.cdn.digitaloceanspaces.com
Scope: RUN_AND_BUILD_TIME
Type: Plain Text
```

**How to get this:**
- Go to your Space in DigitalOcean dashboard
- Click **Settings** → **CDN**
- If CDN is enabled, you'll see the CDN endpoint
- Format: `<space-name>.<region>.cdn.digitaloceanspaces.com`
- Replace `gistagum-media` with your actual Space name
- Replace `sgp1` with your actual region

**Note:** This is optional. If not set, files will be served from the endpoint URL directly (still works, but CDN is faster).

---

## 📋 Quick Checklist

- [ ] Created DigitalOcean Space
- [ ] Generated Spaces Access Keys
- [ ] Added `USE_SPACES=true`
- [ ] Added `AWS_ACCESS_KEY_ID` (marked as SECRET)
- [ ] Added `AWS_SECRET_ACCESS_KEY` (marked as SECRET)
- [ ] Added `AWS_STORAGE_BUCKET_NAME` (your Space name)
- [ ] Added `AWS_S3_ENDPOINT_URL` (correct region)
- [ ] Added `AWS_S3_REGION_NAME` (optional, matches region)
- [ ] Added `AWS_S3_CUSTOM_DOMAIN` (optional, CDN endpoint)

---

## 🔍 Verification

After adding all variables:

1. **Redeploy your app** (or it will pick up changes on next deploy)
2. **Check app logs** - you should see:
   - `✅ DigitalOcean Spaces configured for media storage`
3. **Test uploading an image** through your app
4. **Check your Space** - the file should appear there
5. **View the image** - should load from CDN (if configured)

---

## 🐛 Troubleshooting

### Issue: Still using local storage
- Check `USE_SPACES=true` is set (not `True` or `1`)
- Verify all required variables are set
- Check app logs for warnings

### Issue: 403 Forbidden errors
- Verify Access Key and Secret Key are correct
- Check bucket name matches exactly (case-sensitive)
- Ensure Space is set to "Public" or files have correct ACL

### Issue: Images not loading
- Check `AWS_S3_CUSTOM_DOMAIN` is correct (if using CDN)
- Verify CDN is enabled on your Space
- Check Space region matches endpoint URL

---

## 💡 Example Values (Replace with Your Actual Values)

```
USE_SPACES=true
AWS_ACCESS_KEY_ID=DO00ABCD1234EFGH5678
AWS_SECRET_ACCESS_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
AWS_STORAGE_BUCKET_NAME=gistagum-media
AWS_S3_ENDPOINT_URL=https://sgp1.digitaloceanspaces.com
AWS_S3_REGION_NAME=sgp1
AWS_S3_CUSTOM_DOMAIN=gistagum-media.sgp1.cdn.digitaloceanspaces.com
```

**⚠️ Never commit these values to git! They're already configured as environment variables.**

---

## 📚 Next Steps

After setting up environment variables:
1. Deploy your app
2. Test image uploads
3. Verify images are stored in Spaces
4. Check images load correctly in your app

See `DIGITALOCEAN_SPACES_SETUP.md` for complete setup instructions.

