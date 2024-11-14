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


@student_required
def view_result(request):
    results = StudentMarking.objects.filter(student=request.user)
    return render(request, 'view_result.html', {'results': results})


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
    student_no = Section.objects.get(id=1).students.count()
    return render(request, 'manage_sections.html', {'sections': sections, 'student': student_no })

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
    # Get the selected student and evaluation
    student = get_object_or_404(CustomUser, id=student_id)
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)

    existing_marks = StudentMarking.objects.filter(student=student, evaluation=evaluation)
    if existing_marks.exists():
        messages.error(request, "Marks have already been uploaded for this evaluation.")
        return render(request, 'view_and_mark.html', {'student_id': student_id, 'evaluation_id': evaluation_id})  # Redirect to a suitable page
    # Fetch the evaluation criteria for the selected evaluation
    criteria = EvaluationCriteria.objects.filter(evaluation=evaluation)

    if request.method == 'POST':
        # Process the form submission for marks
        for criterion in criteria:
            mark = request.POST.get(f'criteria_marks_{criterion.id}')
            if mark:
                # Save the mark in StudentMarking model
                StudentMarking.objects.create(
                    student=student,
                    evaluation=evaluation,
                    criterion=criterion,
                    marks_obtained=mark
                )
        messages.success(request, "Marks uploaded successfully.")
        return redirect('view_marks', student_id=student.id, evaluation_id=evaluation.id)

    return render(request, 'evaluation_criteria.html', {
        'student': student,
        'evaluation': evaluation,
        'criteria': criteria
    })


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


@evaluation_panel_required
def mark_section(request, section_id):
    section = Section.objects.get(id=section_id)
    students = CustomUser.objects.filter(section=section)
    return render(request, 'mark_section.html', {'section': section, 'students': students})

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
    return render(request, 'add_marks.html', {'student': student, 'evaluation': evaluation, 'criteria': criteria})

@evaluation_panel_required
def submit_marks(request, student_id, evaluation_id):
    student = get_object_or_404(CustomUser, id=student_id, user_type='student')
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    criteria = EvaluationCriteria.objects.filter(evaluation=evaluation)

    if request.method == "POST":
        for criterion in criteria:
            # Retrieve the marks for each criterion from the form
            marks_obtained = request.POST.get(f'marks_{criterion.id}')
            
            # Save the marks for each criterion in the StudentMarking model
            StudentMarking.objects.create(
                student=student,
                evaluation=evaluation,
                criterion=criterion,
                marks_obtained=marks_obtained
            )
        
        # Redirect to the mark section page after saving marks
        return redirect('mark_section', section_id=student.section.id)
    
    # Render the marks entry form for each criterion if GET request
    return render(request, 'add_marks.html', {
        'student': student,
        'evaluation': evaluation,
        'criteria': criteria
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