from django import forms
from .models import Worker, Product, Order, Attendance
from django.utils import timezone


class WorkerForm(forms.ModelForm):
    join_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()
    )

    class Meta:
        model = Worker
        fields = ['full_name', 'position', 'phone_number', 'join_date']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'stock']


class OrderForm(forms.ModelForm):
    order_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()
    )

    class Meta:
        model = Order
        fields = ['worker', 'product', 'quantity', 'order_date', 'status']


class AttendanceForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()
    )

    class Meta:
        model = Attendance
        fields = ['worker', 'date', 'status']


class AttendanceBulkForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()
    )

    def __init__(self, *args, **kwargs):
        workers = kwargs.pop('workers', None)
        super(AttendanceBulkForm, self).__init__(*args, **kwargs)

        if workers:
            for worker in workers:
                field_name = f'worker_{worker.id}'
                self.fields[field_name] = forms.ChoiceField(
                    choices=Attendance.STATUS_CHOICES,
                    label=worker.full_name,
                    initial='present',
                    widget=forms.Select(attrs={'class': 'form-select'})
                )


class WorkerSearchForm(forms.Form):
    search = forms.CharField(required=False, label='Search by name or position')
    position = forms.ChoiceField(
        required=False,
        choices=[('', 'All Positions')] + [
            ('manager', 'Manager'),
            ('supervisor', 'Supervisor'),
            ('worker', 'Worker'),
            ('quality control', 'Quality Control'),
            ('packer', 'Packer'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )