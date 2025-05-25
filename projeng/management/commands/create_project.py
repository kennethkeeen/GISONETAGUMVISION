from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from projeng.models import Project
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Create project with ID 92'

    def handle(self, *args, **options):
        try:
            # Get the headeng user
            user = User.objects.get(username='headeng')
            
            # Create the project
            project = Project.objects.create(
                id=92,  # Force the ID to be 92
                name='Road Renovation Project',
                description='Major road renovation project in Tagum City',
                barangay='Magugpo Poblacion',
                project_cost=15000000.00,
                source_of_funds='Local Government Fund',
                status='in_progress',
                latitude=7.4475,
                longitude=125.8078,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=180),
                created_by=user
            )
            
            # Add the user as an assigned engineer
            project.assigned_engineers.add(user)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created project with ID {project.id}'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User headeng does not exist'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating project: {str(e)}')) 