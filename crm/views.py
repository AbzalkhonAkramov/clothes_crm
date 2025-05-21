from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
from django.contrib import messages
from .models import Worker, Product, Order, Attendance
from .forms import WorkerForm, ProductForm, OrderForm, AttendanceForm, AttendanceBulkForm, WorkerSearchForm


@login_required
def home(request):
    # Get statistics for the dashboard
    total_workers = Worker.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()

    # Today's attendance summary
    today = timezone.now().date()
    attendance_summary = {
        'present': Attendance.objects.filter(date=today, status='present').count(),
        'absent': Attendance.objects.filter(date=today, status='absent').count(),
        'late': Attendance.objects.filter(date=today, status='late').count(),
    }

    # Recent orders
    recent_orders = Order.objects.order_by('-order_date')[:5]

    # Low stock products
    low_stock_products = Product.objects.filter(stock__lt=10).order_by('stock')

    context = {
        'total_workers': total_workers,
        'total_products': total_products,
        'total_orders': total_orders,
        'attendance_summary': attendance_summary,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
    }

    return render(request, 'crm/home.html', context)


# Worker views
@login_required
def worker_list(request):
    form = WorkerSearchForm(request.GET)
    workers = Worker.objects.all().order_by('full_name')

    if form.is_valid():
        search_term = form.cleaned_data.get('search')
        position = form.cleaned_data.get('position')

        if search_term:
            workers = workers.filter(full_name__icontains=search_term)

        if position:
            workers = workers.filter(position=position)

    context = {
        'workers': workers,
        'form': form,
    }

    return render(request, 'crm/worker_list.html', context)


@login_required
def worker_detail(request, pk):
    worker = get_object_or_404(Worker, pk=pk)
    orders = Order.objects.filter(worker=worker).order_by('-order_date')
    attendance = Attendance.objects.filter(worker=worker).order_by('-date')[:10]

    context = {
        'worker': worker,
        'orders': orders,
        'attendance': attendance,
    }

    return render(request, 'crm/worker_detail.html', context)


@login_required
def worker_create(request):
    if request.method == 'POST':
        form = WorkerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Worker created successfully!')
            return redirect('worker_list')
    else:
        form = WorkerForm()

    return render(request, 'crm/worker_form.html', {'form': form, 'title': 'Add Worker'})


@login_required
def worker_update(request, pk):
    worker = get_object_or_404(Worker, pk=pk)

    if request.method == 'POST':
        form = WorkerForm(request.POST, instance=worker)
        if form.is_valid():
            form.save()
            messages.success(request, 'Worker updated successfully!')
            return redirect('worker_detail', pk=worker.pk)
    else:
        form = WorkerForm(instance=worker)

    return render(request, 'crm/worker_form.html', {'form': form, 'title': 'Update Worker'})


@login_required
def worker_delete(request, pk):
    worker = get_object_or_404(Worker, pk=pk)

    if request.method == 'POST':
        worker.delete()
        messages.success(request, 'Worker deleted successfully!')
        return redirect('worker_list')

    return render(request, 'crm/worker_confirm_delete.html', {'worker': worker})


# Product views
@login_required
def product_list(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'crm/product_list.html', {'products': products})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    orders = Order.objects.filter(product=product).order_by('-order_date')

    context = {
        'product': product,
        'orders': orders,
    }

    return render(request, 'crm/product_detail.html', context)


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'crm/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'crm/product_form.html', {'form': form, 'title': 'Update Product'})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')

    return render(request, 'crm/product_confirm_delete.html', {'product': product})


# Order views
@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'crm/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'crm/order_detail.html', {'order': order})


@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            # Check if there's enough stock
            product = order.product
            if product.stock < order.quantity:
                messages.error(request, f'Not enough stock available. Only {product.stock} units available.')
                return render(request, 'crm/order_form.html', {'form': form, 'title': 'Create Order'})

            # Update stock
            product.stock -= order.quantity
            product.save()

            order.save()
            messages.success(request, 'Order created successfully!')
            return redirect('order_list')
    else:
        form = OrderForm()

    return render(request, 'crm/order_form.html', {'form': form, 'title': 'Create Order'})


@login_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    original_quantity = order.quantity

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            updated_order = form.save(commit=False)

            # Adjust stock based on quantity change
            product = updated_order.product
            quantity_difference = updated_order.quantity - original_quantity

            if quantity_difference > 0 and product.stock < quantity_difference:
                messages.error(request, f'Not enough stock available. Only {product.stock} units available.')
                return render(request, 'crm/order_form.html', {'form': form, 'title': 'Update Order'})

            # Update stock
            product.stock -= quantity_difference
            product.save()

            updated_order.save()
            messages.success(request, 'Order updated successfully!')
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)

    return render(request, 'crm/order_form.html', {'form': form, 'title': 'Update Order'})


@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        # Restore stock
        product = order.product
        product.stock += order.quantity
        product.save()

        order.delete()
        messages.success(request, 'Order deleted successfully!')
        return redirect('order_list')

    return render(request, 'crm/order_confirm_delete.html', {'order': order})


# Attendance views
@login_required
def attendance_list(request):
    today = timezone.now().date()

    if request.GET.get('date'):
        try:
            selected_date = timezone.datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    attendance_records = Attendance.objects.filter(date=selected_date).order_by('worker__full_name')

    context = {
        'attendance_records': attendance_records,
        'selected_date': selected_date,
    }

    return render(request, 'crm/attendance_list.html', context)


@login_required
def attendance_bulk_create(request):
    workers = Worker.objects.all().order_by('full_name')
    today = timezone.now().date()

    if request.method == 'POST':
        form = AttendanceBulkForm(request.POST, workers=workers)

        if form.is_valid():
            date = form.cleaned_data['date']

            # Delete existing attendance records for the selected date
            Attendance.objects.filter(date=date).delete()

            # Create new attendance records
            for worker in workers:
                status = form.cleaned_data[f'worker_{worker.id}']
                Attendance.objects.create(worker=worker, date=date, status=status)

            messages.success(request, 'Attendance recorded successfully!')
            return redirect('attendance_list')
    else:
        # Check if attendance already exists for today
        existing_attendance = Attendance.objects.filter(date=today)

        if existing_attendance.exists():
            # Pre-populate form with existing data
            initial_data = {'date': today}
            for record in existing_attendance:
                initial_data[f'worker_{record.worker.id}'] = record.status

            form = AttendanceBulkForm(initial=initial_data, workers=workers)
        else:
            form = AttendanceBulkForm(workers=workers)

    return render(request, 'crm/attendance_bulk_form.html', {'form': form})