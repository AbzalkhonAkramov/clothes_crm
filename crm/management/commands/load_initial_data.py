from django.core.management.base import BaseCommand
from django.utils import timezone
from crm.models import Worker, Product, Order, Attendance
import random
from datetime import timedelta


class Command(BaseCommand):
    help = 'Loads initial data for the CRM application'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading initial data...')

        # Clear existing data
        Worker.objects.all().delete()
        Product.objects.all().delete()
        Order.objects.all().delete()
        Attendance.objects.all().delete()

        # Create workers
        workers = [
            Worker(
                full_name='John Smith',
                position='manager',
                phone_number='555-123-4567',
                join_date=timezone.now().date() - timedelta(days=365)
            ),
            Worker(
                full_name='Sarah Johnson',
                position='supervisor',
                phone_number='555-234-5678',
                join_date=timezone.now().date() - timedelta(days=300)
            ),
            Worker(
                full_name='Michael Brown',
                position='worker',
                phone_number='555-345-6789',
                join_date=timezone.now().date() - timedelta(days=250)
            ),
            Worker(
                full_name='Emily Davis',
                position='quality control',
                phone_number='555-456-7890',
                join_date=timezone.now().date() - timedelta(days=200)
            ),
            Worker(
                full_name='David Wilson',
                position='packer',
                phone_number='555-567-8901',
                join_date=timezone.now().date() - timedelta(days=150)
            ),
        ]

        Worker.objects.bulk_create(workers)
        self.stdout.write(self.style.SUCCESS(f'Created {len(workers)} workers'))

        # Create products
        products = [
            Product(
                name='Basic T-Shirt',
                category='shirts',
                price=19.99,
                stock=100
            ),
            Product(
                name='Slim Fit Jeans',
                category='pants',
                price=49.99,
                stock=75
            ),
            Product(
                name='Summer Dress',
                category='dresses',
                price=59.99,
                stock=50
            ),
            Product(
                name='Leather Jacket',
                category='jackets',
                price=149.99,
                stock=25
            ),
            Product(
                name='Cotton Socks (3-pack)',
                category='accessories',
                price=9.99,
                stock=200
            ),
        ]

        Product.objects.bulk_create(products)
        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))

        # Create orders
        orders = []
        status_choices = ['pending', 'completed', 'cancelled']

        for i in range(5):
            worker = random.choice(workers)
            product = random.choice(products)
            quantity = random.randint(1, 10)
            status = random.choice(status_choices)
            order_date = timezone.now().date() - timedelta(days=random.randint(0, 30))

            orders.append(Order(
                worker=worker,
                product=product,
                quantity=quantity,
                order_date=order_date,
                status=status
            ))

        Order.objects.bulk_create(orders)
        self.stdout.write(self.style.SUCCESS(f'Created {len(orders)} orders'))

        # Create attendance for today
        today = timezone.now().date()
        attendance_records = []
        status_choices = ['present', 'absent', 'late']

        for worker in workers:
            status = random.choice(status_choices)
            attendance_records.append(Attendance(
                worker=worker,
                date=today,
                status=status
            ))

        Attendance.objects.bulk_create(attendance_records)
        self.stdout.write(self.style.SUCCESS(f'Created {len(attendance_records)} attendance records'))

        self.stdout.write(self.style.SUCCESS('Initial data loaded successfully!'))