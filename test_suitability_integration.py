"""
Quick test script to verify suitability integration in map view
Run: python manage.py shell < test_suitability_integration.py
"""

from projeng.models import Project, LandSuitabilityAnalysis
from monitoring.views import map_view
from django.test import RequestFactory
from django.contrib.auth.models import User

print("=" * 60)
print("TESTING SUITABILITY INTEGRATION")
print("=" * 60)

# Test 1: Check if suitability data exists
print("\n1. Checking suitability data in database...")
total_projects = Project.objects.filter(latitude__isnull=False, longitude__isnull=False).count()
projects_with_suitability = LandSuitabilityAnalysis.objects.count()
print(f"   Total projects with coordinates: {total_projects}")
print(f"   Projects with suitability analysis: {projects_with_suitability}")

if projects_with_suitability > 0:
    sample = LandSuitabilityAnalysis.objects.select_related('project').first()
    print(f"\n   Sample suitability data:")
    print(f"   - Project ID: {sample.project.id}")
    print(f"   - Project Name: {sample.project.name}")
    print(f"   - Overall Score: {sample.overall_score}")
    print(f"   - Category: {sample.suitability_category}")
    print(f"   - Has Flood Risk: {sample.has_flood_risk}")
    print(f"   - Has Zoning Conflict: {sample.has_zoning_conflict}")
else:
    print("   ⚠️  No suitability data found. Run: python manage.py analyze_land_suitability --all --save")

# Test 2: Verify data structure matches what map_view expects
print("\n2. Verifying data structure...")
if projects_with_suitability > 0:
    sample = LandSuitabilityAnalysis.objects.select_related('project').first()
    project = sample.project
    
    # Simulate what map_view does
    suitability_data = {
        'overall_score': float(sample.overall_score) if sample.overall_score else None,
        'suitability_category': sample.suitability_category or '',
        'category_display': sample.get_suitability_category_display() if sample.suitability_category else '',
        'has_flood_risk': sample.has_flood_risk,
        'has_zoning_conflict': sample.has_zoning_conflict,
        'recommendations': sample.recommendations or [],
    }
    
    print(f"   ✓ Suitability data structure:")
    print(f"     - overall_score: {suitability_data['overall_score']} ({type(suitability_data['overall_score'])})")
    print(f"     - suitability_category: {suitability_data['suitability_category']}")
    print(f"     - category_display: {suitability_data['category_display']}")
    print(f"     - has_flood_risk: {suitability_data['has_flood_risk']} ({type(suitability_data['has_flood_risk'])})")
    print(f"     - has_zoning_conflict: {suitability_data['has_zoning_conflict']} ({type(suitability_data['has_zoning_conflict'])})")
    print(f"     - recommendations: {len(suitability_data['recommendations'])} items")

# Test 3: Check if projects_data will include suitability
print("\n3. Simulating map_view projects_data structure...")
projects_with_coords = Project.objects.filter(latitude__isnull=False, longitude__isnull=False)[:3]
project_ids_list = [p.id for p in projects_with_coords]

suitability_data = {}
if project_ids_list:
    suitability_analyses = LandSuitabilityAnalysis.objects.filter(
        project_id__in=project_ids_list
    ).select_related('project')
    for analysis in suitability_analyses:
        suitability_data[analysis.project_id] = {
            'overall_score': float(analysis.overall_score) if analysis.overall_score else None,
            'suitability_category': analysis.suitability_category or '',
            'category_display': analysis.get_suitability_category_display() if analysis.suitability_category else '',
            'has_flood_risk': analysis.has_flood_risk,
            'has_zoning_conflict': analysis.has_zoning_conflict,
            'recommendations': analysis.recommendations or [],
        }

for p in projects_with_coords:
    suitability = suitability_data.get(p.id, {})
    has_suitability = p.id in suitability_data
    print(f"   Project {p.id}: {p.name}")
    print(f"     - Has suitability data: {has_suitability}")
    if has_suitability:
        print(f"     - Score: {suitability.get('overall_score')}")
        print(f"     - Category: {suitability.get('category_display')}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nNext steps:")
print("1. Start the server: python manage.py runserver")
print("2. Navigate to: http://localhost:8000/dashboard/map/")
print("3. Check browser console for suitability data in markers")
print("4. Click on project markers to see suitability in popups")

