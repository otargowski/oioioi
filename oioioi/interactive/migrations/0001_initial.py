# Generated by Django 4.2.8 on 2024-04-05 10:52

from django.db import migrations, models
import django.db.models.deletion
import oioioi.filetracker.fields
import oioioi.problems.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('problems', '0031_auto_20220328_1124'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interactor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exe_file', oioioi.filetracker.fields.FileField(blank=True, max_length=255, null=True, upload_to=oioioi.problems.models.make_problem_filename, verbose_name='interactive executable file')),
                ('problem', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='problems.problem')),
            ],
            options={
                'verbose_name': 'interactive executable file',
                'verbose_name_plural': ('interactive executable files',),
            },
        ),
    ]