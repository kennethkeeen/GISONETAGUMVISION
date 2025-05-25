from monitoring.models import Project
from datetime import date

sample_projects = [
    {
        'prn': 'PRN-2024-001',
        'name': 'Tagum City Hall Renovation',
        'description': 'Major renovation of the Tagum City Hall building including structural improvements, modern office spaces, and enhanced public service areas.',
        'status': 'in_progress',
        'barangay': 'Magugpo Poblacion',
        'project_cost': '₱25,000,000.00',
        'source_of_funds': 'Local Government Fund',
        'start_date': date(2024, 1, 15),
        'end_date': date(2024, 12, 31),
        'latitude': 7.4475,
        'longitude': 125.8078,
    },
    {
        'prn': 'PRN-2024-002',
        'name': 'Tagum Public Market Modernization',
        'description': 'Modernization of the public market with improved facilities, better ventilation, and organized vendor spaces.',
        'status': 'pending',
        'barangay': 'Magugpo Poblacion',
        'project_cost': '₱15,000,000.00',
        'source_of_funds': 'Local Development Fund',
        'start_date': date(2024, 6, 1),
        'end_date': date(2025, 5, 31),
        'latitude': 7.4481,
        'longitude': 125.8030,
    },
    {
        'prn': 'PRN-2023-015',
        'name': 'Tagum River Park Development',
        'description': 'Development of a riverside park with walking trails, playground, and recreational facilities along the Tagum River.',
        'status': 'completed',
        'barangay': 'San Miguel',
        'project_cost': '₱8,500,000.00',
        'source_of_funds': 'Tourism Development Fund',
        'start_date': date(2023, 3, 1),
        'end_date': date(2023, 12, 31),
        'latitude': 7.4450,
        'longitude': 125.8120,
    },
    {
        'prn': 'PRN-2024-003',
        'name': 'Barangay Road Improvement Program',
        'description': 'Comprehensive road improvement program covering major barangay access roads including drainage systems and street lighting.',
        'status': 'in_progress',
        'barangay': 'Multiple Barangays',
        'project_cost': '₱35,000,000.00',
        'source_of_funds': 'National Road Fund',
        'start_date': date(2024, 2, 1),
        'end_date': date(2025, 1, 31),
        'latitude': 7.4500,
        'longitude': 125.8100,
    },
    {
        'prn': 'PRN-2024-004',
        'name': 'Tagum City Library and Learning Center',
        'description': 'Construction of a modern public library and learning center with digital resources and study spaces.',
        'status': 'pending',
        'barangay': 'Magugpo Poblacion',
        'project_cost': '₱12,000,000.00',
        'source_of_funds': 'Education Development Fund',
        'start_date': date(2024, 7, 1),
        'end_date': date(2025, 6, 30),
        'latitude': 7.4520,
        'longitude': 125.8050,
    },
    {
        'prn': 'PRN-2024-005',
        'name': 'Tagum City Sports Complex',
        'description': 'Development of a multi-purpose sports complex with swimming pool, track and field, and indoor sports facilities.',
        'status': 'pending',
        'barangay': 'San Miguel',
        'project_cost': '₱45,000,000.00',
        'source_of_funds': 'Sports Development Fund',
        'start_date': date(2024, 8, 1),
        'end_date': date(2025, 12, 31),
        'latitude': 7.4460,
        'longitude': 125.8080,
    },
    {
        'prn': 'PRN-2023-020',
        'name': 'Public Market Parking Building',
        'description': 'Construction of a multi-level parking building to address parking congestion in the public market area.',
        'status': 'completed',
        'barangay': 'Magugpo Poblacion',
        'project_cost': '₱18,000,000.00',
        'source_of_funds': 'Local Government Fund',
        'start_date': date(2023, 6, 1),
        'end_date': date(2023, 12, 31),
        'latitude': 7.4485,
        'longitude': 125.8035,
    },
    {
        'prn': 'PRN-2024-006',
        'name': 'Tagum City Health Center Upgrade',
        'description': 'Upgrading of health centers with modern medical equipment and improved facilities.',
        'status': 'in_progress',
        'barangay': 'Multiple Barangays',
        'project_cost': '₱20,000,000.00',
        'source_of_funds': 'Health Development Fund',
        'start_date': date(2024, 3, 1),
        'end_date': date(2024, 12, 31),
        'latitude': 7.4490,
        'longitude': 125.8060,
    }
]

sample_projects.append({
    'prn': 'PRN-DUMMY-001',
    'name': 'Dummy Project for Pagination',
    'description': 'This is a dummy project to test pagination controls.',
    'status': 'pending',
    'barangay': 'Apokon',
    'project_cost': '₱1,000,000.00',
    'source_of_funds': 'Test Fund',
    'start_date': date(2025, 1, 1),
    'end_date': date(2025, 12, 31),
    'latitude': 7.4500,
    'longitude': 125.8000,
})

def add_sample_projects():
    for data in sample_projects:
        Project.objects.get_or_create(
            prn=data['prn'],
            defaults=data
        )
    print('Sample projects added successfully.')

if __name__ == '__main__':
    add_sample_projects() 