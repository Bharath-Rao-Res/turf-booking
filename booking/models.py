from django.db import models
from django.contrib.auth.models import User

class Booking(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    date = models.DateField()
    time_slot = models.CharField(max_length=50)

    def __str__(self):
        return self.name



class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # Common fields
    department = models.CharField(max_length=50)
    mobile = models.CharField(max_length=10)

    # Student only
    register_number = models.CharField(max_length=16, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class InternalBooking(models.Model):
    reg_no = models.CharField(max_length=16, null=True, blank=True)
    booking_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.reg_no