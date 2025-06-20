from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone', 'bio')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)