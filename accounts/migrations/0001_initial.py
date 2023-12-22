# Generated by Django 4.2.3 on 2023-08-30 16:08

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=255, unique=True, verbose_name="email address"
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("is_verified", models.BooleanField(default=False)),
                ("staff", models.BooleanField(default=False)),
                ("admin", models.BooleanField(default=False)),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("joined", models.DateTimeField(auto_now_add=True)),
                ("terms_of_use", models.BooleanField(default=False)),
                ("linkedin", models.URLField(blank=True, null=True, unique=True)),
                (
                    "photo",
                    models.ImageField(
                        blank=True, null=True, upload_to=accounts.models.get_dir
                    ),
                ),
                ("role", models.TextField(blank=True, null=True)),
                ("country", models.TextField(blank=True, null=True)),
                ("bio", models.CharField(blank=True, max_length=300, null=True)),
            ],
            options={"abstract": False,},
        ),
    ]
