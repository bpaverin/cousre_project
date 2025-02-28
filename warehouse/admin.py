from django.utils import timezone
from django.contrib import admin
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncDay
from django.utils.html import format_html
from django.utils.timesince import timesince
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponse
import csv
from django.utils.encoding import escape_uri_path
from django.template.response import TemplateResponse
from django.shortcuts import redirect
import json
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required

from .models import Supplier, Customer, Category, Material, Supply, Order


class SupplyInline(admin.TabularInline):
    model = Supply
    extra = 0
    fields = ['material', 'quantity', 'price_per_unit', 'total_cost', 'arrival_time']
    readonly_fields = ['total_cost']
    show_change_link = True


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    fields = ['material', 'quantity', 'total_sum', 'order_datetime']
    readonly_fields = ['order_datetime']
    show_change_link = True


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email']
    search_fields = ['name', 'contact_person']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email']
    search_fields = ['name', 'contact_person']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity', 'unit']
    list_filter = ['category']
    search_fields = ['name', 'description']
    change_list_template = 'admin/material_changelist.html'
    actions = ['export_to_csv']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('export-csv/', self.export_all_to_csv, name='export_all_materials'),
        ]
        return my_urls + urls

    def export_all_to_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=all_materials_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Наименование', 'Категория', 'Описание', 'Единица измерения', 'Количество'])
        
        for material in Material.objects.all():
            writer.writerow([
                material.name,
                material.category.name if material.category else '',
                material.description,
                material.unit,
                material.quantity
            ])
        
        return response

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=materials_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Наименование', 'Категория', 'Описание', 'Единица измерения', 'Количество'])
        
        for material in queryset:
            writer.writerow([
                material.name,
                material.category.name if material.category else '',
                material.description,
                material.unit,
                material.quantity
            ])
        
        return response
    
    export_to_csv.short_description = "Экспортировать выбранные материалы в CSV"

    def changelist_view(self, request, extra_context=None):
        # Получаем статистику изменения количества материалов
        materials = Material.objects.all()
        
        # Данные для круговой диаграммы количества материалов по категориям
        category_stats = (
            Material.objects
            .values('category__name')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')
        )

        # Данные для столбчатой диаграммы топ-10 материалов по количеству
        top_materials = (
            Material.objects
            .values('name', 'quantity', 'unit')
            .order_by('-quantity')[:10]
        )

        # Подготавливаем данные для графиков
        pie_data = {
            'labels': [],
            'data': []
        }

        bar_data = {
            'labels': [],
            'data': [],
            'units': []
        }

        for stat in category_stats:
            category_name = stat['category__name'] or 'Без категории'
            pie_data['labels'].append(category_name)
            pie_data['data'].append(float(stat['total_quantity'] or 0))

        for material in top_materials:
            bar_data['labels'].append(material['name'])
            bar_data['data'].append(float(material['quantity'] or 0))
            bar_data['units'].append(material['unit'])

        extra_context = extra_context or {}
        extra_context['pie_data'] = json.dumps(pie_data)
        extra_context['bar_data'] = json.dumps(bar_data)

        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ['material', 'supplier', 'quantity', 'arrival_time']
    list_filter = ['supplier', 'material', 'arrival_time']
    search_fields = ['supplier__name', 'material__name']


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        material = cleaned_data.get('material')

        if quantity and material:
            if quantity > material.quantity:
                raise ValidationError('Недостаточное количество материала на складе')
        return cleaned_data


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ['id', 'customer', 'material', 'quantity', 'total_sum', 'order_datetime']
    list_filter = ['customer', 'material', 'order_datetime']
    search_fields = ['customer__name', 'material__name']
    date_hierarchy = 'order_datetime'
    change_list_template = 'admin/order_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('dashboard/', admin_dashboard, name='warehouse_dashboard'),
        ]
        return my_urls + urls

    def changelist_view(self, request, extra_context=None):
        # Статистика за последний год
        last_year = timezone.now() - timedelta(days=365)
        
        monthly_stats = (
            Order.objects
            .filter(order_datetime__gte=last_year)
            .annotate(month=TruncMonth('order_datetime'))
            .values('month')
            .annotate(
                total_revenue=Sum('total_sum'),
                order_count=Count('id')
            )
            .order_by('month')
        )

        revenue_data = {
            'labels': [],
            'data': []
        }
        
        orders_data = {
            'labels': [],
            'data': []
        }

        for stat in monthly_stats:
            if stat['month']:
                month_name = stat['month'].strftime('%B %Y')
                revenue_data['labels'].append(month_name)
                revenue_data['data'].append(float(stat['total_revenue'] or 0))
                orders_data['labels'].append(month_name)
                orders_data['data'].append(stat['order_count'])

        if not revenue_data['labels']:
            current_month = timezone.now().strftime('%B %Y')
            revenue_data['labels'].append(current_month)
            revenue_data['data'].append(0)
            orders_data['labels'].append(current_month)
            orders_data['data'].append(0)

        extra_context = extra_context or {}
        extra_context['revenue_data'] = json.dumps(revenue_data)
        extra_context['orders_data'] = json.dumps(orders_data)

        return super().changelist_view(request, extra_context=extra_context)


# Создаем представление для дашборда
@staff_member_required
def admin_dashboard(request):
    # Статистика за последние 30 дней
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Данные по дням
    daily_stats = (
        Order.objects
        .filter(order_datetime__gte=thirty_days_ago)
        .annotate(day=TruncDay('order_datetime'))
        .values('day')
        .annotate(
            revenue=Sum('total_sum'),
            orders=Count('id')
        )
        .order_by('day')
    )

    # Топ материалов
    top_materials = (
        Material.objects
        .annotate(total_orders=Count('order'))
        .order_by('-total_orders')[:5]
    )

    # Подготовка данных для графиков
    days = []
    revenue = []
    orders = []
    
    for stat in daily_stats:
        days.append(stat['day'].strftime('%d.%m'))
        revenue.append(float(stat['revenue'] or 0))
        orders.append(stat['orders'])

    context = {
        'title': 'Статистика склада',
        'days': json.dumps(days),
        'revenue': json.dumps(revenue),
        'orders': json.dumps(orders),
        'top_materials': top_materials,
    }
    
    return TemplateResponse(request, 'admin/dashboard.html', context)


# Кастомизация админ-панели
admin.site.site_header = 'Система управления складом стройматериалов'
admin.site.site_title = 'Управление складом'
admin.site.index_title = 'Администрирование склада'

# Сначала отменим предыдущую регистрацию, если она была
admin.site.unregister(Order)

# Регистрируем остальные модели, если они еще не зарегистрированы
if not admin.site.is_registered(Material):
    admin.site.register(Material)
if not admin.site.is_registered(Supply):
    admin.site.register(Supply)
if not admin.site.is_registered(Customer):
    admin.site.register(Customer)
if not admin.site.is_registered(Supplier):
    admin.site.register(Supplier)
if not admin.site.is_registered(Category):
    admin.site.register(Category)
