from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from projeng.models import Project

class Command(BaseCommand):
    help = 'Check and fix user permissions for project access'

    def handle(self, *args, **options):
        # Get or create Project Engineer group
        engineer_group, created = Group.objects.get_or_create(name='Project Engineer')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Project Engineer group'))

        # Get all active users
        users = User.objects.filter(is_active=True)
        
        # Check each user's groups
        for user in users:
            if not user.groups.filter(name='Project Engineer').exists():
                self.stdout.write(f'User {user.username} is not in Project Engineer group')
                # Add user to group
                user.groups.add(engineer_group)
                self.stdout.write(self.style.SUCCESS(f'Added {user.username} to Project Engineer group'))

        # Check projects
        projects = Project.objects.all()
        self.stdout.write(f'Total projects in database: {projects.count()}')
        
        # List all projects with their IDs
        for project in projects:
            self.stdout.write(f'Project ID {project.id}: {project.name}')
            self.stdout.write(f'Assigned engineers: {[e.username for e in project.assigned_engineers.all()]}') 