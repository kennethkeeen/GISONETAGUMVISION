# Phase 2 Testing Guide: View Mode Toggle

## ✅ Pre-Test Verification

**Implementation Status:**
- ✅ View mode toggle buttons added to filter section
- ✅ Status and Suitability view modes implemented
- ✅ Dynamic legend system added
- ✅ Marker color logic updated for both modes
- ✅ CSS styling for toggle buttons

---

## 🧪 Testing Steps

### Step 1: Start the Server
```bash
python manage.py runserver
```

### Step 2: Navigate to Map View
1. Open browser: `http://localhost:8000/dashboard/map/`
2. Login as Head Engineer or Finance Manager
3. You should see the map with project markers

### Step 3: Locate View Mode Toggle
1. **Look for the toggle buttons** in the filter section (below status filters)
2. **You should see:**
   - "Status" button (should be active/blue by default)
   - "Suitability" button (should be inactive/gray)
3. **Location:** Below the status filter buttons, in a gray rounded container

### Step 4: Test Status View (Default)
1. **Verify Status view is active:**
   - "Status" button should be blue/active
   - "Suitability" button should be gray/inactive

2. **Check marker colors:**
   - Green markers = Completed projects
   - Blue markers = In Progress projects
   - Amber/Yellow markers = Planned projects
   - Small colored badges may appear on markers (suitability indicators)

3. **Check legend (bottom-right of map):**
   - Should show "Project Status" title
   - Should list: Completed, In Progress, Planned
   - Colors should match marker colors

### Step 5: Test Suitability View
1. **Click the "Suitability" button**
2. **Verify button state changes:**
   - "Suitability" button becomes blue/active
   - "Status" button becomes gray/inactive

3. **Check marker colors change:**
   - Green markers = Highly Suitable (80-100)
   - Yellow markers = Suitable (60-79)
   - Orange markers = Moderate (40-59)
   - Red markers = Not Suitable (0-39)
   - Projects without suitability data should use status color as fallback

4. **Check legend updates:**
   - Should show "Land Suitability" title
   - Should list: Highly Suitable (80-100), Suitable (60-79), Moderate (40-59), Not Suitable (0-39)
   - Colors should match marker colors

5. **Verify markers re-render:**
   - All markers should update their colors immediately
   - No markers should disappear
   - Marker positions should remain the same

### Step 6: Test Toggle Back to Status View
1. **Click the "Status" button**
2. **Verify:**
   - Button states swap back
   - Markers return to status-based colors
   - Legend updates to show status information
   - All markers remain visible

### Step 7: Test Multiple Toggles
1. **Toggle between views 3-4 times**
2. **Verify:**
   - Smooth transitions each time
   - No errors in browser console
   - Legend updates correctly each time
   - Markers update correctly each time

### Step 8: Test with Filters
1. **Apply status filter** (e.g., click "Completed")
2. **Toggle to Suitability view**
3. **Verify:**
   - Only filtered projects show (if any)
   - Colors update based on suitability
   - Legend still shows suitability information

4. **Toggle back to Status view**
5. **Verify:**
   - Filtered projects still show
   - Colors return to status-based

### Step 9: Check Browser Console
1. **Open Developer Tools (F12)**
2. **Go to Console tab**
3. **Look for:**
   - `View mode changed to: status` or `View mode changed to: suitability`
   - No JavaScript errors
   - No undefined function errors

---

## 🎯 Expected Results

### ✅ Success Indicators:
- [ ] Toggle buttons visible and clickable
- [ ] Status view shows status-colored markers (green/blue/amber)
- [ ] Suitability view shows suitability-colored markers (green/yellow/orange/red)
- [ ] Legend updates correctly for both views
- [ ] Markers re-render immediately when toggling
- [ ] No JavaScript errors in console
- [ ] Smooth transitions between views
- [ ] Works with existing filters (status, barangay, date)

### ❌ Failure Indicators:
- [ ] Toggle buttons not visible
- [ ] Buttons not clickable
- [ ] Markers don't change color when toggling
- [ ] Legend doesn't update
- [ ] JavaScript errors in console
- [ ] Markers disappear when toggling
- [ ] Page crashes or freezes

---

## 🔍 Visual Verification

### Status View Should Show:
```
[Status] [Suitability]  ← Toggle buttons
Status button: BLUE (active)
Suitability button: GRAY (inactive)

Markers:
🟢 Green = Completed
🔵 Blue = In Progress
🟡 Amber = Planned

Legend (bottom-right):
Project Status
🟢 Completed
🔵 In Progress
🟡 Planned
```

### Suitability View Should Show:
```
[Status] [Suitability]  ← Toggle buttons
Status button: GRAY (inactive)
Suitability button: BLUE (active)

Markers:
🟢 Green = Highly Suitable (80-100)
🟡 Yellow = Suitable (60-79)
🟠 Orange = Moderate (40-59)
🔴 Red = Not Suitable (0-39)

Legend (bottom-right):
Land Suitability
🟢 Highly Suitable (80-100)
🟡 Suitable (60-79)
🟠 Moderate (40-59)
🔴 Not Suitable (0-39)
```

---

## 🐛 Troubleshooting

### Issue: Toggle buttons not visible
**Solution:**
- Check if filter section is visible
- Look below status filter buttons
- Check browser console for errors

### Issue: Buttons not clickable
**Solution:**
- Check if JavaScript is enabled
- Look for JavaScript errors in console
- Verify event listeners are attached

### Issue: Markers don't change color
**Solution:**
- Check browser console for errors
- Verify `viewMode` variable is being set
- Check if `renderMarkers()` is being called
- Verify `createMarkerIcon()` function is using `viewMode`

### Issue: Legend doesn't update
**Solution:**
- Check if `updateLegend()` function exists
- Verify `mapLegend` variable is being managed correctly
- Check browser console for errors
- Verify map is initialized before legend

### Issue: JavaScript errors
**Solution:**
- Check console for specific error messages
- Verify all functions are defined before use
- Check for typos in function names
- Verify DOM elements exist before accessing

---

## 📊 Test Data Reference

**Expected Marker Colors in Suitability View:**
- Project 107: Score 70.0 → Yellow marker
- Project 110: Score 70.0 → Yellow marker
- Project 109: Score 71.5 → Yellow marker
- Project 112: Score 65.5 → Yellow marker
- Project 111: Score 70.0 → Yellow marker

**All projects should show yellow markers in suitability view** (scores 60-79 = Suitable)

---

## ✅ Test Checklist

- [ ] Server starts without errors
- [ ] Map view loads successfully
- [ ] Toggle buttons are visible
- [ ] Status view works (default)
- [ ] Suitability view works
- [ ] Toggle back to Status works
- [ ] Legend updates correctly
- [ ] Markers change color correctly
- [ ] No console errors
- [ ] Works with filters
- [ ] Smooth transitions

---

## 🚀 Next Steps After Testing

**If all tests pass:**
1. ✅ Phase 2 is complete
2. ✅ Ready to push to GitHub
3. ✅ Integration is successful

**If tests fail:**
1. Note the specific issue
2. Check error messages
3. Review implementation
4. Fix issues
5. Re-test
