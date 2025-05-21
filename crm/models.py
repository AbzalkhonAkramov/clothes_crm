from django.db import models
from django.utils import timezone


class Worker(models.Model):
    full_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    join_date = models.DateField()

    def __str__(self):
        return self.full_name


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('shirts', 'Shirts'),
        ('pants', 'Pants'),
        ('dresses', 'Dresses'),
        ('jackets', 'Jackets'),
        ('accessories', 'Accessories'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order #{self.id} - {self.product.name} by {self.worker.full_name}"

    def total_price(self):
        return self.quantity * self.product.price


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ['worker', 'date']

    def __str__(self):
        return f"{self.worker.full_name} - {self.date} - {self.status}"