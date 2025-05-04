from django.urls import path
from .views import LoginAPIView
from rest_framework.authtoken.views import obtain_auth_token
from .views import get_approved_groups, approve_group, UnapprovedGroupListView, GetEvaluationsAPIView
from . import views
from .views import StudentEvaluationResultsView

urlpatterns = [
    # Your other URLs
    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path("groups/approved/", get_approved_groups, name="get_approved_groups"),
    #path("groups/unapproved/", get_unapproved_groups, name="get_unapproved_groups"),
    path("groups/<int:pk>/approve/", approve_group, name="approve_group"),
    path('student-group/', views.fetch_student_group, name='fetch_student_group'),
    path('approved-groups/', views.fetch_approved_groups, name='fetch_approved_groups'),
    path('create-group/', views.create_group, name='create_group'),
    path('join-group/', views.join_group, name='join_group'),
    path("student/announcements/", views.get_announcements, name="get_announcements"),
    path(
        "announcements/<int:announcement_id>/upload-file/",
        views.upload_announcement_file,
        name="upload_announcement_file",
    ),
    path('groups/', views.get_groups, name='get_groups'),  # URL for fetching groups
    #path('edit-marks/<int:group_id>/<int:student_id>/', views.edit_marks, name='edit_marks'),
    path('get-evaluations/<int:student_id>/', GetEvaluationsAPIView.as_view() , name='get_evaluations'),
    path(
      'student/evaluation-results/',
      StudentEvaluationResultsView.as_view(),
      name='student-evaluation-results'
    ),
    path('api/register/student/', views.register_student, name='register_student'),
    path('api/register/evaluator/', views.register_evaluator, name='register_evaluator'),
    path('api/register/coordinator/', views.register_coordinator, name='register_coordinator'),
]
