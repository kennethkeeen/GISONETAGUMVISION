"""
Background tasks for project engineering operations
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Project, ProjectProgress, ProjectCost, Notification
from django.contrib.auth.models import User
import csv
import io
from datetime import datetime
import openpyxl
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
try:
    from xhtml2pdf import pisa
except Exception:
    pisa = None


@shared_task
def generate_project_report_csv(project_id, user_id):
    """
    Generate CSV report for a project in the background
    """
    try:
        project = Project.objects.get(pk=project_id)
        user = User.objects.get(pk=user_id)
        
        progress_updates = ProjectProgress.objects.filter(project=project).order_by('date')
        costs = ProjectCost.objects.filter(project=project)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write project details
        writer.writerow(['Project Report'])
        writer.writerow(['Project Name', project.name])
        writer.writerow(['PRN', project.prn])
        writer.writerow(['Status', project.get_status_display()])
        writer.writerow(['Start Date', project.start_date])
        writer.writerow(['End Date', project.end_date])
        writer.writerow(['Budget', project.project_cost])
        writer.writerow([])
        
        # Write progress updates
        writer.writerow(['Progress Updates'])
        writer.writerow(['Date', 'Percentage Complete', 'Description'])
        for update in progress_updates:
            writer.writerow([update.date, update.percentage_complete, update.description])
        writer.writerow([])
        
        # Write cost breakdown
        writer.writerow(['Cost Breakdown'])
        writer.writerow(['Date', 'Type', 'Description', 'Amount'])
        for cost in costs:
            writer.writerow([cost.date, cost.get_cost_type_display(), cost.description, cost.amount])
        
        csv_content = output.getvalue()
        output.close()
        
        # Store result (you could save to file storage or send via email)
        # For now, we'll just return the content
        return csv_content
        
    except Exception as e:
        return f"Error generating report: {str(e)}"


@shared_task
def generate_project_report_pdf(project_id, user_id):
    """
    Generate PDF report for a project in the background
    """
    try:
        project = Project.objects.get(pk=project_id)
        user = User.objects.get(pk=user_id)
        
        if pisa is None:
            return "PDF export unavailable (missing xhtml2pdf)"
        
        progress_updates = ProjectProgress.objects.filter(project=project).order_by('date')
        costs = ProjectCost.objects.filter(project=project)
        
        # Render template
        template = get_template('projeng/reports/assigned_projects_pdf.html')
        context = {
            'project': project,
            'progress_updates': progress_updates,
            'costs': costs,
        }
        html = template.render(context)
        
        # Generate PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            return result.getvalue()
        else:
            return f"PDF generation error: {pdf.err}"
            
    except Exception as e:
        return f"Error generating PDF: {str(e)}"


@shared_task
def generate_project_report_excel(project_id, user_id):
    """
    Generate Excel report for a project in the background
    """
    try:
        project = Project.objects.get(pk=project_id)
        user = User.objects.get(pk=user_id)
        
        progress_updates = ProjectProgress.objects.filter(project=project).order_by('date')
        costs = ProjectCost.objects.filter(project=project)
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Project Report"
        
        # Write project details
        ws.append(['Project Report'])
        ws.append(['Project Name', project.name])
        ws.append(['PRN', project.prn])
        ws.append(['Status', project.get_status_display()])
        ws.append(['Start Date', project.start_date])
        ws.append(['End Date', project.end_date])
        ws.append(['Budget', project.project_cost])
        ws.append([])
        
        # Write progress updates
        ws.append(['Progress Updates'])
        ws.append(['Date', 'Percentage Complete', 'Description'])
        for update in progress_updates:
            ws.append([update.date, update.percentage_complete, update.description])
        ws.append([])
        
        # Write cost breakdown
        ws.append(['Cost Breakdown'])
        ws.append(['Date', 'Type', 'Description', 'Amount'])
        for cost in costs:
            ws.append([cost.date, cost.get_cost_type_display(), cost.description, cost.amount])
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output.getvalue()
        
    except Exception as e:
        return f"Error generating Excel: {str(e)}"


@shared_task
def send_notification_email(user_id, subject, message):
    """
    Send email notification in the background
    """
    try:
        user = User.objects.get(pk=user_id)
        if user.email:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@onetagumvision.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
            return f"Email sent to {user.email}"
        else:
            return f"User {user.username} has no email address"
    except Exception as e:
        return f"Error sending email: {str(e)}"


@shared_task
def process_delayed_projects():
    """
    Background task to flag overdue projects as delayed
    Runs periodically (can be scheduled)
    """
    try:
        from .utils import flag_overdue_projects_as_delayed
        from .models import Project, ProjectProgress
        
        today = timezone.now().date()
        ongoing_projects = Project.objects.filter(status__in=['in_progress', 'ongoing'])
        
        flagged_count = 0
        for project in ongoing_projects:
            if project.end_date and project.end_date < today:
                latest_progress = ProjectProgress.objects.filter(project=project).order_by('-date').first()
                latest_progress_pct = latest_progress.percentage_complete if latest_progress else 0
                
                if latest_progress_pct < 98 and project.status != 'delayed':
                    project.status = 'delayed'
                    project.save()
                    flagged_count += 1
        
        return f"Flagged {flagged_count} projects as delayed"
    except Exception as e:
        return f"Error processing delayed projects: {str(e)}"

