from django.contrib import admin
from .models import Gen
# Register your models here.
@admin.register(Gen)
class GenAdmin(admin.ModelAdmin):
    list_display = ('data', 'number',)