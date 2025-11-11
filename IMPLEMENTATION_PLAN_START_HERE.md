# Implementation Plan: Simplified Zoning Integration
## Start Here - Step-by-Step Guide

---

## 📋 Overview

**Goal:** Integrate zoning classifications into your system to fulfill capstone requirement

**Approach:** Simplified (barangay-level + keyword matching)

**Timeline:** 1-2 weeks

**Data Available:** ✅ All needed data is ready

---

## 🎯 Phase 1: Data Preparation (Days 1-2)

### Task 1.1: Combine GeoJSON Files
**Goal:** Merge 23 individual GeoJSON files into one

**Steps:**
1. Create Python script to read all GeoJSON files from `coord/` folder
2. Combine into single FeatureCollection
3. Normalize coordinate systems (convert to WGS84)
4. Save to `static/data/tagum_barangays.geojson`

**Files to Create:**
- `projeng/management/commands/combine_geojson.py`

**Expected Output:**
- One combined GeoJSON file with all 23 barangays
- All coordinates in WGS84 format

**Checkpoint:** ✅ Combined GeoJSON file created

---

### Task 1.2: Parse PDF Zoning Data
**Goal:** Extract zoning data from PDF text into structured format

**Steps:**
1. Create management command to parse PDF text
2. Extract zone type, barangay, and location descriptions
3. Generate keywords from location descriptions
4. Prepare data for database insertion

**Files to Create:**
- `projeng/management/commands/parse_zoning_data.py`

**Data Structure:**
```python
{
    'zone_type': 'R-2',
    'barangay': 'MAGUGPO WEST',
    'location_description': 'Domingo Subdivision',
    'keywords': ['Domingo', 'Subdivision', 'Domingo Subdivision']
}
```

**Checkpoint:** ✅ Zoning data parsed and ready

---

## 🗄️ Phase 2: Database Setup (Day 3)

### Task 2.1: Create ZoningZone Model
**Goal:** Database model to store zoning classifications

**Steps:**
1. Add `ZoningZone` model to `projeng/models.py`
2. Define zone type choices (R-1, R-2, C-1, etc.)
3. Add fields: zone_type, barangay, location_description, keywords
4. Create migration: `python manage.py makemigrations projeng`
5. Apply migration: `python manage.py migrate projeng`

**Model Fields:**
- `zone_type` (CharField with choices)
- `barangay` (CharField, indexed)
- `location_description` (TextField)
- `keywords` (JSONField)
- `is_active` (BooleanField)
- Timestamps

**Checkpoint:** ✅ Model created and migrated

---

### Task 2.2: Extend Project Model
**Goal:** Add zone information to projects

**Steps:**
1. Add `zone_type` field to `Project` model
2. Add `zone_validated` field (optional)
3. Create migration
4. Apply migration

**New Fields:**
```python
zone_type = models.CharField(max_length=20, blank=True, null=True)
zone_validated = models.BooleanField(default=False)
```

**Checkpoint:** ✅ Project model extended

---

### Task 2.3: Register in Django Admin
**Goal:** Allow Head Engineers to manage zones via admin

**Steps:**
1. Add `ZoningZoneAdmin` to `projeng/admin.py`
2. Configure list display, filters, search
3. Test admin interface

**Checkpoint:** ✅ Admin interface working

---

## 📥 Phase 3: Data Population (Day 4)

### Task 3.1: Create Populate Command
**Goal:** Populate database with zoning data

**Steps:**
1. Create `populate_zoning_zones.py` management command
2. Use parsed data from Task 1.2
3. Create ZoningZone records
4. Extract and store keywords

**Command:**
```bash
python manage.py populate_zoning_zones
```

**Expected Output:**
- All zones from PDF stored in database
- Keywords extracted and stored
- Ready for zone detection

**Checkpoint:** ✅ Database populated with zones

---

### Task 3.2: Verify Data
**Goal:** Ensure data quality

**Steps:**
1. Check zone count matches PDF data
2. Verify keywords extracted correctly
3. Test zone queries by barangay
4. Fix any data issues

**Checkpoint:** ✅ Data verified and correct

---

## 🔍 Phase 4: Zone Detection (Days 5-6)

### Task 4.1: Create Zone Detection Function
**Goal:** Automatically detect zone for projects

**Steps:**
1. Create `detect_project_zone()` function in `projeng/utils.py`
2. Implement barangay-level matching
3. Add keyword matching logic
4. Return best match or None

**Function Logic:**
```python
def detect_project_zone(project):
    # 1. Get zones for barangay
    # 2. If one zone, return it
    # 3. Try keyword matching
    # 4. Return best match
```

**Checkpoint:** ✅ Detection function working

---

### Task 4.2: Integrate with Project Creation
**Goal:** Auto-detect zone when Head Engineer creates project

**Steps:**
1. Update `project_list` view in `monitoring/views/__init__.py`
2. Call detection function after form validation
3. Pre-populate zone_type field
4. Handle manual override

**Integration Points:**
- After barangay selection
- After project name/description entered
- Before form submission

**Checkpoint:** ✅ Auto-detection working in form

---

### Task 4.3: Add Zone Field to Project Form
**Goal:** Show zone selection in UI

**Steps:**
1. Update `ProjectForm` in `monitoring/forms.py`
2. Add `zone_type` field (dropdown)
3. Update `project_list.html` template
4. Add JavaScript for auto-population
5. Show zone description

**UI Elements:**
- Zone type dropdown
- Auto-populated from detection
- Manual override option
- Zone description display

**Checkpoint:** ✅ Zone field in form

---

## 🗺️ Phase 5: Map Visualization (Days 7-9)

### Task 5.1: Update GeoJSON Endpoint
**Goal:** Use combined GeoJSON file

**Steps:**
1. Update `barangay_geojson_view` in `monitoring/views/__init__.py`
2. Point to new combined GeoJSON file
3. Test endpoint returns correct data

**Checkpoint:** ✅ GeoJSON endpoint updated

---

### Task 5.2: Add Zone Overlay to Map
**Goal:** Show zones on map with colors

**Steps:**
1. Update `simple_choropleth.js`
2. Add new view type: "zoning_zones"
3. Implement color coding by zone type
4. Add zone overlay toggle

**Color Scheme:**
- Residential (R-1, R-2, R-3, SHZ): Green shades
- Commercial (C-1, C-2): Blue shades
- Industrial (I-1, I-2, AGRO): Orange/Red shades
- Institutional (INS-1): Purple
- Other: Gray

**Checkpoint:** ✅ Zone overlay on map

---

### Task 5.3: Add Zone Information to Popups
**Goal:** Show zone details when clicking barangay

**Steps:**
1. Update popup creation in `simple_choropleth.js`
2. Fetch zone data for barangay
3. Display all zones in popup
4. Show zone descriptions

**Popup Content:**
- Barangay name
- All zones in barangay
- Zone descriptions
- Project count per zone

**Checkpoint:** ✅ Zone info in popups

---

### Task 5.4: Add Zone Legend
**Goal:** Show what colors mean

**Steps:**
1. Update legend creation in `simple_choropleth.js`
2. Add zone type legend
3. Show color meanings
4. Update when view changes

**Checkpoint:** ✅ Zone legend working

---

## 📊 Phase 6: Analytics & Insights (Days 10-11)

### Task 6.1: Create Zone Statistics API
**Goal:** Provide zone data for analytics

**Steps:**
1. Create `zone_statistics_api` view in `projeng/views.py`
2. Calculate projects by zone type
3. Return JSON data
4. Add URL route

**API Endpoint:**
```
GET /projeng/api/zone-statistics/
```

**Returns:**
- Projects by zone type
- Zone distribution
- Compliance statistics

**Checkpoint:** ✅ API endpoint working

---

### Task 6.2: Add Zone Analytics Charts
**Goal:** Visualize zone data

**Steps:**
1. Create "Projects by Zone Type" chart
2. Add to Head Engineer dashboard
3. Show zone distribution
4. Display compliance metrics

**Charts:**
- Pie chart: Projects by zone type
- Bar chart: Zone distribution
- Map: Zone visualization

**Checkpoint:** ✅ Analytics charts working

---

### Task 6.3: Add Compliance Checking
**Goal:** Validate projects against zones

**Steps:**
1. Create validation function
2. Check project type vs zone type
3. Show warnings in form
4. Store validation status

**Validation Rules:**
- Industrial projects → I-1, I-2, AGRO zones
- Residential projects → R-1, R-2, R-3, SHZ zones
- Commercial projects → C-1, C-2 zones

**Checkpoint:** ✅ Compliance checking working

---

## 🧪 Phase 7: Testing & Refinement (Days 12-14)

### Task 7.1: Test Zone Detection
**Goal:** Ensure accurate detection

**Steps:**
1. Test with various project names
2. Test keyword matching
3. Test barangay matching
4. Fix edge cases

**Test Cases:**
- Project in barangay with one zone
- Project in barangay with multiple zones
- Project with matching keywords
- Project without keywords

**Checkpoint:** ✅ Detection tested and accurate

---

### Task 7.2: Test Map Visualization
**Goal:** Ensure map displays correctly

**Steps:**
1. Test zone overlay toggle
2. Test color coding
3. Test popups
4. Test legend
5. Test on different browsers

**Checkpoint:** ✅ Map visualization working

---

### Task 7.3: User Testing
**Goal:** Get feedback from Head Engineers

**Steps:**
1. Have Head Engineer test project creation
2. Test zone detection accuracy
3. Test map visualization
4. Gather feedback
5. Make improvements

**Checkpoint:** ✅ User tested and approved

---

## 📝 Phase 8: Documentation (Day 15)

### Task 8.1: Code Documentation
**Goal:** Document the implementation

**Steps:**
1. Add docstrings to functions
2. Document zone detection logic
3. Document API endpoints
4. Update README if needed

**Checkpoint:** ✅ Code documented

---

### Task 8.2: User Documentation
**Goal:** Help users understand the system

**Steps:**
1. Create user guide for Head Engineers
2. Document zone types
3. Explain zone detection
4. Show how to use map

**Checkpoint:** ✅ User documentation complete

---

## ✅ Final Checklist

### Before Starting:
- [ ] Review this plan
- [ ] Understand each phase
- [ ] Prepare development environment
- [ ] Backup current database

### Phase 1: Data Preparation
- [ ] Combine GeoJSON files
- [ ] Parse PDF zoning data

### Phase 2: Database Setup
- [ ] Create ZoningZone model
- [ ] Extend Project model
- [ ] Register in admin

### Phase 3: Data Population
- [ ] Create populate command
- [ ] Populate database
- [ ] Verify data

### Phase 4: Zone Detection
- [ ] Create detection function
- [ ] Integrate with project creation
- [ ] Add zone field to form

### Phase 5: Map Visualization
- [ ] Update GeoJSON endpoint
- [ ] Add zone overlay
- [ ] Add zone popups
- [ ] Add zone legend

### Phase 6: Analytics
- [ ] Create statistics API
- [ ] Add analytics charts
- [ ] Add compliance checking

### Phase 7: Testing
- [ ] Test zone detection
- [ ] Test map visualization
- [ ] User testing

### Phase 8: Documentation
- [ ] Code documentation
- [ ] User documentation

---

## 🚀 Quick Start Commands

### Day 1: Setup
```bash
# Navigate to project
cd C:\Users\kenne\Desktop\GISTAGUM

# Create management command directory (if needed)
mkdir -p projeng/management/commands
touch projeng/management/commands/__init__.py
```

### Day 2: Database
```bash
# Create migrations
python manage.py makemigrations projeng

# Apply migrations
python manage.py migrate projeng
```

### Day 3: Data
```bash
# Combine GeoJSON files
python manage.py combine_geojson

# Populate zones
python manage.py populate_zoning_zones
```

### Day 4: Test
```bash
# Run server
python manage.py runserver

# Test in browser
# Login as Head Engineer
# Create project → Check zone detection
# View map → Check zone overlay
```

---

## 📅 Suggested Timeline

**Week 1:**
- Days 1-2: Data Preparation (Phase 1)
- Days 3-4: Database Setup (Phase 2)
- Day 5: Data Population (Phase 3)

**Week 2:**
- Days 6-7: Zone Detection (Phase 4)
- Days 8-9: Map Visualization (Phase 5)
- Days 10-11: Analytics (Phase 6)
- Days 12-14: Testing (Phase 7)
- Day 15: Documentation (Phase 8)

**Total:** ~2 weeks for complete implementation

---

## 🎯 Success Criteria

### Must Have:
- ✅ Zone data in database
- ✅ Zone detection working
- ✅ Zone overlay on map
- ✅ Zone information in popups
- ✅ Basic analytics

### Nice to Have:
- ✅ Compliance checking
- ✅ Advanced analytics
- ✅ Zone validation warnings
- ✅ Zone history tracking

---

## 🆘 Troubleshooting

### Issue: GeoJSON files won't combine
**Solution:** Check coordinate systems, normalize to WGS84

### Issue: Zone detection not working
**Solution:** Verify keywords extracted correctly, check matching logic

### Issue: Map not showing zones
**Solution:** Check GeoJSON endpoint, verify zone data loaded

### Issue: Colors not displaying
**Solution:** Check color scheme in JavaScript, verify zone types match

---

## 📞 Next Steps

1. **Review this plan** - Understand each phase
2. **Start with Phase 1** - Data preparation
3. **Work through phases** - One at a time
4. **Test frequently** - After each phase
5. **Ask for help** - If stuck on any task

---

**Ready to start? Begin with Phase 1, Task 1.1: Combine GeoJSON Files!** 🚀

