from rest_framework import serializers
from .models import CustomUser, StudentFileUpload, Evaluation, EvaluationCriteria, Section, StudentMarking, Announcement, Group, Settings
from django.contrib.auth.password_validation import validate_password

class CustomUserSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='get_group_name', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'first_name', 'last_name', 'username', 'email',
            'phone_number', 'user_type', 'section', 'group_name'
        ]

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'description', 'coordinator', 'created_at']
        read_only_fields = ['id', 'coordinator', 'created_at']

class GroupSerializer(serializers.ModelSerializer):
    members = CustomUserSerializer(many=True)
    class Meta:
        model = Group
        fields = '__all__'

from rest_framework import serializers

class EvaluationCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCriteria
        fields = '__all__'

class EvaluationSerializer(serializers.ModelSerializer):
    criteria = EvaluationCriteriaSerializer(many=True)

    class Meta:
        model = Evaluation
        fields = '__all__'

class EvaluationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name', 'description', 'coordinator_in_charge', 'capacity']

class StudentMarkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMarking
        fields = ['id', 'student', 'evaluation', 'criterion', 'marks_obtained', 'evaluator']

class StudentFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFileUpload
        fields = ['id', 'file', 'student', 'announcement', 'submission_date']




# evaluations/serializers.py

from django.db.models import Sum
from rest_framework import serializers

from .models import Evaluation, EvaluationCriteria, StudentMarking

class CriterionResultSerializer(serializers.Serializer):
    name         = serializers.CharField()
    marks        = serializers.IntegerField()
    total_marks  = serializers.IntegerField()

class EvaluationResultSerializer(serializers.ModelSerializer):
    criteria     = serializers.SerializerMethodField()
    total_marks  = serializers.IntegerField(read_only=True)
    max_marks    = serializers.IntegerField(read_only=True)
    evaluated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model  = Evaluation
        fields = (
            'id', 'name', 'criteria',
            'total_marks', 'max_marks',
            'evaluated_at',
        )

    def get_criteria(self, evaluation):
        user = self.context['request'].user

        # for each criterion, get all evaluators' marks and calculate average
        out = []
        for crit in evaluation.criteria.all():
            # Get all marks for this criterion from different evaluators
            marks = (
                StudentMarking.objects
                .filter(student=user, evaluation=evaluation, criterion=crit)
                .values_list('marks_obtained', flat=True)
            )
            
            # Calculate average marks
            avg_marks = sum(marks) / len(marks) if marks else 0
            
            out.append({
                'name': crit.name,
                'marks': round(avg_marks, 2),  # Round to 2 decimal places
                'total_marks': crit.marks,
            })
        return out

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # compute total and max
        data['total_marks'] = round(sum(c['marks'] for c in data['criteria']), 2)
        data['max_marks']   = sum(c['total_marks'] for c in data['criteria'])

        # pick an evaluated_at: e.g. the latest marking timestamp
        latest = (
            instance.studentmarking_set
                    .filter(student=self.context['request'].user)
                    .order_by('-evaluated_at')
                    .first()
        )
        data['evaluated_at'] = latest.evaluated_at if latest else None

        return data

class RegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password1', 'password2', 'user_type']
        extra_kwargs = {
            'user_type': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            user_type=validated_data['user_type']
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user

class StudentRegistrationSerializer(RegistrationSerializer):
    def validate(self, attrs):
        attrs['user_type'] = 'student'
        return super().validate(attrs)

class EvaluatorRegistrationSerializer(RegistrationSerializer):
    def validate(self, attrs):
        attrs['user_type'] = 'evaluation_member'
        return super().validate(attrs)

class CoordinatorRegistrationSerializer(RegistrationSerializer):
    def validate(self, attrs):
        attrs['user_type'] = 'coordinator'
        return super().validate(attrs)
