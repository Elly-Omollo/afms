import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from shortuuid.django_fields import ShortUUIDField
# Create your models here.


def user_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" %(instance.user.id, filename)
    return "user_{0}/{1}".format(instance.user.id, filename)


GENDER = [
    ("female","female"),
    ("male","male"),
    ("other","other"),
]

IDENTITY_TYPE = (
    ("1","National ID"),
    ("2","Birth certificate"),
    ("3","Passport"),
)



class User(AbstractUser):
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, name=False,blank=False)
    username = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=100,null=True, blank= True)
    gender = models.CharField(max_length=20, choices=GENDER, default='other')
    user_type = models.CharField(max_length=50, choices=[('buyer', 'Buyer'), ('farm_owner', 'Farm owner')], default='farm_owner')
    is_verified = models.BooleanField(default=False)

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class OTPVerification(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_otp(self):
        return str(random.randint(100000, 999999))

    
class Profile(models.Model):
    pid = ShortUUIDField(length = 7, max_length = 200, alphabet="abcdefghijklmnopqrstuvwxyz123")
    image = models.FileField(upload_to = user_directory_path, default="default.jpg", null = True, blank = True)
    full_name = models.CharField(max_length=200, blank=True,null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    country = models.CharField(max_length=100, null= True, blank = True)
    city = models.CharField(max_length=100, null= True, blank = True)
    state = models.CharField(max_length=100, null= True, blank = True)
    address = models.CharField(max_length=100, null= True, blank = True)

    datecreated = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['datecreated']

    def save(self, *args, **kwargs):
        if not self.full_name:  
            self.full_name = f"{self.user.first_name} {self.user.last_name}"
        super(Profile, self).save(*args, **kwargs)    


    def __str__(self):
        return f"{self.user.username}"
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance) 


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)