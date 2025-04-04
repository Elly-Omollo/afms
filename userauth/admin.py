from django.contrib import admin
from .models import User, Profile
from django.utils.html import format_html

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    search_fields = ['email', 'username']
    list_display = ['username', 'full_name', 'email', 'phone', 'gender', 'is_verified']

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    full_name.short_description = 'Full Name'  # This will be the column name in the admin

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__email']
    list_display = ['user_full_name', 'user', 'image_tag']
    
    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    
    user_full_name.short_description = 'Full Name'

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="30" height="30" style="border-radius: 50%;" />', obj.image.url)
        return "No Image"
    
    image_tag.short_description = 'Profile Picture'

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
