from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# models.py

# models.py

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class Section(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    capacity = models.PositiveIntegerField(default=30)  # Limit the number of students in a section
    coordinator_in_charge = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'user_type': 'coordinator'}, related_name="coordinator_section")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name




class CustomUser(AbstractUser):
    user_type_choices = [
        ('student', 'Student'),
        ('evaluation_member', 'Evaluation Member'),
        ('coordinator', 'Coordinator'),
    ]
    user_type = models.CharField(max_length=20, choices=user_type_choices)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")  # Connect students with sections
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",  # Add unique related_name
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions_set",  # Add unique related_name
        blank=True,
    )

    def get_group_name(self):
        group = Group.objects.filter(members=self).first()  # Assumes one group per student
        return group.name if group else "No Group"

    def __str__(self):
        return self.username



class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(CustomUser, limit_choices_to={'role': 'student'})
    supervisor = models.ForeignKey(CustomUser, related_name='supervised_groups', null=True, on_delete=models.SET_NULL)
    is_approved = models.BooleanField(default=False)  # Add this line

'''
class Evaluation(models.Model):
    name = models.CharField(max_length=100)  # e.g., MID, FINAL
    created_by = models.ForeignKey(CustomUser, limit_choices_to={'role': 'coordinator'}, on_delete=models.CASCADE)
    # Add fields for evaluation criteria, etc.
'''

class Document(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    status = models.CharField(max_length=20, default='Pending')




from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Announcement(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'coordinator'})
    created_at = models.DateTimeField(auto_now_add=True)

class StudentFileUpload(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'student'})
    file = models.FileField(upload_to='student_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.first_name} - {self.announcement.title}"



class EvaluationCriteria(models.Model):
    name = models.CharField(max_length=100)
    marks = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Evaluation(models.Model):
    name = models.CharField(max_length=100)
    criteria = models.ManyToManyField(EvaluationCriteria)

    def __str__(self):
        return self.name

class StudentMarking(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'student'})
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    criterion = models.ForeignKey(EvaluationCriteria, on_delete=models.CASCADE)
    marks_obtained = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.student} - {self.evaluation.name} - {self.criterion.name}"


class Settings(models.Model):
    student_registration_open = models.BooleanField(default=True)
    evaluation_registration_open = models.BooleanField(default=True)
    coordinator_registration_open = models.BooleanField(default=True)

    def __str__(self):
        return "Registration Settings"