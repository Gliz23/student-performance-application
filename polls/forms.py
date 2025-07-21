# class SubjectEntryForm(forms.ModelForm):
#     class Meta:
#         model = SubjectEntry
#         fields = '__all__'
#         exclude = ['student', 'predicted_score', 'study_guide', 'study_plan_pdf', 'created_at', 'updated_at']
#         widgets = {
#             'parental_involvement': forms.Select(choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')]),
#             'access_to_resources': forms.Select(choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')]),
#             'extracurricular_activities': forms.Select(choices=[('Yes', 'Yes'), ('No', 'No')]),
#             'motivation_level': forms.Select(choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')]),
#             'internet_access': forms.Select(choices=[('Yes', 'Yes'), ('No', 'No')]),
#             'family_income': forms.Select(choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')]),
#             'teacher_quality': forms.Select(choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')]),
#             'school_type': forms.Select(choices=[('Public', 'Public'), ('Private', 'Private')]),
#             'peer_influence': forms.Select(choices=[('Positive', 'Positive'), ('Negative', 'Negative')]),
#             'learning_disabilities': forms.Select(choices=[('Yes', 'Yes'), ('No', 'No')]),
#             'parental_education_level': forms.Select(choices=[
#                 ('High School', 'High School'),
#                 ("Bachelor's", "Bachelor's"),
#                 ('Postgraduate', 'Postgraduate'),
#             ]),
#             'distance_from_home': forms.Select(choices=[('Near', 'Near'), ('Far', 'Far')]),
#             'gender': forms.Select(choices=[('Male', 'Male'), ('Female', 'Female')]),
#         }
#         labels = {
#             'subject_name': "Subject Name",
#             'hours_studied': "Study Hours Per Week",
#             'attendance': "Class Attendance (%)",
#             'parental_involvement': "Parental Involvement",
#             'access_to_resources': "Access to Learning Resources",
#             'extracurricular_activities': "Do You Participate in Extracurricular Activities?",
#             'sleep_hours': "Average Sleep Hours per Night",
#             'previous_scores': "Previous Exam Score (%)",
#             'motivation_level': "Motivation Level for this Subject",
#             'internet_access': "Do You Have Internet Access at Home?",
#             'tutoring_sessions': "Tutoring Sessions per Week (on a scale of 1-5)",
#             'family_income': "Family Income Level",
#             'teacher_quality': "Quality of Teaching",
#             'school_type': "Type of School",
#             'peer_influence': "Peer Influence",
#             'physical_activity': "Physical Activity per Week (on a scale of 1-5)",
#             'learning_disabilities': "Do You Have Any Learning Disabilities?",
#             'parental_education_level': "Parent's Education Level",
#             'distance_from_home': "Distance from Home to School",
#             'gender': "Gender",
#         }
#         help_texts = {
#             'attendance': "Enter your attendance percentage (e.g., 90 for 90%)",
#             'previous_scores': "Last exam score in this subject (0-100)",
#             'tutoring_sessions': "How many tutoring sessions do you attend weekly?",
#             'physical_activity': "Estimate your weekly hours of physical activity",
#         }

from django import forms
from .models import SubjectEntry

class Step1Form(forms.Form):
    subject_name = forms.CharField(label="What is the name of this course?")
    previous_scores = forms.FloatField(label="What was your previous grade in related subject?")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_subject_name(self):
        name = self.cleaned_data['subject_name']
        if self.user:
            # prevent duplicates per user
            if SubjectEntry.objects.filter(student=self.user, subject_name__iexact=name).exists():
                raise forms.ValidationError("You have already added a course with this name.")
        return name

    def clean_previous_scores(self):
        data = self.cleaned_data['previous_scores']
        if not (0 < data <= 100):
            raise forms.ValidationError("Hours studied must be between 0 to 100.")
        return data

class Step2Form(forms.Form):
    hours_studied = forms.FloatField(label="How many hours do you study per week?")

    def clean_hours_studied(self):
        data = self.cleaned_data['hours_studied']
        if data < 0:
            raise forms.ValidationError("Hours studied must be positive.")
        return data
    
class Step3Form(forms.Form):
    extracurricular = forms.ChoiceField(label="Do you participate in extracurriculars?", choices=[('Yes', 'Yes'), ('No', 'No')])

class Step4Form(forms.Form):
    sleep_hours = forms.FloatField(label="How many hours do you sleep on average?")

    def clean_sleep_hours(self):
        data = self.cleaned_data['sleep_hours']
        if not (0 < data < 24):
            raise forms.ValidationError("Let's be serious here. We have just 24 hours in a day.")
        return data

class Step5Form(forms.Form):
    question_papers = forms.IntegerField(label="How many question papers have you practiced?")
    motivation = forms.CharField(label="Describe your motivation level", widget=forms.TextInput())
    preferred_learning_style = forms.CharField(label="What is your preferred learning style? ", widget=forms.Textarea())
