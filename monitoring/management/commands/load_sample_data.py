from django.core.management.base import BaseCommand
from monitoring.sample_data import add_sample_projects

class Command(BaseCommand):
    help = 'Loads sample project data into the database'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample projects...')
        add_sample_projects()
        self.stdout.write(self.style.SUCCESS('Successfully loaded sample projects')) 