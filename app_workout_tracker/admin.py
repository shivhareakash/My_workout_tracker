from django.contrib import admin

from .models import Goal, Progress, Mistake, Topic
# Register your models here.
admin.site.register(Goal)
admin.site.register(Progress)
admin.site.register(Mistake)
admin.site.register(Topic)