from django.contrib import admin
from django.contrib.auth.models import User
from .models import Link


class Link_register(admin.ModelAdmin):
    list_display = ['id', 'long_url', 'short_code', 'total_views', 'user', 'created_date']
    fields = ['user', 'long_url']
    ordering = ['id']
    raw_id_fields = ["user"]

    
admin.site.register(Link, Link_register)