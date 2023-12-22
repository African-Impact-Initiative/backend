from django.db import models

from django.conf import settings

def get_dir(instance, filename):
    return f'logos/{instance.name}/{filename}'

class Organization(models.Model):
    class Stages():
        IDEA = ('ID', 'Idea')
        DEVELOPMENT = ('DV', 'Development')
        PRELAUNCH = ('PR', 'Pre-Launch')
        POSTLAUNCH = ('PO', 'Post-Launch')

        CHOICES = [
            IDEA, DEVELOPMENT, PRELAUNCH, POSTLAUNCH
        ]

    class Funding():
        EXPLORE = ('EF', 'Exploring funding opportunities')
        PRESEED = ('PS', 'Pre-seed Stage')
        SEED = ('SR', 'Seed Round')
        SERIESA = ('SA', 'Series A Round')
        SERIESB = ('SB', 'Series B or Beyond')
        NOFUND = ('NF', 'Not Currently Seeking Funding')

        CHOICES = [
            EXPLORE, PRESEED, SERIESA, SEED, SERIESB, NOFUND
        ]

    class Challenges():
        SECURING = ('SF', 'Securing funding')
        DESIGN = ('PD', 'Product design and development')
        CUSTOMERS = ('BC', 'Building a customer base')
        PLANNING = ('BS', 'Business strategy and planning')
        MARKETING = ('MB', 'Marketing and branding')
        SCALING = ('SO', 'Scaling operations')
        FINANCES = ('MF', 'Managing finances')
        LEGAL = ('LR', 'Legal and regulatory compliance')
        HIRING = ('HT', 'Hiring talent')

        CHOICES = [
            SECURING, DESIGN, CUSTOMERS, PLANNING, MARKETING, SCALING, FINANCES, LEGAL, HIRING
        ]

    # meta data
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    # properties
    name = models.CharField(null=False, blank=False, max_length=100, unique=True)
    website = models.URLField(null=True, unique=True, blank=True, max_length=128)
    logo = models.ImageField(upload_to=get_dir, null=True, blank=True)
    identifier = models.CharField(null=False, blank=False, max_length=100, unique=True)
    industry = models.CharField(null=True, blank=True, max_length=100)
    linkedin = models.URLField(null=True, blank=True, max_length=100, unique=True)
    twitter = models.URLField(null=True, blank=True, max_length=100, unique=True)
    facebook = models.URLField(null=True, blank=True, max_length=100, unique=True)
    tagline = models.CharField(null=True, blank=True, max_length=150)

    stage = models.CharField(max_length=2, choices=Stages.CHOICES, default=Stages.IDEA, null=True, blank=True)
    funding = models.CharField(max_length=2, choices=Funding.CHOICES, null=True, blank=True)
    challenge1 = models.CharField(max_length=2, choices=Challenges.CHOICES, null=True, blank=True)
    challenge2 = models.CharField(max_length=2, choices=Challenges.CHOICES, null=True, blank=True)
    challenge3 = models.CharField(max_length=2, choices=Challenges.CHOICES, null=True, blank=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, on_delete=models.CASCADE)
