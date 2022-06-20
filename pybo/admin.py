from django.contrib import admin
from .models import Question, Category

# Register your models here.

class QuestionAdmin(admin.ModelAdmin):
    search_fields = [ 'subject' ]

admin.site.register(Question, QuestionAdmin)

class CategoryAdmin(admin.ModelAdmin):
    search_fields = [ 'name' ]

admin.site.register(Category, CategoryAdmin)