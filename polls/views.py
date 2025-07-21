import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Student, SubjectEntry
from django.core.cache import cache
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404

from django.views.decorators.http import require_POST

import requests
import json

from .forms import Step1Form, Step2Form, Step3Form, Step4Form, Step5Form
from .models import SubjectEntry

from formtools.wizard.views import SessionWizardView
from .forms import Step1Form, Step2Form, Step3Form, Step4Form, Step5Form
 




FASTAPI_URL = 'http://127.0.0.1:8000'


def home(request):
    return render(request, 'base.html')  # This will render base.html as the home page

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Log in the user
            user = form.get_user()
            login(request, user)
            messages.success(request, "Welcome back!")
            return redirect('hero')  # Redirect to the student dashboard
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

 

class SubjectWizard(SessionWizardView):
    form_list = [Step1Form, Step2Form, Step3Form, Step4Form, Step5Form]
    template_name = "multi_form.html"


    def done(self, form_list, **kwargs):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)

        student = self.request.user.student
        
        entry = SubjectEntry.objects.create(
            student=student,
            subject_name=data.get("subject_name", "Unnamed course"),
            hours_studied=data["hours_studied"],
            previous_scores=data["previous_scores"],
            extracurricular=data["extracurricular"],
            sleep_hours=data["sleep_hours"],
            question_papers=data["question_papers"],
            motivation=data.get("motivation", "Medium"),
            preferred_learning_style=data.get("preferred_learning_style", "None"),
        )

        # 🔗 Send to FastAPI
        payload = {
            "hours_studied": entry.hours_studied,
            "previous_scores": entry.previous_scores,
            "extracurricular": entry.extracurricular,
            "sleep_hours": entry.sleep_hours,
            "question_papers": entry.question_papers,
        }

        try:
            response = requests.post("http://127.0.0.1:8000/predict", json=payload)
            response.raise_for_status()  # Raise an error for bad responses
            result = response.json()

            # Log the result to see what is being returned
            print("FastAPI Response:", result)
            print("Sending Payload:", payload)
            entry.predicted_score = result.get('predicted_score')
            entry.study_plan = result.get('study_plan')
            entry.save()
        except Exception as e:
            print("FastAPI prediction failed:", e)
         
        return redirect('subject_results', subject_id=entry.id)
    
    def post(self, request, *args, **kwargs):
        print(f"Current Step: {self.steps.current}")  # Current wizard step
        form = self.get_form()
        print("Form errors:", form.errors)  # Print actual validation errors
        return super().post(request, *args, **kwargs)

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

FASTAPI_PREDICTION_URL = 'http://127.0.0.1:8000/predict-score'

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
    })


@login_required
def student_dashboard_view(request):
    return render(request, 'dashboard.html')   

@login_required



def get_guidance_view(request):
    if request.method == "POST":
        subject_name = request.POST.get("subject_name")

        if not subject_name:
            return render(request, "get_guidance.html", {
                "error": "No course name (ID) provided."
            })
        
        # entry = get_object_or_404(SubjectEntry, id=subject_name, student=request.user.student)

        # try:
        #     student = Student.objects.filter(user=request.user).first()
        #     subject = SubjectEntry.objects.filter(subject_name=subject_name, student=student).first()
        # except SubjectEntry.DoesNotExist:
        #     return render(request, "get_guidance.html", {
        #         "error": f"No course found with name '{subject_name}'."
        #     })


        # Get current student
        student = Student.objects.filter(user=request.user).first()

        # Fetch the subject entry using subject_name
        subject = SubjectEntry.objects.filter(subject_name=subject_name, student=student).first()

        if not subject:
            return render(request, "get_guidance.html", {
                "error": f"No course found with subject name '{subject_name}'."
            })
        

        # Prepare payload for FastAPI
        payload = {
            "msg": "generate_guidance",
            "user_id": str(subject.subject_name),
            "predicted_score": subject.predicted_score,
            "study_hours": subject.hours_studied,
            "motivation_level": str(subject.motivation),
            "preferred_learning_style": str(subject.preferred_learning_style),  
        }

        print("Sending to FastAPI:", json.dumps(payload, indent=2))

        try:
            response = requests.post("http://127.0.0.1:8000/chatbot-advice", json=payload)
            response.raise_for_status()
            result = response.json()


            guidance_text = result.get("response")
            # print(guidance_text)
            # print("Response:", response.status_code, response.text)

            if guidance_text:
                subject.chatbot_guidance = guidance_text
                subject.save()

                # print("Context sent to template:", {"subject": subject.subject_name, "guidance": guidance_text})
                
                return render(request, "get_guidance.html", {
                    "subject": subject,
                    "guidance": guidance_text,
                    })
            else: 
                return render(request, "get_guidance.html", {
                    "subject": subject,
                    "error": "No guidance was returned from the system."
            })

        except requests.RequestException as e:
            return render(request, "get_guidance.html", {
                "error": f"Failed to get guidance: {e}"
            })

    return redirect("hero")  


@require_POST
@login_required
def delete_course(request, course_id):
    course = get_object_or_404(SubjectEntry, id=course_id, student=request.user.student)
    course.delete()
    messages.success(request, f"Deleted course: {course.subject_name}")
    return redirect("hero")


