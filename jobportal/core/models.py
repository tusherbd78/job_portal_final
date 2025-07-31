from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('employer', 'Employer'),
        ('applicant', 'Applicant'),
    )
                                        
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    experience_years = models.IntegerField(blank=True, null=True)

    
class Job(models.Model):
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField()
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['job', 'applicant'], name='unique_application_per_job_per_user')
        ]


class EducationalQualification(models.Model):
    DEGREE_CHOICES = [
        ('school', 'School'), ('college', 'College'), ('diploma', 'Diploma'),
        ('graduation', 'Graduation'), ('masters', 'Masters'), ('phd', 'PhD'),
        ('postdoc', 'Post Doc')
    ]
    RESULT_CHOICES = [
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'), ('D', 'D')
    ]
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='qualifications')
    degree = models.CharField(max_length=20, choices=DEGREE_CHOICES)
    result = models.CharField(max_length=2, choices=RESULT_CHOICES)
    institution = models.CharField(max_length=255, blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.applicant.username} - {self.degree} ({self.result})"





# class EducationalQualification(models.Model):
    # DEGREE_CHOICES = [
        # ('school', 'School'), ('college', 'College'), ('diploma', 'Diploma'),
        # ('graduation', 'Graduation'), ('masters', 'Masters'), ('phd', 'PhD'),
        # ('postdoc', 'Post Doc')
    # ]
    # RESULT_CHOICES = [
        # ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
        # ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        # ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'), ('D', 'D')
    # ]
    # applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='qualifications')
    # degree = models.CharField(max_length=20, choices=DEGREE_CHOICES)
    # result = models.CharField(max_length=2, choices=RESULT_CHOICES)
# 
    # def __str__(self):
        # return f"{self.applicant.username} - {self.degree} ({self.result})"
# 