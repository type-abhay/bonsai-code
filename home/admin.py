from django.contrib import admin
from home.models import problems
from home.models import CodeSubmission
from home.models import test_cases, Profile
# Register your models here.

admin.site.register(problems)
admin.site.register(CodeSubmission)
admin.site.register(test_cases)
admin.site.register(Profile)