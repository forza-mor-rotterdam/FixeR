from apps.context.models import Context
from django.contrib import admin
from django.contrib.admin import AdminSite

AdminSite.site_title = "FixeR Admin"
AdminSite.site_header = "FixeR Admin"
AdminSite.index_title = "FixeR Admin"


class ContextAdmin(admin.ModelAdmin):
    ...


admin.site.register(Context, ContextAdmin)
