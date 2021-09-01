from django.contrib import admin

from tasks.models import FailedProfileUpdateTask, LastUserProfileUpdate

admin.site.register(FailedProfileUpdateTask)
admin.site.register(LastUserProfileUpdate)
