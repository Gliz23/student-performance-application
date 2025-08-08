from django.urls import path
from . import views
from .views import SubjectWizard
from .forms import Step1Form, Step2Form, Step3Form, Step4Form, Step5Form
from .views import SubjectWizard, subject_results_view
from .views import delete_course


urlpatterns = [
    path("", views.sparkles_preview, name='home'),

    path('sparkles/', views.sparkles_preview, name='sparkles_preview'),

    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),

    path('create-subject/', SubjectWizard.as_view(
        [Step1Form, Step2Form, Step3Form, Step4Form, Step5Form]
    ), name='create_subject_entry'),   
    path('results/<int:subject_id>/', subject_results_view, name='subject_results'),
    
    # path("generate-study-plan/<int:entry_id>/", views.generate_study_plan, name="generate_study_plan"),
    path('hero/', views.hero_view, name='hero'),

    path('course/<int:course_id>/', views.subject_dashboard, name='subject_dashboard'),

    # path('charts/', views.my_charts_view, name='my_charts'),
    
    path('guidance/', views.get_guidance_view, name='get_guidance'),
    path("student_dashboard/", views.student_dashboard_view, name="student_dashboard"),
    path('delete-course/<int:course_id>/', delete_course, name='delete_course'),

    path('course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
]

