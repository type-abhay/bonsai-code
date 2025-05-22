from django.db import models

# Create your models here.

class problems(models.Model):
    prblmname = models.CharField(max_length = 30)
    statement = models.CharField(max_length=3000)
    
    def __str__(self):
        return f"{self.prblmname}"
        return f"{self.statement}"