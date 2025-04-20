from django.db import models
from userauth.models import User
from shortuuid.django_fields import ShortUUIDField


FARMTYPES = (
    ('1','crop'),
    ('2','livestock'),
    ('3','poultry'),
)

FARMSIZE =(
    ('1','small scale'),
    ('2','large scale'),
)

RATINGS = [
    (1, '1 Star'),
    (2, '2 Stars'),
    (3, '3 Stars'),
    (4, '4 Stars'),
    (5, '5 Stars'),
]

class Farm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, choices=FARMTYPES, null=False, blank=False)
    location = models.CharField(max_length=100, null=False, blank=False)
    size = models.CharField(max_length=100, choices=FARMSIZE, null=False, blank=False)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('maintenance', 'Under Maintenance')], default='active')
    manager = models.ForeignKey(User, related_name='managed_farms', null=True, blank=True, on_delete=models.SET_NULL)

    def get_type_display(self):
        return dict(FARMTYPES).get(self.type, "Unknown")

    def get_size_display(self):
        return dict(FARMSIZE).get(self.size, "Unknown")

    class Meta:
        verbose_name_plural = 'Farms'
    
    def __str__(self):
        return f"{self.get_type_display()} farm for {self.user.username}"



class Product(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')
    price = models.DecimalField(decimal_places=2, default=0.00, max_digits=10)
    quantity = models.PositiveIntegerField(default=0)  # Track product stock
    category = models.CharField(max_length=100, choices=[('livestock', 'Livestock'), ('crops', 'Crops'), ('poultry', 'Poultry')], default='crops')
    is_available = models.BooleanField(default=True)  # Track if the product is for sale or sold out
    
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
    last_serviced = models.DateTimeField(null=True, blank=True)
    gps_location = models.CharField(max_length=100, null=True, blank=True)  # Optional location tracking

    class Meta:
        verbose_name_plural = 'Vehicles'

    def __str__(self):
        return f"{self.vehicle_type} for {self.owner.username}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="abcdefghijklmnopqrstuvwxyz123")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    destination = models.CharField(max_length=100)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('processing', 'Processing'), ('shipped', 'Shipped')], default='pending')
    payment_status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    total_amount = models.DecimalField(decimal_places=2, max_digits=10)  # Automatically calculate total price

    class Meta:
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order for {self.user.email} - {self.order_id}"

    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_amount = self.product.price * self.quantity
        super().save(*args, **kwargs)




class customer_review(models.Model):
    customer_name = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    rating = models.IntegerField(default='5', choices=RATINGS) 
    date = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.customer_name.username}'
    
    def likes_count(self):
        return self.reactions.filter(reaction='like').count()

    def dislikes_count(self):
        return self.reactions.filter(reaction='dislike').count()
    

class ReviewComment(models.Model):
    review = models.ForeignKey(customer_review, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.review.id}"


class ReviewReaction(models.Model):
    REACTION_CHOICES = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )

    review = models.ForeignKey(customer_review, related_name='reactions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=7, choices=REACTION_CHOICES)

    class Meta:
        unique_together = ('review', 'user')  # 1 reaction per user per review

    def __str__(self):
        return f"{self.user.username} - {self.reaction} on {self.review.id}"
    




class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} on {self.date} ({self.start_time}-{self.end_time}"


