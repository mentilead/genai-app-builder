from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Organization, Team, UserProfile, LLMAPIKey


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'api_id']


# Register your models here.
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization']
    list_select_related = ['organization']


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


class LLMAPIKeyAdmin(admin.ModelAdmin):
    pass



# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(LLMAPIKey, LLMAPIKeyAdmin)