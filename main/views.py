from django.shortcuts import render
from main.models import Group
# Create your views here.

# views.py


# views.py
from django.shortcuts import render

def home(request):
    settings, _ = Settings.objects.get_or_create(id=1)
    context = {
        'student_registration_open': settings.student_registration_open,
        'evaluation_registration_open': settings.evaluation_registration_open,
        'coordinator_registration_open': settings.coordinator_registration_open
    }
    return render(request, 'home.html', context)


from .decorators import student_required, coordinator_required, evaluation_panel_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Group, CustomUser
from django.contrib import messages

# Student Dashboard
@student_required
def student_dashboard(request):
    user = request.user
    # Assuming `Group` model has a `members` field for the students in a group
    is_in_group = Group.objects.filter(members=user).exists()
    disable_group_options = is_in_group
    
    return render(request, 'student_dashboard.html', {'disable_group_options': disable_group_options})
# Create Group
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from .models import Group

User = get_user_model()
@student_required
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        group = Group.objects.create(name=group_name)
        # Make sure to cast request.user to the CustomUser model if needed
        custom_user = User.objects.get(id=request.user.id)  # Get the actual user instance
        group.members.add(custom_user)  # Add the user to the group
        return redirect('student_dashboard')  # Redirect as needed

    return render(request, 'create_group.html')  # Render your group creation form

# Join Group
@student_required
def join_group(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group = Group.objects.get(id=group_id)
        
        # Check if the group already has 3 members
        if group.members.count() < 3:
            group.members.add(request.user)  # Add the user to the group
            messages.success(request, f'You have successfully joined the group: {group.name}')
        else:
            messages.error(request, 'This group is already full.')
        
        return redirect('student_dashboard')  # Redirect to dashboard after action

    groups = Group.objects.all()
    return render(request, 'join_group.html', {'groups': groups})

from .models import StudentFileUpload, Announcement
@student_required
def upload_file(request, announcement_id):
    announcement = Announcement.objects.get(id=announcement_id)
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        StudentFileUpload.objects.create(announcement=announcement, student=request.user, file=file)
        messages.success(request, "File uploaded successfully.")
        return redirect('student_dashboard')
    return render(request, 'upload_file.html', {'announcement': announcement})

@student_required
def view_announcements(request):
    announcements = Announcement.objects.all()
    uploaded_files = {file.announcement_id: True for file in StudentFileUpload.objects.filter(student=request.user)}
    return render(request, 'student_announcements.html', {
        'announcements': announcements,
        'uploaded_files': uploaded_files
    })

from django.db.models import Avg
from collections import defaultdict

@student_required
def view_result(request):
    # Grouping marks by evaluation and criterion, calculating the average
    results = (
        StudentMarking.objects.filter(student=request.user)
        .values('evaluation__name', 'criterion__name', 'criterion__marks')
        .annotate(aggregate_marks=Avg('marks_obtained'))
    )

    # Grouping results by evaluation
    grouped_results = defaultdict(list)
    for result in results:
        evaluation_name = result['evaluation__name']
        grouped_results[evaluation_name].append({
            'criterion': result['criterion__name'],
            'aggregate_marks': result['aggregate_marks'],
            'max_marks': result['criterion__marks']
        })

    # Convert defaultdict to a regular dictionary for template usage
    grouped_results = dict(grouped_results)

    return render(request, 'view_result.html', {'grouped_results': grouped_results})

# views.py
from .models import Settings
# Coordinator Dashboard
@coordinator_required
def coordinator_dashboard(request):
    settings, _ = Settings.objects.get_or_create(id=1)
    if request.method == 'POST':
        if 'toggle_student' in request.POST:
            settings.student_registration_open = not settings.student_registration_open
        elif 'toggle_evaluation' in request.POST:
            settings.evaluation_registration_open = not settings.evaluation_registration_open
        elif 'toggle_coordinator' in request.POST:
            settings.coordinator_registration_open = not settings.coordinator_registration_open
        settings.save()
        return redirect('coordinator_dashboard')
    #return render(request, 'coordinator_dashboard.html')
    context = {
        'settings': settings,
    }
    return render(request, 'coordinator_dashboard.html', context)

# Approve Group
'''
@login_required
def approve_group(request, group_id):
    group = Group.objects.get(id=group_id)
    if group:
        group.is_approved = True
        group.save()
        messages.success(request, f'Group {group.name} approved!')
    else:
        messages.error(request, 'Group not found.')
    return redirect('coordinator_dashboard')
'''

# in main/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Group  # assuming you have a Group model
@coordinator_required
def approve_group(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group = get_object_or_404(Group, id=group_id)
        group.is_approved = True  # assuming there's an `is_approved` field
        group.save()
        return redirect('approve_group')
    
    # Get all unapproved groups
    unapproved_groups = Group.objects.filter(is_approved=False)
    return render(request, 'approve_group.html', {'groups': unapproved_groups})


# Manage Group Members
@coordinator_required
def manage_group_members(request, group_id):
    group = Group.objects.get(id=group_id)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        group.members.remove(user)
        messages.success(request, f'Member removed from the group: {group.name}')
    members = group.members.all()
    return render(request, 'manage_group_members.html', {'group': group, 'members': members})


from .models import Announcement
@coordinator_required
def create_announcement(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        coordinator = request.user
        Announcement.objects.create(title=title, description=description, coordinator=coordinator)
        messages.success(request, "Announcement created successfully.")
        return redirect('coordinator_dashboard')
    return render(request, 'create_announcement.html')

from .forms import EvaluationCriteriaForm
@coordinator_required
def create_evaluation_criteria(request):
    if request.method == 'POST':
        form = EvaluationCriteriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('coordinator_dashboard')
    else:
        form = EvaluationCriteriaForm()
    return render(request, 'create_evaluation_criteria.html', {'form': form})


from .forms import EvaluationForm
@coordinator_required
def create_evaluations(request):
    if request.method == "POST":
        evaluation_name = request.POST.get("evaluation_name")
        selected_criteria_ids = request.POST.getlist("criteria")
        
        # Create the new evaluation
        evaluation = Evaluation.objects.create(name=evaluation_name)
        
        # Add the selected criteria to the evaluation
        for criterion_id in selected_criteria_ids:
            criterion = EvaluationCriteria.objects.get(id=criterion_id)
            evaluation.criteria.add(criterion)
        
        return redirect("coordinator_dashboard")  # Redirect after creation
    
    # For GET requests, show the form
    criteria = EvaluationCriteria.objects.all()
    return render(request, "create_evaluation.html", {"criteria": criteria})

from .models import Evaluation, EvaluationCriteria
@coordinator_required
def view_evaluations(request):
    evaluations = Evaluation.objects.all()
    criteria = EvaluationCriteria.objects.all()
    return render(request, 'view_evaluations.html', {'evaluations': evaluations, 'criteria': criteria})

from .forms import SectionForm
from .models import Section

@coordinator_required
def manage_sections(request):
    sections = Section.objects.all()
    return render(request, 'manage_sections.html', {'sections': sections })

@coordinator_required
def manage_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    students_in_section = CustomUser.objects.filter(section=section, user_type='student')
    students_without_section = CustomUser.objects.filter(section__isnull=True, user_type='student')
    groups = Group.objects.filter(is_approved = True)
    return render(request, 'manage_section.html', {
        'section': section,
        'students_in_section': students_in_section,
        'students_without_section': students_without_section,
        'groups' : groups
    })
@coordinator_required
def delete_student_from_section(request, student_id, section_id):
    student = get_object_or_404(CustomUser, id=student_id, user_type='student')
    section = get_object_or_404(Section, id=section_id)
    
    # Remove the student from the section
    if student.section == section:
        student.section = None
        student.save()
        messages.success(request, f"{student.first_name} {student.last_name} has been removed from section {section.name}.")
    else:
        messages.error(request, f"{student.name} is not in section {section.name}.")

    return redirect('manage_section', section_id=section.id)
@coordinator_required
def add_student_to_section(request, section_id):
    # Fetch the section or return a 404 if not found
    section = get_object_or_404(Section, id=section_id)
    
    # Query for students who are not assigned to any section
    unassigned_students = CustomUser.objects.filter(user_type='student', section__isnull=True)

    if request.method == 'POST':
        # Get the selected student ID from the form submission
        student_id = request.POST.get('student_id')
        
        # Retrieve the selected student and assign them to the section
        student = get_object_or_404(CustomUser, id=student_id, user_type='student')
        student.section = section
        student.save()
        
        # Provide feedback to the user
        messages.success(request, f"{student.first_name} {student.last_name} has been added to section {section.name}.")
        
        # Redirect to the manage section page after successful addition
        return redirect('manage_section', section_id=section.id)
    
    # Render the template with the unassigned students for selection
    return render(request, 'add_student_to_section.html', {
        'section': section,
        'unassigned_students': unassigned_students
    })


@coordinator_required
def create_section(request):
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_sections')
    else:
        form = SectionForm()
    return render(request, 'create_section.html', {'form': form})


# views.py

# Evaluation Panel Dashboard
@evaluation_panel_required
def evaluation_panel_dashboard(request):
    return render(request, 'evaluation_panel_dashboard.html')

# View Groups and Students
@evaluation_panel_required
def view_groups_students(request):
    groups = Group.objects.filter(is_approved=True)
    return render(request, 'view_groups_students.html', {'groups': groups})


@evaluation_panel_required
def view_student_submissions(request):
    submissions = StudentFileUpload.objects.select_related('student', 'announcement').all()
    return render(request, 'evaluation_panel_submissions.html', {'submissions': submissions})

from .models import StudentMarking
'''
@evaluation_panel_required
def view_and_mark_evaluations(request):
    evaluations = Evaluation.objects.all()
    students = CustomUser.objects.filter(user_type='student')
    criteria = EvaluationCriteria.objects.all()
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        evaluation_id = request.POST.get('evaluation_id')
        criteria_marks = request.POST.getlist('criteria_marks')

        for criterion_id, marks in criteria_marks:
            StudentMarking.objects.create(
                student_id=student_id,
                evaluation_id=evaluation_id,
                criterion_id=criterion_id,
                marks_obtained=marks
            )
        return redirect('evaluation_panel_dashboard')
    return render(request, 'view_and_mark_evaluations.html', {'evaluations': evaluations, 'students': students, 'criteria':criteria})
'''

from django.shortcuts import render, get_object_or_404, redirect
from .models import Evaluation, EvaluationCriteria, StudentMarking
@evaluation_panel_required
def view_and_mark_evaluations(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        evaluation_id = request.POST.get('evaluation_id')

        # Get the selected student and evaluation
        student = get_object_or_404(CustomUser, id=student_id)
        evaluation = get_object_or_404(Evaluation, id=evaluation_id)

        # Redirect to the page where criteria are shown
        return redirect('evaluation_criteria', student_id=student.id, evaluation_id=evaluation.id)
    
    evaluations = Evaluation.objects.all()
    students = CustomUser.objects.filter(user_type='student')
    return render(request, 'view_and_mark_evaluations.html', {'evaluations': evaluations, 'students': students})

@evaluation_panel_required
def evaluation_criteria(request, student_id, evaluation_id):
    student = get_object_or_404(CustomUser, id=student_id, user_type='student')
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    evaluator = request.user

    # Fetch the evaluation criteria for the selected evaluation
    criteria = EvaluationCriteria.objects.filter(evaluation=evaluation)

    if request.method == 'POST':
        for criterion in criteria:
            marks_obtained = request.POST.get(f'criteria_marks_{criterion.id}')
            if marks_obtained:
                marks_obtained = int(marks_obtained)  # Ensure integer conversion
                # Check for existing mark entry
                existing_mark = StudentMarking.objects.filter(
                    student=student,
                    evaluation=evaluation,
                    criterion=criterion,
                    evaluator=evaluator
                ).first()

                if existing_mark:
                    # Update the existing mark
                    existing_mark.marks_obtained = marks_obtained
                    existing_mark.save()
                    messages.success(request, f"Updated marks for {student.username} - {criterion.name}.")
                else:
                    # Create a new mark entry
                    StudentMarking.objects.create(
                        student=student,
                        evaluation=evaluation,
                        criterion=criterion,
                        marks_obtained=marks_obtained,
                        evaluator=evaluator
                    )
                    messages.success(request, f"Marks added for {student.username} - {criterion.name}.")
        return redirect('view_and_mark')

    # Prepare marks data for display (if needed for the template)
    existing_marks = {
        mark.criterion.id: mark.marks_obtained for mark in
        StudentMarking.objects.filter(student=student, evaluation=evaluation, evaluator=evaluator)
    }

    return render(request, 'evaluation_criteria.html', {
        'student': student,
        'evaluation': evaluation,
        'criteria': criteria,
        'existing_marks': existing_marks
    })

'''
@evaluation_panel_required
def view_and_mark_evaluation(request, student_id, evaluation_id):
    # Get the evaluation and student objects
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    student = get_object_or_404(CustomUser, id=student_id, user_type='student')

    # Get the criteria for the selected evaluation
    criteria = EvaluationCriteria.objects.filter(evaluation=evaluation)

    # Check if the student has already been marked for this evaluation
    existing_marks = StudentMarking.objects.filter(student=student, evaluation=evaluation)

    if existing_marks.exists():
        return render(request, 'evaluation_panel/view_and_mark.html', {
            'evaluation': evaluation,
            'student': student,
            'criteria': criteria,
            'marks': existing_marks.first(),
            'already_marked': True
        })

    # If the form is submitted
    if request.method == 'POST':
        for criterion in criteria:
            marks_obtained = request.POST.get(f'criterion_{criterion.id}')
            if marks_obtained:
                # Save the marks for this criterion
                StudentMarking.objects.create(
                    student=student,
                    evaluation=evaluation,
                    criterion=criterion,
                    marks_obtained=marks_obtained
                )

        return redirect('view_and_mark_evaluations', student_id=student.id, evaluation_id=evaluation.id)

    return render(request, 'evaluation_panel/view_and_mark.html', {
        'evaluation': evaluation,
        'student': student,
        'criteria': criteria
    })
    '''
@evaluation_panel_required
def view_marks(request, student_id, evaluation_id):
    # Get the selected student and evaluation
    student = get_object_or_404(CustomUser, id=student_id)
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)

    # Fetch the student marks for the selected evaluation
    student_marks = StudentMarking.objects.filter(student=student, evaluation=evaluation)

    return render(request, 'view_marks.html', {
        'student': student,
        'evaluation': evaluation,
        'student_marks': student_marks
    })


@evaluation_panel_required
def mark_sections(request):
    sections = Section.objects.all()
    return render(request, 'mark_sections.html', {'sections': sections})

from django.db.models import Avg

@evaluation_panel_required
def mark_section(request, section_id):
    section = Section.objects.get(id=section_id)
    students = CustomUser.objects.filter(section=section)
    
    # Dictionary to hold total marks for each student
    student_totals = {}

    for student in students:
        # Get average marks for each criterion and evaluation
        marks = (
            StudentMarking.objects.filter(student=student)
            .values('evaluation__name', 'criterion__name', 'criterion__marks')
            .annotate(avg_marks=Avg('marks_obtained'))
        )
        
        # Calculate the total marks as the sum of averages
        total_marks = sum(
            min(mark['avg_marks'], mark['criterion__marks'])  # Ensure marks do not exceed the max for the criterion
            for mark in marks
        )
        student_totals[student.id] = total_marks

    return render(
        request,
        'mark_section.html',
        {
            'section': section,
            'students': students,
            'student_totals': student_totals,
        }
    )


@evaluation_panel_required
def select_evaluation(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id)
    evaluations = Evaluation.objects.all()
    return render(request, 'select_evaluation.html', {'student': student, 'evaluations': evaluations})

@evaluation_panel_required
def add_marks(request, student_id, evaluation_id):
    student = get_object_or_404(CustomUser, id=student_id)
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    criteria = EvaluationCriteria.objects.filter(evaluation=evaluation)
    evaluator = request.user  # Assumes the evaluator is the logged-in user
    # Fetch existing marks for display in the template
    existing_marks = {
        mark.criterion.id: mark.marks_obtained for mark in
        StudentMarking.objects.filter(student=student, evaluation=evaluation, evaluator=evaluator)
    }

    # Render the form for marks entry
    return render(request, 'add_marks.html', {
        'student': student,
        'evaluation': evaluation,
        'criteria': criteria,
        'existing_marks': existing_marks
    })


@evaluation_panel_required
def submit_marks(request, student_id, evaluation_id):
    # Get the student and evaluation objects
    student = get_object_or_404(CustomUser, id=student_id, user_type='student')
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    evaluator = request.user  # Assumes the evaluator is the logged-in user

    # Fetch evaluation criteria for the selected evaluation
    criteria = EvaluationCriteria.objects.filter(evaluation=evaluation)

    if request.method == "POST":
        for criterion in criteria:
            # Retrieve marks obtained from the form input
            marks_obtained = request.POST.get(f'criteria_marks_{criterion.id}')
            if marks_obtained:
                marks_obtained = int(marks_obtained)  # Convert input to integer

                # Check if a mark entry already exists
                existing_mark = StudentMarking.objects.filter(
                    student=student,
                    evaluation=evaluation,
                    criterion=criterion,
                    evaluator=evaluator
                ).first()

                if existing_mark:
                    # Update the existing mark
                    existing_mark.marks_obtained = marks_obtained
                    existing_mark.save()
                    messages.success(
                        request, f"Updated marks for {student.username} - {criterion.name}."
                    )
                else:
                    # Create a new mark entry
                    StudentMarking.objects.create(
                        student=student,
                        evaluation=evaluation,
                        criterion=criterion,
                        marks_obtained=marks_obtained,
                        evaluator=evaluator
                    )
                    messages.success(
                        request, f"Marks added for {student.username} - {criterion.name}."
                    )

        # Redirect to a page (e.g., Mark Section) after processing marks
        return redirect('mark_section', section_id=student.section.id)

    # Fetch existing marks for display in the template
    existing_marks = {
        mark.criterion.id: mark.marks_obtained for mark in
        StudentMarking.objects.filter(student=student, evaluation=evaluation, evaluator=evaluator)
    }

    # Render the form for marks entry
    return render(request, 'add_marks.html', {
        'student': student,
        'evaluation': evaluation,
        'criteria': criteria,
        'existing_marks': existing_marks
    })


# views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import StudentRegistrationForm, EvaluationPanelRegistrationForm, CoordinatorRegistrationForm

# Student Registration View
def register_student(request):
    settings, _ = Settings.objects.get_or_create(id=1)
    if not settings.student_registration_open:
        messages.error(request, "Student registration is currently closed.")
        return redirect('home')  # Redirect to home or any other page
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student registered successfully! Please log in.')
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'register_student.html', {'form': form})


# Evaluation Panel Registration View
def register_evaluation_member(request):
    settings, _ = Settings.objects.get_or_create(id=1)
    if not settings.evaluation_registration_open:
        messages.error(request, "Evaluation Panel registration is currently closed.")
        return redirect('home')  # Redirect to home or any other page
    if request.method == 'POST':
        form = EvaluationPanelRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evaluation panel member registered successfully! Please log in.')
            return redirect('login')
    else:
        form = EvaluationPanelRegistrationForm()
    return render(request, 'register_evaluation_member.html', {'form': form})


# Coordinator Registration View
def register_coordinator(request):
    settings, _ = Settings.objects.get_or_create(id=1)
    if not settings.coordinator_registration_open:
        messages.error(request, "Coordinator registration is currently closed.")
        return redirect('home')  # Redirect to home or any other page
    if request.method == 'POST':
        form = CoordinatorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coordinator registered successfully! Please log in.')
            return redirect('login')
    else:
        form = CoordinatorRegistrationForm()
    return render(request, 'register_coordinator.html', {'form': form})


# views.py

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

# Login View
'''
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on user type
            if user.user_type == 'student':
                return redirect('student_dashboard')
            elif user.user_type == 'evaluation_member':
                return redirect('evaluation_panel_dashboard')
            elif user.user_type == 'coordinator':
                return redirect('coordinator_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')
'''
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # If authentication is successful, log the user in
            login(request, user)
            # Redirect to a homepage or dashboard after login
            if user.user_type == 'student':
                return redirect('student_dashboard')
            elif user.user_type == 'evaluation_member':
                return redirect('evaluation_panel_dashboard')
            elif user.user_type == 'coordinator':
                return redirect('coordinator_dashboard')
        else:
            # If authentication fails, show an error message
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')



'''
def login_view(request):
    # Login logic
    return render(request, 'login.html')

def register_view(request):
    # Registration logic
    return render(request, 'register.html')
'''
    

'''
def student_dashboard(request):
    # Logic to display student data
    return render(request, 'student_dashboard.html')
'''

'''
def coordinator_dashboard(request):
    # Coordinator-specific data, such as list of groups, etc.
    return render(request, 'coordinator_dashboard.html')
'''
'''
def evaluator_dashboard(request):
    # Show assigned groups for evaluation, documents, etc.
    return render(request, 'evaluator_dashboard.html')
'''
'''
def create_group(request):
    # Logic for creating group
    return render(request, 'create_group.html')
'''
def upload_document(request):
    # Logic for uploading a document
    return render(request, 'upload_document.html')


def create_evaluation(request):
    # Logic for creating evaluations
    return render(request, 'create_evaluation.html')


def approve_member(request):
    # Your code for approving members
    return render(request, 'approve_member.html')


def view_groups(request):
    # Fetch all groups to display
    groups = Group.objects.all()
    return render(request, 'view_groups.html', {'groups': groups})





#below are APIS

from rest_framework import viewsets, permissions
from .models import CustomUser, Announcement, Group, Evaluation, EvaluationCriteria, Section, StudentMarking, StudentFileUpload
from .serializers import (
    CustomUserSerializer, AnnouncementSerializer, GroupSerializer, EvaluationSerializer, 
    EvaluationCriteriaSerializer, SectionSerializer, StudentMarkingSerializer, StudentFileUploadSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class LoginAPIView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"detail": "Username and password are required."}, status=400)

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is not None:
            # Generate token
            #login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access_token': str(refresh.access_token),
                'role': user.user_type,
            })
        else:
            return Response({"detail": "Invalid credentials."}, status=401)




class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user_type = self.request.data.get('user_type', 'student')
        serializer.save(user_type=user_type)
'''
class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_announcements(self, request):
        announcements = self.queryset.all()
        serializer = self.get_serializer(announcements, many=True)
        return Response(serializer.data)

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]



class EvaluationCriteriaViewSet(viewsets.ModelViewSet):
    queryset = EvaluationCriteria.objects.all()
    serializer_class = EvaluationCriteriaSerializer
    permission_classes = [permissions.IsAuthenticated]

class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def get_criteria(self, request, pk=None):
        evaluation = self.get_object()
        criteria = EvaluationCriteria.objects.filter(evaluation=evaluation)
        serializer = EvaluationCriteriaSerializer(criteria, many=True)
        return Response(serializer.data)
'''

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]

class StudentMarkingViewSet(viewsets.ModelViewSet):
    queryset = StudentMarking.objects.all()
    serializer_class = StudentMarkingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def get_marks(self, request, pk=None):
        student_markings = StudentMarking.objects.filter(student=pk)
        serializer = StudentMarkingSerializer(student_markings, many=True)
        return Response(serializer.data)

class StudentFileUploadViewSet(viewsets.ModelViewSet):
    queryset = StudentFileUpload.objects.all()
    serializer_class = StudentFileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def get_submissions(self, request, pk=None):
        student_file_uploads = StudentFileUpload.objects.filter(student=pk)
        serializer = StudentFileUploadSerializer(student_file_uploads, many=True)
        return Response(serializer.data)


from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

class RegistrationStatusView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access this endpoint

    def get(self, request, *args, **kwargs):
        settings = Settings.objects.first()
        if not settings:
            return Response(
                {
                    "student_registration_open": False,
                    "evaluation_registration_open": False,
                    "coordinator_registration_open": False,
                }
            )

        return Response(
            {
                "student_registration_open": settings.student_registration_open,
                "evaluation_registration_open": settings.evaluation_registration_open,
                "coordinator_registration_open": settings.coordinator_registration_open,
            }
        )


'''
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Assume `user.role` contains the role (e.g., "student", "coordinator", "evaluation")
            role = getattr(user, "user_type", "unknown")  # Replace with actual logic for role assignment
            return JsonResponse({"message": "Login successful", "role": role}, status=200)
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

'''
'''
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Settings

@api_view(['POST'])
def toggle_registration(request):
    """
    Toggle the registration status for student, coordinator, or evaluation panel.
    """
    type_mapping = {
        'student': 'student_registration_open',
        'evaluation': 'evaluation_registration_open',
        'coordinator': 'coordinator_registration_open',
    }
    
    data = request.data
    reg_type = data.get('type')
    
    if reg_type not in type_mapping:
        return Response(
            {"error": "Invalid registration type"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get the settings object (assuming there's only one settings row)
    settings, created = Settings.objects.get_or_create(id=1)  # Default ID for single-row settings
    
    # Toggle the corresponding field
    field_name = type_mapping[reg_type]
    current_status = getattr(settings, field_name, False)
    new_status = not current_status
    setattr(settings, field_name, new_status)
    settings.save()
    
    return Response(
        {"registration_state": new_status},
        status=status.HTTP_200_OK
    )
'''

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_registration(request):
    reg_type = request.data.get('type')
    settings = Settings.objects.first()

    if not settings:
        settings = Settings.objects.create()

    if reg_type == 'student_registration_open':
        settings.student_registration_open = not settings.student_registration_open
    elif reg_type == 'evaluation_registration_open':
        settings.evaluation_registration_open = not settings.evaluation_registration_open
    elif reg_type == 'coordinator_registration_open':
        settings.coordinator_registration_open = not settings.coordinator_registration_open

    settings.save()
    return Response({reg_type: getattr(settings, reg_type)})



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from .models import Section, CustomUser
from .serializers import CustomUserSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from .models import Section, CustomUser
from .serializers import CustomUserSerializer

class StudentsInSectionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        try:
            section = Section.objects.get(id=section_id)
        except Section.DoesNotExist:
            raise NotFound({"error": "Section not found."})

        # Fetch students in the section
        students = CustomUser.objects.filter(section=section, user_type='student')
        serializer = CustomUserSerializer(students, many=True)
        return Response(serializer.data)

from rest_framework import status

@api_view(['DELETE'])
def remove_student_from_section(request, section_id, student_id):
    try:
        section = Section.objects.get(id=section_id)
        student = CustomUser.objects.get(id=student_id, section=section)
        student.section = None  # Or perform any required logic
        student.save()
        return Response({"detail": "Student removed from section"}, status=status.HTTP_204_NO_CONTENT)
    except Section.DoesNotExist:
        return Response({"detail": "Section not found"}, status=status.HTTP_404_NOT_FOUND)
    except CustomUser.DoesNotExist:
        return Response({"detail": "Student not found in section"}, status=status.HTTP_404_NOT_FOUND)


# views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Section
from .serializers import CustomUserSerializer

@api_view(['GET'])
def unassigned_students(request):
    # Get students that are not assigned to this section
    unassigned_students = CustomUser.objects.filter(user_type='student', section_id=None)

    # Serialize and return the list of unassigned students
    serializer = CustomUserSerializer(unassigned_students, many=True)
    return Response(serializer.data)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Section
import json

@csrf_exempt
def add_student_to_section(request, section_id, student_id):
    if request.method == 'POST':
        try:
            # Fetch the section and student
            section = get_object_or_404(Section, id=section_id)
            student = get_object_or_404(CustomUser, id=student_id)

            # Check if the student is already in a section
            if student.section is not None:
                return JsonResponse(
                    {"error": "Student is already assigned to a section."},
                    status=400
                )

            # Assign the student to the section
            student.section = section
            student.save()

            return JsonResponse(
                {"message": "Student added successfully."},
                status=200
            )

        except Exception as e:
            return JsonResponse(
                {"error": f"An error occurred: {str(e)}"},
                status=500
            )

    return JsonResponse({"error": "Invalid request method."}, status=405)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.user_type
        })



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Announcement

class CreateAnnouncementAPIView(APIView):
    """
    Handle creation of announcements using POST method.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        title = request.data.get("title")
        description = request.data.get("description")
        coordinator = request.user  # Ensure the user is authenticated

        if not title or not description:
            return Response({"error": "Title and description are required."}, status=400)

        # Save the announcement
        Announcement.objects.create(
            title=title, description=description, coordinator=coordinator
        )
        return Response({"message": "Announcement created successfully!"}, status=201)


from rest_framework.permissions import IsAuthenticated

class AnnouncementListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        announcements = Announcement.objects.all().order_by('-created_at')
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_approved_groups(request):
    groups = Group.objects.filter(is_approved=True).prefetch_related('members')
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Group
from .serializers import GroupSerializer

class UnapprovedGroupListView(APIView):
    permission_classes = [IsAuthenticated]  # Ensures only authenticated users can access

    def get(self, request):
        # Query for unapproved groups
        groups = Group.objects.filter(is_approved=False)
        serializer = GroupSerializer(groups, many=True)  # Serialize the data
        return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
def approve_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    group.is_approved = True
    group.save()
    return Response({"success": f"Group '{group.name}' approved!"})



from .serializers import EvaluationCriteriaSerializer

@api_view(['GET'])
def get_evaluation_criteria(request):
    criteria = EvaluationCriteria.objects.all()
    serializer = EvaluationCriteriaSerializer(criteria, many=True)
    return Response(serializer.data)


# views.py
from .serializers import EvaluationCriteriaSerializer

@api_view(['POST'])
def create_evaluation_criteria(request):
    """
    Create a new evaluation criterion.
    """
    if request.method == 'POST':
        serializer = EvaluationCriteriaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new evaluation criteria
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import generics
from main.models import EvaluationCriteria
from main.serializers import EvaluationCriteriaSerializer

class EvaluationCriteriaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = EvaluationCriteria.objects.all()
    serializer_class = EvaluationCriteriaSerializer




from rest_framework import generics
from .models import Evaluation
from .serializers import EvaluationSerializer, EvaluationCreateSerializer

class EvaluationListCreateView(generics.ListCreateAPIView):
    queryset = Evaluation.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EvaluationCreateSerializer
        return EvaluationSerializer

class EvaluationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer


#student module group func

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Group
from .serializers import GroupSerializer
from django.contrib.auth.models import User

# Fetch logged-in student's group
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_student_group(request):
    user = request.user
    group = Group.objects.filter(members=user).first()
    if group:
        serializer = GroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"detail": "No group found for the student."}, status=status.HTTP_404_NOT_FOUND)

# List all approved groups
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_approved_groups(request):
    groups = Group.objects.filter(is_approved=True)
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Create a new group
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    user = request.user
    group_name = request.data.get('group_name')
    if not group_name:
        return Response({"error": "Group name is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Ensure user is not part of any existing group
    if Group.objects.filter(members=user).exists():
        return Response({"error": "You are already part of a group."}, status=status.HTTP_400_BAD_REQUEST)

    group = Group.objects.create(name=group_name, is_approved=False)
    group.members.add(user)  # Add the logged-in user to the group
    serializer = GroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# Join an existing group
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group(request):
    user = request.user
    group_id = request.data.get('group_id')
    if not group_id:
        return Response({"error": "Group ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({"error": "Group not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if the group is approved and not full
    if not group.is_approved:
        return Response({"error": "Cannot join a group that is not approved."}, status=status.HTTP_400_BAD_REQUEST)
    if group.members.count() >= 3:
        return Response({"error": "Group is already full."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Ensure user is not part of any other group
    if Group.objects.filter(members=user).exists():
        return Response({"error": "You are already part of a group."}, status=status.HTTP_400_BAD_REQUEST)

    group.members.add(user)
    serializer = GroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Announcement, StudentFileUpload
from .serializers import AnnouncementSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.db.models import Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_announcements(request):
    announcements = Announcement.objects.all()
    user = request.user
    group = Group.objects.filter(members=user).first()

    uploaded_files = {}

    if group:
        # Get all members of the group
        group_members = group.members.all()

        # Check if any group member has uploaded files for the announcements
        group_uploaded_files = StudentFileUpload.objects.filter(
            student__in=group_members
        ).select_related('announcement', 'student')

        # Populate the uploaded_files dictionary with the announcement and file link
        uploaded_files = {
            file.announcement.id: request.build_absolute_uri(file.file.url)
            for file in group_uploaded_files
        }

    # Serialize announcements
    serialized_announcements = AnnouncementSerializer(announcements, many=True).data

    return Response({"announcements": serialized_announcements, "uploaded_files": uploaded_files})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_announcement_file(request, announcement_id):
    try:
        announcement = Announcement.objects.get(id=announcement_id)
        if request.method == "POST" and request.FILES.get("file"):
            file = request.FILES["file"]
            StudentFileUpload.objects.create(
                announcement=announcement, student=request.user, file=file
            )
            return Response({"success": "File uploaded successfully."}, status=201)
    except Announcement.DoesNotExist:
        return Response({"error": "Announcement not found."}, status=404)
    return Response({"error": "Invalid request."}, status=400)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Group, StudentMarking

@api_view(['GET'])
def get_groups(request):
    # Fetch all groups and their details
    groups = Group.objects.all()
    group_data = []
    evaluators = CustomUser.objects.filter(user_type="evaluation_member")
    for group in groups:
        members = []
        for member in group.members.all():
            student_marks = StudentMarking.objects.filter(student=member)
            each_evaluator_marks = StudentMarking.objects.filter(student=member,evaluator = request.user.id)
            # Calculate aggregated marks (average of all evaluators' marks)
            total_marks = sum([mark.marks_obtained for mark in student_marks])
            total_marks_each_evaluator = sum([mark.marks_obtained for mark in each_evaluator_marks])
            average_marks = total_marks / len(evaluators)
            members.append({
                "id": member.id,
                "name": member.first_name + " " + member.last_name,
                "username": member.username,
                "section": member.section.name,  # Assuming you have a section attribute
                "total_marks": total_marks_each_evaluator,
                "marks": average_marks
            })
        
        group_data.append({
            "id": group.id,
            "name": group.name,
            "members": members
        })

    return Response({"groups": group_data})



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Evaluation, Group

class GetEvaluationsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, student_id):
        try:
            student = get_object_or_404(CustomUser, id=student_id, user_type='student')
            
            # Fetch the evaluations based on the student
            evaluations = Evaluation.objects.filter(studentmarking__student=student)
            evaluation_data = []

            for evaluation in evaluations:
                criteria = evaluation.criteria.all()
                criteria_data = [
                    {"id": criterion.id, "name": criterion.name, "max_marks": criterion.marks}
                    for criterion in criteria
                ]
                evaluation_data.append({
                    "id": evaluation.id,
                    "name": evaluation.name,
                    "criteria": criteria_data,
                })
            
            return Response({"evaluations": evaluation_data})
        except Group.DoesNotExist or CustomUser.DoesNotExist:
            return Response({"error": "Group or Student not found"}, status=404)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Evaluation, EvaluationCriteria, StudentMarking

class EvaluationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        evaluations = Evaluation.objects.all()
        data = [
            {
                'id': evaluation.id,
                'name': evaluation.name
            }
            for evaluation in evaluations
        ]
        return Response({'evaluations': data})


class EvaluationCriteriaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, evaluation_id):
        evaluation = Evaluation.objects.get(id=evaluation_id)
        criteria = EvaluationCriteria.objects.filter(evaluation=evaluation)
        data = [
            {
                'id': criterion.id,
                'name': criterion.name,
                'max_marks': criterion.marks
            }
            for criterion in criteria
        ]
        return Response({'criteria': data})


class SubmitMarksView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, student_id, evaluation_id):
        evaluation = Evaluation.objects.get(id=evaluation_id)
        student = CustomUser.objects.get(id=student_id)
        marks_data = request.data.get('marks', [])
        evaluator = CustomUser.objects.get(id=request.user.id)

        for mark in marks_data:
            criterion_id = mark.get('criterion_id')
            marks_obtained = mark.get('marks_obtained')

            # Save or update the marks for each criterion
            StudentMarking.objects.update_or_create(
                student = student,
                evaluation=evaluation,
                criterion_id=criterion_id,
                evaluator=evaluator,
                defaults={'marks_obtained': marks_obtained}
            )

        return Response({'message': 'Marks updated successfully!'})



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import StudentMarking
from .serializers import StudentMarkingSerializer

class EvaluationStudentMarksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, evaluation_id, student_id):
        try:
            # Get the current evaluator
            evaluator = request.user
            
            # Fetch marks for the given evaluation, student, and evaluator
            marks = StudentMarking.objects.filter(
                evaluation_id=evaluation_id, 
                student_id=student_id,
                evaluator=evaluator
            )
            
            # Serialize the data
            serialized_marks = [
                {
                    "criterion_id": mark.criterion.id,
                    "criterion_name": mark.criterion.name,
                    "marks_obtained": mark.marks_obtained,
                }
                for mark in marks
            ]
            
            return Response({"marks": serialized_marks}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from .serializers import AnnouncementSerializer

class GroupAnnouncementsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        try:
            group = Group.objects.get(id=group_id)
            announcements = group.announcements.all()
            data = {
                "group_id": group.id,
                "group_name": group.name,
                "announcements": AnnouncementSerializer(announcements, many=True).data
            }
            return Response(data, status=200)
        except Group.DoesNotExist:
            return Response({"error": "Group not found."}, status=404)
        

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Announcement, StudentFileUpload
from .models import Group  # Assuming you have a Group model

User = get_user_model()
class GroupAnnouncementFilesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        try:
            # Get the group and its members
            group = Group.objects.get(id=group_id)
            students = group.members.filter(user_type='student')

            # Fetch announcements related to the group
            announcements = Announcement.objects.filter()  # Parentheses added here

            result = []
            for announcement in announcements:
                uploaded_files = StudentFileUpload.objects.filter(
                    announcement=announcement,
                    student__in=students
                )

                # Collect file data
                files = [
                    {
                        "student_id": file.student.id,
                        "student_name": f"{file.student.first_name} {file.student.last_name}",
                        "file_url": request.build_absolute_uri(file.file.url),
                        "uploaded_at": file.uploaded_at
                    }
                    for file in uploaded_files
                ]

                result.append({
                    "id": announcement.id,
                    "title": announcement.title,
                    "description": announcement.description,
                    "files": files if files else None
                })

            return Response({"group_id": group_id, "announcements": result}, status=200)
        except Group.DoesNotExist:
            return Response({"error": "Group not found."}, status=404)







# evaluations/views.py

from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import Evaluation
from .serializers import EvaluationResultSerializer

class StudentEvaluationResultsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = EvaluationResultSerializer

    def get_queryset(self):
        user = self.request.user
        print(f"Fetching evaluation results for user: {user.username}")
        queryset = Evaluation.objects.filter(
            studentmarking__student=user
        ).distinct().order_by('-studentmarking__evaluated_at')
        print(f"Found {queryset.count()} evaluations")
        return queryset

    def list(self, request, *args, **kwargs):
        print("Processing list request")
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            print(f"Returning {len(data)} evaluations")
            return self.get_paginated_response(data)
        serializer = self.get_serializer(qs, many=True)
        data = serializer.data
        print(f"Returning {len(data)} evaluations (non-paginated)")
        return Response({ 'evaluations': data })

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Settings
from .serializers import (
    StudentRegistrationSerializer,
    EvaluatorRegistrationSerializer,
    CoordinatorRegistrationSerializer
)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_student(request):
    settings = Settings.objects.first()
    if not settings or not settings.student_registration_open:
        return Response(
            {"detail": "Student registration is currently closed."},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = StudentRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"detail": "Student registered successfully."},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_evaluator(request):
    settings = Settings.objects.first()
    if not settings or not settings.evaluation_registration_open:
        return Response(
            {"detail": "Evaluator registration is currently closed."},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = EvaluatorRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"detail": "Evaluator registered successfully."},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_coordinator(request):
    settings = Settings.objects.first()
    if not settings or not settings.coordinator_registration_open:
        return Response(
            {"detail": "Coordinator registration is currently closed."},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = CoordinatorRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"detail": "Coordinator registered successfully."},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
