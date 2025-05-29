from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    prblmname = models.CharField(max_length = 30)
    statement = models.CharField(max_length=3000)
    
    def __str__(self):
        return f"{self.prblmname}"
        return f"{self.statement}"


class CodeSubmission(models.Model):
    language = models.CharField(max_length=100)
    code = models.TextField()
    input_data = models.TextField(null=True,blank=True)
    output_data = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)    