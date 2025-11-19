"""Check and fix Magugpo Poblacion projects"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gistagum.settings')
django.setup()

from projeng.models import Project

barangay = 'Magugpo Poblacion'
projects = Project.objects.filter(barangay=barangay)

print(f'Total {barangay} projects: {projects.count()}')
print(f'With zone_type: {projects.exclude(zone_type__isnull=True).exclude(zone_type="").count()}')
print(f'With coordinates: {projects.exclude(latitude__isnull=True).exclude(longitude__isnull=True).count()}')

print(f'\nProjects without zone_type:')
no_zone = projects.filter(zone_type__isnull=True) | projects.filter(zone_type='')
for p in no_zone:
    print(f'  - {p.name} (ID: {p.id})')
    # Assign a default zone_type if missing
    if not p.zone_type:
        p.zone_type = 'C-1'  # Default to Major Commercial for city center
        p.save()
        print(f'    -> Assigned zone_type: C-1')

print(f'\nAfter fix - With zone_type: {Project.objects.filter(barangay=barangay).exclude(zone_type__isnull=True).exclude(zone_type="").count()}')

