# Generated by Django 4.2.3 on 2024-01-03 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_user_organizations_user_leadership_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='linkedin',
            field=models.URLField(blank=True, null=True),
        ),
    ]