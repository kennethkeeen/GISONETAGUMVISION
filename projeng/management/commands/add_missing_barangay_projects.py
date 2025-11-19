"""
Django management command to add sample projects to missing barangays
This ensures all 23 barangays have projects for testing
"""

from django.core.management.base import BaseCommand
from projeng.models import Project
from django.contrib.auth.models import User
from django.db.models import Count
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Add sample projects to missing barangays to ensure all 23 barangays have projects'

    def handle(self, *args, **options):
        # Missing barangays that need projects
        missing_barangays = [
            'Bincungan',
            'Busaon', 
            'Cuambogan',
            'Liboganon',
            'Magdum',
            'Magugpo Poblacion',
            'Nueva Fuerza',
            'Pagsabangan',
            'San Isidro'
        ]

        # Sample coordinates for each barangay (approximate locations in Tagum City)
        barangay_coordinates = {
            'Bincungan': (7.50, 125.75),  # Coastal area
            'Busaon': (7.48, 125.78),     # Coastal area
            'Cuambogan': (7.46, 125.82),  # Plains area
            'Liboganon': (7.52, 125.80),  # Coastal area
            'Magdum': (7.44, 125.81),     # Urban area
            'Magugpo Poblacion': (7.45, 125.80),  # City center
            'Nueva Fuerza': (7.47, 125.79),  # Rural area
            'Pagsabangan': (7.49, 125.77),  # Rural area
            'San Isidro': (7.43, 125.83),   # Urban area
        }

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
        self.stdout.write(self.style.SUCCESS('ADDING SAMPLE PROJECTS TO MISSING BARANGAYS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        created_count = 0

        for barangay in missing_barangays:
            # Check if barangay already has projects
            existing = Project.objects.filter(barangay=barangay).count()
            
            if existing > 0:
                self.stdout.write(self.style.WARNING(f'{barangay}: Already has {existing} project(s) - skipping'))
                continue
            
            # Get coordinates
            base_lat, base_lng = barangay_coordinates.get(barangay, (7.45, 125.80))
            
            # Create 3-5 sample projects per barangay
            num_projects = random.randint(3, 5)
            
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
                self.stdout.write(self.style.SUCCESS(f'Created: {project.name} in {barangay}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} new projects'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # Show summary
        self.stdout.write('\nBarangay Project Count:')
        all_barangays = Project.objects.values('barangay').annotate(
            count=Count('id')
        ).order_by('barangay')

        for item in all_barangays:
            if item['barangay']:
                self.stdout.write(f'   {item["barangay"]}: {item["count"]} projects')

        total_barangays = Project.objects.exclude(barangay__isnull=True).exclude(barangay='').values('barangay').distinct().count()
        self.stdout.write(f'\nTotal unique barangays with projects: {total_barangays}')

