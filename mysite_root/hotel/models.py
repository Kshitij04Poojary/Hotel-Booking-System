from django.db import models
from django.contrib.auth.models import User,AbstractBaseUser,BaseUserManager, PermissionsMixin
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.utils import timezone
# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **other_fields):
        if not email:
            raise ValueError('User must enter email')
        email = self.normalize_email(email)
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_admin', True)
        other_fields.setdefault('is_verified',True)
        self.is_staff = True
        self.is_superuser=True
        self.set_password=password

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **other_fields)

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.room_number

class CustomUser(AbstractBaseUser, PermissionsMixin):
    #user_id = models.UUIDField(default=uuid.uuid4, auto_created=True, primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    dob = models.DateField(null=True)
    address = models.TextField(max_length=500,default='123,Main Street')
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    
    def __str__(self):
        return self.email


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    guest_name = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"Booking for {self.guest_name} - Room {self.room.room_number}"



