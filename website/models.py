from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Q

class Originate(models.Model):
    hr_no = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    appt = models.CharField(max_length=50)
    dept = models.CharField(max_length=50, choices=[
        ('Adm', 'Adm'),
        ('Operations', 'Operations'),
        ('ICT', 'ICT'),
        ('HR', 'HR'),
        ('Marketing', 'Marketing'),
        ('Finance', 'Finance'),
        ('Media', 'Media'),
        ('Security', 'Security'),
        ('Planning', 'Planning'),
        ('Business', 'Business'),
        ('Sales', 'Sales'),
        ('BT', 'BT'),
        ('Engineers', 'Engineers')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_requests')
    cleared_by = models.ManyToManyField(User, related_name='cleared_requests', blank=True)
    is_completed = models.BooleanField(default=False)
    is_completed_by_adm = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.hr_no} - {self.name}"

    def check_completion(self):
        # Get all users except those in 'Adm' and 'HR' departments
        # Assuming that we check the users who cleared the request
        
        users_involved = User.objects.filter(
            created_requests__dept__in=['Adm', 'HR']
        ).distinct()

        # Check if all non-admin and non-HR users have cleared the request
        cleared_count = self.cleared_by.count()
        if cleared_count >= users_involved.count():
            self.is_completed = True
            self.save()
