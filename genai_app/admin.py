from django.contrib import admin
from .models.genai import OrgProvider


class OrgProviderAdmin(admin.ModelAdmin):
    pass


admin.site.register(OrgProvider, OrgProviderAdmin)