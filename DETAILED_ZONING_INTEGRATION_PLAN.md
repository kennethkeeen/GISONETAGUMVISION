# Detailed Zoning Integration Plan

## Overview
This plan outlines how to integrate the detailed zoning classification data (R-1, R-2, C-1, I-2, etc.) into the existing GISTAGUM system.

---

## Phase 1: Database Design

### 1.1 Create New Model: `ZoningZone`

Store detailed zone classifications with specific locations.

```python
class ZoningZone(models.Model):
    """Detailed zoning classification for specific areas within barangays"""
    
    # Zone Classification Types
    ZONE_TYPE_CHOICES = [
        # Residential
        ('R-1', 'Low Density Residential Zone'),
        ('R-2', 'Medium Density Residential Zone'),
        ('R-3', 'High Density Residential Zone'),
        ('SHZ', 'Socialized Housing Zone'),
        # Commercial
        ('C-1', 'Major Commercial Zone'),
        ('C-2', 'Minor Commercial Zone'),
        # Industrial
        ('I-1', 'Heavy Industrial Zone'),
        ('I-2', 'Light and Medium Industrial Zone'),
        ('AGRO', 'Agro-Industrial Zone'),
        # Other
        ('INS-1', 'Institutional Zone'),
        ('PARKS', 'Parks & Playgrounds/Open Spaces'),
        ('AGRICULTURAL', 'Agricultural Zone'),
        ('ECO-TOURISM', 'Eco-tourism Zone'),
        ('SPECIAL', 'Special Use Zone'),
    ]
    
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES)
    barangay = models.CharField(max_length=255, db_index=True)
    
    # Location details (from the PDF data)
    specific_locations = models.TextField(
        help_text="Specific locations: subdivisions, roads, sites (comma-separated)"
    )
    
    # Geographic boundaries (optional - for future polygon mapping)
    # For now, we'll use text descriptions, later can add GeoJSON polygons
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['barangay', 'zone_type']
        unique_together = ['zone_type', 'barangay', 'specific_locations']
    
    def __str__(self):
        return f"{self.get_zone_type_display()} - {self.barangay}"
```

### 1.2 Extend Project Model

Add zone information to projects.

```python
# Add to Project model:
zone_type = models.CharField(
    max_length=20, 
    blank=True, 
    null=True,
    help_text="Zoning classification at project location"
)
zone_validated = models.BooleanField(
    default=False,
    help_text="Whether zone has been validated against official zoning"
)
zone_notes = models.TextField(
    blank=True,
    null=True,
    help_text="Notes about zone validation or compliance"
)
```

### 1.3 Create Management Command: `populate_zoning_zones`

Parse the PDF data and populate the database.

---

## Phase 2: Data Population

### 2.1 Parse PDF Data

Extract zone classifications from the provided data:
- Zone type (R-1, R-2, C-1, etc.)
- Barangay name
- Specific locations (subdivisions, roads, sites)

### 2.2 Data Structure

For each zone entry:
```python
{
    'zone_type': 'R-1',
    'barangay': 'VISAYAN VILLAGE',
    'specific_locations': 'Specific areas defined by roads/boundaries',
    'description': 'Low Density Residential Zone'
}
```

### 2.3 Handle Multiple Locations

Some zones have multiple specific locations. Options:
1. **One record per location** (more granular)
2. **One record with comma-separated locations** (simpler)

**Recommendation**: Start with option 2, can split later if needed.

---

## Phase 3: Zone Detection & Validation

### 3.1 Zone Detection Logic

When a project is created/updated with coordinates:

```python
def detect_project_zone(project):
    """
    Determine which zone a project belongs to based on:
    1. Barangay name
    2. Latitude/Longitude (if we have polygon boundaries)
    3. Project description/name (keyword matching)
    """
    # Step 1: Get zones for the barangay
    zones = ZoningZone.objects.filter(
        barangay=project.barangay,
        is_active=True
    )
    
    # Step 2: Try to match by location description
    # (For now, match by barangay + keyword matching)
    # Later: Use polygon boundaries if available
    
    # Step 3: Return best match or None
    return matched_zone
```

### 3.2 Project Validation

When creating/editing a project:

```python
def validate_project_zone(project):
    """
    Validate if project type matches zone type.
    Returns warnings/errors if mismatch.
    """
    zone = project.zone_type
    
    # Validation rules:
    # - Industrial projects should be in I-1, I-2, or AGRO zones
    # - Residential projects should be in R-1, R-2, R-3, or SHZ
    # - Commercial projects should be in C-1 or C-2
    # - Institutional projects should be in INS-1
    
    warnings = []
    if project.is_industrial() and zone not in ['I-1', 'I-2', 'AGRO']:
        warnings.append("Industrial project may not be allowed in this zone")
    
    return warnings
```

---

## Phase 4: API Endpoints

### 4.1 Get Zones by Barangay

```
GET /projeng/api/zones/?barangay=Apokon
```

Returns all zones for a barangay.

### 4.2 Get Zone for Project Location

```
GET /projeng/api/zones/detect/?lat=7.4475&lng=125.8078&barangay=Apokon
```

Attempts to detect which zone a location belongs to.

### 4.3 Validate Project Zone

```
POST /projeng/api/zones/validate/
{
    "project_id": 123,
    "zone_type": "R-1"
}
```

Validates if project is compatible with zone.

### 4.4 Get Zones Statistics (Head Engineers)

```
GET /projeng/api/zones/stats/
```

Returns analytics: projects by zone type, zone distribution, etc.

---

## Phase 5: Frontend Integration

### 5.1 Project Creation/Edit Form

**Add Zone Selection:**
- Dropdown to select zone type
- Auto-detect based on location (if possible)
- Show validation warnings
- Display zone description

**UI Elements:**
```html
<div class="form-group">
    <label>Zoning Classification</label>
    <select name="zone_type" id="zone-type">
        <option value="">Auto-detect</option>
        <option value="R-1">R-1: Low Density Residential</option>
        <option value="R-2">R-2: Medium Density Residential</option>
        <!-- etc -->
    </select>
    <div id="zone-validation-warning" class="alert alert-warning" style="display:none;">
        <!-- Validation messages -->
    </div>
</div>
```

### 5.2 Map Visualization

**Add Zone Overlay:**
- New view option: "Zoning Zones"
- Color-code barangays by dominant zone type
- Or show zone boundaries (if polygon data available)

**Color Scheme:**
- Residential (R-1, R-2, R-3, SHZ): Green shades
- Commercial (C-1, C-2): Blue shades
- Industrial (I-1, I-2, AGRO): Orange/Red shades
- Institutional (INS-1): Purple
- Other: Gray

### 5.3 Project Details

**Display Zone Information:**
- Show zone type in project details
- Show zone description
- Show validation status
- Link to zone regulations (if available)

### 5.4 Analytics Dashboard

**New Charts:**
1. **Projects by Zone Type**: Pie/bar chart
2. **Zone Distribution**: Map showing zone types
3. **Zone Compliance**: Projects with/without zone validation
4. **Zone vs Project Type**: Compatibility analysis

---

## Phase 6: Implementation Steps

### Step 1: Database Setup
1. Create `ZoningZone` model
2. Add fields to `Project` model
3. Create and run migrations
4. Register in Django admin

### Step 2: Data Population
1. Create `populate_zoning_zones` management command
2. Parse PDF data into database
3. Verify data integrity
4. Test data retrieval

### Step 3: Backend Logic
1. Implement zone detection function
2. Implement project validation function
3. Create API endpoints
4. Add unit tests

### Step 4: Frontend Integration
1. Add zone selection to project form
2. Add zone display to project details
3. Add zone overlay to map
4. Add zone analytics charts

### Step 5: Testing & Refinement
1. Test zone detection accuracy
2. Test validation logic
3. User testing
4. Refine based on feedback

---

## Phase 7: Advanced Features (Future)

### 7.1 Polygon Boundaries
- Store GeoJSON polygons for each zone
- Precise zone detection using point-in-polygon
- Visual zone boundaries on map

### 7.2 Zone Regulations
- Store allowed/prohibited uses per zone
- Automatic compliance checking
- Regulatory documentation

### 7.3 Zone History
- Track zone changes over time
- Historical project-zone relationships
- Planning evolution

### 7.4 Integration with Planning Department
- Import official zone updates
- Sync with city planning database
- Compliance reporting

---

## Data Mapping from PDF

### Residential Zones
- **R-1**: Low Density → `'R-1'`
- **R-2**: Medium Density → `'R-2'`
- **R-3**: High Density → `'R-3'`
- **SHZ**: Socialized Housing → `'SHZ'`

### Commercial Zones
- **C-1**: Major Commercial → `'C-1'`
- **C-2**: Minor Commercial → `'C-2'`

### Industrial Zones
- **I-1**: Heavy Industrial → `'I-1'`
- **I-2**: Light/Medium Industrial → `'I-2'`
- **Agro-Industrial**: → `'AGRO'`

### Other Zones
- **Institutional**: → `'INS-1'`
- **Parks & Playgrounds**: → `'PARKS'`
- **Agricultural**: → `'AGRICULTURAL'`
- **Eco-tourism**: → `'ECO-TOURISM'`
- **Special Use**: → `'SPECIAL'`

---

## Benefits of Integration

1. **Compliance**: Ensure projects match zone requirements
2. **Planning**: Better strategic development decisions
3. **Analytics**: Detailed insights by zone type
4. **Validation**: Automatic zone detection and validation
5. **Documentation**: Official zoning data in system
6. **Future-Proof**: Foundation for advanced features

---

## Challenges & Considerations

### Challenge 1: Precise Location Matching
**Problem**: PDF data has text descriptions, not coordinates
**Solution**: 
- Start with barangay + keyword matching
- Later: Add polygon boundaries for precise detection

### Challenge 2: Multiple Zones per Barangay
**Problem**: One barangay can have many zones
**Solution**: 
- Store all zones, detect best match
- Show all zones for a barangay in UI

### Challenge 3: Zone Updates
**Problem**: Zones may change over time
**Solution**: 
- Add `is_active` flag
- Track zone history
- Version control for zone data

### Challenge 4: Project-Zone Relationship
**Problem**: Projects may span multiple zones
**Solution**: 
- Store primary zone
- Add notes for complex cases
- Future: Multi-zone support

---

## Next Steps

1. **Review this plan** - Confirm approach
2. **Start with Phase 1** - Database design
3. **Populate sample data** - Test with one barangay
4. **Iterate** - Refine based on results
5. **Scale up** - Add all barangays and zones

---

## Questions to Consider

1. **Priority**: Which features are most important?
   - Zone validation on project creation?
   - Map visualization?
   - Analytics?

2. **Accuracy**: How precise does zone detection need to be?
   - Barangay-level (good enough for now)?
   - Sub-barangay level (requires polygon data)?

3. **Compliance**: Should zone validation block project creation?
   - Warning only?
   - Require approval?
   - Just informational?

4. **Data Source**: Is this the official/complete zoning data?
   - Are there updates?
   - Other sources to integrate?

---

This plan provides a comprehensive roadmap for integrating detailed zoning data while maintaining compatibility with the existing system.

