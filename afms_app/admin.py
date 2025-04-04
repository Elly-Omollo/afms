from django.contrib import admin
from django.utils.html import format_html
from .models import Farm,Product,Vehicle

class FarmAdmin(admin.ModelAdmin):
    list_display = ['type','user__username','size','location']
    search_fields = ['type']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','farm__type','price','image_tag']
    search_fields=['image','name']

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="30" height="30" style="border-radius: 50%;" />', obj.image.url)
        return "No Image"
    
    image_tag.short_description = 'Product Picture'


class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_type','color','state','image_tag','owner__username','is_available']
    search_fields = ['vehicle_type','owner__username']


    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="30" height="30" style="border-radius: 50%;" />', obj.image.url)
        return "No Image"
    
    image_tag.short_description = 'Vehicle Picture'


admin.site.register(Farm,FarmAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Vehicle,VehicleAdmin)