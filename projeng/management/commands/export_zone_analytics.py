from django.core.management.base import BaseCommand
from projeng.models import Project
from django.db.models import Q, Count, Sum
import json
import csv
import os
from django.conf import settings
from datetime import datetime

def get_zone_display_name(zone_type):
    """Helper function to get display name for zone type"""
    zone_names = {
        'R-1': 'Low Density Residential',
        'R-2': 'Medium Density Residential',
        'R-3': 'High Density Residential',
        'SHZ': 'Socialized Housing',
        'C-1': 'Major Commercial',
        'C-2': 'Minor Commercial',
        'I-1': 'Heavy Industrial',
        'I-2': 'Light/Medium Industrial',
        'AGRO': 'Agro-Industrial',
        'INS-1': 'Institutional',
        'PARKS': 'Parks & Open Spaces',
        'AGRICULTURAL': 'Agricultural',
        'ECO-TOURISM': 'Eco-tourism',
        'SPECIAL': 'Special Use',
    }
    return zone_names.get(zone_type, zone_type)


class Command(BaseCommand):
    help = 'Export zone analytics data for Google Colab testing (CSV and JSON formats)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='.',
            help='Directory to save exported files (default: current directory)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['both', 'csv', 'json'],
            default='both',
            help='Export format: both, csv, or json (default: both)'
        )
    
    def handle(self, *args, **options):
        output_dir = options['output_dir']
        export_format = options['format']
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('EXPORTING ZONE ANALYTICS DATA'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # Get all projects with zone_type
        projects_with_zones = Project.objects.filter(
            zone_type__isnull=False
        ).exclude(zone_type='')
        
        total_projects = projects_with_zones.count()
        self.stdout.write(f'\n📊 Found {total_projects} projects with zone types')
        
        if total_projects == 0:
            self.stdout.write(self.style.WARNING('⚠ No projects with zone types found!'))
            return
        
        # Export 1: Raw Project Data (CSV) - For running algorithm in Colab
        if export_format in ['both', 'csv']:
            csv_filename = os.path.join(output_dir, f'projects_zone_data_{timestamp}.csv')
            
            self.stdout.write(f'\n📝 Exporting raw project data to CSV...')
            
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'name', 'zone_type', 'status', 'project_cost', 
                            'barangay', 'latitude', 'longitude', 'created_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for project in projects_with_zones.select_related('project_type'):
                    writer.writerow({
                        'id': project.id,
                        'name': project.name,
                        'zone_type': project.zone_type or '',
                        'status': project.status or '',
                        'project_cost': float(project.project_cost) if project.project_cost else 0.0,
                        'barangay': project.barangay or '',
                        'latitude': project.latitude or '',
                        'longitude': project.longitude or '',
                        'created_at': project.created_at.isoformat() if project.created_at else ''
                    })
            
            self.stdout.write(self.style.SUCCESS(f'✅ CSV exported: {csv_filename}'))
            self.stdout.write(f'   Contains {total_projects} projects')
        
        # Export 2: Aggregated Zone Analytics (JSON) - Matching API response
        if export_format in ['both', 'json']:
            json_filename = os.path.join(output_dir, f'zone_analytics_{timestamp}.json')
            
            self.stdout.write(f'\n📊 Calculating zone analytics...')
            
            # Aggregate by zone_type (same algorithm as API)
            zone_stats = projects_with_zones.values('zone_type').annotate(
                total_projects=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                in_progress=Count('id', filter=Q(status__in=['in_progress', 'ongoing'])),
                planned=Count('id', filter=Q(status__in=['planned', 'pending'])),
                delayed=Count('id', filter=Q(status='delayed')),
                total_cost=Sum('project_cost')
            ).order_by('zone_type')
            
            # Format response (matching API format)
            zones = []
            for stat in zone_stats:
                zones.append({
                    'zone_type': stat['zone_type'],
                    'display_name': get_zone_display_name(stat['zone_type']),
                    'total_projects': stat['total_projects'],
                    'completed': stat['completed'],
                    'in_progress': stat['in_progress'],
                    'planned': stat['planned'],
                    'delayed': stat.get('delayed', 0),
                    'total_cost': float(stat['total_cost'] or 0)
                })
            
            # Create output matching API response format
            output = {
                'export_date': datetime.now().isoformat(),
                'total_projects': total_projects,
                'zones': zones
            }
            
            with open(json_filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(output, jsonfile, indent=2, ensure_ascii=False)
            
            self.stdout.write(self.style.SUCCESS(f'✅ JSON exported: {json_filename}'))
            self.stdout.write(f'   Contains {len(zones)} zone types')
            
            # Display summary
            self.stdout.write(f'\n📈 Zone Distribution Summary:')
            for zone in zones:
                self.stdout.write(f'   {zone["zone_type"]:8} ({zone["display_name"]:30}): {zone["total_projects"]:3} projects')
        
        # Export 3: Summary Statistics (TXT)
        summary_filename = os.path.join(output_dir, f'zone_analytics_summary_{timestamp}.txt')
        with open(summary_filename, 'w', encoding='utf-8') as summary_file:
            summary_file.write('=' * 70 + '\n')
            summary_file.write('ZONE ANALYTICS DATA EXPORT SUMMARY\n')
            summary_file.write('=' * 70 + '\n\n')
            summary_file.write(f'Export Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            summary_file.write(f'Total Projects: {total_projects}\n\n')
            
            if export_format in ['both', 'json']:
                summary_file.write('Zone Distribution:\n')
                summary_file.write('-' * 70 + '\n')
                for zone in zones:
                    summary_file.write(f'{zone["zone_type"]:8} | {zone["display_name"]:30} | ')
                    summary_file.write(f'Total: {zone["total_projects"]:3} | ')
                    summary_file.write(f'Completed: {zone["completed"]:2} | ')
                    summary_file.write(f'In Progress: {zone["in_progress"]:2} | ')
                    summary_file.write(f'Planned: {zone["planned"]:2} | ')
                    summary_file.write(f'Delayed: {zone["delayed"]:2}\n')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Summary exported: {summary_filename}'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('EXPORT COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'\n📁 Files saved in: {os.path.abspath(output_dir)}')
        self.stdout.write(f'\n💡 Next steps:')
        self.stdout.write(f'   1. Upload the CSV file to Google Colab')
        self.stdout.write(f'   2. Use the JSON file to verify results')
        self.stdout.write(f'   3. Run the algorithm in Colab with your real data!')

