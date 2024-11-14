# Generated by Django 5.0.1 on 2024-11-07 15:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_announcement_studentfileupload'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluationCriteria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('marks', models.PositiveIntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='evaluation',
            name='created_by',
        ),
        migrations.AddField(
            model_name='evaluation',
            name='criteria',
            field=models.ManyToManyField(to='main.evaluationcriteria'),
        ),
        migrations.CreateModel(
            name='StudentMarking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marks_obtained', models.PositiveIntegerField()),
                ('criterion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.evaluationcriteria')),
                ('evaluation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.evaluation')),
                ('student', models.ForeignKey(limit_choices_to={'user_type': 'student'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
