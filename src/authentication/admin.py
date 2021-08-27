from django.contrib import admin

from authentication.models import CachedCredentials

admin.site.register(CachedCredentials)
