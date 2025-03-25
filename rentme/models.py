from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.email

class Property(models.Model):
    PROPERTY_TYPES = (
        ('pg', 'PG'),
        ('room', 'Room'),
    )
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    property_type = models.CharField(max_length=4, choices=PROPERTY_TYPES)
    
    # Common Fields
    location = models.CharField(max_length=255)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.CharField(max_length=100)
    details = models.TextField(max_length=500, blank=True)
    image1 = models.ImageField(upload_to='property_images/', null=True, blank=True)
    image2 = models.ImageField(upload_to='property_images/', null=True, blank=True)
    image3 = models.ImageField(upload_to='property_images/', null=True, blank=True)
    
    # PG Specific Fields
    pg_name = models.CharField(max_length=100, blank=True)
    pg_room_type = models.CharField(max_length=20, blank=True)
    pg_capacity = models.PositiveIntegerField(null=True, blank=True)
    pg_wifi = models.BooleanField(default=False)
    pg_meals = models.BooleanField(default=False)
    pg_ac = models.BooleanField(default=False)
    pg_laundry = models.BooleanField(default=False)
    pg_security = models.BooleanField(default=False)
    pg_power = models.BooleanField(default=False)
    pg_parking = models.BooleanField(default=False)
    pg_meal_type = models.CharField(max_length=20, blank=True)
    pg_tenants = models.CharField(max_length=20, blank=True)
    
    # Room Specific Fields
    room_title = models.CharField(max_length=100, blank=True)
    room_size = models.CharField(max_length=20, blank=True)
    room_floor = models.PositiveIntegerField(null=True, blank=True)
    room_bathroom = models.BooleanField(default=False)
    room_balcony = models.BooleanField(default=False)
    room_furnished = models.BooleanField(default=False)
    room_kitchen = models.BooleanField(default=False)
    room_light = models.BooleanField(default=False)
    room_wardrobe = models.BooleanField(default=False)
    room_parking = models.BooleanField(default=False)
    room_bathroom_type = models.CharField(max_length=20, blank=True)
    room_tenants = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.property_type.upper()} - {self.location} by {self.seller.email}"