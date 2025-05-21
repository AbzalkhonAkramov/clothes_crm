from django.contrib import admin
from .models import Worker, Product, Order, Attendance


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'phone_number', 'join_date')
    list_filter = ('position', 'join_date')
    search_fields = ('full_name', 'position', 'phone_number')
    date_hierarchy = 'join_date'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name', 'category')
    list_editable = ('price', 'stock')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'worker', 'product', 'quantity', 'order_date', 'status', 'total_price')
    list_filter = ('status', 'order_date')
    search_fields = ('worker__full_name', 'product__name')
    date_hierarchy = 'order_date'

    def total_price(self, obj):
        return f"${obj.quantity * obj.product.price}"

    total_price.short_description = 'Total Price'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('worker', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('worker__full_name',)
    date_hierarchy = 'date'