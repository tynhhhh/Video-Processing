from django.contrib import admin
from .models import Videos,Subclips, ConcatVideo

# Register your models here.
admin.site.register(Videos)
admin.site.register(Subclips)
admin.site.register(ConcatVideo)