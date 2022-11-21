from django.contrib import admin
from .models import Cart, CartItem
# Register your models here.
class CartAdming(admin.ModelAdmin):
    list_display = ('cart_id','date_added')

class CartItemAdming(admin.ModelAdmin):
    list_display = ('product','cart', 'quantity', 'is_active')

admin.site.register(Cart, CartAdming)
admin.site.register(CartItem,CartItemAdming)
