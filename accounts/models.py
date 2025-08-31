from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
from django.conf import settings

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, username,email, password = None):
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError('Email is required')
        user = self.model(username = username, email = self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username,email, password):
        user = self.create_user(username =username, email = email,  password = password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using = self._db)
        return user
    

class CustomUser(AbstractBaseUser,PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(unique=True)
    points = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return self.username

class Role(models.Model):
    name = models.CharField(max_length=25)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='roles')

    def __str__(self):
        return self.name
    

class VerifiedEmail(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)
    
    def __str__(self):
        return f"Verification for {self.user.username} - Code : {self.code}"

class Problem(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True , null=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=[("Easy" , 'Easy'), ("Medium" , 'Medium'), ("Hard" , 'Hard')] , default="Easy")
    input_format = models.TextField()
    output_format = models.TextField()
    constraints = models.TextField()
    sample_input = models.TextField()
    sample_output = models.TextField()
    points = models.IntegerField(default=0)
    time_limit = models.FloatField(default=1.5)
    memory_limit = models.IntegerField(default=130000)

    def __str__(self):
        return self.title
    
    def success_rate(self):
        total_submissions = self.submissions.count()
        if total_submissions == 0:
            return 0
        accepted_submissions = self.submissions.filter(status="Accepted").count()
        return round((accepted_submissions / total_submissions) * 100, 2)
    
    def save(self, *args , **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            num = 1
            while Problem.objects.filter(slug = unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num+=1
            self.slug = unique_slug
        super().save(*args, **kwargs)
    
class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='testcases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)

    def __str__(self):
        return f'Test case for {self.problem.title}'
    

class Submission(models.Model):
    STATUS_CHOICES = [
        ("PENDING" , 'Pending'),
        ("RUNNING" , 'Running'),
        ("ACCEPTED" , 'Accepted'),
        ("WRONG_ANSWER" , 'Wrong Answer'),
        ("TLE" , 'Time Limit Exceeded'),
        ("RE" , 'Runtime Error'),
        ("CE" , 'Compilation Error'),
        ("ERROR" , 'System Error'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem,related_name="submissions", on_delete=models.CASCADE)
    code = models.TextField()
    language_id = models.IntegerField()
    language_name = models.CharField(max_length=50, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    time = models.FloatField(null=True, blank=True)
    memory = models.IntegerField(null=True, blank=True)
    output = models.TextField(blank=True, null=True)
    token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Submitted to {self.problem.title}"
    

class SubmissionTestCaseResult(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="testcase_results")
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    output = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=55)
    time = models.FloatField(null=True, blank=True)
    memory = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.submission.user.username} - {self.testcase.problem.title} {'Sample' if self.testcase.is_sample else 'Hidden' }"


