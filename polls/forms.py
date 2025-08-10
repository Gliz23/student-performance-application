from django import forms
from .models import SubjectEntry
from .models import StudyPlanQuestionnaire

class Step1Form(forms.Form):
    subject_name = forms.CharField(label="SubjectEntry Name")

    previous_scores = forms.FloatField(
        label="Previous Scores (%)",
        initial=50,  # Default value matching your model
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'step': '0.1'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_subject_name(self):
        name = self.cleaned_data['subject_name']
        if self.user:
            # prevent duplicates per user
            qs = SubjectEntry.objects.filter(student=self.user.student, subject_name__iexact=name)
            if self.course:
                qs = qs.exclude(id=self.course.id)
            if qs.exists():
                raise forms.ValidationError("You already have a course with this name.")  
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




# class StudyPlanQuestionnaireForm(forms.ModelForm):
#     subjects = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g., Math, Physics'}))
    
#     class Meta:
#         model = StudyPlanQuestionnaire
#         fields = ['subjects', 'learning_style', 'goal', 'hours_per_week',  'hours_studied', 'sleep_hours', 'extracurricular', 'question_papers_solved', 'study_habits', 'previous_grades', 'motivation_level']
#         widgets = {
#             'learning_style': forms.Select(choices=[
#                 ('visual', 'Visual'),
#                 ('auditory', 'Auditory'),
#                 ('kinesthetic', 'Kinesthetic'),
#                 ('reading_writing', 'Reading/Writing')
#             ]),
#             'goal': forms.TextInput(attrs={'placeholder': 'e.g., Pass exam, Master topic'}),
#             'hours_per_week': forms.NumberInput(attrs={'min': 1})
#         }

#     def clean_subjects(self):
#         subjects = self.cleaned_data['subjects']
#         return [s.strip() for s in subjects.split(',')]
    
class StudyPlanQuestionnaireForm(forms.ModelForm):
    subjects = forms.CharField(max_length=255, required=True, help_text="Enter subjects (e.g., Math, Science)")
    learning_style = forms.ChoiceField(
        choices=[
            ('visual', 'Visual'),
            ('auditory', 'Auditory'),
            ('kinesthetic', 'Kinesthetic'),
            ('reading_writing', 'Reading/Writing')
        ],
        required=True
    )
    goal = forms.CharField(max_length=100, required=True, help_text="Enter your academic goal")
    hours_per_week = forms.IntegerField(min_value=1, required=True, help_text="Hours available per week")
    hours_studied = forms.IntegerField(min_value=0, required=True, help_text="Hours studied per week")
    sleep_hours = forms.IntegerField(min_value=0, required=True, help_text="Average sleep hours per night")
    extracurricular = forms.IntegerField(min_value=0, required=True, help_text="Hours spent on extracurricular activities")
    question_papers_solved = forms.IntegerField(min_value=0, required=True, help_text="Number of question papers solved")
    study_habits = forms.CharField(max_length=255, required=True, help_text="Describe your study habits")
    previous_grades = forms.IntegerField(min_value=0, max_value=100, required=True, help_text="Previous grades (0-100)")
    motivation_level = forms.ChoiceField(
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High')
        ],
        required=True
    )

    class Meta:
        model = StudyPlanQuestionnaire
        fields = [
            'subjects',
            'learning_style',
            'goal',
            'hours_per_week',
            'hours_studied',
            'sleep_hours',
            'extracurricular',
            'question_papers_solved',
            'study_habits',
            'previous_grades',
            'motivation_level'
        ]
    
 