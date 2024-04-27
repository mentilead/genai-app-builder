from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, Organization, Team


class OrganizationAdmin(admin.ModelAdmin):
    """
    :class: OrganizationAdmin(admin.ModelAdmin) The OrganizationAdmin class is a subclass of admin.ModelAdmin that is
    used for displaying and managing organizations in the admin interface.
    """
    list_display = ['name', 'api_id']


# Register your models here.
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization']
    list_select_related = ['organization']


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("email", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
         ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Team, TeamAdmin)
