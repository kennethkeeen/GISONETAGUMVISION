from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from projeng.models import Project

class Command(BaseCommand):
    help = 'Fix specific user permissions for project access'

    def handle(self, *args, **options):
        # Get or create Project Engineer group
        engineer_group, created = Group.objects.get_or_create(name='Project Engineer')
        
        # Get the headeng user
        try:
            user = User.objects.get(username='headeng')
            
            # Add user to Project Engineer group
            if not user.groups.filter(name='Project Engineer').exists():
                user.groups.add(engineer_group)
                self.stdout.write(self.style.SUCCESS(f'Added {user.username} to Project Engineer group'))
            
            # Assign user to all existing projects
            projects = Project.objects.all()
            for project in projects:
                if user not in project.assigned_engineers.all():
                    project.assigned_engineers.add(user)
                    self.stdout.write(self.style.SUCCESS(f'Assigned {user.username} to project {project.name}'))
            
            self.stdout.write(self.style.SUCCESS('Successfully fixed permissions'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User headeng does not exist')) 