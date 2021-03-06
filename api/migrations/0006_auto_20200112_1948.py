# Generated by Django 3.0.1 on 2020-01-12 11:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20200112_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursedetail',
            name='course_detail',
        ),
        migrations.RemoveField(
            model_name='coursedetail',
            name='name',
        ),
        migrations.AddField(
            model_name='course',
            name='course_img',
            field=models.FileField(default='/static/course_img/default.png', upload_to=''),
        ),
        migrations.AddField(
            model_name='course',
            name='level',
            field=models.CharField(choices=[{1, '初级'}, {2, '中级'}, {3, '高级'}], default=1, max_length=1),
        ),
        migrations.AddField(
            model_name='coursedetail',
            name='recommend',
            field=models.ManyToManyField(to='api.Course'),
        ),
        migrations.AddField(
            model_name='coursedetail',
            name='why',
            field=models.CharField(default=1, max_length=128),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.ForeignKey(max_length=128, on_delete=django.db.models.deletion.CASCADE, to='api.Course')),
            ],
        ),
    ]
