from django.shortcuts import render, redirect, get_object_or_404
from django.core.serializers import serialize
from .models import Project as MonitoringProject
from projeng.models import Project as ProjEngProject, ProjectProgress, ProjectCost, ProgressPhoto
from .forms import ProjectForm
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest, Http404, HttpResponseForbidden, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from collections import Counter
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.db import transaction, models
from django.db.models import OuterRef, Max, Subquery, IntegerField, Q, Sum, Exists
from itertools import chain
from django.utils import timezone
import logging
from projeng.utils import flag_overdue_projects_as_delayed

def is_head_engineer(user):
    return user.is_authenticated and user.groups.filter(name='Head Engineer').exists()

def is_project_or_head_engineer(user):
    return user.is_authenticated and (user.groups.filter(name='Head Engineer').exists() or user.groups.filter(name='Project Engineer').exists())

@login_required(login_url='/accounts/login/')
def home(request):
    print(f"Inside home view. User is authenticated: {request.user.is_authenticated}")
    print(f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
    if request.user.is_authenticated:
        print(f"User groups inside home view: {list(request.user.groups.values_list('name', flat=True))}")
    return render(request, 'monitoring/home.html')

@user_passes_test(is_head_engineer, login_url='/accounts/login/')
def dashboard(request):
    project_count = MonitoringProject.objects.count()
    completed_count = MonitoringProject.objects.filter(status='completed').count()
    in_progress_count = MonitoringProject.objects.filter(status='in_progress').count()
    delayed_count = MonitoringProject.objects.filter(status='delayed').count()
    recent_projects = MonitoringProject.objects.order_by('-created_at')[:5]
    return render(request, 'monitoring/dashboard.html', {
        'project_count': project_count,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'delayed_count': delayed_count,
        'recent_projects': recent_projects,
    })

def project_to_dict(project):
    data = model_to_dict(project)
    data['image'] = project.image.url if project.image else None
    # Serialize assigned_engineers ManyToMany field
    if 'assigned_engineers' in data and data['assigned_engineers'] is not None:
        # Convert the QuerySet of Users to a list of user IDs
        data['assigned_engineers'] = list(project.assigned_engineers.values_list('id', flat=True))
    # Add a source field to identify the database the project came from
    data['source'] = 'projeng' if isinstance(project, ProjEngProject) else 'monitoring'
    return data

@transaction.atomic
def project_list(request):
    try:
        form = ProjectForm()  # Always define form
        if request.method == 'POST':
            form = ProjectForm(request.POST, request.FILES)
            if form.is_valid():
                # Save to project engineer database (primary)
                projeng_project = form.save(commit=False)
                projeng_project.created_by = request.user
                try:
                    projeng_project.save()
                    form.save_m2m()  # Save many-to-many relationships for projeng_project

                    # Check if a corresponding project already exists in the monitoring database
                    # Use PRN as the unique identifier for matching
                    monitoring_project, created = MonitoringProject.objects.get_or_create(
                        prn=projeng_project.prn,
                        defaults={
                            'name': projeng_project.name,
                            'description': projeng_project.description,
                            'barangay': projeng_project.barangay,
                            'project_cost': projeng_project.project_cost,
                            'source_of_funds': projeng_project.source_of_funds,
                            'status': projeng_project.status,
                            'latitude': projeng_project.latitude,
                            'longitude': projeng_project.longitude,
                            'start_date': projeng_project.start_date,
                            'end_date': projeng_project.end_date,
                             # Copy image on creation - handled by model save
                            'image': projeng_project.image 
                        }
                    )

                    if not created:
                        # If project existed, update its fields from the projeng project
                        monitoring_project.name = projeng_project.name
                        monitoring_project.description = projeng_project.description
                        monitoring_project.barangay = projeng_project.barangay
                        monitoring_project.project_cost = projeng_project.project_cost
                        monitoring_project.source_of_funds = projeng_project.source_of_funds
                        monitoring_project.status = projeng_project.status
                        monitoring_project.latitude = projeng_project.latitude
                        monitoring_project.longitude = projeng_project.longitude
                        monitoring_project.start_date = projeng_project.start_date
                        monitoring_project.end_date = projeng_project.end_date
                        if projeng_project.image:
                            monitoring_project.image = projeng_project.image # Update image if present
                        monitoring_project.save()

                    # --- Copy assigned engineers from projeng_project to monitoring_project ---
                    if hasattr(monitoring_project, 'assigned_engineers'):
                        monitoring_project.assigned_engineers.clear()
                        monitoring_project.assigned_engineers.set(projeng_project.assigned_engineers.all())
                    else:
                        print("Warning: MonitoringProject model does not have assigned_engineers field. Cannot copy assignments.")
                    # --- End copy assigned engineers ---

                    print("Project saved/synced in both databases.")
                    print("Project Engineer Project:", projeng_project)
                    print("Head Engineer Project:", monitoring_project)

                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'project': project_to_dict(projeng_project)}) # Return projeng project data
                    else:
                        # For non-AJAX requests, redirect to the project list page
                        return redirect('project_list')
                except Exception as save_error:
                    logging.exception("Error saving project after form validation")
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': f'Error saving project: {save_error}'}, status=500)
                    else:
                        # For non-AJAX, show error on the page
                        form.add_error(None, f'Error saving project: {save_error}')

            else:
                # For invalid POST, if it was AJAX, return errors.
                logging.warning(f"Project form validation failed: {form.errors}")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': form.errors}, status=400)
                else:
                    pass # Fall through to GET handling with form errors

        # --- GET request handling (and non-AJAX POST with errors) ---

        # Fetch all projects from both databases, ordered by most recent first
        # Now that MonitoringProject has assigned_engineers, we can filter here
        if request.user.groups.filter(name='Project Engineer').exists():
             # Project Engineers only see projects assigned to them from the Monitoring DB
             combined_projects = MonitoringProject.objects.filter(assigned_engineers=request.user).order_by('-created_at')
        elif request.user.groups.filter(name='Head Engineer').exists() or request.user.is_superuser or request.user.is_staff:
            # Head Engineers and staff see all projects from Monitoring DB
            # For simplicity here, they see Monitoring Projects. Adjust if they should see ProjEng Projects.
             combined_projects = MonitoringProject.objects.all().order_by('-created_at')
        else:
             # Other users see no projects
             combined_projects = MonitoringProject.objects.none()

        # Apply barangay filter if selected
        barangay = request.GET.get('barangay')
        if barangay:
            combined_projects = [p for p in combined_projects if p.barangay == barangay] # Filtering list in Python after fetching - could optimize with DB filter

        # Note: Sorting already done by order_by in DB query

        # Debug output: print all project names and PRNs in the combined list
        # print('Combined Projects:')
        # for p in combined_projects:
        #     print(f'PRN: {getattr(p, "prn", "")}, Name: {p.name}, Barangay: {p.barangay}, Assigned: {list(p.assigned_engineers.values_list('username', flat=True)) if hasattr(p, 'assigned_engineers') else 'N/A'}')

        # Paginate the combined projects
        paginator = Paginator(list(combined_projects), 10)  # Use list() for pagination after potential Python filtering
        page_number = request.GET.get('page')

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page_obj = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 999), deliver last page of results.
            page_obj = paginator.page(paginator.num_pages)

        # Create a JSON-serializable list of all projects for JavaScript
        # Ensure correct project objects (MonitoringProject) are used here
        projects_data = []
        for p in page_obj.object_list: # Iterate over projects on the current page
             # Attempt to get latest progress for MonitoringProject - needs annotation or similar approach
             # For now, setting progress to 0 or N/A
             progress = 0 # Default or fetch from related model if available on MonitoringProject
             # You would need a similar Subquery annotation as in map_view if progress is tracked per project in Monitoring DB

             # Convert date fields to ISO strings for JSON
             start_date_str = p.start_date.isoformat() if p.start_date else '';
             end_date_str = p.end_date.isoformat() if p.end_date else '';
             created_at_str = p.created_at.isoformat() if p.created_at else '';

             projects_data.append({
                 "id": p.id,
                 "prn": getattr(p, "prn", ""),
                 "name": p.name,
                 "description": p.description,
                 "barangay": p.barangay,
                 "project_cost": str(getattr(p, "project_cost", "")) if getattr(p, "project_cost", None) else "",
                 "source_of_funds": getattr(p, "source_of_funds", ""),
                 "status": p.status,
                 "latitude": str(getattr(p, "latitude", "")) if getattr(p, "latitude", None) else "",
                 "longitude": str(getattr(p, "longitude", "")) if getattr(p, "longitude", None) else "",
                 "start_date": start_date_str,
                 "end_date": end_date_str,
                 "image": p.image.url if getattr(p, "image", None) else "",
                 "progress": progress, # Placeholder progress
                 "assigned_engineers": list(p.assigned_engineers.values_list('username', flat=True)) if hasattr(p, 'assigned_engineers') else [], # Use assigned_engineers from MonitoringProject
             })

        context = {
            'page_obj': page_obj, # Pass the Page object for pagination in template
            'form': form, # Always defined
            'projects_data': projects_data, # Pass the list directly for json_script
        }
        return render(request, 'monitoring/project_list.html', context)

    except Exception as e:
        print(f"Error in project_list view: {str(e)}")
        # Return a server error response for AJAX requests
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        # For non-AJAX requests, re-raise the exception for Django to handle
        raise

@user_passes_test(is_head_engineer, login_url='/accounts/login/')
def map_view(request):
    # Fetch all Monitoring Projects that have valid latitude and longitude (not null)
    all_projects = MonitoringProject.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
    )

    # Filter out projects with empty strings in latitude or longitude in Python
    projects_with_coords = []
    for project in all_projects:
        if project.latitude != '' and project.longitude != '':
            projects_with_coords.append(project)

    # Prepare projects_data for the map, ensuring latitude and longitude are floats
    projects_data = []
    for p in projects_with_coords:
        latest_progress = None
        # Find the corresponding project in the ProjEng DB using PRN
        try:
            projeng_project = ProjEngProject.objects.filter(prn=p.prn).first()
            if projeng_project:
                # Get latest progress from ProjEng DB
                progress_update = ProjectProgress.objects.filter(project=projeng_project).order_by('-date').first()
                if progress_update:
                    latest_progress = progress_update.percentage_complete
        except Exception as e:
            print(f"Error fetching progress for project {p.prn}: {e}")
            latest_progress = 0 # Default to 0 on error

        projects_data.append({
            "id": p.id,
            "name": p.name,
            "prn": getattr(p, "prn", ""),
            "barangay": p.barangay,
            "status": p.status,
            "latitude": float(p.latitude) if p.latitude else None,
            "longitude": float(p.longitude) if p.longitude else None,
            "image": p.image.url if getattr(p, "image", None) else "",
            "progress": latest_progress if latest_progress is not None else 0, # Include progress
            "assigned_engineers": [e.get_full_name() or e.username for e in p.assigned_engineers.all()] if hasattr(p, 'assigned_engineers') else [], # Include assigned engineers
            "description": p.description,
            "project_cost": str(getattr(p, "project_cost", "")) if getattr(p, "project_cost", None) else "",
            "source_of_funds": getattr(p, "source_of_funds", ""),
            "start_date": p.start_date.isoformat() if p.start_date else '',
            "end_date": p.end_date.isoformat() if p.end_date else '',
        })

    context = {
        'projects_data': projects_data, # projects_data is now a list of dicts
    }
    return render(request, 'monitoring/map.html', context)

def reports(request):
    projects = MonitoringProject.objects.all()
    project_list = [
        {
            "prn": p.prn,
            "name": p.name,
            "description": p.description,
            "barangay": p.barangay,
            "location": p.barangay,  # If you have a separate location field, use p.location
            "project_cost": p.project_cost,
            "source_of_funds": p.source_of_funds,
            "start_date": p.start_date.strftime('%Y-%m-%d') if p.start_date else '',
            "end_date": p.end_date.strftime('%Y-%m-%d') if p.end_date else '',
            "status": p.status,
        }
        for p in projects
    ]
    context = {}
    context['projects_json'] = json.dumps(project_list)

    # Chart data
    status_labels = ['Completed', 'Ongoing', 'Planned', 'Delayed']
    status_map = {
        'completed': 'Completed',
        'in_progress': 'Ongoing',
        'ongoing': 'Ongoing',
        'planned': 'Planned',
        'pending': 'Planned',
        'delayed': 'Delayed',
    }
    status_counts = Counter(status_map.get(p['status'].lower(), p['status'].capitalize()) for p in project_list)
    context['status_labels'] = json.dumps(status_labels)
    context['status_counts'] = json.dumps([status_counts.get(label, 0) for label in status_labels])

    barangay_labels = sorted(set(p['barangay'] for p in project_list if p['barangay']))
    barangay_counts = Counter(p['barangay'] for p in project_list if p['barangay'])
    context['barangay_labels'] = json.dumps(barangay_labels)
    context['barangay_counts'] = json.dumps([barangay_counts.get(label, 0) for label in barangay_labels])

    # For table rendering (optional, not used by JS filtering)
    context['projects'] = projects
    return render(request, 'monitoring/reports.html', context)

@csrf_exempt
def project_update_api(request, pk):
    if request.method == 'POST':
        try:
            # Update in project engineer database (primary)
            projeng_project = ProjEngProject.objects.get(pk=pk)
            data = json.loads(request.body)
            # Update fields from request data
            projeng_project.status = data.get('status', projeng_project.status)
            # You might want to update other fields here if the API allows
            projeng_project.save()

            # Update corresponding project in head engineer database
            try:
                # Find by name and barangay, assuming uniqueness
                monitoring_project = MonitoringProject.objects.get(
                    name=projeng_project.name,
                    barangay=projeng_project.barangay
                )
                monitoring_project.status = projeng_project.status
                # Update other fields as needed
                monitoring_project.save()
            except MonitoringProject.DoesNotExist:
                # If corresponding project doesn't exist, create it
                 monitoring_project = MonitoringProject(
                    prn=projeng_project.prn,
                    name=projeng_project.name,
                    description=projeng_project.description,
                    barangay=projeng_project.barangay,
                    project_cost=projeng_project.project_cost,
                    source_of_funds=projeng_project.source_of_funds,
                    status=projeng_project.status,
                    latitude=projeng_project.latitude,
                    longitude=projeng_project.longitude,
                    start_date=projeng_project.start_date,
                    end_date=projeng_project.end_date,
                    image=projeng_project.image
                )
                 monitoring_project.save()
            except MonitoringProject.MultipleObjectsReturned:
                 # Handle case where multiple monitoring projects match (log or raise error)
                 print(f"Warning: Multiple monitoring projects found for {projeng_project.name} - {projeng_project.barangay}")
                 # Decide how to handle: update first one? log and skip? raise error?

            return JsonResponse({'success': True, 'status': projeng_project.status}) # Return status from primary source
        except ProjEngProject.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error updating project API: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return HttpResponseNotAllowed(['POST'])

@csrf_exempt
def project_delete_api(request, pk):
    print(f"DEBUG: Received delete request for project id: {pk}, method: {request.method}")
    if request.method == 'POST' or request.method == 'DELETE':
        try:
            # First try to find the project in MonitoringProject
            try:
                monitoring_project = MonitoringProject.objects.get(pk=pk)
                project_name = monitoring_project.name
                project_barangay = monitoring_project.barangay
                monitoring_project.delete()
                print(f"DEBUG: Deleted MonitoringProject with id {pk}")

                # Try to find and delete corresponding ProjEngProject
                try:
                    projeng_project = ProjEngProject.objects.get(
                        name=project_name,
                        barangay=project_barangay
                    )
                    projeng_project.delete()
                    print(f"DEBUG: Deleted ProjEngProject with name {project_name} and barangay {project_barangay}")
                except ProjEngProject.DoesNotExist:
                    print("DEBUG: No corresponding ProjEngProject found")
                except ProjEngProject.MultipleObjectsReturned:
                    print("DEBUG: Multiple ProjEngProjects found")

            except MonitoringProject.DoesNotExist:
                # If not found in MonitoringProject, try ProjEngProject
                try:
                    projeng_project = ProjEngProject.objects.get(pk=pk)
                    project_name = projeng_project.name
                    project_barangay = projeng_project.barangay
                    projeng_project.delete()
                    print(f"DEBUG: Deleted ProjEngProject with id {pk}")

                    # Try to find and delete corresponding MonitoringProject
                    try:
                        monitoring_project = MonitoringProject.objects.get(
                            name=project_name,
                            barangay=project_barangay
                        )
                        monitoring_project.delete()
                        print(f"DEBUG: Deleted MonitoringProject with name {project_name} and barangay {project_barangay}")
                    except MonitoringProject.DoesNotExist:
                        print("DEBUG: No corresponding MonitoringProject found")
                    except MonitoringProject.MultipleObjectsReturned:
                        print("DEBUG: Multiple MonitoringProjects found")

                except ProjEngProject.DoesNotExist:
                    print("DEBUG: Project not found in either model")
                    return JsonResponse({'error': 'Project not found'}, status=404)

            return JsonResponse({'success': True})
        except Exception as e:
            print(f"DEBUG: Exception occurred: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    print("DEBUG: Method not allowed")
    return HttpResponseNotAllowed(['POST', 'DELETE'])

@user_passes_test(is_head_engineer, login_url='/accounts/login/')
def delayed_projects(request):
    today = timezone.now().date()
    # Get all delayed projects from MonitoringProject
    monitoring_delayed = MonitoringProject.objects.filter(status='delayed')
    # Get all delayed projects from ProjEngProject
    projeng_delayed = ProjEngProject.objects.filter(status='delayed')
    seen = set()
    all_delayed = []
    # Add Monitoring projects first (preferred source)
    for p in monitoring_delayed:
        key = (getattr(p, 'prn', None), getattr(p, 'barangay', None))
        seen.add(key)
        all_delayed.append({
            'prn': getattr(p, 'prn', ''),
            'name': getattr(p, 'name', ''),
            'barangay': getattr(p, 'barangay', ''),
            'progress': getattr(p, 'progress', 0),
            'start_date': p.start_date.strftime('%Y-%m-%d') if p.start_date else '',
            'end_date': p.end_date.strftime('%Y-%m-%d') if p.end_date else '',
            'assigned_engineers': [e.get_full_name() or e.username for e in p.assigned_engineers.all()] if hasattr(p, 'assigned_engineers') else [],
            'source': 'Monitoring',
        })
    # Add ProjEng projects only if not already present
    for p in projeng_delayed:
        key = (getattr(p, 'prn', None), getattr(p, 'barangay', None))
        if key not in seen:
            all_delayed.append({
                'prn': getattr(p, 'prn', ''),
                'name': getattr(p, 'name', ''),
                'barangay': getattr(p, 'barangay', ''),
                'progress': getattr(p, 'progress', 0),
                'start_date': p.start_date.strftime('%Y-%m-%d') if p.start_date else '',
                'end_date': p.end_date.strftime('%Y-%m-%d') if p.end_date else '',
                'assigned_engineers': [e.get_full_name() or e.username for e in p.assigned_engineers.all()] if hasattr(p, 'assigned_engineers') else [],
                'source': 'ProjEng',
            })
    context = {
        'delayed_projects': all_delayed,
        'total_delayed': len(all_delayed),
    }
    return render(request, 'monitoring/delayed_projects.html', context)

@login_required
def project_engineer_analytics(request):
    # Get projects assigned to the current project engineer from the ProjEng DB
    assigned_projeng_projects = ProjEngProject.objects.filter(assigned_engineers=request.user)

    projects_data = []
    for projeng_project in assigned_projeng_projects:
        print(f"DEBUG: Processing ProjEngProject ID: {projeng_project.id}, PRN: {projeng_project.prn}")
        # Try to find the corresponding MonitoringProject using PRN
        monitoring_project = MonitoringProject.objects.filter(prn=projeng_project.prn).first()

        if monitoring_project:
            print(f"DEBUG: Found corresponding MonitoringProject ID: {monitoring_project.id}, PRN: {monitoring_project.prn}")
        else:
            print(f"DEBUG: No corresponding MonitoringProject found for PRN: {projeng_project.prn}")

        # Use data from ProjEngProject, supplement with MonitoringProject data if available
        project_id = projeng_project.id # Use ProjEng Project ID for the link
        project_name = projeng_project.name
        project_description = projeng_project.description
        project_barangay = projeng_project.barangay
        project_status = projeng_project.status
        project_start_date = projeng_project.start_date
        project_end_date = projeng_project.end_date
        project_prn = projeng_project.prn
        project_budget = projeng_project.project_cost
        project_location = getattr(projeng_project, 'location', '')
        project_contractor = getattr(projeng_project, 'contractor', '')
        project_remarks = getattr(projeng_project, 'remarks', '')
        project_images = [] # Assuming images are linked to ProgressPhoto in ProjEng DB
        project_assigned_to = ', '.join([user.get_full_name() or user.username for user in projeng_project.assigned_engineers.all()])

        # Get latest progress from ProjEng DB
        progress_updates = ProjectProgress.objects.filter(project=projeng_project).order_by('-date')
        latest_progress = progress_updates.first()

        # If a corresponding MonitoringProject exists, use its status or other preferred fields if needed
        if monitoring_project:
            project_status = monitoring_project.status # Prioritize status from Monitoring if needed
            # You could prioritize other fields from monitoring_project here as well

        projects_data.append({
            'id': project_id, # This is the ProjEng Project ID now
            'name': project_name,
            'description': project_description,
            'barangay': project_barangay,
            'progress': latest_progress.percentage_complete if latest_progress else 0, # Use progress from ProjEng
            'start_date': project_start_date.isoformat() if project_start_date else '',
            'end_date': project_end_date.isoformat() if project_end_date else '',
            'status': project_status,
            'created_at': projeng_project.created_at.isoformat() if hasattr(projeng_project, 'created_at') and projeng_project.created_at else '',
            'assigned_to': project_assigned_to,
            'prn': project_prn,
            'budget': project_budget,
            'location': project_location,
            'contractor': project_contractor,
            'remarks': project_remarks,
            'images': project_images,
            'projeng_id': project_id, # Still include projeng_id for clarity
        })

        print(f"DEBUG: Added project to projects_data - ID: {project_id}, ProjEng ID: {project_id}")

    # Recalculate counts based on the filtered projects_data list
    total_projects = len(projects_data)
    completed_projects = len([p for p in projects_data if p['status'] == 'completed'])
    ongoing_projects = len([p for p in projects_data if p['status'] in ['ongoing', 'in_progress']]),
    planned_projects = len([p for p in projects_data if p['status'] in ['planned', 'pending']]),
    delayed_projects_count = len([p for p in projects_data if p['status'] == 'delayed']),

    # Ensure single values for counts if they were tuples
    if isinstance(ongoing_projects, tuple): ongoing_projects = ongoing_projects[0]
    if isinstance(planned_projects, tuple): planned_projects = planned_projects[0]
    if isinstance(delayed_projects_count, tuple): delayed_projects_count = delayed_projects_count[0]

    context = {
        'projects': projects_data,  # Pass the list, not a JSON string
        'user_role': 'project_engineer',
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'ongoing_projects': ongoing_projects,
        'planned_projects': planned_projects,
        'delayed_projects_count': delayed_projects_count,
    }

    return render(request, 'projeng/project_analytics.html', context)

@user_passes_test(is_head_engineer, login_url='/accounts/login/')
def head_engineer_analytics(request):
    all_projects = MonitoringProject.objects.all()
    from projeng.models import ProjectProgress
    flag_overdue_projects_as_delayed(all_projects, ProjectProgress)
    projects_data = []
    today = timezone.now().date()
    for project in all_projects:
        # Check and update status to 'delayed' if overdue and not complete
        is_overdue = hasattr(project, 'end_date') and project.end_date and project.end_date < today
        is_not_completed = True # Default to True, refine based on project type and progress

        progress = getattr(project, 'progress', None)
        if progress is None and hasattr(project, 'latest_progress'):
            progress = project.latest_progress or 0

        if progress is not None:
            is_not_completed = progress < 100
        elif hasattr(project, 'status') and project.status == 'completed':
             is_not_completed = False

        if is_overdue and is_not_completed and (hasattr(project, 'status') and project.status != 'delayed'):
            project.status = 'delayed'
            # Note: Saving here updates the database. Consider if this is desired on every page load.
            try:
                 project.save()
                 print(f"DEBUG: Updated status of project {project.name} to delayed in head_engineer_analytics.")
            except Exception as e:
                 print(f"DEBUG: Failed to save project {project.name} in head_engineer_analytics: {e}")

        status_raw = project.status if hasattr(project, 'status') else ''
        status_display = status_raw.replace('_', ' ').title()
        try:
            # Get all matching projects and take the first one
            matching_projects = ProjEngProject.objects.filter(prn=project.prn)
            if matching_projects.exists():
                projeng_project = matching_projects.first()
                updates = []
                total_progress = 0
                for update in ProjectProgress.objects.filter(project=projeng_project):
                    if hasattr(update, 'created_by') and update.created_by:
                        engineer_name = update.created_by.get_full_name() or update.created_by.username or 'Unknown'
                    else:
                        engineer_name = 'Unknown'
                    updates.append({
                        'date': update.date.strftime('%Y-%m-%d'),
                        'percentage_complete': update.percentage_complete,
                        'description': update.description,
                        'engineer': engineer_name,
                        'photos': [photo.image.url for photo in ProgressPhoto.objects.filter(progress_update=update)],
                    })
                    total_progress += update.percentage_complete
                projects_data.append({
                    'id': project.id,
                    'name': project.name,
                    'prn': project.prn,
                    'barangay': project.barangay,
                    'status': status_raw,
                    'status_display': status_display,
                    'assigned_to': [e.get_full_name() or e.username for e in projeng_project.assigned_engineers.all()],
                    'progress_updates': updates,
                    'total_progress': total_progress,
                    'project_cost': project.project_cost,
                    'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else None,
                    'end_date': project.end_date.strftime('%Y-%m-%d') if project.end_date else None,
                    'cost_entries': [{
                        'date': cost.date.strftime('%Y-%m-%d'),
                        'cost_type': cost.get_cost_type_display(),
                        'description': cost.description,
                        'amount': str(cost.amount),
                        'receipt_url': cost.receipt.url if cost.receipt else None,
                    } for cost in ProjectCost.objects.filter(project=projeng_project).order_by('date')],
                })
            else:
                # Handle case where no matching project is found
                projects_data.append({
                    'id': project.id,
                    'name': project.name,
                    'prn': project.prn,
                    'barangay': project.barangay,
                    'status': status_raw,
                    'status_display': status_display,
                    'assigned_to': [],
                    'progress_updates': [],
                    'total_progress': 0,
                    'project_cost': project.project_cost,
                    'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else None,
                    'end_date': project.end_date.strftime('%Y-%m-%d') if project.end_date else None,
                    'cost_entries': [],
                })
        except Exception as e:
            print(f"Error processing project {project.name}: {e}")
            # Add project with minimal data in case of error
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'prn': project.prn,
                'barangay': project.barangay,
                'status': status_raw,
                'status_display': status_display,
                'assigned_to': [],
                'progress_updates': [],
                'total_progress': 0,
                'project_cost': project.project_cost,
                'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else None,
                'end_date': project.end_date.strftime('%Y-%m-%d') if project.end_date else None,
                'cost_entries': [],
            })
    context = {
        'projects': projects_data,
        'user_role': 'head_engineer',
    }
    print('Projects in analytics:')
    for p in projects_data:
        print(f"Name: {p['name']}, Status: {p['status']}, Status Display: {p['status_display']}")
    return render(request, 'monitoring/analytics.html', context)

def project_detail(request, pk):
    project = get_object_or_404(MonitoringProject, pk=pk)
    return render(request, 'monitoring/project_detail.html', {'project': project})

@user_passes_test(is_project_or_head_engineer, login_url='/accounts/login/')
def head_engineer_project_detail(request, pk):
    try:
        # Fetch the project from the Monitoring DB (Head Engineer's view)
        project = get_object_or_404(MonitoringProject, pk=pk)

        # Although Head Engineers can see all projects, it's good practice to ensure
        # they have the 'Head Engineer' permission to access this specific view.
        # The user_passes_test decorator already handles this.

        # --- Fetch related data from the ProjEng DB ---
        # Find the corresponding project in the ProjEng DB using PRN or other identifier
        # Assuming PRN is unique across both DBs for corresponding projects
        try:
            projeng_project = ProjEngProject.objects.filter(prn=project.prn).first()
        except ProjEngProject.DoesNotExist:
            projeng_project = None # Handle case where no corresponding ProjEng project exists

        latest_progress = None
        progress_updates = None
        costs = None
        total_cost = 0
        cost_by_type = None
        budget_utilization = 0
        timeline_data = None
        project_photos = None

        if projeng_project:
            # Get progress data from ProjEng DB
            progress_updates = ProjectProgress.objects.filter(project=projeng_project).order_by('-date')
            latest_progress = progress_updates.first()
            # Get project photos related to progress updates from ProjEng DB
            project_photos = ProgressPhoto.objects.filter(progress_update__project=projeng_project).order_by('-progress_update__date') if projeng_project else ProgressPhoto.objects.none()

            # Get cost data from ProjEng DB
            costs = ProjectCost.objects.filter(project=projeng_project) if projeng_project else ProjectCost.objects.none()
            total_cost = costs.aggregate(total=Sum('amount'))['total'] or 0
            cost_by_type = costs.values('cost_type').annotate(total=Sum('amount')) if costs else []

            # Calculate budget utilization (using ProjEng project cost if available)
            budget_utilization = (total_cost / projeng_project.project_cost * 100) if projeng_project and projeng_project.project_cost and projeng_project.project_cost > 0 else 0
            
            # Get timeline data from ProjEng DB dates
            timeline_data = {
                'start_date': projeng_project.start_date if projeng_project else None,
                'end_date': projeng_project.end_date if projeng_project else None,
                'days_elapsed': (timezone.now().date() - projeng_project.start_date).days if projeng_project and projeng_project.start_date else None,
                'total_days': (projeng_project.end_date - projeng_project.start_date).days if projeng_project and projeng_project.start_date and projeng_project.end_date else None,
            }
        
        # If no corresponding ProjEng project, use Monitoring project dates for timeline if available
        if not timeline_data or (not timeline_data['start_date'] and project.start_date):
             timeline_data = {
                 'start_date': project.start_date,
                 'end_date': project.end_date,
                 'days_elapsed': (timezone.now().date() - project.start_date).days if project.start_date else None,
                 'total_days': (project.end_date - project.start_date).days if project.start_date and project.end_date else None,
             }


        context = {
            'project': project, # Pass the MonitoringProject object
            'projeng_project': projeng_project, # Pass the related ProjEngProject object (can be None)
            'latest_progress': latest_progress,
            'progress_updates': progress_updates, # Pass all progress updates
            'total_cost': total_cost,
            'cost_by_type': cost_by_type,
            'costs': costs, # Pass all cost entries
            'budget_utilization': budget_utilization,
            'timeline_data': timeline_data,
            'project_photos': project_photos, # Pass project photos
            'user_role': 'head_engineer', # Indicate the role for template logic
        }

        return render(request, 'monitoring/head_engineer_project_detail.html', context)

    except Http404:
        raise # Re-raise Http404
    except Exception as e:
        logging.error(f"Error in head_engineer_project_detail view for project {pk}: {e}")
        return HttpResponseServerError("An error occurred while loading project details.") 