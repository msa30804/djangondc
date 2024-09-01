from django.db import models
from django.contrib.auth.models import User

class Originate(models.Model):
    ndc_no = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    appt = models.CharField(max_length=50)
    dept = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    cleared_by = models.ManyToManyField(User, related_name='cleared_requests', blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ndc_no} - {self.name}"

    def check_completion(self):
        # Check if all 13 other departments have cleared the request
        if self.cleared_by.count() == 13:
            self.is_completed = True
            self.save()
