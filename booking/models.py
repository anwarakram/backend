from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'SYSTEM_ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('user_type') != 'SYSTEM_ADMIN':
            raise ValueError('Superuser must have user_type=SYSTEM_ADMIN.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('SYSTEM_ADMIN', 'System Admin'),
        ('BUSINESS_ADMIN', 'Business Admin'),
        ('STAFF', 'Staff'),
    )

    username = None
    email = models.EmailField('email address', unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    business = models.ForeignKey('Business', on_delete=models.CASCADE, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_type']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Business(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    duration = models.DurationField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.name} - {self.business.name}"

    class Meta:
        unique_together = ('business', 'name')

class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()

    def __str__(self):
        return f"{self.user.get_full_name()}"

class Appointment(models.Model):
    APPOINTMENT_STATUS = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    staff = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, limit_choices_to={'user_type': 'STAFF'})
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS, default='SCHEDULED')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")
        if self.start_time < timezone.now():
            raise ValidationError("Cannot book appointments in the past")
        
        # Check staff availability
        staff_appointments = Appointment.objects.filter(
            staff=self.staff,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)
        
        if staff_appointments.exists():
            raise ValidationError("The selected staff member is not available during this time slot")

        # Check for overlapping appointments
        overlapping_appointments = Appointment.objects.filter(
            business=self.business,
            service=self.service,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)
        
        if overlapping_appointments.exists():
            raise ValidationError("This time slot is already booked")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} - {self.service} - {self.start_time}"

class Schedule(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'STAFF'})
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.staff} - {self.date} {self.start_time}-{self.end_time}"