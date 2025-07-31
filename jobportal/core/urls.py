from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('post-job/', views.post_job, name='post_job'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('jobs/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('job/<int:job_id>/applicants/', views.job_applicants, name='job_applicants'),
    path('applicant-profiles/', views.applicant_profiles, name='applicant_profiles'),
    path('view-resumes/', views.view_resumes, name='view_resumes'),
    path('manage-qualifications/', views.manage_qualifications, name='manage_qualifications'),
    path('jobs/<int:job_id>/applicants/', views.job_applicants, name='job_applicants'),
    

]
