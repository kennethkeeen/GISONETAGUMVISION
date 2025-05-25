from django import forms
from projeng.models import Project
from django.contrib.auth.models import User, Group

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'prn', 'name', 'description', 'barangay', 'project_cost', 'source_of_funds',
            'status', 'latitude', 'longitude', 'start_date', 'end_date', 'image', 'assigned_engineers'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter the queryset for assigned_engineers to only include Project Engineers
        try:
            project_engineer_group = Group.objects.get(name='Project Engineer')
            self.fields['assigned_engineers'].queryset = User.objects.filter(groups=project_engineer_group)
        except Group.DoesNotExist:
            # If the group doesn't exist, show no users in the dropdown
            self.fields['assigned_engineers'].queryset = User.objects.none() 