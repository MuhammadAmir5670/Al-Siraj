# Generated by Django 3.0.8 on 2020-12-11 06:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0002_auto_20201210_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='trial',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Course'),
        ),
        migrations.AlterField(
            model_name='trial',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trial', to=settings.AUTH_USER_MODEL),
        ),
    ]
