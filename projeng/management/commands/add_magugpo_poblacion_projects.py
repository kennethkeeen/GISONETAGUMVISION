"""
Django management command to add sample projects to Magugpo Poblacion
This ensures all 23 barangays have projects for testing
"""

from django.core.management.base import BaseCommand
from projeng.models import Project
from django.contrib.auth.models import User
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Add sample projects to Magugpo Poblacion to complete all 23 barangays'

    def handle(self, *args, **options):
        barangay = 'Magugpo Poblacion'
        
        # Check if barangay already has projects
        existing = Project.objects.filter(barangay=barangay).count()
        
        if existing > 0:
            self.stdout.write(self.style.WARNING(f'{barangay} already has {existing} project(s)'))
            return
        
        # Coordinates for Magugpo Poblacion (city center)
        base_lat, base_lng = 7.45, 125.80
        
        # Zone types to use
        zone_types = ['AGRO', 'C-1', 'C-2', 'R-1', 'R-2']
        statuses = ['completed', 'in_progress', 'planned', 'delayed']
        
        # Get or create a user for project creation
        try:
            user = User.objects.filter(is_staff=True).first()
            if not user:
                user = User.objects.first()
        except:
            user = None
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'ADDING PROJECTS TO {barangay.upper()}'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        created_count = 0
        
        # Create 5 sample projects
        num_projects = 5
        
        for i in range(num_projects):
            # Add small random offset to coordinates
            lat = base_lat + random.uniform(-0.01, 0.01)
            lng = base_lng + random.uniform(-0.01, 0.01)
            
            project = Project.objects.create(
                name=f"Sample Project - {barangay} {i+1}",
                barangay=barangay,
                zone_type=random.choice(zone_types),
                status=random.choice(statuses),
                project_cost=Decimal(random.randint(1000000, 10000000)),
                latitude=lat,
                longitude=lng,
                created_by=user
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'Created: {project.name}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} new projects in {barangay}'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # Show summary
        total_barangays = Project.objects.exclude(barangay__isnull=True).exclude(barangay='').values('barangay').distinct().count()
        self.stdout.write(f'\nTotal unique barangays with projects: {total_barangays}')
        self.stdout.write(self.style.SUCCESS('\nNow re-export your data: python manage.py export_zone_analytics'))

