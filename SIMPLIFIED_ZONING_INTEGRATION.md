# Simplified Zoning Integration - Working with Limited Data

## What We Have
1. ✅ **Barangay Boundaries**: GeoJSON files for each barangay (in `coord/` folder)
2. ✅ **Zoning Classifications**: Text descriptions from PDF (R-1, R-2, C-1, etc. with specific locations)
3. ❌ **Missing**: Precise polygon boundaries for each zone type

## Solution: Simplified Approach

Since we don't have precise zone boundaries, we'll use a **barangay-level + keyword matching** approach.

---

## Phase 1: Combine Barangay GeoJSON Files

### Step 1.1: Create Combined GeoJSON
- Combine all 23 individual GeoJSON files into one
- Normalize coordinate systems (convert to WGS84)
- Store in `static/data/tagum_barangays.geojson`

**This gives us accurate barangay boundaries for the map.**

---

## Phase 2: Store Zoning Data (Simplified)

### Step 2.1: Create Simple Zoning Model

Instead of precise polygons, store:
- Zone type (R-1, R-2, C-1, etc.)
- Barangay name
- Location description (text from PDF)
- Keywords for matching (subdivision names, road names, etc.)

```python
class ZoningZone(models.Model):
    """Simplified zoning classification - barangay-level with location descriptions"""
    
    ZONE_TYPE_CHOICES = [
        ('R-1', 'Low Density Residential Zone'),
        ('R-2', 'Medium Density Residential Zone'),
        ('R-3', 'High Density Residential Zone'),
        ('SHZ', 'Socialized Housing Zone'),
        ('C-1', 'Major Commercial Zone'),
        ('C-2', 'Minor Commercial Zone'),
        ('I-1', 'Heavy Industrial Zone'),
        ('I-2', 'Light and Medium Industrial Zone'),
        ('AGRO', 'Agro-Industrial Zone'),
        ('INS-1', 'Institutional Zone'),
        ('PARKS', 'Parks & Playgrounds'),
        ('AGRICULTURAL', 'Agricultural Zone'),
        ('ECO-TOURISM', 'Eco-tourism Zone'),
        ('SPECIAL', 'Special Use Zone'),
    ]
    
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES)
    barangay = models.CharField(max_length=255, db_index=True)
    location_description = models.TextField(
        help_text="Specific locations: subdivisions, roads, sites"
    )
    keywords = models.JSONField(
        default=list,
        help_text="Keywords for matching (subdivision names, road names, etc.)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['barangay', 'zone_type']
    
    def __str__(self):
        return f"{self.get_zone_type_display()} - {self.barangay}"
```

### Step 2.2: Extract Keywords from PDF Data

For each zone entry, extract keywords:
- Subdivision names (e.g., "Domingo Subdivision", "Cristo Rey Village")
- Road names (e.g., "Madaum road", "Pioneer Avenues")
- Site names (e.g., "Makabayan Village", "Barangay Residential Site")

**Example:**
```python
{
    'zone_type': 'R-2',
    'barangay': 'MAGUGPO WEST',
    'location_description': 'Domingo Subdivision',
    'keywords': ['Domingo', 'Subdivision', 'Domingo Subdivision']
}
```

---

## Phase 3: Zone Detection (Simplified)

### Step 3.1: Barangay-Level Detection

When a project is created:
1. **Primary**: Match by barangay name
2. **Secondary**: If multiple zones in barangay, use keyword matching
3. **Fallback**: Use most common zone type for that barangay

```python
def detect_project_zone(project):
    """
    Simplified zone detection:
    1. Get all zones for the barangay
    2. Try keyword matching on project name/description
    3. Return best match or most common zone
    """
    zones = ZoningZone.objects.filter(
        barangay=project.barangay,
        is_active=True
    )
    
    if not zones.exists():
        return None
    
    # If only one zone, return it
    if zones.count() == 1:
        return zones.first()
    
    # Try keyword matching
    project_text = f"{project.name} {project.description}".lower()
    for zone in zones:
        for keyword in zone.keywords:
            if keyword.lower() in project_text:
                return zone
    
    # Fallback: return most common zone type for barangay
    return zones.first()  # Or calculate most common
```

### Step 3.2: Manual Selection

**Add to Project Form:**
- Dropdown to manually select zone type
- Auto-populate based on barangay
- Allow manual override

---

## Phase 4: Map Visualization (Simplified)

### Step 4.1: Barangay-Level Zone Display

Since we don't have zone boundaries, show:
- **Barangay color** = Dominant zone type in that barangay
- **Multiple zones** = Show in popup/legend

**Color Scheme:**
- Residential zones (R-1, R-2, R-3, SHZ): Green shades
- Commercial zones (C-1, C-2): Blue shades  
- Industrial zones (I-1, I-2, AGRO): Orange/Red shades
- Institutional (INS-1): Purple
- Other: Gray

### Step 4.2: Zone Information in Popup

When clicking a barangay:
- Show all zones in that barangay
- Show zone descriptions
- Show projects in each zone (if available)

---

## Phase 5: Data Population Strategy

### Step 5.1: Parse PDF Data

Create management command to:
1. Parse the PDF text data you provided
2. Extract zone type, barangay, and location descriptions
3. Generate keywords from location descriptions
4. Store in database

**Example Parsing:**
```
Input: "MAGUGPO WEST (Domingo Subdivision)"
Output:
- zone_type: 'R-2'
- barangay: 'MAGUGPO WEST'
- location_description: 'Domingo Subdivision'
- keywords: ['Domingo', 'Subdivision', 'Domingo Subdivision']
```

### Step 5.2: Handle Multiple Locations

For entries with multiple locations:
```
"MAGUGPO WEST (Domingo Subdivision), MAGUGPO NORTH (Suaybaguio District)"
```

Create separate records:
- Record 1: MAGUGPO WEST, Domingo Subdivision
- Record 2: MAGUGPO NORTH, Suaybaguio District

---

## Phase 6: Implementation Steps

### Step 1: Combine GeoJSON Files ✅
- Script to merge all barangay GeoJSON files
- Normalize coordinates
- Replace existing `tagum_barangays.geojson`

### Step 2: Create Zoning Model ✅
- Add `ZoningZone` model
- Create migration
- Register in admin

### Step 3: Populate Zone Data ✅
- Create management command
- Parse PDF data
- Extract keywords
- Store in database

### Step 4: Add Zone to Projects ✅
- Add `zone_type` field to Project model
- Add zone detection function
- Update project form

### Step 5: Map Visualization ✅
- Add zone overlay view
- Color-code by dominant zone
- Show zone info in popups

### Step 6: Analytics ✅
- Projects by zone type chart
- Zone distribution map
- Basic compliance checking

---

## Benefits of This Approach

✅ **Works with limited data** - No need for precise polygons
✅ **Quick to implement** - Simpler than full GIS integration
✅ **Accurate enough** - Barangay-level + keywords is practical
✅ **Upgradeable** - Can add precise boundaries later
✅ **User-friendly** - Manual selection available

---

## Limitations & Future Enhancements

### Current Limitations:
- Zone detection is barangay-level, not sub-barangay
- Keyword matching may not be 100% accurate
- Can't show precise zone boundaries on map

### Future Enhancements (when you have more data):
- Add polygon boundaries for each zone
- Precise point-in-polygon detection
- Visual zone boundaries on map
- Sub-barangay zone visualization

---

## Quick Start Plan

1. **Week 1**: Combine GeoJSON files + Create model
2. **Week 2**: Populate zone data from PDF
3. **Week 3**: Add zone detection + Project form updates
4. **Week 4**: Map visualization + Analytics

**Total**: ~4 weeks for basic implementation

---

## Example: How It Works

### Scenario: Creating a Project

1. **User creates project** in "Magugpo West"
2. **System detects zones** for Magugpo West:
   - R-2: Domingo Subdivision
   - R-3: Cristo Rey Village
   - C-1: Major Commercial Area
3. **Keyword matching**: Project name contains "Domingo" → Matches R-2
4. **Auto-select**: Zone type = R-2
5. **User can override** if needed
6. **Validation**: Check if project type matches zone (optional)

### Scenario: Viewing Map

1. **User selects "Zoning Zones" view**
2. **System colors barangays** by dominant zone:
   - Magugpo West → Blue (C-1 is dominant)
   - Apokon → Green (R-1 is dominant)
3. **User clicks barangay** → Popup shows:
   - All zones in that barangay
   - Zone descriptions
   - Projects in each zone

---

This simplified approach gives you **80% of the value with 20% of the complexity**!

