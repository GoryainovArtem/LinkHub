# Generated by Django 4.1.6 on 2023-03-26 09:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('links', '0003_auto_20230325_2051'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_group_project',
            field=models.BooleanField(default=False, help_text='Тип', verbose_name='групповой проект?'),
        ),
        migrations.AddField(
            model_name='project',
            name='is_private',
            field=models.BooleanField(choices=[(True, 'Private'), (False, 'Public')], default=False, verbose_name='is private project'),
        ),
        migrations.AlterField(
            model_name='head',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='дата создания'),
        ),
        migrations.AlterField(
            model_name='head',
            name='last_edit',
            field=models.DateTimeField(auto_now=True, verbose_name='дата последнего редактирования'),
        ),
        migrations.AlterField(
            model_name='link',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='дата создания'),
        ),
        migrations.AlterField(
            model_name='link',
            name='last_edit',
            field=models.DateTimeField(auto_now=True, verbose_name='дата последнего редактирования'),
        ),
        migrations.AlterField(
            model_name='project',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='дата создания'),
        ),
        migrations.AlterField(
            model_name='project',
            name='editor',
            field=models.ManyToManyField(related_name='projects_edit', to=settings.AUTH_USER_MODEL, verbose_name='оедакторы'),
        ),
        migrations.AlterField(
            model_name='project',
            name='last_edit',
            field=models.DateTimeField(auto_now=True, verbose_name='дата последнего редактирования'),
        ),
        migrations.AlterField(
            model_name='project',
            name='main_admin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_projects', to=settings.AUTH_USER_MODEL, verbose_name='создатель'),
        ),
    ]