from django.http import Http404
import requests
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Student, SubjectEntry, CourseSpecificEntry
from django.core.cache import cache
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
from .forms import StudyPlanQuestionnaireForm
from .models import StudyPlanQuestionnaire

from django.views.decorators.http import require_POST
from .forms import Step1Form, Step2Form, Step3Form, Step4Form, Step5Form
from formtools.wizard.views import SessionWizardView
from .forms import Step1Form, Step2Form, Step3Form, Step4Form, Step5Form





FASTAPI_URL = 'http://127.0.0.1:8000'


def home(request):
    return render(request, 'base.html')  

def sparkles_preview(request):
    return render(request, 'sparkles_preview.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Log in the user
            user = form.get_user()
            login(request, user)
            messages.success(request, "Welcome back!")
            return redirect('hero')  
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create a Student record for this user
            Student.objects.create(user=user)

            # Log the user in
            login(request, user)

            messages.success(request, "You have successfully signed up and are now logged in!")
            return redirect('hero')  # make sure this is defined in your urls/views
        else:
            messages.error(request, "There was an error with your signup. Please try again.")
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})

FASTAPI_PREDICTION_URL = 'http://127.0.0.1:8000/predict'

class SubjectWizard(SessionWizardView):
    form_list = [Step1Form, Step2Form, Step3Form, Step4Form, Step5Form]
    template_name = "multi_form.html"


    def done(self, form_list, **kwargs):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)

        student = self.request.user.student
        subject_name = data.get("subject_name", "Unnamed course")

        # Check if we're editing an existing course or creating a new one
        course_id = self.request.session.get('editing_course_id')
        
        if course_id:
            # Editing an existing course - get the course and create a prediction entry
            subject = get_object_or_404(SubjectEntry, id=course_id, student=student)
            
            # Create a new prediction entry
            entry = CourseSpecificEntry.objects.create(
                subject=subject,
                hours_studied=data["hours_studied"],
                previous_scores=data["previous_scores"],
                extracurricular=data["extracurricular"],
                sleep_hours=data["sleep_hours"],
                question_papers=data["question_papers"],
                motivation=data.get("motivation", "Medium"),
                preferred_learning_style=data.get("preferred_learning_style", "None"),
            )
            
            # Clear the editing flag from session
            if 'editing_course_id' in self.request.session:
                del self.request.session['editing_course_id']
                
            redirect_id = subject.id
        else:
            # Creating a new course
            subject = SubjectEntry.objects.create(
                student=student,
                subject_name=subject_name,
                hours_studied=data["hours_studied"],
                previous_scores=data["previous_scores"],
                extracurricular=data["extracurricular"],
                sleep_hours=data["sleep_hours"],
                question_papers=data["question_papers"],
                motivation=data.get("motivation", "Medium"),
                preferred_learning_style=data.get("preferred_learning_style", "None"),
            )

            # Also create a prediction entry for consistency
            entry = CourseSpecificEntry.objects.create(
                subject=subject,
                hours_studied=data["hours_studied"],
                previous_scores=data["previous_scores"],
                extracurricular=data["extracurricular"],
                sleep_hours=data["sleep_hours"],
                question_papers=data["question_papers"],
                motivation=data.get("motivation", "Medium"),
                preferred_learning_style=data.get("preferred_learning_style", "None"),
            )
        
            redirect_id = subject.id

        # 🔗 Send to FastAPI
        payload = {
            "hours_studied": entry.hours_studied,
            "previous_scores": entry.previous_scores,
            "extracurricular": entry.extracurricular,
            "sleep_hours": entry.sleep_hours,
            "question_papers": entry.question_papers,
        }

        try:
            response = requests.post(FASTAPI_PREDICTION_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Update both the prediction entry and the subject entry
            entry.predicted_score = result.get('predicted_score')
            entry.save()
            
            # Also update the main subject entry with the latest prediction
            subject.predicted_score = result.get('predicted_score')
            subject.save()

            # Log the result to see what is being returned
            # print("FastAPI Response:", result)
            # print("Sending Payload:", payload)

        except Exception as e:
            print("FastAPI prediction failed:", e)
         
        return redirect('subject_dashboard', course_id=redirect_id)
    
    def post(self, request, *args, **kwargs):
        print(f"Current Step: {self.steps.current}")  
        form = self.get_form()
        print("Form errors:", form.errors)  
        return super().post(request, *args, **kwargs)


def subject_dashboard(request, course_id):
    course = get_object_or_404(SubjectEntry, id=course_id)
    
    # Get the Student instance associated with the user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        raise Http404("Student profile not found")
    
    return render(request, 'dashboard.html', {
        'course': course,
        'courses': SubjectEntry.objects.filter(student=student),
        'current_page': 'dashboard'
    })


@login_required
def subject_results_view(request, subject_id):
    subject_entry = get_object_or_404(SubjectEntry, id=subject_id, student=request.user.student)

    return render(request, 'subject_results.html', {
        'subject_entry': subject_entry,
    })


def multi_step_form(request):
    if request.method == 'POST':
        step = request.POST.get('step')

        if step == '1':
            form = Step1Form(request.POST or None, user=request.user)
            if form.is_valid():
                request.session['previous_scores'] = form.cleaned_data['previous_scores']
                return redirect('step2')
        
        elif step == '2':
            form = Step2Form(request.POST)
            if form.is_valid():
                request.session['hours_studied'] = form.cleaned_data['hours_studied']
                return redirect('step3')
        
        elif step == '3':
            form = Step3Form(request.POST)
            if form.is_valid():
                request.session['extracurricular'] = form.cleaned_data['extracurricular']
                return redirect('step4')
        
        elif step == '4':
            form = Step4Form(request.POST)
            if form.is_valid():
                request.session['sleep_hours'] = form.cleaned_data['sleep_hours']
                return redirect('step5')
        
        elif step == '5':
            form = Step5Form(request.POST)
            if form.is_valid():
                subject_entry = SubjectEntry(
                    student=request.user,
                    subject_name=request.session.get('subject_name', 'Subject 1'),  # Update as needed
                    previous_scores=request.session['previous_scores'],
                    hours_studied=request.session['hours_studied'],
                    extracurricular=request.session['extracurricular'],
                    sleep_hours=request.session['sleep_hours'],
                    question_papers=form.cleaned_data['question_papers'],
                    preferred_learning_style=form.cleaned_data['preferred_learning_style']
                )


                subject_entry.save()
                # Optionally send data to FastAPI
                send_to_fastapi(subject_entry)
                return redirect('success')  # Redirect to a success page

    else:
        # Determine which form to display based on the current step
        step = request.GET.get('step', '1')
        if step == '1':
            form = Step1Form()
        elif step == '2':
            form = Step2Form()
        elif step == '3':
            form = Step3Form()
        elif step == '4':
            form = Step4Form()
        elif step == '5':
            form = Step5Form()

    return render(request, 'multi_step_form.html', {'form': form, 'step': step})



def send_to_fastapi(subject_entry):
    import requests
    data = {
        "hours_studied": subject_entry.hours_studied,
        "previous_scores": subject_entry.previous_scores,
        "extracurricular": subject_entry.extracurricular,
        "sleep_hours": subject_entry.sleep_hours,
        "question_papers": subject_entry.question_papers,
    }
    try:
        response = requests.post(FASTAPI_URL, json=data)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()  # Return the JSON response if needed
    except requests.exceptions.RequestException as e:
        print("Error sending data to FastAPI:", e)
        return None  # Return None or handle the error as needed



  
@login_required
def hero_view(request):
    
    student = request.user.student
    latest_score = SubjectEntry.objects.filter(student=student).last()
    recent_feedback = "Try practicing 1 more paper this week!"
    courses = SubjectEntry.objects.filter(student__user=request.user)

    return render(request, 'hero.html', {
        'latest_score': latest_score,
        'recent_feedback': recent_feedback,
        'courses': courses,
        'current_page': 'hero'
    })


@login_required
def student_dashboard_view(request):
    return render(request, 'dashboard.html')   

# @login_required         
# def get_guidance_view(request, course_id):

#     course = get_object_or_404(SubjectEntry, id=course_id)

#     # print("Button clicked for guidance")

#     if request.method == "POST":
        
#         subject_name = request.POST.get("subject_name")
        
#         print(subject_name)
#         if not subject_name:
#             return render(request, "get_guidance.html", {
#                 "error": "No course name (ID) provided."
#             })

#         # Get current student
#         student = Student.objects.filter(user=request.user).first()

#         # Fetch the subject entry using subject_name
#         subject = SubjectEntry.objects.filter(subject_name=subject_name, student=student).first()

#         if not subject:
#             return render(request, "get_guidance.html", {
#                 "error": f"No course found with subject name '{subject_name}'."
#             })
        

#         # Prepare payload for FastAPI
#         payload = {
#             "msg": "generate_guidance",
#             "user_id": str(subject.subject_name),
#             "predicted_score": subject.predicted_score,
#             "study_hours": subject.hours_studied,
#             "motivation_level": str(subject.motivation),
#             "preferred_learning_style": str(subject.preferred_learning_style),  
#         }

#         print("Sending to FastAPI:", json.dumps(payload, indent=2))

#         try:
#             response = requests.post("http://127.0.0.1:8000/chatbot-advice", json=payload)
#             response.raise_for_status()
#             result = response.json()


#             guidance_text = result.get("response")
#             # print(guidance_text)
#             # print("Response:", response.status_code, response.text)

#             if guidance_text:
#                 subject.chatbot_guidance = guidance_text
#                 subject.save()

#                 # print("Context sent to template:", {"subject": subject.subject_name, "guidance": guidance_text})
                
#                 return render(request, "dashboard.html", {
#                     "subject": subject,
#                     "guidance": guidance_text,
#                     })
#             else: 
#                 return render(request, "dashboard.html", {
#                     "subject": subject,
#                     "error": "No guidance was returned from the system."
#             })

#         except requests.RequestException as e:
#             return render(request, "get_guidance.html", {
#                 "error": f"Failed to get guidance: {e}"
#             })

#     return redirect("subject_dashboard", course_id = course.id)  


@login_required
def get_guidance_view(request, course_id):
    course = get_object_or_404(SubjectEntry, id=course_id)

    if request.method == "POST":

        student = Student.objects.filter(user=request.user).first()
        if not student:
            return render(request, "dashboard.html", {
                "error": "Student profile not found.",
                "course": course,
            })

        # Use the course fetched earlier (course_id) instead of querying again
        if not course:
            return render(request, "dashboard.html", {
                "error": f"Course not found.",
                "course": course,
            })

        # Prepare payload for FastAPI (corrected fields)
        payload = {
            "subject": str(course.subject_name),
            "user_id": str(request.user.id),  
            "predicted_score": course.predicted_score,
            "subject_weekly_study_hours": course.hours_studied,
            "motivation_level": str(course.motivation),
            "preferred_learning_style": str(course.preferred_learning_style),
        }

        print("Sending to FastAPI:", json.dumps(payload, indent=2))

        try:
            # Send to FastAPI (adjust URL if needed)
            FASTAPI_URL = "http://127.0.0.1:8000/chatbot-advice"  
            response = requests.post(FASTAPI_URL, json=payload, timeout=20)  
            response.raise_for_status()  
            result = response.json()
            print("This is your result")
            print(result)

            guidance_text = result.get("study_guide")
            
            if not guidance_text:
                return render(request, "dashboard.html", {
                    "error": "Empty response from guidance service.",
                    "course": course,
                    "courses": SubjectEntry.objects.filter(student=request.user.student),
                })

            # Save guidance to the course
            course.study_guide = guidance_text
            course.save()

            return render(request, "dashboard.html", {
                "course": course,
                "guidance": guidance_text,
                "courses": SubjectEntry.objects.filter(student=request.user.student),
            })

        except requests.exceptions.RequestException as e:
            return render(request, "dashboard.html", {
                "error": f"Failed to connect to guidance service: {str(e)}",
                "course": course,
                "courses": SubjectEntry.objects.filter(student=request.user.student),
            })

    # If not POST, redirect to dashboard
    return redirect("subject_dashboard", course_id=course.id)



@require_POST
@login_required
def delete_course(request, course_id):
    course = get_object_or_404(SubjectEntry, id=course_id, student=request.user.student)
    course.delete()
    messages.success(request, f"Deleted course: {course.subject_name}")
    return redirect("hero")



@login_required
def questionnaire_view(request):
    if request.method == 'POST':
        form = StudyPlanQuestionnaireForm(request.POST)
        if form.is_valid():
            # Save questionnaire data
            questionnaire = form.save(commit=False)
            questionnaire.user = request.user
            questionnaire.save()
            
            # Prepare data for FastAPI (all fields are required and validated)
            data = {
                'subjects': form.cleaned_data['subjects'],
                'learning_style': form.cleaned_data['learning_style'],
                'goal': form.cleaned_data['goal'],
                'hours_per_week': form.cleaned_data['hours_per_week'],
                'hours_studied': form.cleaned_data['hours_studied'],
                'sleep_hours': form.cleaned_data['sleep_hours'],
                'extracurricular': form.cleaned_data['extracurricular'],
                'question_papers_solved': form.cleaned_data['question_papers_solved'],
                'study_habits': form.cleaned_data['study_habits'],
                'previous_grades': form.cleaned_data['previous_grades'],
                'motivation_level': form.cleaned_data['motivation_level'],
            }
            
            # Send to FastAPI
            try:
                response = requests.post(f"{FASTAPI_URL}/api/study-plan", json=data)
                response.raise_for_status()
                result = response.json()
                return render(request, 'templates/study_plan.html', {
                    'study_plan': result['study_plan'],
                    'prediction': result.get('prediction')
                })
            except requests.RequestException as e:
                print(f"Error contacting FastAPI: {e}")
                form.add_error(None, f'Error contacting backend: {e}')
        return render(request, 'templates/questionnaire.html', {'form': form})
    else:
        form = StudyPlanQuestionnaireForm()
    
    return render(request, 'templates/questionnaire.html', {'form': form})

# @login_required We can use this if the form works without errors.
# def questionnaire_view(request):
#     latest_entry = SubjectEntry.objects.filter(student=request.user.student).last()
#     initial_data = {}
#     if latest_entry:
#         initial_data = {
#             'hours_studied': latest_entry.hours_studied,
#             'sleep_hours': latest_entry.sleep_hours,
#             'extracurricular': latest_entry.extracurricular,
#             'question_papers_solved': latest_entry.question_papers,
#             'previous_grades': latest_entry.previous_scores,
#             'motivation_level': latest_entry.motivation,
#             'learning_style': latest_entry.preferred_learning_style,
#         }
#     if request.method == 'POST':
#         form = StudyPlanQuestionnaireForm(request.POST)
#         if form.is_valid():
#             # ... existing logic ...
#         return render(request, 'performance/questionnaire.html', {'form': form})
#     else:
#         form = StudyPlanQuestionnaireForm(initial=initial_data)
#     return render(request, 'performance/questionnaire.html', {'form': form})
 


@login_required
def edit_course(request, course_id):
    # Store the course ID in session to indicate we're editing
    request.session['editing_course_id'] = course_id
    
    # Redirect to the wizard which will detect we're in edit mode
    return redirect('create_subject_entry')  


@login_required
def course_history_dashboard(request, course_id):
    course = get_object_or_404(SubjectEntry, id=course_id, student=request.user.student)
    
    # Get all prediction entries for this course, ordered by most recent
    prediction_entries = course.entries.all().order_by('-created_at')
    
    # Prepare data for charts with proper fallbacks
    dates = [entry.created_at.strftime('%Y-%m-%d') for entry in prediction_entries]
    scores = [float(entry.predicted_score) if entry.predicted_score else 0 for entry in prediction_entries]
    hours_studied = [float(entry.hours_studied) for entry in prediction_entries]
    
    # Convert to JSON strings for the template
    dates_json = json.dumps(dates)
    scores_json = json.dumps(scores)
    hours_json = json.dumps(hours_studied)

    return render(request, 'course_history_dashboard.html', {
        'course': course,
        'prediction_entries': prediction_entries,
        'dates': dates_json,
        'scores': scores_json,
        'hours_studied': hours_json,
        'courses': SubjectEntry.objects.filter(student=request.user.student),
        'current_page': 'history'
    })