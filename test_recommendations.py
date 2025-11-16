#!/usr/bin/env python
"""Quick test script for zone recommendations"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gistagum.settings')
django.setup()

from projeng.zone_recommendation import ZoneCompatibilityEngine
from projeng.models import ProjectType, ZoneAllowedUse

print("=" * 60)
print("Testing Zone Recommendations Format Conversion")
print("=" * 60)

engine = ZoneCompatibilityEngine()

# Test format conversion
print("\n1. Format Conversion Tests:")
print(f"   R-1 → {engine.normalize_zone_type('R-1')} (for query)")
print(f"   R1 → {engine.format_zone_type_for_display('R1')} (for display)")
print(f"   C-1 → {engine.normalize_zone_type('C-1')} (for query)")
print(f"   In → {engine.format_zone_type_for_display('In')} (for display)")

# Test with actual project type
print("\n2. Real Data Tests:")
pt = ProjectType.objects.first()
if pt:
    print(f"   Project Type: {pt.name} ({pt.code})")
    
    # Test validation with hyphenated format
    result = engine.validate_project_zone(pt.code, 'R-1')
    print(f"   Validation for 'R-1': {result['is_allowed']} - {result['message']}")
    
    # Test finding allowed zones
    allowed = engine.find_allowed_zones(pt.code)
    print(f"   Allowed zones (first 5):")
    for z in allowed[:5]:
        print(f"      - {z['zone_type']}: {z['zone_name']} ({'Primary' if z['is_primary'] else 'Conditional'})")
    
    # Test recommendations
    print("\n3. Recommendation Tests:")
    recommendations = engine.recommend_zones(pt.code, limit=3)
    if recommendations.get('recommendations'):
        print(f"   Top 3 Recommendations:")
        for i, rec in enumerate(recommendations['recommendations'][:3], 1):
            print(f"      {i}. {rec['zone_type']} ({rec['zone_name']}) - Score: {rec['overall_score']:.1f}")
    else:
        print("   No recommendations found")
else:
    print("   No project types found in database")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)

