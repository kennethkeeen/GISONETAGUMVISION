# Testing Suitability Integration on Map View

## ✅ Pre-Test Verification

**Database Status:**
- ✅ 10 projects with coordinates
- ✅ 10 projects with suitability analysis
- ✅ Sample: Project 107 - Score: 70.0, Category: "suitable"

**Code Status:**
- ✅ Django system check: No issues
- ✅ No linter errors
- ✅ Backend: Suitability data added to `map_view`
- ✅ Frontend: Marker icons and popups enhanced

---

## 🧪 Manual Testing Steps

### Step 1: Start the Server
```bash
python manage.py runserver
```

### Step 2: Navigate to Map View
1. Open browser: `http://localhost:8000/dashboard/map/`
2. Login as Head Engineer or Finance Manager
3. You should see the map with project markers

### Step 3: Check Browser Console
1. Open Developer Tools (F12)
2. Go to Console tab
3. Look for logs like:
   ```
   Adding marker for project ID: 107 Suitability: 70
   ```
4. Verify `window.projects` contains suitability data:
   ```javascript
   console.log(window.projects[0].suitability_score);
   // Should show: 70 (or similar number)
   ```

### Step 4: Visual Inspection - Marker Icons
1. **Look for colored badges on markers:**
   - Green dot = Highly Suitable (80-100)
   - Yellow dot = Suitable (60-79)
   - Orange dot = Moderate (40-59)
   - Red dot = Not Suitable (0-39)
   - No dot = No suitability data (backward compatible)

2. **Expected behavior:**
   - All 10 projects should have colored badges
   - Badge appears in top-right corner of marker icon
   - Status-based marker color (blue/green/amber) still visible

### Step 5: Test Popup Display
1. **Click on any project marker**
2. **Look for "Land Suitability" section** in the popup:
   - Should appear between location and progress sections
   - Color-coded background (green/yellow/orange/red)
   - Shows score out of 100
   - Shows category label (e.g., "Suitable")
   - Progress bar visualization

3. **Check for risk indicators:**
   - ⚠️ Flood Risk badge (if applicable)
   - ⚠️ Zoning Conflict badge (if applicable)

### Step 6: Test Backward Compatibility
1. **Projects without suitability data should:**
   - Still display on map
   - Show normal status-based markers (no suitability badge)
   - Popup should NOT show suitability section
   - No errors in console

---

## 🎯 Expected Results

### ✅ Success Indicators:
- [ ] All markers display correctly
- [ ] Suitability badges visible on markers with data
- [ ] Popups show suitability section for projects with data
- [ ] No JavaScript errors in console
- [ ] No 500 errors in Django logs
- [ ] Projects without suitability data still work

### ❌ Failure Indicators:
- [ ] JavaScript errors in console
- [ ] Markers not displaying
- [ ] Suitability data not showing in popups
- [ ] 500 errors when loading map view
- [ ] Projects without suitability data breaking

---

## 🔍 Debugging

### If suitability data is not showing:

1. **Check backend data:**
   ```python
   python manage.py shell
   >>> from projeng.models import LandSuitabilityAnalysis
   >>> LandSuitabilityAnalysis.objects.count()
   ```

2. **Check browser console:**
   - Look for `window.projects` array
   - Verify `suitability_score` property exists
   - Check for JavaScript errors

3. **Check Django logs:**
   - Look for errors in `map_view` function
   - Verify `LandSuitabilityAnalysis` import works

4. **Verify template:**
   - Check `templates/monitoring/map.html`
   - Ensure `getSuitabilityColor()` function exists
   - Ensure `createMarkerIcon()` accepts second parameter

---

## 📊 Test Data Reference

**Sample Projects with Suitability:**
- Project 107: Score 70.0, Category: "suitable"
- Project 110: Score 70.0, Category: "suitable"
- Project 109: Score 71.5, Category: "suitable"
- Project 112: Score 65.5, Category: "suitable"
- Project 111: Score 70.0, Category: "suitable"

**Expected Colors:**
- 70.0 = Yellow (#eab308) - Suitable
- 71.5 = Yellow (#eab308) - Suitable
- 65.5 = Yellow (#eab308) - Suitable

---

## ✅ Test Checklist

- [ ] Server starts without errors
- [ ] Map view loads successfully
- [ ] All project markers display
- [ ] Suitability badges visible on markers
- [ ] Popups show suitability information
- [ ] No console errors
- [ ] No Django errors
- [ ] Backward compatibility works (projects without suitability)

---

## 🚀 Next Steps After Testing

If all tests pass:
1. ✅ Integration is successful
2. ✅ Ready for production
3. ✅ Can proceed with Phase 2 (optional view toggle)

If tests fail:
1. Check error messages
2. Review implementation
3. Fix issues
4. Re-test

