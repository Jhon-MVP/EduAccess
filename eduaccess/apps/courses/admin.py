from django.contrib import admin
from .models import Course, AcademicTerm, CourseOffering, Enrollment, Module, Material, ModuleProgress
from django.conf import settings

User = settings.AUTH_USER_MODEL


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "credits", "active")
    list_filter = ("active",)
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "active")
    list_filter = ("active",)
    ordering = ("-start_date",)


@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ("course", "term", "published")  # CORRECCIÓN: nombre real del campo
    list_filter = ("term", "published")
    search_fields = ("course__name", "course__code")
    filter_horizontal = ("teachers",)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "teachers":
            UserModel = db_field.remote_field.model
            kwargs["queryset"] = UserModel.objects.filter(
                userprofile__role="TEACHER"
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "offering", "enrolled_at", "active")
    list_filter = ("active", "offering__term")
    search_fields = ("student__username",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            UserModel = db_field.remote_field.model
            kwargs["queryset"] = UserModel.objects.filter(
                userprofile__role="STUDENT"
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "offering", "order")
    list_filter = ("offering__term",)
    ordering = ("offering", "order")


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "material_type",
        "module",
        "has_text",
        "has_alt_text",
        "has_captions",
        "uploaded_at",
    )
    list_filter = ("material_type",)
    search_fields = ("title",)

@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "module", "completed", "last_accessed")
    list_filter = ("completed",)
    search_fields = ("user__username", "module__title")
