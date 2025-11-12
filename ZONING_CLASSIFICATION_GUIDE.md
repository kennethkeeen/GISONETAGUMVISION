# 🗺️ Zoning Classification System - Complete Guide

## 📚 Table of Contents
1. [What is Zoning Classification?](#what-is-zoning-classification)
2. [Two Types of Zoning in Your System](#two-types-of-zoning)
3. [Detailed Zoning (R-1, R-2, C-1, etc.)](#detailed-zoning)
4. [Simplified Zoning (Urban/Rural, Economic, Elevation)](#simplified-zoning)
5. [How Zone Detection Works](#how-zone-detection-works)
6. [Map Visualization](#map-visualization)
7. [Use Cases](#use-cases)

---

## What is Zoning Classification?

**Zoning classification** is a way to categorize different areas of Tagum City based on:
- **What can be built there** (residential, commercial, industrial)
- **How dense development can be** (low, medium, high density)
- **Economic characteristics** (growth center, emerging, satellite)
- **Geographic features** (urban, rural, coastal, highland)

This helps city planners make better decisions about:
- Where to build projects
- What types of projects are appropriate
- Resource allocation
- Strategic development planning

---

## Two Types of Zoning in Your System

Your system has **TWO different zoning classification systems** that work together:

### 1. **Detailed Zoning** (R-1, R-2, C-1, I-2, etc.)
- **Purpose**: Precise land use classification
- **Source**: Official zoning ordinance data (from PDF)
- **Level**: Sub-barangay (specific locations within barangays)
- **Example**: "Domingo Subdivision in Magugpo West = R-2 zone"

### 2. **Simplified Zoning** (Urban/Rural, Economic, Elevation)
- **Purpose**: Administrative-level insights for planning
- **Source**: Barangay metadata (population, economic data)
- **Level**: Barangay-wide classification
- **Example**: "Magugpo West = Urban, Growth Center, Plains"

---

## Detailed Zoning (R-1, R-2, C-1, etc.)

### Zone Types Available

#### 🏠 **Residential Zones**
- **R-1** (Low Density Residential): Single-family homes, low density
- **R-2** (Medium Density Residential): Townhouses, medium density
- **R-3** (High Density Residential): Apartment buildings, high density
- **SHZ** (Socialized Housing Zone): Government housing projects

#### 🏪 **Commercial Zones**
- **C-1** (Major Commercial): Large commercial centers, malls
- **C-2** (Minor Commercial): Small shops, neighborhood stores

#### 🏭 **Industrial Zones**
- **I-1** (Heavy Industrial): Factories, heavy manufacturing
- **I-2** (Light and Medium Industrial): Light manufacturing, warehouses
- **AGRO** (Agro-Industrial): Agricultural processing, food production

#### 🏛️ **Other Zones**
- **INS-1** (Institutional): Schools, hospitals, government buildings
- **PARKS** (Parks & Playgrounds): Open spaces, recreational areas
- **AGRICULTURAL**: Farming areas
- **ECO-TOURISM**: Tourism and conservation areas
- **SPECIAL**: Special use zones

### How It's Stored

**Database Table: `ZoningZone`**
```python
ZoningZone:
  - zone_type: "R-2"
  - barangay: "MAGUGPO WEST"
  - location_description: "Domingo Subdivision"
  - keywords: ["Domingo", "Subdivision", "Domingo Subdivision"]
  - is_active: True
```

### Example Data
```
Zone Type: R-2 (Medium Density Residential)
Barangay: MAGUGPO WEST
Location: Domingo Subdivision
Keywords: ["Domingo", "Subdivision", "Domingo Subdivision"]

Zone Type: C-1 (Major Commercial)
Barangay: MAGUGPO POBLACION
Location: Major Commercial Area
Keywords: ["Commercial", "Poblacion", "CBD"]
```

---

## Simplified Zoning (Urban/Rural, Economic, Elevation)

### 1. **Barangay Class** (Urban/Rural)

**Purpose**: Classify barangays as urban or rural

**Classifications:**
- **Urban**: Densely populated, developed infrastructure, commercial activity
- **Rural**: Less dense, agricultural focus, natural resources

**Examples:**
- **Urban**: Apokon, Magugpo Poblacion, Visayan Village, Mankilam
- **Rural**: Bincungan, Busaon, New Balamban, Nueva Fuerza

**Color on Map:**
- Urban = 🔴 Red
- Rural = 🟡 Yellow

---

### 2. **Economic Classification**

**Purpose**: Classify barangays by economic development level

**Classifications:**
- **Growth Center**: Primary economic hubs, high commercial activity
- **Emerging**: Developing areas with growth potential
- **Satellite**: Support areas, lower economic activity

**Examples:**
- **Growth Center**: Apokon, Magugpo Poblacion, San Miguel, Visayan Village
- **Emerging**: La Filipina, Madaum, Magdum, San Agustin
- **Satellite**: Bincungan, Busaon, Canocotan, Cuambogan

**Color on Map:**
- Growth Center = 🔵 Blue
- Emerging = 🟢 Green
- Satellite = 🟡 Yellow

---

### 3. **Elevation Type**

**Purpose**: Classify by geographic terrain

**Classifications:**
- **Highland**: Elevated terrain, different engineering challenges
- **Plains**: Flat terrain, standard infrastructure
- **Coastal**: Near water bodies, special considerations

**Examples:**
- **Highland**: San Agustin, Pandapan
- **Plains**: Apokon, Magugpo Poblacion, Visayan Village
- **Coastal**: Bincungan, Busaon, Liboganon, Madaum

**Color on Map:**
- Highland = 🟣 Purple
- Plains = 🟢 Lime Green
- Coastal = 🔵 Cyan

---

### 4. **Industrial Zones** (Multiple per barangay)

**Purpose**: Identify special development zones

**Zone Types:**
- **CBD** (Central Business District): Core commercial areas
- **Urban Expansion**: Areas for future urban growth
- **Commercial Expansion**: Expanding commercial districts
- **Institutional & Recreational**: Government facilities, parks
- **Agro-Industrial**: Agricultural processing zones

**Examples:**
- **CBD**: Magugpo Poblacion, Visayan Village
- **Institutional & Recreational**: Apokon (university, hospital), Mankilam (sports complex)
- **Agro-Industrial**: Cuambogan (plywood, banana chips), Magdum (NESTLE, demo farm)

---

## How Zone Detection Works

### Automatic Zone Detection

When you create a project, the system **automatically detects** the zone using a 3-step process:

#### Step 1: Keyword Matching (Highest Priority)
```
Project Name: "Road Construction in Domingo Subdivision"
Barangay: "Magugpo West"

System searches for zones with keywords matching:
- "Domingo" ✅ Found in R-2 zone
- "Subdivision" ✅ Found in R-2 zone
- "Domingo Subdivision" ✅ Exact match!

Result: R-2 (Medium Density Residential) - Confidence: 85%
```

#### Step 2: Barangay Matching
```
If no keyword match found:
- System finds all zones in "Magugpo West"
- If one zone type is dominant → Use that zone
- Confidence: 20-30%
```

#### Step 3: Manual Selection (Fallback)
```
If no automatic match:
- System shows dropdown with all zones in that barangay
- User manually selects the correct zone
```

### Detection Algorithm

**Scoring System:**
- **Exact barangay match**: +30 points
- **Partial barangay match**: +15 points
- **Exact keyword match**: +40 points
- **Partial keyword match**: +25 points
- **Substring match**: +10 points
- **Common words in description**: +5 points per word

**Minimum Confidence**: 30 points required for auto-detection

**Example Scoring:**
```
Project: "Drainage System - Domingo Subdivision"
Barangay: "Magugpo West"

Zone: R-2, "Domingo Subdivision", Magugpo West
- Barangay exact match: +30
- Keyword "Domingo" exact match: +40
- Keyword "Subdivision" exact match: +40
Total: 110 points → Confidence: 100% ✅
```

---

## Map Visualization

### How Zones Are Displayed on the Map

#### 1. **Zoning Overlay Toggle**
- Checkbox: "Show Zoning Overlay"
- When enabled, shows colored zones on the map

#### 2. **View Type Selector**
Dropdown with options:
- **Projects** (default): Shows project density
- **Zoning Zones**: Shows detailed zones (R-1, R-2, etc.)
- **Urban/Rural**: Shows urban vs rural classification
- **Economic**: Shows growth center/emerging/satellite
- **Elevation**: Shows highland/plains/coastal

#### 3. **Color Coding**

**Detailed Zones (R-1, R-2, etc.):**
- R-1, R-2, R-3 = 🟢 Green (various shades)
- C-1, C-2 = 🔵 Blue
- I-1, I-2 = 🔴 Red/Orange
- AGRO = 🟤 Brown
- INS-1 = 🟣 Purple
- PARKS = 🟢 Light Green
- AGRICULTURAL = 🟡 Yellow

**Simplified Zones:**
- Urban = 🔴 Red
- Rural = 🟡 Yellow
- Growth Center = 🔵 Blue
- Emerging = 🟢 Green
- Satellite = 🟡 Yellow
- Highland = 🟣 Purple
- Plains = 🟢 Lime Green
- Coastal = 🔵 Cyan

#### 4. **Barangay Popups**

When you click a barangay, you see:
```
Magugpo West
━━━━━━━━━━━━━━━━━━━━
Zones in this barangay:
• R-2: Domingo Subdivision
• R-3: Cristo Rey Village
• C-1: Major Commercial Area

Projects:
• 5 projects in R-2 zones
• 3 projects in R-3 zones
• 8 projects in C-1 zones
```

---

## Use Cases

### 1. **Project Creation**
```
Head Engineer creates project:
- Name: "Road Construction in Domingo Subdivision"
- Barangay: "Magugpo West"
- System auto-detects: R-2 zone
- Shows zone info: "Medium Density Residential"
- Engineer confirms or changes if needed
```

### 2. **Zone Validation**
```
Project: "Factory Construction"
Detected Zone: R-2 (Residential)
System Warning: ⚠️ "Industrial project may not be allowed in Residential zone"
Options:
- Change project type
- Change location
- Add justification note
- Override if justified
```

### 3. **Strategic Planning**
```
Head Engineer views map with "Economic" view:
- Sees: Growth Centers (Blue), Emerging (Green), Satellite (Yellow)
- Decision: Prioritize infrastructure in Growth Centers
- Allocates more budget to blue areas
```

### 4. **Resource Allocation**
```
View: "Elevation" classification
- Coastal areas (Cyan): Need flood control projects
- Highland areas (Purple): Need slope stability projects
- Plains (Lime Green): Standard infrastructure
```

### 5. **Compliance Checking**
```
System checks:
- Residential project in R-2 zone? ✅ Allowed
- Factory in R-2 zone? ⚠️ Warning
- Commercial building in C-1 zone? ✅ Allowed
```

---

## Database Structure

### Project Model
```python
Project:
  - zone_type: "R-2"  # Detected or manually set
  - zone_validated: True/False  # Whether validated
  - barangay: "Magugpo West"
  - name: "Road Construction"
  - description: "Improve roads in Domingo Subdivision"
```

### ZoningZone Model
```python
ZoningZone:
  - zone_type: "R-2"
  - barangay: "MAGUGPO WEST"
  - location_description: "Domingo Subdivision"
  - keywords: ["Domingo", "Subdivision", "Domingo Subdivision"]
  - is_active: True
```

### BarangayMetadata Model
```python
BarangayMetadata:
  - name: "Magugpo West"
  - barangay_class: "urban"
  - economic_class: "growth_center"
  - elevation_type: "plains"
  - industrial_zones: ["CBD", "Commercial Expansion"]
```

---

## Summary

### What You Have:
1. ✅ **Detailed Zoning**: R-1, R-2, C-1, I-2, etc. (from PDF data)
2. ✅ **Simplified Zoning**: Urban/Rural, Economic, Elevation (from metadata)
3. ✅ **Automatic Detection**: System detects zones for projects
4. ✅ **Map Visualization**: Color-coded zones on the map
5. ✅ **Validation**: Warnings for incompatible projects

### How It Works:
1. **Data**: Stored in `ZoningZone` and `BarangayMetadata` tables
2. **Detection**: Keyword matching + barangay matching
3. **Visualization**: Color-coded choropleth map
4. **Validation**: Checks project type vs zone type

### Benefits:
- ✅ Better planning decisions
- ✅ Compliance checking
- ✅ Resource optimization
- ✅ Strategic development
- ✅ Visual analysis

---

**This zoning system helps you make smarter decisions about where and what to build in Tagum City!** 🏙️

