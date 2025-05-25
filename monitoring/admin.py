from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'prn', 'barangay', 'status', 'progress', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'barangay', 'created_at', 'start_date', 'end_date')
    search_fields = ('name', 'prn', 'barangay', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'prn', 'description', 'image')
        }),
        ('Location', {
            'fields': ('barangay', 'latitude', 'longitude')
        }),
        ('Project Details', {
            'fields': ('project_cost', 'source_of_funds', 'status', 'progress')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'created_at', 'updated_at')
        }),
    )
    list_per_page = 20
    ordering = ('-created_at',)

    def get_list_display_links(self, request, list_display):
        return ['name', 'prn']

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at') 