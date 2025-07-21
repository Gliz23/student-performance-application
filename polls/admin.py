from django.contrib import admin
from .models import Student, SubjectEntry

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user']

@admin.register(SubjectEntry)
class SubjectEntryAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject_name', 'predicted_score', 'created_at']
    list_filter = ['student', 'subject_name']
    search_fields = ['subject_name']

