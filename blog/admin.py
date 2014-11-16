from django.contrib import admin
from applib.mptt.admin import MPTTModelAdmin
from blog.models import Category, Tag, Entry

def model_delete(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()
model_delete.short_description = "Delete selected"

class CategoryAdmin(MPTTModelAdmin):
    fields = ('title', 'description', 'parent')
    list_display = ('title', 'slug', 'description')
    actions = [model_delete]

class TagAdmin(admin.ModelAdmin):
    fields = ('name',)
    list_display = ('name', 'slug')
    actions = [model_delete]

class EntryAdmin(admin.ModelAdmin):
    fields = ('title', 'content', 'hidden', 'pub_date', 'image', 'category', 'user', 'tags')
    list_display = ('title', 'slug', 'content', 'hidden', 'pub_date', 'image', 'category', 'user')
    actions = [model_delete]

admin.site.disable_action('delete_selected')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Entry, EntryAdmin)