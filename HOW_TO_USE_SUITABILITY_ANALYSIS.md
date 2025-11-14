# 🚀 How to Use Land Suitability Analysis

## Quick Start Guide

---

## 📍 **1. View on Dashboard**

### **Access the Dashboard:**
1. Login as **Head Engineer**
2. Go to: `/dashboard/`
3. **Scroll down** past the 6 charts in "Analytics & Insights" section
4. You'll see the **"Land Suitability Analysis"** section with 3 widgets:

   - **Suitability Overview Card** - Shows statistics
   - **Suitability Distribution Chart** - Visual chart
   - **Risk Summary Card** - Risk counts

---

## 📊 **2. View Individual Project Analysis**

### **On Project Detail Page:**
1. Go to any project detail page
2. Scroll to the right column
3. You'll see the **"Land Suitability Analysis"** card showing:
   - Overall suitability score (0-100)
   - All 6 factor scores
   - Risk factors (if any)
   - Recommendations
   - Constraints

### **Example:**
- Open any project from the project list
- The analysis appears automatically if the project has location data

---

## 🔍 **3. Analyze Projects**

### **Option A: Automatic Analysis**
- When you **create a new project** with location data (latitude, longitude, barangay)
- The suitability analysis is **automatically created**

### **Option B: Manual Analysis**
Run the management command:
```bash
# Analyze all projects
python manage.py analyze_land_suitability --all --save

# Analyze specific project
python manage.py analyze_land_suitability --project-id 1 --save

# Analyze by barangay
python manage.py analyze_land_suitability --barangay "Magugpo Poblacion" --save

# Re-analyze existing projects
python manage.py analyze_land_suitability --all --force --save
```

---

## 📱 **4. View via API**

### **Get Project Suitability:**
```
GET /projeng/api/suitability/<project_id>/
```

**Example:**
```javascript
fetch('/projeng/api/suitability/106/')
  .then(r => r.json())
  .then(data => console.log(data));
```

### **Get Statistics:**
```
GET /projeng/api/suitability/stats/
```

### **Get Dashboard Data:**
```
GET /projeng/api/suitability/dashboard-data/
```

---

## 🎯 **5. Understanding the Scores**

### **Overall Score (0-100):**
- **80-100**: Highly Suitable ✅
- **60-79**: Suitable ✅
- **40-59**: Moderately Suitable ⚠️
- **20-39**: Marginally Suitable ⚠️
- **0-19**: Not Suitable ❌

### **Factor Scores:**
1. **Zoning Compliance** - How well project matches zone type
2. **Flood Risk** - Lower risk = higher score
3. **Infrastructure Access** - Availability of utilities/roads
4. **Elevation Suitability** - How suitable the elevation is
5. **Economic Alignment** - Alignment with economic goals
6. **Population Density** - Appropriate density for project type

### **Risk Factors:**
- ⚠️ **Flood Risk** - Location prone to flooding
- ⚠️ **Slope Risk** - Highland areas with potential slope issues
- ⚠️ **Zoning Conflict** - Project type doesn't match zone
- ⚠️ **Infrastructure Gap** - Limited infrastructure access

---

## 💡 **6. Using Recommendations**

Each analysis provides:
- **Recommendations** - Actions to improve suitability
- **Constraints** - Limitations to be aware of

**Example Recommendations:**
- "Verify zoning classification matches project type"
- "Conduct detailed flood risk assessment"
- "Assess infrastructure needs"

---

## 🔧 **7. Admin Interface**

### **View All Analyses:**
1. Go to Django Admin: `/admin/`
2. Navigate to **Projeng → Land Suitability Analyses**
3. View, filter, and search all analyses

### **Manage Criteria:**
1. Go to **Projeng → Suitability Criteria**
2. Adjust weights for different factors
3. Create project-type-specific criteria

---

## 📈 **8. Dashboard Widgets Explained**

### **Suitability Overview:**
- Total analyses count
- Breakdown by category (Highly Suitable, Suitable, etc.)

### **Distribution Chart:**
- Visual pie/doughnut chart
- Shows how many projects fall into each category
- Color-coded for easy understanding

### **Risk Summary:**
- Total projects with risks
- Individual risk type counts
- Color-coded alerts (red/orange for active risks)

---

## ✅ **9. Current Status**

**Already Analyzed:**
- ✅ 10 projects analyzed
- ✅ All saved to database
- ✅ Ready to view on dashboard

**To Analyze More:**
- Create new projects with location data (auto-analysis)
- Or run: `python manage.py analyze_land_suitability --all --save`

---

## 🎯 **Quick Test**

### **Test the Dashboard:**
1. Login as Head Engineer
2. Go to `/dashboard/`
3. Scroll down to "Land Suitability Analysis" section
4. You should see:
   - Total Analyses: 10
   - Distribution chart
   - Risk summary

### **Test Project Detail:**
1. Go to any project (e.g., project ID 106)
2. View the project detail page
3. Check the right column for "Land Suitability Analysis" card
4. You should see the full analysis with scores

### **Test API:**
Open browser console and run:
```javascript
fetch('/projeng/api/suitability/dashboard-data/')
  .then(r => r.json())
  .then(d => console.log('Dashboard Data:', d));
```

---

## 🚀 **Ready to Use!**

Everything is set up and ready:
- ✅ Code implemented
- ✅ Migrations applied
- ✅ Projects analyzed
- ✅ Dashboard widgets ready
- ✅ API endpoints working

**Just refresh your dashboard and scroll down to see it!** 🎉

---

## 📚 **Need Help?**

- Check `DASHBOARD_SUITABILITY_LOCATION.md` for location details
- Check `ALL_PHASES_COMPLETE.md` for full implementation summary
- Check individual project detail pages for detailed analysis

**Enjoy using the Land Suitability Analysis feature!** 🎊

