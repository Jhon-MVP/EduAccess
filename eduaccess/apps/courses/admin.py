from django.contrib import admin
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.forms import Textarea
from .models import (
    Course, AcademicTerm, CourseOffering, Enrollment,
    Module, Material, ModuleProgress, Content
)

User = get_user_model()

class ContentInline(admin.StackedInline):
    model = Content
    extra = 1
    classes = ['collapse']
    ordering = ('order',)
    fieldsets = (
        ("Configuración del Bloque", {
            'fields': (('order', 'content_type'), 'title'),
        }),
        ("Contenido", {
            'fields': ('text_content', 'video_url', 'file_upload'),
        }),
    )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 15, 'style': 'width: 90%; font-family: monospace;'})},
    }

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "credits", "active", "preview_image")
    readonly_fields = ("preview_image",)
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:80px;border-radius:10px;" />', obj.image.url)
        return "Sin imagen"

@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "active")

@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ("course", "term", "published")
    filter_horizontal = ("teachers",)
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "teachers":
            kwargs["queryset"] = User.objects.filter(userprofile__role="TEACHER")
        return super().formfield_for_manytomany(db_field, request, **kwargs)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "offering", "enrolled_at", "active")
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            kwargs["queryset"] = User.objects.filter(userprofile__role="STUDENT")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "offering", "order")
    inlines = [ContentInline]

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "content_type", "order")
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 20, 'style': 'width: 90%;'})},
    }
    fields = ('module', 'title', 'content_type', 'text_content', 'video_url', 'file_upload', 'order',
              'ai_accessibility_text', 'is_processed_by_ia')
    readonly_fields = ('is_processed_by_ia',)

admin.site.register(Material)
admin.site.register(ModuleProgress)