# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class StudentRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'section', 'password1', 'password2', 'email', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        if commit:
            user.save()
        return user


class EvaluationPanelRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2', 'email', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'evaluation_member'
        if commit:
            user.save()
        return user


class CoordinatorRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2', 'email', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'coordinator'
        if commit:
            user.save()
        return user


from .models import EvaluationCriteria, Evaluation

class EvaluationCriteriaForm(forms.ModelForm):
    class Meta:
        model = EvaluationCriteria
        fields = ['name', 'marks']

class EvaluationForm(forms.ModelForm):
    criteria = forms.ModelMultipleChoiceField(
        queryset=EvaluationCriteria.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Evaluation
        fields = ['name', 'criteria']


from .models import Section

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name', 'description', 'coordinator_in_charge', 'capacity']

