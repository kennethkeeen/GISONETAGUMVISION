# GIS-Driven Project Monitoring Platform for Tagum Government

A Django-based platform for monitoring and visualizing government projects using Leaflet and OpenStreetMap.

## Features

- Project listing and details
- Interactive map visualization
- Admin interface for project management

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd gistagum
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Create a superuser (optional):
   ```
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```
   python manage.py runserver
   ```

6. Visit http://127.0.0.1:8000/ to view the project list and map.

## Usage

- Admin: http://127.0.0.1:8000/admin/
- Project List: http://127.0.0.1:8000/
- Map View: http://127.0.0.1:8000/map/ 