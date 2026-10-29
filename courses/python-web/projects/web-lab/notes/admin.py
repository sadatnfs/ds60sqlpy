from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "owner", "version"]
    list_select_related = ["owner"]
    search_fields = ["title"]
