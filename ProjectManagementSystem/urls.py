"""
URL configuration for ProjectManagementSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/evaluation-member/', views.register_evaluation_member, name='register_evaluation_member'),
    path('register/coordinator/', views.register_coordinator, name='register_coordinator'),
    path('login/', views.login_view, name='login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('evaluation-panel/dashboard/', views.evaluation_panel_dashboard, name='evaluation_panel_dashboard'),
    path('coordinator/dashboard/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('coordinator/approve-group/', views.approve_group, name='approve_group'),
    path('create-group/', views.create_group, name='create_group'),
    path('approve-member/', views.approve_member, name='approve_member'),
    path('view-groups/', views.view_groups, name='view_groups'),  # Ensure this matches
    path('view-groups-students/', views.view_groups_students, name='view_groups_students'),
    path('join-group/', views.join_group, name='join_group'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('coordinator/create-announcement/', views.create_announcement, name='create_announcement'),
    path('student/announcements/', views.view_announcements, name='student_announcements'),
    path('student/upload-file/<int:announcement_id>/', views.upload_file, name='upload_file'),
    path('evaluation/view-submissions/', views.view_student_submissions, name='view_student_submissions'),
    path('coordinator/create_criteria/', views.create_evaluation_criteria, name='create_criteria'),
    path('coordinator/create_evaluation/', views.create_evaluations, name='create_evaluation'),
    path('coordinator/view_evaluations/', views.view_evaluations, name='view_evaluations'),
    path('coordinator/manage_sections/', views.manage_sections, name='manage_sections'),
    path('coordinator/create_section/', views.create_section, name='create_section'),
    path('coordinator/manage_section/<int:section_id>/', views.manage_section, name='manage_section'),
    path('coordinator/add_student_to_section/<int:section_id>/', views.add_student_to_section, name='add_student_to_section'),
    path('coordinator/delete_student_from_section/<int:student_id>/<int:section_id>/', views.delete_student_from_section, name='delete_student_from_section'),
    path('evaluation_panel/view_and_mark/', views.view_and_mark_evaluations, name='view_and_mark'),
    path('student/view_result/', views.view_result, name='view_result'),
    path('evaluation_criteria/<int:student_id>/<int:evaluation_id>/', views.evaluation_criteria, name='evaluation_criteria'),
    path('view_marks/<int:student_id>/<int:evaluation_id>/', views.view_marks, name='view_marks'),
    path('evaluation_panel/view_and_mark/<int:student_id>/<int:evaluation_id>/', views.view_and_mark_evaluation, name='view_and_mark_evaluation'),
    path('evaluation/mark_sections/', views.mark_sections, name='mark_sections'),
    path('evaluation/mark_section/<int:section_id>/', views.mark_section, name='mark_section'),
    path('evaluation/select_evaluation/<int:student_id>/', views.select_evaluation, name='select_evaluation'),
    path('evaluation/add_marks/<int:student_id>/<int:evaluation_id>/', views.add_marks, name='add_marks'),
    path('evaluation/submit_marks/<int:student_id>/<int:evaluation_id>/', views.submit_marks, name='submit_marks'),
    #path('approve-group/<int:group_id>/', views.approve_group, name='approve_group'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)