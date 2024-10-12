from django.contrib import admin
from .models import data,Transcript,Genomic
# Register your models here.
admin.site.register(data)
admin.site.register(Genomic)
admin.site.register(Transcript)