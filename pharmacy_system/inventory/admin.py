from django.contrib import admin
from .models import Medication, CartItem, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    inlines = [OrderItemInline]

admin.site.register(Medication)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)