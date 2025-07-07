from django.contrib import admin
from .models import donorregister,receiverregister
# Register your models here.

admin.site.register(donorregister)
admin.site.register(receiverregister)