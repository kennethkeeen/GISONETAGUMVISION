# Phase 3 Testing Guide - WebSocket Broadcasting

## 🎯 Goal
Verify that Phase 3 changes (WebSocket broadcasting) work correctly and send updates via WebSocket alongside SSE.

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

### Step 2: Test WebSocket Broadcasting (Browser Console)

#### 2.1 Setup WebSocket Connection
1. **Open your app** in browser
2. **Login** as Head Engineer (or any authorized user)
3. **Open browser console** (F12 → Console tab)
4. **Run this JavaScript to connect to WebSocket:**

```javascript
// Connect to project updates WebSocket
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/ws/projects/`;

const ws = new WebSocket(wsUrl);

ws.onopen = () => {
    console.log('✅ Project updates WebSocket connected!');
    console.log('Waiting for project updates...');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('📨 Project update received:', data);
    
    // Display update in console
    if (data.type === 'project_created') {
        console.log(`🆕 New project: ${data.name} (PRN: ${data.prn})`);
    } else if (data.type === 'project_status_changed') {
        console.log(`🔄 Status changed: ${data.name} - ${data.old_status} → ${data.new_status}`);
    } else if (data.type === 'project_deleted') {
        console.log(`🗑️  Project deleted: ${data.name}`);
    } else if (data.type === 'cost_updated') {
        console.log(`💰 Cost updated: ${data.project_name} - ${data.cost_data.formatted_amount}`);
    } else if (data.type === 'progress_updated') {
        console.log(`📊 Progress updated: ${data.project_name} - ${data.progress_data.percentage_complete}%`);
    }
};

ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
};

ws.onclose = () => {
    console.log('🔌 WebSocket closed');
};

// Keep connection open
console.log('WebSocket connection established. Perform actions in another tab to see updates!');
```

**Expected:** Console shows "Project updates WebSocket connected!"

#### 2.2 Test Project Creation Broadcast
1. **Keep WebSocket connection open** (from Step 2.1)
2. **Open a new tab** (or use another browser)
3. **Login** as Head Engineer
4. **Create a new project**
5. **Check the console** in the first tab

**Expected:**
- ✅ Console shows: `📨 Project update received: {type: 'project_created', ...}`
- ✅ Console shows: `🆕 New project: [Project Name] (PRN: [PRN])`
- ✅ SSE notification also appears (both systems work!)

#### 2.3 Test Project Status Change Broadcast
1. **Keep WebSocket connection open**
2. **In another tab**, update a project's status
3. **Check the console**

**Expected:**
- ✅ Console shows: `📨 Project update received: {type: 'project_status_changed', ...}`
- ✅ Console shows: `🔄 Status changed: [Project Name] - [old] → [new]`
- ✅ SSE notification also appears

#### 2.4 Test Cost Update Broadcast
1. **Keep WebSocket connection open**
2. **In another tab**, add a cost entry to a project
3. **Check the console**

**Expected:**
- ✅ Console shows: `📨 Project update received: {type: 'cost_updated', ...}`
- ✅ Console shows: `💰 Cost updated: [Project Name] - ₱[amount]`
- ✅ SSE notification also appears

#### 2.5 Test Progress Update Broadcast
1. **Keep WebSocket connection open**
2. **In another tab**, add a progress update to a project
3. **Check the console**

**Expected:**
- ✅ Console shows: `📨 Project update received: {type: 'progress_updated', ...}`
- ✅ Console shows: `📊 Progress updated: [Project Name] - [X]%`
- ✅ SSE notification also appears

#### 2.6 Test Project Deletion Broadcast
1. **Keep WebSocket connection open**
2. **In another tab**, delete a project
3. **Check the console**

**Expected:**
- ✅ Console shows: `📨 Project update received: {type: 'project_deleted', ...}`
- ✅ Console shows: `🗑️  Project deleted: [Project Name]`
- ✅ SSE notification also appears

---

### Step 3: Test Notifications WebSocket

#### 3.1 Connect to Notifications WebSocket
```javascript
// Connect to notifications WebSocket
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;

const wsNotifications = new WebSocket(wsUrl);

wsNotifications.onopen = () => {
    console.log('✅ Notifications WebSocket connected!');
};

wsNotifications.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('📨 Notification received:', data);
};

wsNotifications.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
};

wsNotifications.onclose = () => {
    console.log('🔌 Notifications WebSocket closed');
};
```

**Expected:** Console shows "Notifications WebSocket connected!"

---

### Step 4: Verify Both SSE and WebSocket Work

#### 4.1 Test Parallel Systems
1. **Connect WebSocket** (from Step 2.1)
2. **Perform an action** (create project, update status, etc.)
3. **Check both:**
   - [ ] SSE notification appears (badge count, browser notification)
   - [ ] WebSocket message appears in console

**Expected:** Both systems send updates simultaneously ✅

#### 4.2 Test Failsafe Behavior
1. **Disconnect WebSocket** (close connection)
2. **Perform an action**
3. **Check:**
   - [ ] SSE notification still appears
   - [ ] No errors in console
   - [ ] System continues to work

**Expected:** SSE continues to work even if WebSocket fails ✅

---

### Step 5: Check Logs for Broadcast Messages

#### 5.1 Check DigitalOcean Logs
After performing actions, check logs for:

**Expected messages:**
```
✅ WebSocket project update broadcast: project_created
✅ WebSocket project update broadcast: project_status_changed
✅ WebSocket project update broadcast: cost_updated
✅ WebSocket project update broadcast: progress_updated
✅ WebSocket project update broadcast: project_deleted
```

**If you see:**
```
⚠️  WebSocket broadcast failed (SSE still works): [error]
```
This is OK - it means WebSocket failed but SSE still works (failsafe design)

---

### Step 6: Test Multiple Users (Real-time Collaboration)

#### 6.1 Test with Two Users
1. **User 1:** Connect WebSocket, keep console open
2. **User 2:** Login in another browser/device
3. **User 2:** Create/update a project
4. **User 1:** Check console

**Expected:**
- ✅ User 1 sees update in WebSocket console immediately
- ✅ User 1 also sees SSE notification
- ✅ Both users see updates in real-time

#### 6.2 Test Map Updates
1. **User 1:** Open map view, connect WebSocket
2. **User 2:** Create a new project with location
3. **User 1:** Check console and map

**Expected:**
- ✅ WebSocket receives project_created message
- ✅ Map should update (if frontend handles WebSocket messages)
- ✅ SSE also sends update

---

## 🔍 How to Check Logs in DigitalOcean

### Method 1: Runtime Logs
1. Go to **DigitalOcean → Apps → ONETAGUMVISION**
2. Click on **Runtime Logs** tab
3. Look for:
   - `✅ WebSocket project update broadcast: [type]`
   - `✅ WebSocket notification broadcast to user_[id]`
   - Any error messages

### Method 2: Filter Logs
Look for these patterns:
- `WebSocket broadcast` - Shows successful broadcasts
- `WebSocket broadcast failed` - Shows failures (SSE still works)

---

## ✅ Success Criteria

Phase 3 is successful if:

1. ✅ **All existing features work** (most important!)
2. ✅ **SSE notifications still work**
3. ✅ **WebSocket receives broadcasts** (visible in console)
4. ✅ **Both systems work in parallel** (SSE + WebSocket)
5. ✅ **Failsafe works** (SSE continues if WebSocket fails)
6. ✅ **Real-time updates work** (multiple users see updates)

---

## ⚠️ Common Issues & Solutions

### Issue 1: WebSocket Connects But No Messages
**Symptoms:**
- Connection succeeds
- No messages received when actions are performed

**Possible Causes:**
- WebSocket broadcasting not triggered
- Channel layer not configured correctly
- Actions not triggering signals

**Solutions:**
- ✅ Check logs for broadcast messages
- ✅ Verify signals are being called
- ✅ Check that `WEBSOCKET_AVAILABLE = True` in signals
- ✅ Verify Redis/Valkey connection

### Issue 2: WebSocket Messages But SSE Doesn't Work
**This shouldn't happen, but if it does:**
- ✅ Check SSE endpoint is still accessible
- ✅ Verify SSE client is still connected
- ✅ Check browser console for SSE errors

### Issue 3: Both Systems Work But Messages Are Duplicate
**This is expected and OK!**
- Both SSE and WebSocket send updates
- Frontend can choose which to use
- Or use both for redundancy

### Issue 4: WebSocket Broadcast Fails
**Symptoms:**
- Logs show: `⚠️  WebSocket broadcast failed (SSE still works)`

**This is OK!**
- Failsafe design is working
- SSE continues to work
- Check Redis/Valkey connection
- Verify Channel Layers configuration

---

## 📊 Test Results Template

Copy this and fill it out:

```
Phase 3 Testing Results
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

Step 2: WebSocket Broadcasting
- [ ] WebSocket connects: Yes/No
- [ ] Project created broadcast: Yes/No
- [ ] Status change broadcast: Yes/No
- [ ] Cost update broadcast: Yes/No
- [ ] Progress update broadcast: Yes/No
- [ ] Project deleted broadcast: Yes/No

Step 3: Notifications WebSocket
- [ ] Notifications WebSocket connects: Yes/No
- [ ] Receives messages: Yes/No

Step 4: Both Systems Work
- [ ] SSE still works: Yes/No
- [ ] WebSocket receives broadcasts: Yes/No
- [ ] Both work in parallel: Yes/No

Step 5: Logs Check
- [ ] Broadcast messages in logs: Yes/No
- [ ] Any errors: Yes/No (if yes, describe: ___________)

Step 6: Multi-User Test
- [ ] User 1 sees User 2's updates: Yes/No
- [ ] Real-time collaboration works: Yes/No

Overall Result: ✅ PASS / ❌ FAIL

Notes:
_________________________________
_________________________________
```

---

## 🎯 What to Expect

### ✅ Normal Behavior:
- WebSocket connects successfully
- Console shows broadcast messages when actions are performed
- SSE notifications continue to work
- Both systems send updates simultaneously
- No errors in logs

### 📨 Message Types You'll See:
- `project_created` - When a new project is created
- `project_status_changed` - When project status changes
- `project_updated` - When project details are updated
- `project_deleted` - When a project is deleted
- `cost_updated` - When a cost entry is added
- `progress_updated` - When progress is updated

---

## 🚀 Next Steps After Phase 3 Passes

Once Phase 3 testing is successful:
- ✅ WebSocket broadcasting is working
- ✅ Both SSE and WebSocket send updates
- ✅ Real-time collaboration is possible
- ✅ Can proceed to Phase 4 (frontend WebSocket client) or use as-is

**Phase 4 (Optional):** Add frontend JavaScript to automatically connect to WebSocket and update UI in real-time (instead of just showing in console).

---

## 🔄 Rollback Plan (If Needed)

If Phase 3 causes issues:

1. **Remove WebSocket broadcasts from signals.py**
   - Comment out or remove `if WEBSOCKET_AVAILABLE:` blocks
   - System returns to Phase 2 state
   - SSE continues to work

2. **Remove channels_utils.py**
   - Delete the file
   - System returns to Phase 2 state

**Time to rollback:** < 5 minutes

---

## 💡 Tips for Testing

1. **Use two browsers** - One for WebSocket connection, one for actions
2. **Keep console open** - See WebSocket messages in real-time
3. **Check logs frequently** - Verify broadcasts are happening
4. **Test all actions** - Create, update, delete, add costs, add progress
5. **Test with multiple users** - Verify real-time collaboration

---

## ✅ Phase 3 Complete!

If all tests pass:
- ✅ WebSocket broadcasting is working
- ✅ Real-time updates are possible
- ✅ System is ready for production use
- ✅ Can add frontend client in Phase 4 (optional)

