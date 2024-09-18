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
    # Count users who have cleared the request
    cleared_users = self.cleared_by.count()

    # Determine the required number of users who should clear the request
    total_users = User.objects.exclude(
        Q(username='Adm') | Q(username='HR')
    ).count() + 2  # Adding 2 for ADM and HR

    if cleared_users >= total_users:
        self.is_completed = True
        self.is_completed_by_adm = self.is_completed_by_adm or self.is_completed_by_adm
        self.save()
