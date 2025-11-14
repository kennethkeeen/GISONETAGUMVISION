# Phase 3 Testing Guide: GEO-RBAC + Combined Analytics

## ✅ Pre-Test Verification

**Implementation Status:**
- ✅ UserSpatialAssignment model created
- ✅ Combined analytics API endpoint created
- ✅ Analytics view and template created
- ✅ Charts and visualizations added
- ✅ GEO-RBAC filtering implemented

---

## 🧪 Testing Steps

### Step 1: Verify Database Migration
```bash
python manage.py migrate projeng
```

**Expected:** Migration `0020_userspatialassignment` should be applied successfully.

### Step 2: Test Model Creation (Django Shell)
```bash
python manage.py shell
```

```python
from projeng.models import UserSpatialAssignment
from django.contrib.auth.models import User

# Check if model exists
print(UserSpatialAssignment.objects.count())

# Test creating an assignment
user = User.objects.first()  # Get any user
assignment = UserSpatialAssignment.objects.create(
    user=user,
    barangay='Magugpo Poblacion',
    is_active=True
)
print(f"Created: {assignment}")

# Test helper methods
barangays = UserSpatialAssignment.get_user_barangays(user)
print(f"User barangays: {list(barangays)}")

has_access = UserSpatialAssignment.user_has_access(user, 'Magugpo Poblacion')
print(f"Has access: {has_access}")
```

**Expected:**
- Model creates successfully
- Helper methods work correctly
- No errors

### Step 3: Test API Endpoint

**Option A: Using Browser**
1. Login to the system
2. Navigate to: `http://localhost:8000/projeng/api/combined-analytics/`
3. Should see JSON response with clusters and summary

**Option B: Using curl/Postman**
```bash
# First, get your session cookie or use authentication
curl -X GET http://localhost:8000/projeng/api/combined-analytics/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

**Expected Response Structure:**
```json
{
  "clusters": [
    {
      "barangay": "Magugpo Poblacion",
      "project_count": 5,
      "suitability_stats": {
        "average_score": 70.5,
        "highly_suitable_count": 0,
        "suitable_count": 5,
        "moderate_count": 0,
        "low_suitable_count": 0,
        "projects_with_analysis": 5,
        "flood_risk_count": 0,
        "zoning_conflict_count": 0
      },
      "projects": [...]
    }
  ],
  "summary": {
    "total_barangays": 3,
    "total_projects": 10,
    "total_projects_with_suitability": 10,
    "average_suitability": 70.0,
    "accessible_barangays": "all"
  }
}
```

### Step 4: Test Analytics View

1. **Start the server:**
   ```bash
   python manage.py runserver
   ```

2. **Navigate to analytics page:**
   - URL: `http://localhost:8000/projeng/analytics/combined/`
   - Login as Head Engineer or Project Engineer

3. **Verify page loads:**
   - Should see "Combined Analytics" heading
   - Should see 4 summary cards at the top
   - Should see 2 charts (Suitability Distribution, Barangay Comparison)
   - Should see clusters table below

4. **Check summary cards:**
   - Total Barangays: Should show number > 0
   - Total Projects: Should show number > 0
   - Avg Suitability: Should show score (e.g., "70.0/100")
   - Projects Analyzed: Should show number > 0

5. **Check charts:**
   - **Suitability Distribution Chart (Doughnut):**
     - Should show 4 segments (Highly Suitable, Suitable, Moderate, Low)
     - Colors: Green, Yellow, Orange, Red
     - Should be interactive (hover shows tooltips)
   
   - **Barangay Suitability Chart (Bar):**
     - Should show top 10 barangays by average suitability
     - Bars should be color-coded
     - Y-axis: 0-100
     - X-axis: Barangay names

6. **Check clusters table:**
   - Should list all barangays with projects
   - Each row should show:
     - Barangay name
     - Project count
     - Average suitability (color-coded)
     - Counts for each suitability category
     - Risk indicators

### Step 5: Test GEO-RBAC Filtering

1. **Create a spatial assignment:**
   - Go to Django Admin: `http://localhost:8000/admin/`
   - Navigate to: Projeng → User Spatial Assignments
   - Create a new assignment:
     - User: Select a Project Engineer
     - Barangay: Select a specific barangay (e.g., "Magugpo Poblacion")
     - Is Active: ✓
     - Save

2. **Test as assigned engineer:**
   - Logout and login as the assigned engineer
   - Navigate to: `http://localhost:8000/projeng/analytics/combined/`
   - Should only see data for assigned barangay
   - Check summary cards - should reflect filtered data
   - Check clusters table - should only show assigned barangay

3. **Test as Head Engineer:**
   - Login as Head Engineer (admin)
   - Navigate to analytics page
   - Should see ALL barangays (no filtering)
   - Summary should show "accessible_barangays: all"

### Step 6: Test API with Different Users

**Test 1: Head Engineer (should see all)**
```python
# In Django shell
from django.test import Client
from django.contrib.auth.models import User

client = Client()
head_eng = User.objects.filter(is_superuser=True).first()
client.force_login(head_eng)

response = client.get('/projeng/api/combined-analytics/')
data = response.json()
print(f"Total barangays: {data['summary']['total_barangays']}")
print(f"Accessible: {data['summary']['accessible_barangays']}")
# Should show all barangays
```

**Test 2: Project Engineer with assignment (should see filtered)**
```python
# Create assignment first
from projeng.models import UserSpatialAssignment
proj_eng = User.objects.filter(groups__name='Project Engineer').first()
UserSpatialAssignment.objects.create(
    user=proj_eng,
    barangay='Magugpo Poblacion',
    is_active=True
)

client = Client()
client.force_login(proj_eng)
response = client.get('/projeng/api/combined-analytics/')
data = response.json()
print(f"Total barangays: {data['summary']['total_barangays']}")
print(f"Accessible: {data['summary']['accessible_barangays']}")
# Should show only assigned barangay
```

### Step 7: Check Browser Console

1. **Open Developer Tools (F12)**
2. **Go to Console tab**
3. **Navigate to analytics page**
4. **Look for:**
   - No JavaScript errors
   - Chart.js loading successfully
   - API call to `/projeng/api/combined-analytics/` succeeding
   - Data being rendered correctly

### Step 8: Test Edge Cases

1. **No spatial assignments:**
   - Login as Project Engineer with NO assignments
   - Should see empty data (0 barangays, 0 projects)
   - Should show message or empty state

2. **No suitability data:**
   - If projects exist but no suitability analysis
   - Should still show clusters
   - Suitability stats should show "N/A" or 0

3. **Empty barangay:**
   - Projects with empty/null barangay
   - Should be excluded from results

---

## 🎯 Expected Results

### ✅ Success Indicators:
- [ ] API endpoint returns valid JSON
- [ ] Analytics page loads without errors
- [ ] Summary cards show correct numbers
- [ ] Charts render correctly
- [ ] Clusters table displays data
- [ ] GEO-RBAC filtering works (engineers see only assigned barangays)
- [ ] Head Engineers see all data
- [ ] No JavaScript errors in console
- [ ] No Django errors in logs

### ❌ Failure Indicators:
- [ ] 500 error on API endpoint
- [ ] 404 error on analytics page
- [ ] Charts not rendering
- [ ] Empty data when data exists
- [ ] GEO-RBAC not filtering correctly
- [ ] JavaScript errors
- [ ] Django errors in logs

---

## 🔍 Visual Verification

### Analytics Page Should Show:

**Summary Cards:**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Total       │ Total       │ Avg         │ Projects    │
│ Barangays   │ Projects    │ Suitability │ Analyzed    │
│     3       │     10      │   70.0/100  │     10      │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Charts:**
- Left: Doughnut chart showing suitability distribution
- Right: Bar chart showing top barangays by suitability

**Table:**
- Columns: Barangay | Projects | Avg Suitability | Highly Suitable | Suitable | Moderate | Low | Risks
- Rows: One per barangay cluster
- Color-coded suitability scores

---

## 🐛 Troubleshooting

### Issue: API returns 500 error
**Solution:**
- Check Django logs for error details
- Verify UserSpatialAssignment model is migrated
- Check if LandSuitabilityAnalysis exists
- Verify user authentication

### Issue: Charts not rendering
**Solution:**
- Check if Chart.js is loaded (check browser console)
- Verify API is returning data
- Check for JavaScript errors
- Verify canvas elements exist in DOM

### Issue: GEO-RBAC not filtering
**Solution:**
- Verify UserSpatialAssignment records exist
- Check if `is_active=True`
- Verify user is logged in correctly
- Check API response for `accessible_barangays`

### Issue: Empty data
**Solution:**
- Verify projects have barangay values
- Check if suitability analyses exist
- Verify user has spatial assignments (if not admin)
- Check API response structure

---

## 📊 Test Data Reference

**To create test data:**

1. **Create spatial assignment:**
   ```python
   from projeng.models import UserSpatialAssignment
   from django.contrib.auth.models import User
   
   user = User.objects.get(username='engineer1')
   UserSpatialAssignment.objects.create(
       user=user,
       barangay='Magugpo Poblacion',
       is_active=True
   )
   ```

2. **Verify projects have barangay:**
   ```python
   from projeng.models import Project
   projects = Project.objects.filter(barangay__isnull=False).exclude(barangay='')
   print(f"Projects with barangay: {projects.count()}")
   ```

---

## ✅ Test Checklist

- [ ] Migration applied successfully
- [ ] Model can be created
- [ ] API endpoint accessible
- [ ] API returns valid JSON
- [ ] Analytics page loads
- [ ] Summary cards display correctly
- [ ] Charts render
- [ ] Clusters table displays data
- [ ] GEO-RBAC filtering works
- [ ] Head Engineers see all data
- [ ] No console errors
- [ ] No Django errors

---

## 🚀 Quick Test Commands

```bash
# 1. Check system
python manage.py check

# 2. Test model
python manage.py shell
>>> from projeng.models import UserSpatialAssignment
>>> UserSpatialAssignment.objects.count()

# 3. Start server
python manage.py runserver

# 4. Test API (in browser while logged in)
# http://localhost:8000/projeng/api/combined-analytics/

# 5. Test view
# http://localhost:8000/projeng/analytics/combined/
```

---

## 📝 Notes

- GEO-RBAC is **optional** - if no assignments exist, Head Engineers see all data
- Charts require Chart.js (loaded from CDN)
- API respects user permissions
- All data is aggregated in real-time

**Ready to test!** Start the server and navigate to the analytics page.
