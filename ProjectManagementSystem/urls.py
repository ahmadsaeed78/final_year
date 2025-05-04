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
from django.urls import path, include
from django.conf.urls.static import static
from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('main.urls')),
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
    #path('evaluation_panel/view_and_mark/<int:student_id>/<int:evaluation_id>/', views.view_and_mark_evaluation, name='view_and_mark_evaluation'),
    path('evaluation/mark_sections/', views.mark_sections, name='mark_sections'),
    path('evaluation/mark_section/<int:section_id>/', views.mark_section, name='mark_section'),
    path('evaluation/select_evaluation/<int:student_id>/', views.select_evaluation, name='select_evaluation'),
    path('evaluation/add_marks/<int:student_id>/<int:evaluation_id>/', views.add_marks, name='add_marks'),
    path('evaluation/submit_marks/<int:student_id>/<int:evaluation_id>/', views.submit_marks, name='submit_marks'),
    #path('approve-group/<int:group_id>/', views.approve_group, name='approve_group'),
    #API
]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from main.views import (
    CustomUserViewSet, SectionViewSet, StudentMarkingViewSet, StudentFileUploadViewSet, RegistrationStatusView, login_view, toggle_registration, StudentsInSectionView, remove_student_from_section, CurrentUserView
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
#router.register(r'announcements', AnnouncementViewSet)
#router.register(r'groups', GroupViewSet)
#router.register(r'evaluations', EvaluationViewSet)
#router.register(r'evaluation-criteria', EvaluationCriteriaViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'student-markings', StudentMarkingViewSet)
router.register(r'student-submissions', StudentFileUploadViewSet)

from main.views import CreateAnnouncementAPIView, AnnouncementListView, UnapprovedGroupListView, get_evaluation_criteria, create_evaluation_criteria, EvaluationListCreateView, EvaluationDetailView
from main import views
from main.views import EvaluationListView, EvaluationCriteriaView, SubmitMarksView, EvaluationStudentMarksView, GroupAnnouncementFilesAPIView

urlpatterns += [
    path('api/', include(router.urls)),
    path("api/registration-status/", RegistrationStatusView.as_view(), name="registration_status"),
    path('api/toggle-registration/', toggle_registration, name='toggle-registration'),
    path('api/sections/<int:section_id>/students/', StudentsInSectionView.as_view(), name='students_in_section'),
    path('api/sections/<int:section_id>/students/<int:student_id>/', remove_student_from_section),
    path('api/unassigned-students/', views.unassigned_students, name='unassigned_students'),
    path('api/sections/<int:section_id>/add-student/<int:student_id>/', views.add_student_to_section, name='add_student_to_section'),
    #path("api/login/", login_view, name="login"),
    path('api/auth/user/', CurrentUserView.as_view(), name='current_user'),
    path("api/announcements/create/", CreateAnnouncementAPIView.as_view(), name="create_announcement"),
    path('api/announcements/', AnnouncementListView.as_view(), name='announcement-list'),
    path('api/groups/unapproved/', UnapprovedGroupListView.as_view(), name='unapproved-groups'),
    path('api/evaluation-criteria/', get_evaluation_criteria, name='get_evaluation_criteria'),
    path('api/evaluation-criteria-create/', create_evaluation_criteria, name='create_evaluation_criteria'),
    path('api/evaluation-criteria/<int:pk>/', views.EvaluationCriteriaDetail.as_view(), name='evaluation-criteria-detail'),
    path('api/evaluations/', EvaluationListCreateView.as_view(), name='evaluation-list-create'),
    path('api/evaluations/<int:pk>/', EvaluationDetailView.as_view(), name='evaluation-detail'),
    path('api/evaluator/evaluations/', EvaluationListView.as_view(), name='evaluation-list'),
    path('api/evaluator/evaluations/<int:evaluation_id>/criteria/', EvaluationCriteriaView.as_view(), name='evaluation-criteria'),
    path('api/evaluator/evaluations/<int:student_id>/<int:evaluation_id>/submit_marks/', SubmitMarksView.as_view(), name='submit-marks'),
    path('api/evaluator/evaluations/<int:evaluation_id>/<int:student_id>/marks/', EvaluationStudentMarksView.as_view(), name='evaluation_student_marks'),
    path('api/groups/<int:group_id>/announcement-files/', GroupAnnouncementFilesAPIView.as_view(), name='group-announcement-files'),
    # Add registration API endpoints
    path('api/register/student/', views.register_student, name='register_student'),
    path('api/register/evaluator/', views.register_evaluator, name='register_evaluator'),
    path('api/register/coordinator/', views.register_coordinator, name='register_coordinator'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)