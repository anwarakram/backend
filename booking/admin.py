from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Business, Service, Customer, Appointment, Schedule

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('user_type', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Business', {'fields': ('business',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type', 'is_staff', 'is_active', 'business')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'created_at')
    search_fields = ('name', 'phone')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'duration', 'price')
    list_filter = ('business',)
    search_fields = ('name', 'business__name')

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth')
    search_fields = ('user__email', 'phone')

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('business', 'customer', 'service', 'staff', 'start_time', 'end_time', 'status')
    list_filter = ('business', 'status')
    search_fields = ('customer__user__email', 'service__name', 'staff__email')

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('business', 'staff', 'date', 'start_time', 'end_time')
    list_filter = ('business', 'date')
    search_fields = ('staff__email',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Business, BusinessAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Schedule, ScheduleAdmin)