"""
Quick test script for Phase 3 API endpoint
Run: python manage.py shell < test_phase3_api.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gistagum.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import json

print("=" * 60)
print("PHASE 3 API TESTING")
print("=" * 60)

# Test 1: Check model
print("\n1. Testing UserSpatialAssignment model...")
from projeng.models import UserSpatialAssignment
print(f"   [OK] Model exists")
print(f"   [OK] Total assignments: {UserSpatialAssignment.objects.count()}")

# Test 2: Test API as Head Engineer
print("\n2. Testing API endpoint as Head Engineer...")
client = Client()
user = User.objects.filter(is_superuser=True).first()

if user:
    client.force_login(user)
    response = client.get('/projeng/api/combined-analytics/')
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = json.loads(response.content)
        summary = data.get('summary', {})
        clusters = data.get('clusters', [])
        
        print(f"   [OK] API returned 200 OK")
        print(f"   [OK] Total barangays: {summary.get('total_barangays', 0)}")
        print(f"   [OK] Total projects: {summary.get('total_projects', 0)}")
        print(f"   [OK] Average suitability: {summary.get('average_suitability', 0)}")
        print(f"   [OK] Clusters returned: {len(clusters)}")
        
        if clusters:
            print(f"\n   Sample cluster:")
            sample = clusters[0]
            print(f"     - Barangay: {sample.get('barangay')}")
            print(f"     - Projects: {sample.get('project_count')}")
            stats = sample.get('suitability_stats', {})
            print(f"     - Avg Score: {stats.get('average_score')}")
            print(f"     - Highly Suitable: {stats.get('highly_suitable_count')}")
            print(f"     - Suitable: {stats.get('suitable_count')}")
    else:
        print(f"   [ERROR] API returned {response.status_code}")
        print(f"   Response: {response.content[:200]}")
else:
    print("   [ERROR] No superuser found")

# Test 3: Test helper methods
print("\n3. Testing helper methods...")
if user:
    barangays = UserSpatialAssignment.get_user_barangays(user)
    print(f"   [OK] get_user_barangays() works: {list(barangays)}")
    
    has_access = UserSpatialAssignment.user_has_access(user, 'Magugpo Poblacion')
    print(f"   [OK] user_has_access() works: {has_access}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nNext steps:")
print("1. Start server: python manage.py runserver")
print("2. Navigate to: http://localhost:8000/projeng/analytics/combined/")
print("3. Test API: http://localhost:8000/projeng/api/combined-analytics/")

