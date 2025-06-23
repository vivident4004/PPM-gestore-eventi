from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'phone', 'is_adult')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'bio', 'date_of_birth', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone', 'bio', 'date_of_birth', 'address')}),
    )

    def is_adult(self, obj):
        return obj.is_adult()
    is_adult.boolean = True
    is_adult.short_description = 'Adult'

admin.site.register(CustomUser, CustomUserAdmin)
