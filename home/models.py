from django.db import models
from accounts.models import CustomUser


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField()

    def __str__(self):
        return self.user.username

class test_cases(models.Model):
    Test_Name = models.CharField(max_length=30,null=True, blank=True)
    input_data = models.TextField(max_length = 1000, null=True, blank=True)
    output_data = models.TextField(max_length = 1000, null=True, blank=True)
    prblm_id = models.ForeignKey("problems",null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.Test_Name}"


class problems(models.Model):
    DIFF_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    prblmname = models.CharField(max_length = 30)
    statement = models.CharField(max_length=3000)
    sip = models.CharField(max_length=50)
    sop = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=10, choices=DIFF_CHOICES, default='Easy')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.prblmname}"
        return f"{self.statement}"


class CodeSubmission(models.Model):
    language = models.CharField(max_length=100)
    code = models.TextField()
    input_data = models.TextField(null=True,blank=True)
    output_data = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)    


class UserSubmission(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)