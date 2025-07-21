from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class SubjectEntry(models.Model):
    # Link to the user (student)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='subject_entries')
    
    # Subject information
    subject_name = models.CharField(max_length=100)
    hours_studied = models.FloatField(default=0)
    previous_scores = models.FloatField(default=50)
    extracurricular = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')
    sleep_hours = models.FloatField(default=8)
    question_papers = models.IntegerField(default=0)
    motivation = models.CharField(max_length=255, default='Medium')
    preferred_learning_style = models.TextField(default='None')


    # Outputs
    predicted_score = models.FloatField(null=True, blank=True)
    study_guide = models.TextField(null=True, blank=True)
    study_plan_pdf = models.FileField(upload_to='study_plans/', null=True, blank=True)
    

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'subject_name')  # 🚨 This line enforces the rule

    def __str__(self):
        return f"{self.student.user.username} - {self.subject_name}"
 

        
#   Each student is linked to a User and can have multiple subject entries.
# Each SubjectEntry contains both input data and optional output data (score and guide).
# You can easily build views to:
# Create predictions per subject
# Update/delete subjects
# Display progress and scores in a dashboard