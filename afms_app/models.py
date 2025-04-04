from django.db import models
from userauth.models import User


FARMTYPES = (
    ('1','crop'),
    ('2','livestock'),
    ('3','poultry'),
)

FARMSIZE =(
    ('1','small scale'),
    ('2','large scale'),
)

class Farm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, choices=FARMTYPES, null=False, blank=False)
    location = models.CharField(max_length=100, null=False, blank=False)
    size = models.CharField(max_length=100, choices=FARMSIZE, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Farms'
    def __str__(self):
        return f"{self.type} farm for {self.user.full_name}"
    


class Product(models.Model):
    name= models.CharField(max_length=100, null=False,blank=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')
    price = models.DecimalField(decimal_places=2, default=0.00, max_digits=10)
    
    class Meta:
        verbose_name_plural = 'Products'

    def __str__(self):
        return f"{self.name}"

class Vehicle(models.Model):
    vehicle_type = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    number_plate = models.CharField(max_length=20)
    state = models.CharField(max_length=50)
    image = models.ImageField(upload_to='vehicle_images')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Vehicles'

    def __str__(self):
        return f"{self.vehicle_type} for {self.owner.username}"    