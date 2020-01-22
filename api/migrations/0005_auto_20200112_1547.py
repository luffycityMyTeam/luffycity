# Generated by Django 3.0.1 on 2020-01-12 07:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20200112_1546'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='course_detail',
        ),
        migrations.AddField(
            model_name='coursedetail',
            name='course_detail',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.CourseDetail'),
            preserve_default=False,
        ),
    ]
