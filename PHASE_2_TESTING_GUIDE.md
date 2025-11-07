# Phase 2 Testing Guide - WebSocket Support

## 🎯 Goal
Verify that Phase 2 changes (WebSocket consumers and routing) don't break anything and WebSocket connections work properly.

---

## ✅ Testing Checklist

### Step 1: Verify System Still Works (Most Important!)

#### 1.1 Test All Existing Features
- [ ] Login works (all user types)
- [ ] Dashboards load correctly
- [ ] **SSE notifications still work** (critical!)
- [ ] Projects can be created/updated/deleted
- [ ] Map view works
- [ ] Reports generation works
- [ ] All pages load without errors

**Expected:** Everything works exactly as before

---

### Step 2: Check Logs for WebSocket Setup

#### 2.1 Check Deployment Logs
After deployment, check DigitalOcean logs for:

**Expected messages:**
```
✅ Django Channels configured with SSL Redis connection
```

**No errors should appear:**
- ❌ No import errors
- ❌ No routing errors
- ❌ No consumer errors

#### 2.2 Check Runtime Logs
Look for WebSocket connection messages when users connect:
```
✅ WebSocket connected: User username - Group: user_X_notifications
✅ Project updates WebSocket connected: User username
```

---

### Step 3: Test WebSocket Connection (Browser Console)

#### 3.1 Test Notifications WebSocket
1. **Open your app** in browser
2. **Login** as any user
3. **Open browser console** (F12 → Console tab)
4. **Run this JavaScript:**

```javascript
// Test WebSocket connection for notifications
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;

const ws = new WebSocket(wsUrl);

ws.onopen = () => {
    console.log('✅ WebSocket connected!');
};

ws.onmessage = (event) => {
    console.log('📨 Message received:', JSON.parse(event.data));
};

ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
};

ws.onclose = () => {
    console.log('🔌 WebSocket closed');
};

// Keep connection open for testing
setTimeout(() => {
    console.log('WebSocket connection test complete');
}, 5000);
```

**Expected results:**
- ✅ Console shows: "WebSocket connected!"
- ✅ No errors
- ✅ Connection stays open

**If you see errors:**
- Check if you're logged in (WebSocket requires authentication)
- Check browser console for CORS/connection errors
- Verify the URL matches your domain

#### 3.2 Test Project Updates WebSocket
```javascript
// Test WebSocket connection for project updates
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/ws/projects/`;

const ws = new WebSocket(wsUrl);

ws.onopen = () => {
    console.log('✅ Project updates WebSocket connected!');
};

ws.onmessage = (event) => {
    console.log('📨 Project update:', JSON.parse(event.data));
};

ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
};

ws.onclose = () => {
    console.log('🔌 WebSocket closed');
};
```

**Expected results:**
- ✅ Console shows: "Project updates WebSocket connected!"
- ✅ No errors
- ✅ Connection stays open

---

### Step 4: Verify Both SSE and WebSocket Work

#### 4.1 Test SSE Still Works
- [ ] Notification badge updates in real-time
- [ ] Dashboard updates via SSE
- [ ] No errors in console related to SSE

#### 4.2 Test WebSocket Connection
- [ ] Can connect via WebSocket (from Step 3)
- [ ] Connection stays open
- [ ] No errors in console

**Expected:** Both systems work in parallel ✅

---

### Step 5: Test Authentication

#### 5.1 Test Without Login
1. **Logout** from the app
2. **Try to connect WebSocket** (use code from Step 3)
3. **Expected:** Connection should be rejected/closed immediately

#### 5.2 Test With Login
1. **Login** as any user
2. **Try to connect WebSocket**
3. **Expected:** Connection succeeds

---

### Step 6: Test Different User Roles

#### 6.1 Test as Head Engineer
- [ ] Can connect to `/ws/notifications/`
- [ ] Can connect to `/ws/projects/`
- [ ] Both connections work

#### 6.2 Test as Project Engineer
- [ ] Can connect to `/ws/notifications/`
- [ ] Can connect to `/ws/projects/`
- [ ] Both connections work

#### 6.3 Test as Finance Manager
- [ ] Can connect to `/ws/notifications/`
- [ ] Can connect to `/ws/projects/`
- [ ] Both connections work

---

## 🔍 How to Check Logs in DigitalOcean

### Method 1: Runtime Logs
1. Go to **DigitalOcean → Apps → ONETAGUMVISION**
2. Click on **Runtime Logs** tab
3. Look for:
   - WebSocket connection messages
   - Any errors related to WebSocket
   - Channels configuration messages

### Method 2: Build Logs
1. Go to **DigitalOcean → Apps → ONETAGUMVISION**
2. Click on **Activity** tab
3. Find the latest deployment
4. Check for any build errors

---

## ✅ Success Criteria

Phase 2 is successful if:

1. ✅ **All existing features work** (most important!)
2. ✅ **SSE notifications still work**
3. ✅ **WebSocket connections succeed** (from browser console)
4. ✅ **No errors in logs**
5. ✅ **Authentication works** (logged-in users can connect)
6. ✅ **Both SSE and WebSocket work in parallel**

---

## ⚠️ Common Issues & Solutions

### Issue 1: WebSocket Connection Fails
**Symptoms:**
- Console shows connection error
- Connection closes immediately

**Solutions:**
- ✅ Make sure you're logged in
- ✅ Check if URL is correct (ws:// for http, wss:// for https)
- ✅ Verify domain matches your DigitalOcean app URL
- ✅ Check browser console for specific error message

### Issue 2: "404 Not Found" for WebSocket
**Symptoms:**
- WebSocket connection returns 404

**Solutions:**
- ✅ Verify `asgi.py` is properly configured
- ✅ Check that `routing.py` exists and has correct patterns
- ✅ Ensure Daphne is installed (for production)
- ✅ For now, Gunicorn handles HTTP, Daphne needed for WebSocket in production

### Issue 3: Authentication Errors
**Symptoms:**
- Connection closes immediately after opening
- Logs show authentication failure

**Solutions:**
- ✅ Make sure user is logged in
- ✅ Check that session cookies are being sent
- ✅ Verify `AuthMiddlewareStack` is in `asgi.py`

### Issue 4: SSE Still Works But WebSocket Doesn't
**This is OK for now!**
- SSE is still working (good!)
- WebSocket will work once we add broadcasting in Phase 3
- Phase 2 just sets up the infrastructure

---

## 📊 Test Results Template

Copy this and fill it out:

```
Phase 2 Testing Results
=======================

Date: ___________
Tester: ___________

Step 1: System Still Works
- [ ] Login works
- [ ] Dashboards load
- [ ] SSE notifications work
- [ ] Projects work
- [ ] Map works
- [ ] All features functional

Step 2: Logs Check
- [ ] Channels configured message: Yes/No
- [ ] WebSocket connection messages: Yes/No
- [ ] Any errors: Yes/No (if yes, describe: ___________)

Step 3: WebSocket Connection Test
- [ ] Notifications WebSocket connects: Yes/No
- [ ] Project updates WebSocket connects: Yes/No
- [ ] Console shows connection success: Yes/No
- [ ] Any errors in console: Yes/No

Step 4: Both Systems Work
- [ ] SSE still works: Yes/No
- [ ] WebSocket connects: Yes/No
- [ ] Both work in parallel: Yes/No

Step 5: Authentication
- [ ] WebSocket rejects unauthenticated: Yes/No
- [ ] WebSocket accepts authenticated: Yes/No

Step 6: User Roles
- [ ] Head Engineer can connect: Yes/No
- [ ] Project Engineer can connect: Yes/No
- [ ] Finance Manager can connect: Yes/No

Overall Result: ✅ PASS / ❌ FAIL

Notes:
_________________________________
_________________________________
```

---

## 🎯 What to Expect

### ✅ Normal Behavior:
- WebSocket connects successfully when logged in
- Connection stays open
- Console shows "WebSocket connected!"
- No errors in logs
- SSE continues to work

### ⚠️ Note About Messages:
- **You won't see messages yet** - that's Phase 3!
- Phase 2 just sets up the connection infrastructure
- Messages will be sent in Phase 3 when we add broadcasting

---

## 🚀 Next Steps After Phase 2 Passes

Once Phase 2 testing is successful:
- ✅ WebSocket infrastructure is ready
- ✅ Can proceed to Phase 3 (broadcasting)
- ✅ Phase 3 will send actual updates via WebSocket

**Ready for Phase 3?** We'll add broadcasting functions that send updates via WebSocket (parallel to SSE).

---

## 🔄 Rollback Plan (If Needed)

If Phase 2 causes issues:

1. **Revert asgi.py** to Phase 1 version (remove WebSocket routing)
2. **Remove consumers.py and routing.py**
3. **System returns to Phase 1 state**
4. **SSE continues to work**

**Time to rollback:** < 5 minutes

